from bs4 import BeautifulSoup
import re
import logging
import json
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)

def normalize_phone(phone):
    """
    Normaliza um número de telefone removendo formatação para comparação
    """
    return ''.join(filter(str.isdigit, phone))

def extract_contact_info(text, url, store_name=None, global_phone_registry=None):
    """
    Extrai informações de contato de um texto
    """
    # Resultados a serem retornados
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
    
    # Buscar emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    results['emails'] = list(set(emails))
    
    # Buscar telefones
    phone_pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,3}\)?[-.\s]?\d{4,5}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    
    # Processamento de telefones para evitar duplicatas e limitar a 5
    if global_phone_registry is None:
        global_phone_registry = {}
        
    unique_phones = []
    normalized_phones = []
    
    # Classificar telefones - priorizar formatos internacionais
    prioritized_phones = []
    regular_phones = []
    
    for phone in phones:
        norm_phone = normalize_phone(phone)
        
        # Verificar se já existe no registro global
        if norm_phone in global_phone_registry:
            continue
            
        # Verificar se já foi adicionado para esta loja
        if norm_phone in normalized_phones:
            continue
            
        # Verificar se o número parece ser um telefone brasileiro válido (8+ dígitos)
        if len(norm_phone) < 8:
            continue
            
        # Classificar por prioridade
        if '+' in phone or phone.startswith('00'):
            prioritized_phones.append((phone, norm_phone))
        else:
            regular_phones.append((phone, norm_phone))
    
    # Combinar os telefones priorizados e regulares
    all_phones = prioritized_phones + regular_phones
    
    # Limitar a 5 telefones únicos
    for phone, norm_phone in all_phones:
        if len(unique_phones) >= 5:
            break
            
        unique_phones.append(phone)
        normalized_phones.append(norm_phone)
        
        # Registrar no dicionário global para evitar duplicatas entre lojas
        if store_name:
            global_phone_registry[norm_phone] = store_name
    
    # Adicionar ao resultado
    results['phones'] = unique_phones
    
    # Buscar WhatsApp
    whatsapp_pattern = r'(?:https?://)?(?:api\.whatsapp\.com|wa\.me|whatsapp\.com)/(?:send\?phone=)?(\d+)'
    whatsapp_links = re.findall(whatsapp_pattern, text)
    results['whatsapp']['links'] = [f"https://wa.me/{num}" for num in whatsapp_links]
    results['whatsapp']['numbers'] = whatsapp_links
    
    # Buscar redes sociais
    social_patterns = {
        'facebook': r'(?:https?://)?(?:www\.)?facebook\.com/[a-zA-Z0-9.]+',
        'instagram': r'(?:https?://)?(?:www\.)?instagram\.com/[a-zA-Z0-9_.]+',
        'twitter': r'(?:https?://)?(?:www\.)?twitter\.com/[a-zA-Z0-9_]+',
        'linkedin': r'(?:https?://)?(?:www\.)?linkedin\.com/(?:company|in)/[a-zA-Z0-9_-]+',
        'youtube': r'(?:https?://)?(?:www\.)?youtube\.com/(?:user|channel|c)/[a-zA-Z0-9_-]+'
    }
    
    for platform, pattern in social_patterns.items():
        matches = re.findall(pattern, text)
        results['socialMedia'][platform] = list(set(matches))
    
    return results

def process_html(html_content, url, store_name=None, global_phone_registry=None):
    """
    Processa o conteúdo HTML para extrair informações de contato
    """
    try:
        # Criar objeto BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extrair todo o texto da página
        text = soup.get_text(separator=' ', strip=True)
        
        # Extrair também todos os atributos href
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if href:
                text += ' ' + href
        
        # Extrair informações de contato
        contact_info = extract_contact_info(text, url, store_name, global_phone_registry)
        
        return {
            'success': True,
            'url': url,
            'store_name': store_name,
            'data': contact_info
        }
    except Exception as e:
        return {
            'success': False,
            'url': url,
            'store_name': store_name,
            'error': str(e)
        }

def process_stores_json(json_file_path="lojas_oficiais_emergencia.json", output_file=None):
    """
    Processa o arquivo JSON com lojas e extrai contatos
    """
    # Verificar se o arquivo existe
    if not os.path.exists(json_file_path):
        logging.error(f"Arquivo não encontrado: {json_file_path}")
        return None
        
    try:
        # Carregar o arquivo JSON
        with open(json_file_path, 'r', encoding='utf-8') as f:
            stores_data = json.load(f)
            
        logging.info(f"Carregadas {len(stores_data)} lojas do arquivo {json_file_path}")
        
        # Dicionário global para rastrear telefones já extraídos
        global_phone_registry = {}
        
        # Processar cada loja
        results = []
        
        for i, store in enumerate(stores_data):
            store_name = store.get('nome', f"Loja {i+1}")
            store_url = store.get('url', '')
            
            logging.info(f"Processando loja {i+1}/{len(stores_data)}: {store_name}")
            
            if not store_url:
                logging.warning(f"URL não encontrada para a loja: {store_name}")
                continue
                
            try:
                # Para este exemplo, simularemos o conteúdo HTML
                # Em um cenário real, você faria uma requisição para obter o HTML
                html_content = fetch_html(store_url)
                
                if not html_content:
                    logging.warning(f"Não foi possível obter conteúdo da URL: {store_url}")
                    continue
                    
                # Processar HTML e extrair contatos
                result = process_html(html_content, store_url, store_name, global_phone_registry)
                
                # Adicionar nome da loja ao resultado
                result['nome_loja'] = store_name
                
                # Registrar quantos telefones foram extraídos
                phones_count = len(result.get('data', {}).get('phones', []))
                logging.info(f"Extraídos {phones_count} telefones da loja {store_name}")
                
                results.append(result)
                
            except Exception as e:
                logging.error(f"Erro ao processar loja {store_name}: {str(e)}")
        
        # Salvar resultados se solicitado
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logging.info(f"Resultados salvos em {output_file}")
            
        return results
        
    except Exception as e:
        logging.error(f"Erro ao processar arquivo JSON: {str(e)}")
        return None

def fetch_html(url):
    """
    Função para buscar o HTML de uma URL
    Em um cenário real, você usaria requests ou similar
    """
    try:
        import requests
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(f"Erro ao buscar HTML de {url}: {str(e)}")
        return None

# Função principal para executar o processamento
def main():
    # Processar o arquivo de lojas
    process_stores_json(
        json_file_path="lojas_oficiais_emergencia.json",
        output_file="resultados/contatos_processados.json"
    )
    
    # Remover arquivos temporários se necessário
    temp_files = []  # Lista de arquivos temporários que seriam criados durante o processo
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                logging.info(f"Arquivo temporário removido: {temp_file}")
            except Exception as e:
                logging.warning(f"Não foi possível remover arquivo temporário {temp_file}: {str(e)}")

# Se este arquivo for executado diretamente
if __name__ == "__main__":
    main()
