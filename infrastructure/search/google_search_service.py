<<<<<<< HEAD
# Importação das bibliotecas necessárias
# logging: Para registrar informações e erros
# build: Cliente oficial do Google para APIs
# time: Para implementar delays entre tentativas
# random: Para adicionar variação aos delays
=======
>>>>>>> origin/main
import logging
from googleapiclient.discovery import build
import time
import random

class GoogleSearchService:
<<<<<<< HEAD
    """
    Classe responsável por realizar buscas usando a API do Google
    
    Esta classe implementa:
    1. Buscas gerais no Google usando Custom Search API
    2. Buscas específicas por informações de contato de lojas
    3. Sistema de retry com backoff exponencial
    4. Logging detalhado das operações
    
    Requer:
    - API Key válida do Google
    - ID do mecanismo de busca personalizado (Custom Search Engine)
    """
    
    def __init__(self, api_key, engine_id):
        """
        Inicializa o serviço de busca do Google
        
        Parâmetros:
            api_key (str): Chave de API do Google para autenticação
            engine_id (str): ID do mecanismo de busca personalizado
        
        A API Key pode ser obtida no Google Cloud Console
        O Engine ID pode ser obtido no Google Custom Search Console
        """
        # Credenciais necessárias para usar a API
        self.api_key = api_key      # Chave de API do Google
        self.engine_id = engine_id  # ID do mecanismo de busca
        
        # Configuração do logger para esta classe
=======
    """Serviço para realizar pesquisas utilizando a API do Google."""
    
    def __init__(self, api_key, engine_id):
        self.api_key = api_key
        self.engine_id = engine_id
>>>>>>> origin/main
        self.logger = logging.getLogger(__name__)
    
    def search(self, query, max_results=10, retry_attempts=3):
        """
<<<<<<< HEAD
        Executa uma busca no Google usando a Custom Search API
        
        Este método:
        1. Tenta executar a busca até retry_attempts vezes
        2. Implementa backoff exponencial entre tentativas
        3. Registra todo o processo no log
        
        Parâmetros:
            query (str): Texto da busca a ser realizada
            max_results (int): Número máximo de resultados (padrão: 10)
            retry_attempts (int): Máximo de tentativas em caso de erro
            
        Retorna:
            list: Lista de resultados da busca, cada resultado é um dict
                 Lista vazia em caso de falha em todas as tentativas
        """
        # Tenta a busca várias vezes em caso de erro
        for attempt in range(retry_attempts):
            try:
                # Registra a busca que será realizada
                self.logger.info(f"Realizando pesquisa: '{query}'")
                
                # Cria um cliente para a API de busca personalizada
                # usando as credenciais fornecidas
                service = build("customsearch", "v1", developerKey=self.api_key)
                
                # Configura e executa a busca com os parâmetros:
                # q: texto da busca
                # cx: ID do mecanismo de busca
                # num: quantidade de resultados
=======
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
>>>>>>> origin/main
                request = service.cse().list(
                    q=query,
                    cx=self.engine_id,
                    num=max_results
                )
                
<<<<<<< HEAD
                # Executa a requisição e obtém a resposta
                response = request.execute()
                
                # Extrai apenas os itens (resultados) da resposta
                # Se não houver resultados, retorna lista vazia
                items = response.get("items", [])
                
                # Registra o sucesso da operação
=======
                # Obter resultados
                response = request.execute()
                
                # Extrair itens
                items = response.get("items", [])
                
>>>>>>> origin/main
                self.logger.info(f"Pesquisa concluída. Encontrados {len(items)} resultados.")
                return items
                
            except Exception as e:
<<<<<<< HEAD
                # Registra a falha desta tentativa
                self.logger.warning(f"Tentativa {attempt+1}/{retry_attempts} falhou: {str(e)}")
                
                # Se ainda houver tentativas restantes
                if attempt < retry_attempts - 1:
                    # Calcula o tempo de espera usando backoff exponencial
                    # Fórmula: 2^tentativa + random(1,3)
                    # Exemplo: 1ª falha = 2-4s, 2ª falha = 4-6s, 3ª falha = 8-10s
                    delay = 2 ** attempt + random.uniform(1, 3)
                    
                    # Registra e executa o delay
                    self.logger.info(f"Aguardando {delay:.2f}s antes de nova tentativa...")
                    time.sleep(delay)
                else:
                    # Registra falha definitiva após todas as tentativas
                    self.logger.error(f"Pesquisa falhou após {retry_attempts} tentativas: {str(e)}")
        
        # Retorna lista vazia se todas as tentativas falharam
=======
                self.logger.warning(f"Tentativa {attempt+1}/{retry_attempts} falhou: {str(e)}")
                
                if attempt < retry_attempts - 1:
                    # Aplicar backoff exponencial entre tentativas
                    delay = 2 ** attempt + random.uniform(1, 3)
                    self.logger.info(f"Aguardando {delay:.2f}s antes de nova tentativa...")
                    time.sleep(delay)
                else:
                    self.logger.error(f"Pesquisa falhou após {retry_attempts} tentativas: {str(e)}")
        
>>>>>>> origin/main
        return []
    
    def search_store_contacts(self, store_name):
        """
<<<<<<< HEAD
        Realiza uma busca otimizada por informações de contato
        
        Este método especializado:
        1. Formata uma query específica para buscar contatos
        2. Limita os resultados para maior eficiência
        3. Inclui palavras-chave relevantes na busca
        
        Parâmetros:
            store_name (str): Nome da loja para buscar contatos
            
        Retorna:
            list: Lista com até 3 resultados mais relevantes
                 Cada resultado é um dict com dados da página
        """
        # Formata uma query específica para buscar contatos
        # Inclui palavras-chave relevantes como:
        # - contato: páginas de contato
        # - telefone: números de telefone
        # - email: endereços de e-mail
        # - whatsapp: números e links de WhatsApp
        # - site oficial: para priorizar o site oficial da loja
        query = f"{store_name} contato telefone email whatsapp site oficial"
        
        # Executa a busca limitada a 3 resultados
        # Menos resultados = mais rápido e mais relevante
=======
        Pesquisa informações de contato de uma loja específica.
        
        Args:
            store_name (str): Nome da loja para pesquisar
            
        Returns:
            list: Resultados de pesquisa
        """
        # Formatar consulta específica para contatos
        query = f"{store_name} contato telefone email whatsapp site oficial"
        
        # Executar pesquisa
>>>>>>> origin/main
        return self.search(query, max_results=3)
