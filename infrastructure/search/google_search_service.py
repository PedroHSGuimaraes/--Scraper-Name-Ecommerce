import logging
from googleapiclient.discovery import build
import time
import random

class GoogleSearchService:
    """Serviço para realizar pesquisas utilizando a API do Google."""
    
    def __init__(self, api_key, engine_id):
        self.api_key = api_key
        self.engine_id = engine_id
        self.logger = logging.getLogger(__name__)
    
    def search(self, query, max_results=10, retry_attempts=3):
        """
        Realiza uma pesquisa no Google.
        
        Args:
            query (str): Consulta para pesquisar
            max_results (int): Número máximo de resultados
            retry_attempts (int): Número máximo de tentativas em caso de erro
            
        Returns:
            list: Lista de resultados da pesquisa
        """
        for attempt in range(retry_attempts):
            try:
                self.logger.info(f"Realizando pesquisa: '{query}'")
                
                # Criar serviço de pesquisa
                service = build("customsearch", "v1", developerKey=self.api_key)
                
                # Executar pesquisa
                request = service.cse().list(
                    q=query,
                    cx=self.engine_id,
                    num=max_results
                )
                
                # Obter resultados
                response = request.execute()
                
                # Extrair itens
                items = response.get("items", [])
                
                self.logger.info(f"Pesquisa concluída. Encontrados {len(items)} resultados.")
                return items
                
            except Exception as e:
                self.logger.warning(f"Tentativa {attempt+1}/{retry_attempts} falhou: {str(e)}")
                
                if attempt < retry_attempts - 1:
                    # Aplicar backoff exponencial entre tentativas
                    delay = 2 ** attempt + random.uniform(1, 3)
                    self.logger.info(f"Aguardando {delay:.2f}s antes de nova tentativa...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"Pesquisa falhou após {retry_attempts} tentativas: {str(e)}")
        
        return []
    
    def search_store_contacts(self, store_name):
        """
        Pesquisa informações de contato de uma loja específica.
        
        Args:
            store_name (str): Nome da loja para pesquisar
            
        Returns:
            list: Resultados de pesquisa
        """
        # Formatar consulta específica para contatos
        query = f"{store_name} contato telefone email whatsapp site oficial"
        
        # Executar pesquisa
        return self.search(query, max_results=3)
