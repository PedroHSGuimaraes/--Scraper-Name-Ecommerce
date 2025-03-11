import requests
import logging
import random
import time
from bs4 import BeautifulSoup

class HtmlFetcher:
    """Serviço para buscar e processar conteúdo HTML."""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.google.com/'
        }
    
    def fetch(self, url, max_retries=3):
        """
        Busca conteúdo HTML de uma URL com suporte a retentativas.
        
        Args:
            url (str): URL para buscar
            max_retries (int): Número máximo de tentativas
            
        Returns:
            str: Conteúdo HTML ou None em caso de falha
        """
        for attempt in range(max_retries):
            try:
                # Adicionar delay aleatório para evitar bloqueios
                if attempt > 0:
                    delay = 2 ** attempt + random.uniform(1, 3)
                    self.logger.info(f"Aguardando {delay:.2f}s antes de nova tentativa...")
                    time.sleep(delay)
                
                # Fazer requisição
                response = requests.get(
                    url,
                    headers=self.default_headers,
                    timeout=30
                )
                response.raise_for_status()
                return response.text
                
            except requests.RequestException as e:
                self.logger.warning(f"Tentativa {attempt+1}/{max_retries} falhou: {str(e)}")
                
        self.logger.error(f"Todas as {max_retries} tentativas falharam ao buscar {url}")
        return None
    
    def extract_text(self, html_content):
        """
        Extrai texto e links de conteúdo HTML.
        
        Args:
            html_content (str): Conteúdo HTML
            
        Returns:
            str: Texto extraído, incluindo URLs de links
        """
        if not html_content:
            return ""
            
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extrair texto principal
            text = soup.get_text(separator=' ', strip=True)
            
            # Extrair URLs de links
            link_texts = []
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if href:
                    link_texts.append(href)
            
            # Combinar texto e links
            all_text = f"{text} {' '.join(link_texts)}"
            return all_text
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair texto do HTML: {str(e)}")
            return ""
