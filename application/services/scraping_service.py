import logging
import time
import random

'''
SCRAPING SERVICE - MOTOR PRINCIPAL DE COLETA DE DADOS

Funcionamento Geral:
Age como um coordenador que:
1. Recebe o nome de uma loja
2. Busca informações em mecanismos de busca (como um bibliotecário digital)
3. Coleta páginas web relevantes
4. Extrai contatos e informações
5. Armazena resultados

Fluxo Principal:
[Pesquisa] → [Coleta HTML] → [Extrai Contatos] → [Consolida Resultados]

Boas Práticas:
- Delay adaptativo entre requisições (evita bloqueios)
- Balanceamento entre sucessos/erros
- Logs detalhados para diagnóstico
'''

class ScrapingService:
    """
    Coordenador principal do processo de coleta de dados
    
    Analogia: Imagine um detetive especializado em encontrar informações de lojas na internet
    
    Componentes:
    - search_service: Localizador de pistas iniciais (como Google)
    - html_fetcher: Coletor de páginas web
    - contact_extractor: Especialista em extrair contatos
    - store_repository: Arquivo onde guarda as descobertas
    """
    
    def __init__(self, search_service, html_fetcher, contact_extractor, store_repository, config):
        '''
        INICIALIZAÇÃO DO SISTEMA
        
        Parâmetros recebidos:
        - search_service: Vem da configuração inicial do sistema
        - html_fetcher: Configurado com ferramentas anti-bloqueio
        - contact_extractor: Definido com regras de extração
        - store_repository: Conexão com banco de dados
        - config: Arquivo de configurações (config.yaml)
        '''
        self.search_service = search_service
        self.html_fetcher = html_fetcher
        self.contact_extractor = contact_extractor
        self.store_repository = store_repository
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Contador para ajuste adaptativo de delays
        self.success_count = 0
        self.error_count = 0
    
    def scrape_store(self, store_name):
        '''
        PROCESSO PRINCIPAL - Fluxo passo a passo:
        
        1. Pesquisa inicial (como procurar em um catálogo telefônico)
        2. Para cada resultado relevante:
           a. Aguarda tempo variável (para não chamar atenção)
           b. Coleta página completa
           c. Extrai informações úteis
        3. Consolida melhores resultados
        4. Atualiza contadores de performance
        
        Parâmetro:
        - store_name: Recebido do agendador de tarefas ou interface do usuário
        '''
        try:
            self.logger.info(f"Iniciando scraping da loja: {store_name}")
            
            # Pesquisar loja no Google
            search_results = self.search_service.search_store_contacts(store_name)
            
            if not search_results:
                self.logger.warning(f"Nenhum resultado encontrado para '{store_name}'")
                self.error_count += 1
                return {
                    'success': False,
                    'nome_loja': store_name,
                    'error': "Nenhum resultado de pesquisa encontrado"
                }
            
            # Processar os primeiros resultados
            all_contacts = []
            
            for i, result in enumerate(search_results[:2]):  # Processar os 2 primeiros resultados
                if i > 0:
                    # Adicionar delay entre requisições
                    delay = self._get_adaptive_delay()
                    self.logger.info(f"Aguardando {delay:.2f}s antes de processar próximo resultado...")
                    time.sleep(delay)
                
                url = result.get('link')
                if not url:
                    continue
                
                self.logger.info(f"Processando resultado {i+1}: {url}")
                
                # Buscar conteúdo HTML
                html_content = self.html_fetcher.fetch(url)
                
                if not html_content:
                    continue
                
                # Extrair texto do HTML
                html_text = self.html_fetcher.extract_text(html_content)
                
                # Extrair contatos
                contacts = self.contact_extractor.execute(html_text, url, store_name)
                all_contacts.append(contacts)
            
            # Se não encontrou contatos
            if not all_contacts:
                self.error_count += 1
                return {
                    'success': False,
                    'nome_loja': store_name,
                    'error': "Não foi possível extrair contatos"
                }
            
            # Mesclar contatos encontrados em diferentes resultados
            final_contacts = all_contacts[0]
            for contact in all_contacts[1:]:
                final_contacts.merge(contact)
            
            self.success_count += 1
            self.error_count = max(0, self.error_count - 0.5)  # Reduz gradualmente os erros com sucessos
            
            return {
                'success': True,
                'nome_loja': store_name,
                'contacts': final_contacts
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao processar '{store_name}': {str(e)}")
            self.error_count += 1
            self.success_count = max(0, self.success_count - 1)
            
            return {
                'success': False,
                'nome_loja': store_name,
                'error': str(e)
            }
    
    def _get_adaptive_delay(self):
        '''
        CONTROLE DE VELOCIDADE - Sistema anti-bloqueio
        
        Funciona como o pedal de acelerador de um carro:
        - Base: Velocidade normal (config.yaml)
        - Erros: Reduz velocidade (aumenta delay)
        - Sucessos: Aumenta velocidade gradualmente
        
        Calcula tempo de espera usando:
        - Contadores internos de sucesso/erro
        - Aleatoriedade (impede padrões detectáveis)
        '''
        base_delay = self.config.get("scraping.base_delay", 5)
        
        # Aumentar delay substancialmente se houver erros
        if self.error_count > 0:
            return base_delay + (self.error_count * 5) + random.uniform(1, 3)
        
        # Delay moderado para requisições bem-sucedidas
        return base_delay + random.uniform(1, 3) - min(2, self.success_count * 0.1)
