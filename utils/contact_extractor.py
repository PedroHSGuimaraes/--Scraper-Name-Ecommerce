# Importação das bibliotecas necessárias
# BeautifulSoup: Biblioteca para análise de HTML, facilita a extração de informações de páginas web
# re: Biblioteca para trabalhar com expressões regulares (encontrar padrões em texto)
# logging: Biblioteca para registrar logs (informações sobre a execução do programa)
# json: Biblioteca para trabalhar com arquivos JSON
# os: Biblioteca para operações do sistema operacional
from bs4 import BeautifulSoup
import re
import logging
import json
import os

# Configuração do sistema de logs
# Isso permite que o programa salve informações sobre sua execução tanto em um arquivo quanto na tela
logging.basicConfig(
    level=logging.INFO,  # Define o nível de detalhamento dos logs
    format='%(asctime)s - %(levelname)s - %(message)s',  # Define o formato das mensagens de log
    handlers=[
        logging.FileHandler("scraper.log"),  # Salva os logs em um arquivo
        logging.StreamHandler()  # Mostra os logs no terminal
    ]
)

def normalize_phone(phone):
    """
    Função que limpa um número de telefone, removendo todos os caracteres que não são dígitos
    Por exemplo: "(11) 9999-9999" vira "11999999999"
    """
    return ''.join(filter(str.isdigit, phone))

def extract_contact_info(text, url, store_name=None, global_phone_registry=None):
    """
    Função principal que extrai todas as informações de contato de um texto
    Procura por: emails, telefones, WhatsApp e links de redes sociais
    
    Parâmetros:
    - text: O texto onde procurar as informações
    - url: URL da página sendo analisada
    - store_name: Nome da loja (opcional)
    - global_phone_registry: Registro global de telefones para evitar duplicatas
    """
    # Dicionário que vai guardar todas as informações encontradas
    results = {
        'emails': [],
        'phones': [],
        'whatsapp': {
            'links': [],
            'numbers': []
        },
        'socialMedia': {
            'facebook': [],
            'instagram': [],
            'twitter': [],
            'linkedin': [],
            'youtube': []
        }
    }
    
    # Busca por emails usando expressão regular
    # Procura por padrões como: nome@dominio.com
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    results['emails'] = list(set(emails))  # set() remove duplicatas
    
    # Busca por telefones usando expressão regular
    # Aceita vários formatos como: +55 (11) 99999-9999 ou 11999999999
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,3}\)?[-.\s]?\d{4,5}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    
    # Inicializa o registro global de telefones se não existir
    if global_phone_registry is None:
        global_phone_registry = {}
        
    unique_phones = []
    normalized_phones = []
    
    # Separa os telefones em duas categorias:
    # - prioritized_phones: números com formato internacional (+55 ou 00)
    # - regular_phones: números em formato nacional
    prioritized_phones = []
    regular_phones = []
    
    # Processa cada telefone encontrado
    for phone in phones:
        # Normaliza o número (remove formatação)
        norm_phone = normalize_phone(phone)
        
        # Pula se o telefone já existe no registro global
        if norm_phone in global_phone_registry:
            continue
            
        # Pula se o telefone já foi adicionado para esta loja
        if norm_phone in normalized_phones:
            continue
            
        # Verifica se o número tem pelo menos 8 dígitos
        if len(norm_phone) < 8:
            continue
            
        # Classifica o telefone como prioritário ou regular
        if '+' in phone or phone.startswith('00'):
            prioritized_phones.append((phone, norm_phone))
        else:
            regular_phones.append((phone, norm_phone))
    
    # Junta os telefones, colocando os prioritários primeiro
    all_phones = prioritized_phones + regular_phones
    
    # Limita a 5 telefones únicos por loja
    for phone, norm_phone in all_phones:
        if len(unique_phones) >= 5:
            break
            
        unique_phones.append(phone)
        normalized_phones.append(norm_phone)
        
        # Registra o telefone no dicionário global
        if store_name:
            global_phone_registry[norm_phone] = store_name
    
    # Adiciona os telefones encontrados ao resultado
    results['phones'] = unique_phones
    
    # Busca por links de WhatsApp
    # Procura por padrões como: wa.me/5511999999999 ou api.whatsapp.com/send?phone=5511999999999
    whatsapp_pattern = r'(?:https?://)?(?:api\.whatsapp\.com|wa\.me|whatsapp\.com)/(?:send\?phone=)?(\d+)'
    whatsapp_links = re.findall(whatsapp_pattern, text)
    results['whatsapp']['links'] = [f"https://wa.me/{num}" for num in whatsapp_links]
    results['whatsapp']['numbers'] = whatsapp_links
    
    # Busca por links de redes sociais
    # Define padrões para encontrar URLs de diferentes redes sociais
    social_patterns = {
        'facebook': r'(?:https?://)?(?:www\.)?facebook\.com/[a-zA-Z0-9.]+',
        'instagram': r'(?:https?://)?(?:www\.)?instagram\.com/[a-zA-Z0-9_.]+',
        'twitter': r'(?:https?://)?(?:www\.)?twitter\.com/[a-zA-Z0-9_]+',
        'linkedin': r'(?:https?://)?(?:www\.)?linkedin\.com/(?:company|in)/[a-zA-Z0-9_-]+',
        'youtube': r'(?:https?://)?(?:www\.)?youtube\.com/(?:user|channel|c)/[a-zA-Z0-9_-]+'
    }
    
    # Procura por cada rede social e adiciona ao resultado
    for platform, pattern in social_patterns.items():
        matches = re.findall(pattern, text)
        results['socialMedia'][platform] = list(set(matches))
    
    return results

def process_html(html_content, url, store_name=None, global_phone_registry=None):
    """
    Função que processa o conteúdo HTML de uma página
    
    Parâmetros:
    - html_content: Conteúdo HTML da página
    - url: URL da página
    - store_name: Nome da loja
    - global_phone_registry: Registro global de telefones
    """
    try:
        # Cria um objeto BeautifulSoup para analisar o HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extrai todo o texto da página, removendo tags HTML
        text = soup.get_text(separator=' ', strip=True)
        
        # Também extrai todos os links (href) da página
        # Isso é útil porque muitas vezes contatos estão em links
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if href:
                text += ' ' + href
        
        # Extrai as informações de contato do texto
        contact_info = extract_contact_info(text, url, store_name, global_phone_registry)
        
        return {
            'success': True,
            'url': url,
            'store_name': store_name,
            'data': contact_info
        }
    except Exception as e:
        # Se ocorrer algum erro, retorna um dicionário com informações do erro
        return {
            'success': False,
            'url': url,
            'store_name': store_name,
            'error': str(e)
        }

def process_stores_json(json_file_path="lojas_oficiais_emergencia.json", output_file=None):
    """
    Função que processa um arquivo JSON contendo informações das lojas
    
    Parâmetros:
    - json_file_path: Caminho do arquivo JSON com as lojas
    - output_file: Arquivo onde salvar os resultados (opcional)
    """
    # Verifica se o arquivo JSON existe
    if not os.path.exists(json_file_path):
        logging.error(f"Arquivo não encontrado: {json_file_path}")
        return None
        
    try:
        # Carrega o arquivo JSON com as lojas
        with open(json_file_path, 'r', encoding='utf-8') as f:
            stores_data = json.load(f)
            
        logging.info(f"Carregadas {len(stores_data)} lojas do arquivo {json_file_path}")
        
        # Dicionário para evitar duplicação de telefones entre lojas
        global_phone_registry = {}
        
        # Lista para guardar os resultados
        results = []
        
        # Processa cada loja do arquivo
        for i, store in enumerate(stores_data):
            store_name = store.get('nome', f"Loja {i+1}")
            store_url = store.get('url', '')
            
            logging.info(f"Processando loja {i+1}/{len(stores_data)}: {store_name}")
            
            if not store_url:
                logging.warning(f"URL não encontrada para a loja: {store_name}")
                continue
                
            try:
                # Busca o conteúdo HTML da página da loja
                html_content = fetch_html(store_url)
                
                if not html_content:
                    logging.warning(f"Não foi possível obter conteúdo da URL: {store_url}")
                    continue
                    
                # Processa o HTML e extrai os contatos
                result = process_html(html_content, store_url, store_name, global_phone_registry)
                
                # Adiciona o resultado à lista
                if result['success']:
                    results.append(result)
                else:
                    logging.error(f"Erro ao processar {store_url}: {result['error']}")
                    
            except Exception as e:
                logging.error(f"Erro ao processar loja {store_name}: {str(e)}")
                continue
                
        # Se foi especificado um arquivo de saída, salva os resultados
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
        return results
        
    except Exception as e:
        logging.error(f"Erro ao processar arquivo JSON: {str(e)}")
        return None

def fetch_html(url):
    """
    Função que busca o conteúdo HTML de uma URL
    
    Esta é uma função de exemplo - em um caso real,
    você usaria a biblioteca 'requests' ou similar para
    fazer a requisição HTTP e obter o HTML
    """
    # Aqui você implementaria a lógica real para buscar o HTML
    # Por exemplo:
    # import requests
    # response = requests.get(url)
    # return response.text
    pass

def main():
    """
    Função principal que inicia o processamento
    
    Esta função:
    1. Define os arquivos de entrada e saída
    2. Processa as lojas
    3. Salva os resultados
    """
    input_file = "lojas_oficiais_emergencia.json"
    output_file = "contatos_extraidos.json"
    
    logging.info("Iniciando extração de contatos...")
    
    results = process_stores_json(input_file, output_file)
    
    if results:
        logging.info(f"Processamento concluído. Resultados salvos em: {output_file}")
    else:
        logging.error("Falha no processamento")

# Verifica se este arquivo está sendo executado diretamente
if __name__ == "__main__":
    main()
