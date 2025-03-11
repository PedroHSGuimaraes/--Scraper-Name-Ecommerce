import os
import json
import csv
import glob
import time

def formatar_tamanho(tamanho_bytes):
    """Formata o tamanho do arquivo para exibição amigável"""
    for unidade in ['B', 'KB', 'MB', 'GB']:
        if tamanho_bytes < 1024.0:
            return f"{tamanho_bytes:.2f} {unidade}"
        tamanho_bytes /= 1024.0
    return f"{tamanho_bytes:.2f} TB"

def contar_registros_json(arquivo_path):
    """Conta quantos registros existem em um arquivo JSON"""
    try:
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            if isinstance(dados, list):
                return len(dados)
            elif isinstance(dados, dict) and "resultados" in dados:
                return len(dados["resultados"])
            else:
                return "Não é lista"
    except Exception as e:
        return f"Erro: {str(e)}"

def contar_registros_csv(arquivo_path):
    """Conta quantas linhas existem em um arquivo CSV"""
    try:
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            leitor = csv.reader(f)
            linhas = sum(1 for _ in leitor)
            return linhas - 1  # Subtrair cabeçalho
    except Exception as e:
        return f"Erro: {str(e)}"

def encontrar_todos_resultados():
    """Encontra todos os arquivos de resultados do scraper"""
    raiz = os.path.dirname(os.path.abspath(__file__))
    
    print("\n===== BUSCANDO ARQUIVOS DE RESULTADOS DO SCRAPER =====")
    print(f"Diretório base: {raiz}")
    print("=" * 70)
    
    # Padrões de nomes de arquivos conhecidos
    padroes = [
        "lojas_oficiais*.json",
        "lojas_oficiais*.csv",
        "resultados/*.json",
        "resultados/*.csv",
        "resultados/*.html",
        "resultados.json",
        "contatos*.json",
        "contatos*.csv"
    ]
    
    # Armazenar resultados
    arquivos_encontrados = []
    
    # Buscar por todos os padrões
    for padrao in padroes:
        caminho_busca = os.path.join(raiz, padrao)
        for arquivo in glob.glob(caminho_busca):
            tamanho = os.path.getsize(arquivo)
            data_mod = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(os.path.getmtime(arquivo)))
            
            # Contar registros
            num_registros = "N/A"
            if arquivo.endswith('.json'):
                num_registros = contar_registros_json(arquivo)
            elif arquivo.endswith('.csv'):
                num_registros = contar_registros_csv(arquivo)
            
            arquivos_encontrados.append({
                "caminho": arquivo,
                "tamanho": tamanho,
                "tamanho_formatado": formatar_tamanho(tamanho),
                "data_modificacao": data_mod,
                "num_registros": num_registros
            })
    
    # Ordenar por tamanho (maior primeiro)
    arquivos_encontrados.sort(key=lambda x: x["tamanho"], reverse=True)
    
    # Exibir resultados
    print(f"\nTotal de arquivos encontrados: {len(arquivos_encontrados)}\n")
    
    print(f"{'ARQUIVO':<50} {'REGISTROS':<10} {'TAMANHO':<10} {'MODIFICADO':<20}")
    print("-" * 90)
    
    for arquivo in arquivos_encontrados:
        nome_arquivo = os.path.basename(arquivo["caminho"])
        print(f"{nome_arquivo:<50} {arquivo['num_registros']:<10} {arquivo['tamanho_formatado']:<10} {arquivo['data_modificacao']:<20}")
        
    print("\n\nDIRETÓRIOS ONDE PROCURAR:")
    print(f"Raiz do projeto: {raiz}")
    print(f"Pasta de resultados: {os.path.join(raiz, 'resultados')}")
    
    # Sugerir com base no número de registros
    print("\nARQUIVOS QUE PODEM TER APROXIMADAMENTE 8000 REGISTROS:")
    for arquivo in arquivos_encontrados:
        if isinstance(arquivo['num_registros'], int) and 7000 <= arquivo['num_registros'] <= 9000:
            print(f"* {os.path.basename(arquivo['caminho'])} ({arquivo['num_registros']} registros)")

# Executar a busca
if __name__ == "__main__":
    encontrar_todos_resultados()
    
    print("\nPressione ENTER para sair...")
    input()
