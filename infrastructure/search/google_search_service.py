'''
GOOGLE SEARCH SERVICE - MOTOR DE BUSCA INTELIGENTE

Propósito Geral:
Este arquivo funciona como um "detetive digital" que:
1. Conecta-se ao Google para encontrar informações (como pesquisar em uma biblioteca global)
2. Formula perguntas específicas para encontrar contatos de lojas
3. Lida com falhas de conexão automaticamente (como ligar novamente após chamada interrompida)
4. Organiza os resultados em formato útil para o sistema

Fluxo de Trabalho:
[Consulta] → [API Google] → [Filtragem] → [Resultados Organizados]

Bibliotecas Externas:
- googleapiclient.discovery: Para acessar a API oficial do Google
- logging: Para registro de operações e erros
- time: Para controlar esperas entre tentativas
- random: Para adicionar aleatoriedade nas esperas
'''

import logging
from googleapiclient.discovery import build
import time
import random

class GoogleSearchService:
    """
    Serviço de Pesquisa com API Google
    
    Analogia: Funciona como um assistente de pesquisa que consulta uma enciclopédia gigante
    
    Boas Práticas:
    - Retry com backoff exponencial (espera cada vez maior entre tentativas)
    - Controle de quantidade máxima de resultados
    - Tratamento completo de erros para garantir robustez
    """
    
    def __init__(self, api_key, engine_id):
        '''
        CONFIGURAÇÃO INICIAL
        
        Parâmetros:
        - api_key: Chave secreta de acesso à API Google (como senha de biblioteca VIP)
        - engine_id: Identificador do mecanismo de busca (como escolher seção específica)
        
        O que acontece:
        - Guarda as credenciais para uso posterior
        - Configura sistema de registro de atividades (logging)
        '''
        self.api_key = api_key
        self.engine_id = engine_id
        self.logger = logging.getLogger(__name__)
    
    def search(self, query, max_results=10, retry_attempts=3):
        '''
        PESQUISADOR PRINCIPAL
        
        Fluxo passo a passo:
        1. Prepara a consulta para o Google
        2. Envia a pergunta através da API oficial
        3. Recebe e processa os resultados
        4. Em caso de erro, tenta novamente com espera adaptativa
        
        Parâmetros:
        - query: Texto da pergunta (o que estamos procurando)
        - max_results: Limite de resultados (padrão: 10)
        - retry_attempts: Quantas vezes tentar em caso de falha (padrão: 3)
        
        Retorno:
        - Lista de resultados (como páginas de livro com informações)
        
        Sistema Anti-Falha:
        - Se a conexão falhar, espera um tempo e tenta novamente
        - Cada nova tentativa espera mais tempo (2ˣ segundos + valor aleatório)
        - Após todas tentativas, retorna lista vazia se continuar falhando
        '''
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
        '''
        LOCALIZADOR DE CONTATOS DE LOJAS
        
        O que faz:
        - Cria uma pergunta específica para encontrar contatos
        - Usa palavras-chave como "contato", "telefone", "email"
        - Limita a 3 resultados para eficiência
        
        Parâmetro:
        - store_name: Nome da loja a ser pesquisada
        
        Estratégia:
        - Formata a consulta para maximizar chances de encontrar dados de contato
        - Concatena termos relevantes (site oficial, whatsapp, etc.)
        - Aproveita o método search() para executar a pesquisa
        
        Resultado final:
        - Retorna até 3 melhores fontes de informação sobre a loja
        '''
        # Formatar consulta específica para contatos
        query = f"{store_name} contato telefone email whatsapp site oficial"
        
        # Executar pesquisa
        return self.search(query, max_results=3)
