# Importação das bibliotecas necessárias
# logging: Para registrar informações e erros durante a execução
# Store: Nossa classe que representa uma loja e seus dados
import logging
from domain.entities.store import Store

class ProcessStoresUseCase:
    """
    Classe responsável por processar lojas e extrair suas informações
    
    Esta classe coordena todo o processo de:
    1. Carregar dados das lojas de um arquivo JSON
    2. Buscar o conteúdo HTML de cada loja
    3. Extrair informações de contato do HTML
    4. Salvar os resultados em um arquivo
    
    Utiliza três componentes principais:
    - html_fetcher: Para buscar e processar conteúdo HTML
    - contact_extractor: Para extrair informações de contato
    - store_repository: Para carregar e salvar dados das lojas
    """
    
    def __init__(self, html_fetcher, contact_extractor, store_repository):
        """
        Inicializa o caso de uso com seus componentes necessários
        
        Parâmetros:
            html_fetcher: Componente para buscar e processar HTML
            contact_extractor: Componente para extrair contatos
            store_repository: Componente para persistência de dados
        """
        # Componentes principais do caso de uso
        self.html_fetcher = html_fetcher          # Busca e processa HTML
        self.contact_extractor = contact_extractor # Extrai contatos
        self.store_repository = store_repository   # Gerencia dados
        
        # Configuração do logger para esta classe
        self.logger = logging.getLogger(__name__)
    
    def execute(self, json_file_path=None, output_file=None):
        """
        Executa o processamento completo das lojas
        
        Este método:
        1. Carrega os dados das lojas do arquivo JSON
        2. Para cada loja:
           - Busca o conteúdo HTML da URL
           - Extrai o texto do HTML
           - Extrai informações de contato
           - Registra sucesso ou falha
        3. Salva os resultados em um arquivo
        
        Parâmetros:
            json_file_path (str): Caminho do arquivo JSON com dados das lojas
            output_file (str): Caminho para salvar os resultados
            
        Retorna:
            list: Lista de objetos Store com os resultados do processamento
        """
        # Carrega os dados das lojas do arquivo JSON
        stores_data = self.store_repository.load_stores(json_file_path)
        if not stores_data:
            self.logger.error("Não foi possível carregar lojas de entrada")
            return []
            
        self.logger.info(f"Carregadas {len(stores_data)} lojas para processamento")
        
        # Lista para armazenar os resultados do processamento
        processed_stores = []
        
        # Processa cada loja individualmente
        for i, store_data in enumerate(stores_data):
            # Extrai informações básicas da loja
            store_name = store_data.get('nome', f"Loja {i+1}")  # Nome ou número
            store_url = store_data.get('url', '')               # URL da loja
            
            # Log do progresso
            self.logger.info(f"Processando loja {i+1}/{len(stores_data)}: {store_name}")
            
            # Verifica se tem URL para processar
            if not store_url:
                self.logger.warning(f"URL não encontrada para a loja: {store_name}")
                continue
                
            try:
                # Etapa 1: Buscar o conteúdo HTML da loja
                html_content = self.html_fetcher.fetch(store_url)
                
                # Verifica se conseguiu obter o HTML
                if not html_content:
                    self.logger.warning(f"Não foi possível obter conteúdo HTML da URL: {store_url}")
                    continue
                
                # Etapa 2: Extrair texto do HTML e buscar contatos
                html_text = self.html_fetcher.extract_text(html_content)
                contacts = self.contact_extractor.execute(html_text, store_url, store_name)
                
                # Etapa 3: Criar objeto Store com os dados extraídos
                store = Store(name=store_name, url=store_url)
                store.contact_info = contacts
                
                # Adiciona à lista de resultados
                processed_stores.append(store)
                
                # Log das informações extraídas
                phones_count = len(contacts.phones)
                self.logger.info(f"Extraídos {phones_count} telefones da loja {store_name}")
                
            except Exception as e:
                # Registra o erro no log
                self.logger.error(f"Erro ao processar loja {store_name}: {str(e)}")
                
                # Cria um objeto Store marcando a falha
                failed_store = Store(name=store_name, url=store_url)
                failed_store.success = False           # Marca como falha
                failed_store.error = str(e)           # Salva a mensagem de erro
                
                # Adiciona à lista de resultados
                processed_stores.append(failed_store)
        
        # Se foi especificado um arquivo de saída, salva os resultados
        if output_file:
            # Converte os objetos Store para dicionários
            stores_dict = [store.to_dict() for store in processed_stores]
            # Salva no arquivo especificado
            self.store_repository.save_stores(stores_dict, output_file)
        
        return processed_stores
