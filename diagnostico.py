import os
import sys
import importlib.util
import subprocess
import shutil
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("diagnostico.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def verificar_python():
    """Verifica a versão do Python e se está corretamente instalada"""
    logger.info(f"Python versão: {sys.version}")
    return sys.version_info.major >= 3 and sys.version_info.minor >= 6

def verificar_dependencias():
    """Verifica se todas as dependências necessárias estão instaladas"""
    dependencias = [
        "requests", "pandas", "beautifulsoup4", "selenium", 
        "google-api-python-client", "webdriver-manager"
    ]
    
    dependencias_faltantes = []
    
    for dep in dependencias:
        if importlib.util.find_spec(dep) is None:
            dependencias_faltantes.append(dep)
    
    if dependencias_faltantes:
        logger.warning(f"Dependências faltantes: {', '.join(dependencias_faltantes)}")
        return False, dependencias_faltantes
    else:
        logger.info("Todas as dependências necessárias estão instaladas")
        return True, []

def instalar_dependencias(deps=None):
    """Instala as dependências faltantes"""
    try:
        if deps:
            cmd = [sys.executable, "-m", "pip", "install"] + deps
        else:
            cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        
        logger.info(f"Executando: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Dependências instaladas com sucesso")
            return True
        else:
            logger.error(f"Erro ao instalar dependências: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Erro ao instalar dependências: {str(e)}")
        return False

def verificar_estrutura_diretorios():
    """Verifica se a estrutura de diretórios está correta"""
    diretorios_necessarios = [
        "domain", "domain/entities", "domain/usecases",
        "application", "application/services",
        "infrastructure", "infrastructure/repositories", "infrastructure/web", "infrastructure/search",
        "interfaces", "interfaces/controllers", "interfaces/presenters",
        "config", "resultados"
    ]
    
    diretorios_faltantes = []
    
    for diretorio in diretorios_necessarios:
        if not os.path.exists(diretorio):
            diretorios_faltantes.append(diretorio)
    
    if diretorios_faltantes:
        logger.warning(f"Diretórios faltantes: {', '.join(diretorios_faltantes)}")
        return False, diretorios_faltantes
    else:
        logger.info("Estrutura de diretórios está correta")
        return True, []

def criar_diretorios_faltantes(diretorios):
    """Cria os diretórios faltantes"""
    for diretorio in diretorios:
        try:
            os.makedirs(diretorio, exist_ok=True)
            logger.info(f"Diretório criado: {diretorio}")
        except Exception as e:
            logger.error(f"Erro ao criar diretório {diretorio}: {str(e)}")

def verificar_arquivos_principais():
    """Verifica se os arquivos principais existem"""
    arquivos_necessarios = [
        "main.py",
        "domain/entities/contact_info.py",
        "domain/entities/store.py",
        "domain/usecases/extract_contacts_usecase.py",
        "domain/usecases/process_stores_usecase.py",
        "infrastructure/repositories/store_repository.py",
        "infrastructure/web/html_fetcher.py",
        "infrastructure/search/google_search_service.py",
        "config/settings.py"
    ]
    
    arquivos_faltantes = []
    
    for arquivo in arquivos_necessarios:
        if not os.path.exists(arquivo):
            arquivos_faltantes.append(arquivo)
    
    if arquivos_faltantes:
        logger.warning(f"Arquivos faltantes: {', '.join(arquivos_faltantes)}")
        return False, arquivos_faltantes
    else:
        logger.info("Todos os arquivos principais estão presentes")
        return True, []

def corrigir_imports():
    """Corrige problemas comuns de imports no arquivo main.py"""
    if not os.path.exists("main.py"):
        logger.error("Arquivo main.py não encontrado")
        return False
    
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            conteudo = f.read()
        
        # Corrigir imports comuns que podem estar faltando
        imports_corrigidos = """
import os
import sys
import logging
import json
import signal
import atexit
import traceback
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Adicionar o diretório raiz ao path para permitir imports relativos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
"""
        
        # Se o arquivo não tiver estes imports, adicionar no início
        if "import sys" not in conteudo or "sys.path.insert" not in conteudo:
            novo_conteudo = imports_corrigidos + conteudo
            
            with open("main.py", "w", encoding="utf-8") as f:
                f.write(novo_conteudo)
            
            logger.info("Imports corrigidos no arquivo main.py")
        
        return True
    except Exception as e:
        logger.error(f"Erro ao corrigir imports: {str(e)}")
        return False

def verificar_arquivo_init():
    """Verifica e cria arquivos __init__.py em todos os diretórios Python"""
    diretorios = [
        "domain", "domain/entities", "domain/usecases",
        "application", "application/services",
        "infrastructure", "infrastructure/repositories", "infrastructure/web", "infrastructure/search",
        "interfaces", "interfaces/controllers", "interfaces/presenters",
        "config"
    ]
    
    for diretorio in diretorios:
        if os.path.exists(diretorio):
            init_file = os.path.join(diretorio, "__init__.py")
            if not os.path.exists(init_file):
                try:
                    with open(init_file, "w", encoding="utf-8") as f:
                        f.write("# Arquivo de inicialização do pacote Python\n")
                    logger.info(f"Arquivo __init__.py criado em: {diretorio}")
                except Exception as e:
                    logger.error(f"Erro ao criar arquivo __init__.py em {diretorio}: {str(e)}")

def criar_script_execucao_simples():
    """Cria um script de execução muito simples para teste"""
    conteudo = """@echo off
echo Este eh um script de execucao simplificado para teste
echo.

echo Verificando se o Python esta instalado...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo Erro: Python nao encontrado. Instale o Python e tente novamente.
    pause
    exit /b 1
)

echo.
echo Ativando ambiente virtual...
call venv\\Scripts\\activate.bat

echo.
echo Executando o script principal...
python main.py

echo.
echo Execucao concluida.
pause
"""
    
    try:
        with open("executar_teste.bat", "w", encoding="utf-8") as f:
            f.write(conteudo)
        logger.info("Script de teste criado: executar_teste.bat")
    except Exception as e:
        logger.error(f"Erro ao criar script de teste: {str(e)}")

def main():
    """Função principal de diagnóstico"""
    logger.info("=== Iniciando diagnóstico do sistema de scraper ===")
    
    # Verificar versão do Python
    if not verificar_python():
        logger.error("Versão do Python incompatível. É necessário Python 3.6 ou superior.")
        return
    
    # Verificar estrutura de diretórios
    estrutura_ok, diretorios_faltantes = verificar_estrutura_diretorios()
    if not estrutura_ok:
        logger.info("Criando diretórios faltantes...")
        criar_diretorios_faltantes(diretorios_faltantes)
    
    # Verificar existência de arquivos principais
    arquivos_ok, _ = verificar_arquivos_principais()
    if not arquivos_ok:
        logger.warning("Alguns arquivos principais estão faltando. Isto pode causar erros.")
    
    # Verificar dependências
    deps_ok, deps_faltantes = verificar_dependencias()
    if not deps_ok:
        logger.info("Instalando dependências faltantes...")
        instalar_dependencias(deps_faltantes)
    
    # Corrigir imports
    corrigir_imports()
    
    # Verificar e criar arquivos __init__.py
    verificar_arquivo_init()
    
    # Criar script de execução simples
    criar_script_execucao_simples()
    
    logger.info("=== Diagnóstico e correções concluídos ===")
    logger.info("Tente executar o script 'executar_teste.bat' para verificar se o problema foi resolvido.")

if __name__ == "__main__":
    main()
