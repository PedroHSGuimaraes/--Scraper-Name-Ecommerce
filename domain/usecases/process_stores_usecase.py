import logging
from domain.entities.store import Store

class ProcessStoresUseCase:
    """Caso de uso para processamento de lojas."""
    
    def __init__(self, html_fetcher, contact_extractor, store_repository):
        self.html_fetcher = html_fetcher
        self.contact_extractor = contact_extractor
        self.store_repository = store_repository
        self.logger = logging.getLogger(__name__)
    
    def execute(self, json_file_path=None, output_file=None):
        """
        Processa lojas de um arquivo JSON e extrai seus contatos.
        
        Args:
            json_file_path: Caminho para arquivo JSON de entrada
            output_file: Caminho para arquivo de saída
            
        Returns:
            list: Lista de lojas processadas
        """
        # Carregar dados das lojas
        stores_data = self.store_repository.load_stores(json_file_path)
        if not stores_data:
            self.logger.error("Não foi possível carregar lojas de entrada")
            return []
            
        self.logger.info(f"Carregadas {len(stores_data)} lojas para processamento")
        
        # Processamento das lojas
        processed_stores = []
        
        for i, store_data in enumerate(stores_data):
            store_name = store_data.get('nome', f"Loja {i+1}")
            store_url = store_data.get('url', '')
            
            self.logger.info(f"Processando loja {i+1}/{len(stores_data)}: {store_name}")
            
            if not store_url:
                self.logger.warning(f"URL não encontrada para a loja: {store_name}")
                continue
                
            try:
                # Buscar conteúdo HTML
                html_content = self.html_fetcher.fetch(store_url)
                
                if not html_content:
                    self.logger.warning(f"Não foi possível obter conteúdo HTML da URL: {store_url}")
                    continue
                
                # Processar HTML com o extrator de contatos
                html_text = self.html_fetcher.extract_text(html_content)
                contacts = self.contact_extractor.execute(html_text, store_url, store_name)
                
                # Criar objeto Store
                store = Store(name=store_name, url=store_url)
                store.contact_info = contacts
                
                # Adicionar ao resultado
                processed_stores.append(store)
                
                # Registrar estatísticas
                phones_count = len(contacts.phones)
                self.logger.info(f"Extraídos {phones_count} telefones da loja {store_name}")
                
            except Exception as e:
                self.logger.error(f"Erro ao processar loja {store_name}: {str(e)}")
                
                # Criar store com erro
                failed_store = Store(name=store_name, url=store_url)
                failed_store.success = False
                failed_store.error = str(e)
                
                processed_stores.append(failed_store)
        
        # Salvar resultados
        if output_file:
            stores_dict = [store.to_dict() for store in processed_stores]
            self.store_repository.save_stores(stores_dict, output_file)
        
        return processed_stores
