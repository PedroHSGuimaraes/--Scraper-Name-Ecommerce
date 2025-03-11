'''
CONTACT EXTRACTOR - MINERADOR DE INFORMAÇÕES DE CONTATO

Propósito Geral:
Este arquivo funciona como um "garimpeiro digital" especializado em:
1. Encontrar informações de contato escondidas em páginas web
2. Filtrar e organizar diferentes tipos de contatos (emails, telefones, WhatsApp)
3. Descobrir links para redes sociais de lojas
4. Processar múltiplas lojas em lote através de arquivos JSON

Fluxo de Trabalho:
[HTML/Texto] → [Extração com RegEx] → [Filtragem/Normalização] → [Resultados Organizados]

Bibliotecas Externas:
- BeautifulSoup: Para processar e navegar no HTML (como um "tradutor" de páginas web)
- re: Para encontrar padrões específicos com expressões regulares
- logging: Para registrar o que acontece durante a execução
- json: Para ler/escrever dados estruturados
- os: Para verificar existência de arquivos e manipular o sistema de arquivos
- requests: Para buscar conteúdo de páginas web
'''

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
    '''
    LIMPADOR DE TELEFONES
    
    O que faz:
    - Remove todos os caracteres não-numéricos de um telefone
    - Retorna apenas os dígitos para facilitar comparação
    
    Analogia: 
    - Como limpar um número de telefone rabiscado em um papel, removendo 
      parênteses, traços e espaços para ver só os números
    
    Parâmetro:
    - phone: Número de telefone em qualquer formato
    
    Retorno:
    - Apenas os dígitos do telefone (ex: "11999887766")
    '''
    return ''.join(filter(str.isdigit, phone))

def extract_contact_info(text, url, store_name=None, global_phone_registry=None):
    '''
    DETECTOR DE CONTATOS
    
    Propósito:
    - Encontra diferentes tipos de contatos escondidos em um texto
    
    Analogia:
    - Como um detetive analisando um documento com uma lupa, 
      identificando números de telefone, emails e perfis sociais
    
    Processo passo a passo:
    1. Prepara "caixas" para organizar os diferentes tipos de contatos
    2. Procura emails usando padrões específicos (formato usuario@dominio.com)
    3. Localiza telefones com diferentes formatações 
    4. Filtra telefones para evitar duplicatas e limitar quantidade
    5. Detecta links de WhatsApp
    6. Encontra perfis de redes sociais (Facebook, Instagram, etc.)
    
    Parâmetros:
    - text: Conteúdo da página onde procurar
    - url: Endereço da página (para referência)
    - store_name: Nome da loja (opcional, para registro)
    - global_phone_registry: Registro global para evitar números duplicados entre lojas
    
    Retorno:
    - Dicionário organizado com todos os contatos encontrados
    
    Observações importantes:
    - Usa expressões regulares (como "receitas de busca")
    - Prioriza telefones em formato internacional
    - Limita a 5 telefones por loja para evitar falsas detecções
    '''
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
    '''
    PROCESSADOR DE PÁGINAS WEB
    
    Propósito:
    - Transforma uma página web em texto plano para facilitar a extração
    
    Analogia:
    - Como um liquidificador que transforma uma fruta inteira em suco,
      este processo transforma uma página web complexa em texto simples
    
    Fluxo de processamento:
    1. Cria um "tradutor de HTML" usando BeautifulSoup
    2. Extrai todo o texto visível da página
    3. Coleta também todos os links (href) para não perder informações escondidas
    4. Envia o texto resultante para o extrator de contatos
    
    Parâmetros:
    - html_content: Código HTML da página
    - url: Endereço da página
    - store_name: Nome da loja (para referência)
    - global_phone_registry: Registro global de telefones
    
    Retorno:
    - Dicionário com resultado da extração ou informação de erro
    
    Tratamento de erros:
    - Captura qualquer problema durante o processamento
    - Retorna um relatório de erro sem interromper a aplicação
    '''
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
    '''
    PROCESSADOR DE LOTES DE LOJAS
    
    Propósito:
    - Processa várias lojas de uma vez a partir de um arquivo JSON
    
    Analogia:
    - Como uma linha de produção que recebe uma caixa de peças (arquivo JSON) 
      e processa cada peça separadamente, montando um relatório final
    
    Fluxo de trabalho:
    1. Verifica se o arquivo de lojas existe
    2. Carrega a lista de lojas do arquivo
    3. Cria um "registro central" de telefones para evitar duplicatas
    4. Para cada loja na lista:
       a. Extrai nome e URL
       b. Busca o conteúdo HTML da página
       c. Processa a página para extrair contatos
       d. Registra quantos telefones foram encontrados
    5. Se solicitado, salva todos os resultados em um novo arquivo
    
    Parâmetros:
    - json_file_path: Caminho para o arquivo com a lista de lojas
    - output_file: Arquivo onde salvar os resultados (opcional)
    
    Retorno:
    - Lista com os resultados de todas as lojas processadas
    
    Tratamento de erros:
    - Verifica existência do arquivo de entrada
    - Captura e registra erros específicos de cada loja
    - Captura erros gerais no processamento do arquivo
    '''
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
    '''
    COLETOR DE PÁGINAS WEB
    
    Propósito:
    - Busca o conteúdo HTML de uma página na internet
    
    Analogia:
    - Como um mensageiro que vai até um endereço e traz de volta 
      uma cópia exata do documento que encontrou lá
    
    Processo:
    1. Usa a biblioteca requests para fazer uma chamada HTTP
    2. Define um tempo limite de 30 segundos para evitar travamentos
    3. Verifica se a resposta foi bem-sucedida
    
    Parâmetro:
    - url: Endereço da página a ser buscada
    
    Retorno:
    - Conteúdo HTML da página ou None em caso de erro
    
    Tratamento de erros:
    - Captura qualquer falha na requisição
    - Registra o erro específico no log
    - Retorna None para que o programa possa continuar com outras URLs
    '''
    try:
        import requests
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(f"Erro ao buscar HTML de {url}: {str(e)}")
        return None

def main():
    '''
    FUNÇÃO PRINCIPAL - PONTO DE ENTRADA
    
    Propósito:
    - Coordena a execução do programa como um todo
    
    Analogia:
    - Como o maestro de uma orquestra, que dá entrada para cada instrumento
      no momento certo para que a música flua corretamente
    
    O que faz:
    1. Inicia o processamento do arquivo JSON de lojas
    2. Define o arquivo de saída para os resultados
    3. Remove arquivos temporários que possam ter sido criados
    
    Observações:
    - Esta função é chamada quando o script é executado diretamente
    - Mantém o código organizado com uma estrutura clara de início/fim
    - Facilita testes e manutenção do programa
    '''
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
