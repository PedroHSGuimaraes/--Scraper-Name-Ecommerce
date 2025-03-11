import os
import logging
from config.settings import Settings
from domain.usecases.extract_contacts_usecase import ExtractContactsUseCase
from infrastructure.repositories.store_repository import StoreRepository
from infrastructure.web.html_fetcher import HtmlFetcher
from infrastructure.search.google_search_service import GoogleSearchService
from application.services.scraping_service import ScrapingService

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper_service_direct.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Executa o Scraper Service diretamente para uma lista de lojas"""
    logger.info("=== Inicializando Scraper Service ===")
    
    # 1. Carregar configurações
    settings = Settings()
    
    # 2. Criar repositório
    store_repository = StoreRepository()
    
    # 3. Criar serviços auxiliares
    html_fetcher = HtmlFetcher(settings.config.get("scraping", {}))
    google_search = GoogleSearchService(
        api_key=settings.get("google_api.api_key"),
        engine_id=settings.get("google_api.engine_id")
    )
    
    # 4. Criar caso de uso para extração de contatos
    phone_registry = {}  # Registro global para evitar duplicatas
    contact_extractor = ExtractContactsUseCase(phone_registry)
    
    # 5. Criar o Scraper Service
    scraping_service = ScrapingService(
        search_service=google_search,
        html_fetcher=html_fetcher,
        contact_extractor=contact_extractor,
        store_repository=store_repository,
        config=settings
    )
    
    # 6. Carregar lista de lojas
    lojas_para_processar = []
    try:
        # Tentar carregar de arquivo JSON
        if os.path.exists("lojas_oficiais_parcial.json"):
            lojas_data = store_repository.load_stores("lojas_oficiais_parcial.json")
            lojas_para_processar = [item.get("nome") for item in lojas_data if "nome" in item]
        else:
            # Lista manual para testes
            lojas_para_processar = [
                "Nike Store",
                "Samsung Brasil",
                "Apple Brasil",
                "Adidas Brasil"
            ]
    except Exception as e:
        logger.error(f"Erro ao carregar lista de lojas: {e}")
        return
    
    # 7. Processar cada loja
    resultados = []
    
    for i, nome_loja in enumerate(lojas_para_processar):
        logger.info(f"Processando loja {i+1}/{len(lojas_para_processar)}: {nome_loja}")
        
        # Executar scraping para a loja
        resultado = scraping_service.scrape_store(nome_loja)
        resultados.append(resultado)
        
        # Opcional: Salvar resultado individual
        if resultado.get('success', False):
            logger.info(f"✓ Obtidos dados de contato para '{nome_loja}'")
        else:
            logger.warning(f"✗ Falha ao processar '{nome_loja}': {resultado.get('error', 'Erro desconhecido')}")
    
    # 8. Salvar todos os resultados
    os.makedirs("resultados", exist_ok=True)
    store_repository.save_stores(resultados, "resultados/scraper_service_results.json")
    
    logger.info(f"=== Processamento concluído. {len(resultados)} lojas processadas ===")
    logger.info("Resultados salvos em 'resultados/scraper_service_results.json'")

if __name__ == "__main__":
    main()
