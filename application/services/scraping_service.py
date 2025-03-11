# Importação das bibliotecas necessárias
# logging: Para registrar informações e erros durante a execução
# time: Para adicionar delays entre as requisições
# random: Para gerar números aleatórios usados nos delays
import logging
import time
import random

class ScrapingService:
    """
    Serviço principal que coordena todo o processo de scraping (extração de dados)
    
    Esta classe é responsável por:
    1. Coordenar a busca de lojas no Google
    2. Extrair informações de contato das páginas
    3. Gerenciar delays adaptativos para evitar bloqueios
    4. Armazenar os resultados encontrados
    """
    
    def __init__(self, search_service, html_fetcher, contact_extractor, store_repository, config):
        """
        Inicializa o serviço com todas as dependências necessárias
        
        Parâmetros:
        - search_service: Serviço para fazer buscas no Google
        - html_fetcher: Serviço para baixar e processar páginas HTML
        - contact_extractor: Serviço para extrair contatos do texto
        - store_repository: Repositório para salvar dados das lojas
        - config: Configurações do sistema
        """
        self.search_service = search_service
        self.html_fetcher = html_fetcher
        self.contact_extractor = contact_extractor
        self.store_repository = store_repository
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Contadores para ajustar os delays de forma inteligente
        # Quanto mais sucessos, menor o delay; quanto mais erros, maior o delay
        self.success_count = 0  # Conta quantas extrações foram bem-sucedidas
        self.error_count = 0    # Conta quantos erros ocorreram
    
    def scrape_store(self, store_name):
        """
        Executa o processo completo de scraping para uma loja específica
        
        O processo inclui:
        1. Buscar a loja no Google
        2. Processar os primeiros resultados encontrados
        3. Extrair contatos de cada página
        4. Combinar todos os contatos encontrados
        
        Parâmetros:
            store_name (str): Nome da loja para buscar
            
        Retorna:
            dict: Dicionário com os resultados do scraping:
                - success: True/False indicando se teve sucesso
                - nome_loja: Nome da loja processada
                - contacts: Contatos encontrados (se success=True)
                - error: Mensagem de erro (se success=False)
        """
        try:
            self.logger.info(f"Iniciando scraping da loja: {store_name}")
            
            # Primeiro passo: Pesquisar a loja no Google
            # Isso retorna uma lista de URLs relacionadas à loja
            search_results = self.search_service.search_store_contacts(store_name)
            
            # Se não encontrou nenhum resultado, registra o erro
            if not search_results:
                self.logger.warning(f"Nenhum resultado encontrado para '{store_name}'")
                self.error_count += 1
                return {
                    'success': False,
                    'nome_loja': store_name,
                    'error': "Nenhum resultado de pesquisa encontrado"
                }
            
            # Lista para armazenar todos os contatos encontrados
            # em diferentes páginas
            all_contacts = []
            
            # Processa apenas os 2 primeiros resultados do Google
            # para não sobrecarregar os servidores
            for i, result in enumerate(search_results[:2]):
                # Adiciona um delay entre as requisições para evitar bloqueios
                if i > 0:
                    delay = self._get_adaptive_delay()
                    self.logger.info(f"Aguardando {delay:.2f}s antes de processar próximo resultado...")
                    time.sleep(delay)
                
                # Pega a URL do resultado
                url = result.get('link')
                if not url:
                    continue
                
                self.logger.info(f"Processando resultado {i+1}: {url}")
                
                # Baixa o conteúdo da página
                html_content = self.html_fetcher.fetch(url)
                
                if not html_content:
                    continue
                
                # Extrai apenas o texto útil do HTML
                # removendo códigos e scripts
                html_text = self.html_fetcher.extract_text(html_content)
                
                # Procura por contatos no texto extraído
                contacts = self.contact_extractor.execute(html_text, url, store_name)
                all_contacts.append(contacts)
            
            # Se não conseguiu encontrar nenhum contato
            # em nenhuma das páginas, registra o erro
            if not all_contacts:
                self.error_count += 1
                return {
                    'success': False,
                    'nome_loja': store_name,
                    'error': "Não foi possível extrair contatos"
                }
            
            # Combina todos os contatos encontrados em diferentes páginas
            # removendo duplicatas e organizando as informações
            final_contacts = all_contacts[0]
            for contact in all_contacts[1:]:
                final_contacts.merge(contact)
            
            # Atualiza os contadores de sucesso/erro
            # Isso ajuda a ajustar os delays futuros
            self.success_count += 1
            self.error_count = max(0, self.error_count - 0.5)  # Reduz gradualmente os erros com sucessos
            
            # Retorna os resultados encontrados
            return {
                'success': True,
                'nome_loja': store_name,
                'contacts': final_contacts
            }
            
        except Exception as e:
            # Se ocorrer qualquer erro durante o processo
            # registra no log e atualiza os contadores
            self.logger.error(f"Erro ao processar '{store_name}': {str(e)}")
            self.error_count += 1
            self.success_count = max(0, self.success_count - 1)
            
            return {
                'success': False,
                'nome_loja': store_name,
                'error': str(e)
            }
    
    def _get_adaptive_delay(self):
        """
        Calcula o tempo de espera entre requisições de forma inteligente
        
        O delay é ajustado com base em:
        1. Quantidade de erros recentes (aumenta o delay)
        2. Quantidade de sucessos recentes (diminui o delay)
        3. Valor aleatório para evitar padrões detectáveis
        
        Retorna:
            float: Tempo de espera em segundos
        """
        # Pega o delay base das configurações (padrão: 5 segundos)
        base_delay = self.config.get("scraping.base_delay", 5)
        
        # Se houver erros recentes, aumenta bastante o delay
        # para dar tempo dos servidores "esfriarem"
        if self.error_count > 0:
            return base_delay + (self.error_count * 5) + random.uniform(1, 3)
        
        # Para requisições normais, usa um delay moderado
        # que vai diminuindo conforme temos mais sucessos
        return base_delay + random.uniform(1, 3) - min(2, self.success_count * 0.1)
