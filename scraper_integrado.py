"""
SCRAPER INTEGRADO - SISTEMA UNIFICADO DE COLETA DE CONTATOS DE LOJAS

Propósito Geral:
Este script funciona como o "cérebro" do sistema, gerenciando todas as etapas do processo de scraping:
1. Obtém a lista de lojas a serem processadas
2. Realiza buscas para cada loja usando a API do Google
3. Extrai informações de contato dos resultados encontrados
4. Salva os dados em múltiplos formatos (JSON, CSV e HTML)
5. Implementa mecanismos de segurança para evitar perda de dados

Fluxo de Trabalho:
[Lista de Lojas] → [Pesquisa Google] → [Extração de Contatos] → [Salvamento de Resultados]

Recursos Avançados:
- Tratamento de interrupções (Ctrl+C) com salvamento automático
- Delays adaptativos para evitar bloqueios durante o scraping
- Sistema de retry com backoff exponencial para falhas de conexão
- Salvamento parcial em vários formatos para análise de dados
- Tratamento de exceções para alta resiliência

Bibliotecas Externas:
- pandas: Para manipulação de dados e geração de relatórios
- requests: Para requisições HTTP
- BeautifulSoup: Para análise de HTML
- contact_extractor: Módulo personalizado para extração de informações de contato
- api_google: Módulo personalizado para interface com a API do Google
"""

import time
import json
import random
import sys
import signal
import traceback
import logging
import os
import datetime
import pandas as pd
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from datetime import datetime

# Import the converted JavaScript function
from contact_extractor import extract_contact_info, process_html
from api_google import pesquisa_google

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper_integrado.log"),
        logging.StreamHandler()
    ]
)

# Global variable to store results (to access in the signal handler)
collected_results = []

"""
SISTEMA DE SALVAMENTO DE RESULTADOS

Propósito:
Garante que os dados coletados sejam salvos corretamente, mesmo em caso de interrupção
ou falha do programa, evitando perda de informações valiosas.

Analogia:
Como um sistema automático de backup que preserva os documentos produzidos até o momento,
mesmo se ocorrer uma queda de energia no meio do trabalho.
"""

def save_results(results_list, suffix="parcial"):
    """
    Salva os resultados coletados em múltiplos formatos.
    
    Esta função salva os dados nos seguintes formatos:
    - JSON: Dados completos para processamento posterior
    - CSV: Formato tabular para importação em Excel/planilhas
    - HTML: Visualização rápida dos resultados em navegador
    
    Parâmetros:
    - results_list: Lista com os resultados coletados
    - suffix: Sufixo para os nomes dos arquivos (padrão: "parcial")
    
    Retorno:
    - Boolean: True se o salvamento for bem-sucedido, False caso contrário
    """
    try:
        if not results_list:
            logging.warning("Nenhum resultado para salvar.")
            return False
            
        logging.info(f"Salvando {len(results_list)} resultados coletados...")
        
        # Ensure output directory exists
        os.makedirs("resultados", exist_ok=True)
        
        # Save results to a JSON file
        json_filename = f"resultados/contatos_{suffix}.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(results_list, f, ensure_ascii=False, indent=4)
        
        logging.info(f"Resultados salvos em '{json_filename}'")
        
        # Also save as CSV for easy import into spreadsheets
        try:
            # Create a flattened structure for CSV
            csv_data = []
            for item in results_list:
                if not item.get('success', False) or not item.get('data'):
                    continue
                    
                row = {
                    'nome_loja': item.get('nome_loja', 'Desconhecido'),
                    'url': item.get('url', 'N/A'),
                    'data_scraping': item.get('scrapingTime', 'N/A'),
                    'emails': ', '.join(item.get('data', {}).get('emails', [])),
                    'telefones': ', '.join(item.get('data', {}).get('phones', [])),
                    'whatsapp_links': ', '.join(item.get('data', {}).get('whatsapp', {}).get('links', [])),
                    'whatsapp_numeros': ', '.join(item.get('data', {}).get('whatsapp', {}).get('numbers', [])),
                    'facebook': ', '.join(item.get('data', {}).get('socialMedia', {}).get('facebook', [])),
                    'instagram': ', '.join(item.get('data', {}).get('socialMedia', {}).get('instagram', [])),
                    'linkedin': ', '.join(item.get('data', {}).get('socialMedia', {}).get('linkedin', [])),
                    'twitter': ', '.join(item.get('data', {}).get('socialMedia', {}).get('twitter', [])),
                    'youtube': ', '.join(item.get('data', {}).get('socialMedia', {}).get('youtube', []))
                }
                csv_data.append(row)
            
            # Create DataFrame and save to CSV
            if csv_data:
                df = pd.DataFrame(csv_data)
                csv_filename = f"resultados/contatos_{suffix}.csv"
                df.to_csv(csv_filename, index=False, encoding='utf-8')
                logging.info(f"Resultados CSV salvos em '{csv_filename}'")
                
                # Also generate an HTML table for better visualization
                html_filename = f"resultados/contatos_{suffix}.html"
                df.to_html(html_filename, index=False, border=1, classes='table table-striped')
                logging.info(f"Tabela HTML salva em '{html_filename}'")
            else:
                logging.warning("Não há dados válidos para exportar para CSV")
                
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar CSV: {str(e)}")
            return False
    except Exception as e:
        logging.error(f"Erro ao salvar dados: {str(e)}")
        return False

"""
SISTEMA DE TRATAMENTO DE INTERRUPÇÕES

Propósito:
Garante que o programa finalize de forma limpa quando o usuário pressiona Ctrl+C,
salvando os dados coletados até o momento.

Analogia:
Como um gerente de projetos que, ao ser notificado de uma emergência,
organiza rapidamente os materiais e garante que nada seja perdido.
"""

def interrupt_handler(signal, frame):
    """
    Manipulador de sinal para interrupção do usuário (Ctrl+C).
    
    Quando o usuário interrompe o programa com Ctrl+C, esta função:
    1. Registra a interrupção no log
    2. Salva os dados coletados até o momento
    3. Finaliza o programa de forma limpa
    
    Parâmetros:
    - signal: O sinal recebido (SIGINT)
    - frame: Frame atual de execução (não utilizado)
    """
    logging.info("\n\nInterrupção detectada (Ctrl+C). Finalizando de forma limpa...")
    
    # Save data collected so far
    save_results(collected_results)
    
    logging.info("Script finalizado pelo usuário.")
    sys.exit(0)

def finalize_program():
    """
    Função executada automaticamente quando o programa termina
    (independentemente da causa).
    
    Esta função serve como uma rede de segurança final para salvar
    os dados em caso de finalização inesperada do programa.
    """
    logging.info("\n\nFinalizando programa (função de saída de emergência)...")
    
    # Save collected data (using different suffix to not overwrite other saves)
    save_results(collected_results, "emergencia")

"""
FUNÇÕES DE IMPORTAÇÃO E PREPARAÇÃO DE DADOS

Propósito:
Obtém a lista de lojas a serem processadas a partir de diferentes fontes,
garantindo que o sistema tenha dados para trabalhar.
"""

def extract_store_names():
    """
    Extrai nomes de lojas de arquivos existentes ou do módulo principal.
    
    Esta função tenta duas abordagens, em ordem:
    1. Primeiro tenta ler de um arquivo JSON existente
    2. Se não encontrar, importa a função do arquivo main.py
    
    Analogia:
    Como um pesquisador consultando primeiro seus arquivos pessoais
    e, se não encontrar o que procura, indo à biblioteca principal.
    
    Retorno:
    - Lista de nomes de lojas a serem processados
    """
    try:
        # First try to read from the existing JSON file
        try:
            with open("lojas_oficiais_parcial.json", "r", encoding="utf-8") as f:
                lojas_data = json.load(f)
            
            stores = [loja.get('nome', '').strip() for loja in lojas_data if loja.get('nome')]
            logging.info(f"Extraídos {len(stores)} nomes de lojas do arquivo JSON")
            return stores
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.warning(f"Não foi possível ler o arquivo JSON: {str(e)}")
        
        # As a fallback, import the function from main.py and run it
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from main import extrair_lojas_oficiais
        
        logging.info("Executando a função de extração de lojas...")
        lojas_data = extrair_lojas_oficiais()
        
        if not lojas_data:
            logging.error("Falha ao extrair lojas via função")
            return []
        
        stores = [loja.get('nome', '').strip() for loja in lojas_data if loja.get('nome')]
        logging.info(f"Extraídos {len(stores)} nomes de lojas da função")
        return stores
    except Exception as e:
        logging.error(f"Erro ao extrair nomes de lojas: {str(e)}")
        return []

"""
FUNÇÕES DE CONTROLE DE TRÁFEGO

Propósito:
Implementa mecanismos para evitar que o script seja bloqueado por sites
durante o scraping, usando delays adaptativos e tentativas com backoff.
"""

def get_adaptive_delay(success_count, error_count):
    """
    Calcula o tempo de espera adaptativo com base nos sucessos e erros.
    
    Esta função ajusta dinamicamente o tempo de espera entre requisições:
    - Aumenta o tempo quando ocorrem erros (possível bloqueio)
    - Diminui ligeiramente o tempo após sucessos consecutivos
    - Adiciona aleatoriedade para evitar padrões detectáveis
    
    Analogia:
    Como um pescador que espera mais quando não está tendo sucesso,
    e reduz gradualmente a espera quando as coisas estão funcionando bem.
    
    Parâmetros:
    - success_count: Número de sucessos consecutivos
    - error_count: Número de erros consecutivos
    
    Retorno:
    - Tempo de espera em segundos (float)
    """
    base_delay = 5  # Base delay in seconds
    
    # If we've had errors, increase delay substantially
    if error_count > 0:
        return base_delay + (error_count * 5) + random.uniform(1, 3)
    
    # For regular successful requests, use moderate randomized delay
    return base_delay + random.uniform(1, 3) - min(2, success_count * 0.1)  # Gradually decrease delay with success

def fetch_html(url, max_retries=3):
    """
    Busca conteúdo HTML de uma URL com sistema de tentativas e tratamento de erros.
    
    Esta função:
    1. Tenta acessar a URL com cabeçalhos realistas (simulando navegador)
    2. Em caso de falha, implementa backoff exponencial entre tentativas
    3. Desiste após número máximo de tentativas configurável
    
    Analogia:
    Como um cliente que, ao encontrar uma porta fechada, espera um tempo
    crescente antes de bater novamente, e eventualmente desiste.
    
    Parâmetros:
    - url: URL da página a ser acessada
    - max_retries: Número máximo de tentativas (padrão: 3)
    
    Retorno:
    - Conteúdo HTML em texto, ou None em caso de falha
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/'
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.warning(f"Tentativa {attempt+1}/{max_retries} falhou: {str(e)}")
            if attempt < max_retries - 1:
                # Exponential backoff
                wait_time = 2 ** attempt + random.uniform(0, 1)
                logging.info(f"Aguardando {wait_time:.2f} segundos antes de tentar novamente...")
                time.sleep(wait_time)
            else:
                logging.error(f"Falha após {max_retries} tentativas: {str(e)}")
                return None

def search_and_extract_contacts(store_name, api_key, engine_id):
    """
    Busca informações sobre uma loja e extrai dados de contato dos resultados.
    
    Esta função coordena o processo completo para uma loja:
    1. Realiza busca no Google usando a API personalizada
    2. Processa cada resultado da busca, extraindo informações de contato
    3. Combina os resultados em um objeto consolidado
    
    Analogia:
    Como um detetive que primeiro pesquisa sobre uma empresa,
    depois visita cada endereço encontrado para coletar informações,
    e finalmente organiza tudo em um único relatório.
    
    Parâmetros:
    - store_name: Nome da loja a ser pesquisada
    - api_key: Chave da API do Google
    - engine_id: ID do mecanismo de busca personalizado
    
    Retorno:
    - Dicionário com todas as informações de contato encontradas
    """
    try:
        # Create search query with contact information terms
        query = f"{store_name} contato telefone email whatsapp site oficial"
        logging.info(f"Pesquisando: {query}")
        
        # Search using Google API
        search_results = pesquisa_google(api_key, engine_id, query)
        
        if not search_results:
            logging.warning(f"Nenhum resultado encontrado para '{store_name}'")
            return {
                'success': False,
                'nome_loja': store_name,
                'error': "Nenhum resultado de pesquisa encontrado"
            }
        
        # Process the top 2 results
        all_results = []
        for i, result in enumerate(search_results[:2]):
            try:
                result_url = result.get('link')
                if not result_url:
                    continue
                    
                logging.info(f"Processando resultado {i+1}: {result_url}")
                
                # Fetch HTML content from the URL
                html_content = fetch_html(result_url)
                if not html_content:
                    logging.warning(f"Não foi possível obter conteúdo HTML de {result_url}")
                    continue
                
                # Extract contact information
                extraction_result = process_html(html_content, result_url)
                extraction_result['nome_loja'] = store_name
                extraction_result['scrapingTime'] = datetime.now().isoformat()
                
                # Add to results list
                all_results.append(extraction_result)
                
            except Exception as e:
                logging.error(f"Erro ao processar resultado {i+1} para '{store_name}': {str(e)}")
        
        # If we processed multiple results, merge them
        if len(all_results) > 1:
            # Start with the first result
            merged_result = all_results[0]
            
            # For each additional result, merge the data
            for result in all_results[1:]:
                if not result.get('success', False) or not result.get('data'):
                    continue
                
                # Merge emails
                merged_result['data']['emails'] = list(set(
                    merged_result['data'].get('emails', []) + 
                    result['data'].get('emails', [])
                ))
                
                # Merge phones
                merged_result['data']['phones'] = list(set(
                    merged_result['data'].get('phones', []) + 
                    result['data'].get('phones', [])
                ))
                
                # Merge WhatsApp links and numbers
                merged_result['data']['whatsapp']['links'] = list(set(
                    merged_result['data'].get('whatsapp', {}).get('links', []) + 
                    result['data'].get('whatsapp', {}).get('links', [])
                ))
                merged_result['data']['whatsapp']['numbers'] = list(set(
                    merged_result['data'].get('whatsapp', {}).get('numbers', []) + 
                    result['data'].get('whatsapp', {}).get('numbers', [])
                ))
                
                # Merge social media
                for platform in merged_result['data'].get('socialMedia', {}):
                    merged_result['data']['socialMedia'][platform] = list(set(
                        merged_result['data'].get('socialMedia', {}).get(platform, []) + 
                        result['data'].get('socialMedia', {}).get(platform, [])
                    ))
            
            # Use this merged result
            return merged_result
        
        # Otherwise, use the first (and only) result
        return all_results[0] if all_results else {
            'success': False,
            'nome_loja': store_name,
            'error': "Falha ao processar resultados"
        }
        
    except Exception as e:
        logging.error(f"Erro ao pesquisar e extrair para '{store_name}': {str(e)}")
        traceback.print_exc()
        return {
            'success': False,
            'nome_loja': store_name,
            'error': str(e)
        }

def main():
    """
    Função principal que coordena todo o processo de scraping.
    
    Esta função:
    1. Configura os manipuladores de sinal para interrupções
    2. Obtém a lista de lojas para processamento
    3. Processa cada loja, coletando dados de contato
    4. Salva resultados parciais periodicamente
    5. Finaliza com um resumo da operação
    
    Analogia:
    Como um gerente de projeto que define a estratégia, distribui as tarefas,
    monitora o progresso, e garante que os resultados sejam salvos.
    """
    # Register the signal handler for Ctrl+C
    signal.signal(signal.SIGINT, interrupt_handler)
    # Register the exit function
    atexit.register(finalize_program)
    
    logging.info("=== Iniciando sistema integrado de scraping de contatos ===")
    
    # Extract store names
    store_names = extract_store_names()
    if not store_names:
        logging.error("Nenhum nome de loja encontrado. Abortando.")
        return
    
    logging.info(f"Encontrados {len(store_names)} nomes de lojas para processar")
    
    # Google API credentials - from api_google.py
    api_key = "AIzaSyDkwgWLJ_NISwA6Nk-4X0__e68jRK7eyLw"
    engine_id = "47366a2537ee841e9"
    
    # Process each store
    success_count = 0
    error_count = 0
    
    for i, store_name in enumerate(store_names):
        try:
            logging.info(f"Processando loja {i+1}/{len(store_names)}: {store_name}")
            
            # Search and extract contact information
            result = search_and_extract_contacts(store_name, api_key, engine_id)
            
            # Add to collected results
            collected_results.append(result)
            
            # Update statistics for adaptive delay
            if result.get('success', False):
                success_count += 1
                error_count = max(0, error_count - 0.5)  # Gradually reduce error count with successes
            else:
                error_count += 1
                success_count = max(0, success_count - 1)  # Reduce success count on error
            
            # Save intermediate results every 10 stores
            if (i + 1) % 10 == 0:
                save_results(collected_results, f"parcial_{i+1}")
            
            # Apply adaptive delay between requests
            if i < len(store_names) - 1:  # Don't delay after the last item
                delay = get_adaptive_delay(success_count, error_count)
                logging.info(f"Aguardando {delay:.2f} segundos até a próxima loja...")
                time.sleep(delay)
                
        except Exception as e:
            logging.error(f"Erro ao processar '{store_name}': {str(e)}")
            traceback.print_exc()
            error_count += 1
    
    # Save final results
    save_results(collected_results, "final")
    
    logging.info("=== Processo de extração de contatos concluído ===")
    logging.info(f"Total de lojas processadas: {len(store_names)}")
    logging.info(f"Resultados finais salvos em 'resultados/contatos_final.json'")

# Entry point
if __name__ == "__main__":
    import atexit
    main()
