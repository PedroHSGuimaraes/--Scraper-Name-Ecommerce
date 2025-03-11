import os
import json
import sys
import logging

# Tentar configurar o console em UTF-8 (somente Windows)
if sys.platform == "win32":
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)  # Set input codepage to UTF-8
        kernel32.SetConsoleOutputCP(65001)  # Set output codepage to UTF-8
    except Exception:
        pass  # Ignorar se falhar

# Configurar logging com tratamento de erro para caracteres fora do padrão
class SafeLogFormatter(logging.Formatter):
    def format(self, record):
        try:
            return super().format(record)
        except UnicodeEncodeError:
            # Substituir caracteres problemáticos com alternativas ASCII
            record.msg = record.msg.encode('ascii', 'replace').decode('ascii')
            return super().format(record)

formatter = SafeLogFormatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler("scraper_parcial.log", encoding="utf-8")
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

# Verificar dependências necessárias
required_packages = ['requests', 'bs4', 'google-api-python-client']
missing_packages = []

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        missing_packages.append(package)

# Se houver pacotes faltando, instale-os
if missing_packages:
    logger.error(f"Dependências faltantes: {', '.join(missing_packages)}")
    logger.info("Tentando instalar automaticamente...")
    
    try:
        import subprocess
        for package in missing_packages:
            logger.info(f"Instalando {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        logger.info("Instalação concluída. Recarregando módulos...")
    except Exception as e:
        logger.error(f"Erro ao instalar dependências: {str(e)}")
        sys.exit(1)

# Pandas é opcional - tentar importar, mas não instalar automaticamente
pandas_available = False
try:
    import pandas as pd
    pandas_available = True
except ImportError:
    logger.warning("Pandas não está disponível. O CSV não será gerado.")

# Agora importa os módulos necessários
try:
    from config.settings import Settings
    from domain.usecases.extract_contacts_usecase import ExtractContactsUseCase
    from infrastructure.repositories.store_repository import StoreRepository
    from infrastructure.web.html_fetcher import HtmlFetcher
    from infrastructure.search.google_search_service import GoogleSearchService
    from application.services.scraping_service import ScrapingService
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {str(e)}")
    logger.error("Verifique se a estrutura de diretórios está correta e se os pacotes estão instalados.")
    sys.exit(1)

def main():
    """Processa empresas do arquivo lojas_oficiais_parcial.json"""
    logger.info("=== Iniciando processamento de lojas do arquivo parcial ===")
    
    # Configurar componentes
    try:
        settings = Settings()
        store_repo = StoreRepository()
        html_fetcher = HtmlFetcher()
        google_search = GoogleSearchService(
            api_key=settings.get("google_api.api_key"), 
            engine_id=settings.get("google_api.engine_id")
        )
        phone_registry = {}
        contact_extractor = ExtractContactsUseCase(phone_registry)
        scraping_service = ScrapingService(
            google_search, 
            html_fetcher, 
            contact_extractor, 
            store_repo, 
            settings
        )
    except Exception as e:
        logger.error(f"Erro ao inicializar componentes: {str(e)}")
        return

    # Carregar arquivo de lojas
    try:
        logger.info("Carregando lojas_oficiais_parcial.json...")
        with open("lojas_oficiais_parcial.json", "r", encoding="utf-8") as f:
            stores = json.load(f)
        
        if not isinstance(stores, list):
            logger.error("O arquivo não contém uma lista de lojas")
            return
            
        logger.info(f"Carregadas {len(stores)} lojas para processamento")
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo: {e}")
        return

    # Processar cada loja
    results = []
    for i, store in enumerate(stores):
        store_name = store.get('nome')
        if not store_name:
            logger.warning(f"Loja #{i+1} não tem nome definido, pulando...")
            continue
            
        logger.info(f"Processando loja {i+1}/{len(stores)}: {store_name}")
        try:
            result = scraping_service.scrape_store(store_name)
            results.append(result)
            
            # Verificar se conseguimos extrair dados - sem caracteres Unicode especiais
            if result.get('success', False):
                logger.info(f"[OK] Dados extraidos com sucesso para '{store_name}'")
            else:
                logger.warning(f"[FALHA] Nao foi possivel extrair dados para '{store_name}': {result.get('error', 'Erro desconhecido')}")
                
        except Exception as e:
            logger.error(f"Erro ao processar '{store_name}': {str(e)}")
            results.append({
                'success': False,
                'nome_loja': store_name,
                'error': str(e)
            })

    # Salvar resultados
    if not results:
        logger.warning("Nenhum resultado para salvar")
        return

    os.makedirs("resultados", exist_ok=True)
    output_file = "resultados/lojas_parcial_processadas.json"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f"Resultados salvos em {output_file}")
        
        # Criar também versão CSV para facilitar visualização, apenas se o pandas estiver disponível
        if pandas_available:
            try:
                flat_data = []
                for item in results:
                    if not item.get('success', False):
                        continue
                        
                    contacts = item.get('contacts', {})
                    row = {
                        'nome_loja': item.get('nome_loja', 'Desconhecido'),
                        'emails': ', '.join(contacts.emails if hasattr(contacts, 'emails') else []),
                        'telefones': ', '.join(contacts.phones if hasattr(contacts, 'phones') else []),
                    }
                    flat_data.append(row)
                    
                if flat_data:
                    df = pd.DataFrame(flat_data)
                    csv_file = "resultados/lojas_parcial_processadas.csv"
                    df.to_csv(csv_file, index=False)
                    logger.info(f"Versão CSV salva em {csv_file}")
            except Exception as e:
                logger.warning(f"Não foi possível criar versão CSV: {e}")
        else:
            logger.info("CSV não gerado pois pandas não está disponível")
    except Exception as e:
        logger.error(f"Erro ao salvar resultados: {e}")

if __name__ == "__main__":
    main()
