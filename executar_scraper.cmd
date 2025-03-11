@echo off
setlocal enabledelayedexpansion
title Mercado Livre Scraper

:: Cores para melhor visualização
color 0A

:: Configurar código de página para UTF-8
chcp 65001 >nul

:: Exibir cabeçalho
echo ===============================================
echo      SCRAPER DE MERCADO LIVRE - VERSAO CMD      
echo ===============================================
echo.

:: Verificar Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado! Verifique se o Python esta instalado e no PATH.
    pause
    exit /b 1
)

:: Verificar ambiente virtual
if not exist venv\Scripts\activate.bat (
    echo Criando ambiente virtual Python...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
)

:: Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Erro ao ativar ambiente virtual. Continuando com Python do sistema...
)

:: Instalar dependências - Versão robusta
echo Instalando/verificando dependencias...
echo.
echo Atualizando pip...
python -m pip install --upgrade pip

echo Instalando pacotes essenciais...
python -m pip install requests beautifulsoup4 google-api-python-client selenium webdriver-manager

:: Tentar instalar pandas usando wheels pré-compilados
echo Tentando instalar pandas (pode falhar, mas nao eh critico)...
python -m pip install --only-binary=:all: pandas || echo Pandas nao instalado, mas o script continuara funcionando

echo Instalando dependencias do requirements.txt...
pip install -r requirements.txt

:: Verificar se o módulo requests está instalado (este é crítico)
python -c "import requests" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] O modulo 'requests' nao foi instalado corretamente. Tentando novamente...
    python -m pip install requests --force-reinstall
)

:: Criar diretório de resultados
if not exist resultados mkdir resultados

:: Menu de opções
:MENU
echo.
echo Escolha uma opcao:
echo [1] Extrair lista de lojas oficiais
echo [2] Extrair contatos das lojas
echo [3] Executar processo completo (lojas + contatos)
echo [4] Verificar arquivos de resultados
echo [5] Processar empresas de lojas_oficiais_parcial.json
echo [6] Sair
echo.

set /p opcao="Digite o numero da opcao desejada: "

:: Processar escolha
if "%opcao%"=="1" (
    cls
    echo EXTRAINDO LISTA DE LOJAS OFICIAIS
    echo =================================
    echo.
    echo Esta operacao pode demorar varios minutos.
    echo Um navegador Chrome sera aberto para realizar o scraping.
    echo.
    echo Pressione qualquer tecla para iniciar...
    pause >nul
    
    python main.py
    
    echo.
    echo Processo finalizado!
    echo Os resultados estao em: lojas_oficiais.json e lojas_oficiais.csv
    pause
    goto MENU
)

if "%opcao%"=="2" (
    cls
    echo EXTRAINDO CONTATOS DAS LOJAS
    echo ============================
    echo.
    
    :: Verificar se existe arquivo de lojas
    if not exist lojas_oficiais.json (
        if not exist lojas_oficiais_parcial.json (
            echo [ERRO] Nenhum arquivo de lojas encontrado!
            echo Execute a opcao 1 primeiro para extrair a lista de lojas.
            pause
            goto MENU
        )
    )
    
    echo Esta operacao usa a API Google para pesquisar contatos.
    echo Pode demorar dependendo do numero de lojas.
    echo.
    echo Pressione qualquer tecla para iniciar...
    pause >nul
    
    python execute_scraper_service.py
    
    echo.
    echo Processo finalizado.
    echo Os resultados estao em: resultados/scraper_service_results.json
    pause
    goto MENU
)

if "%opcao%"=="3" (
    cls
    echo EXECUTANDO PROCESSO COMPLETO
    echo ============================
    echo.
    echo Esta operacao combina a extracao de lojas e contatos.
    echo Pode demorar bastante tempo para completar.
    echo.
    echo Pressione qualquer tecla para iniciar...
    pause >nul
    
    echo Etapa 1: Extraindo lojas...
    python main.py
    
    echo.
    echo Etapa 2: Extraindo contatos...
    python execute_scraper_service.py
    
    echo.
    echo Processo completo finalizado!
    echo Verifique a pasta resultados/ para os arquivos gerados.
    pause
    goto MENU
)

if "%opcao%"=="4" (
    cls
    echo VERIFICANDO ARQUIVOS DE RESULTADOS
    echo =================================
    echo.
    
    python localizar_resultados.py
    
    echo.
    echo Pressione qualquer tecla para voltar ao menu...
    pause >nul
    goto MENU
)

if "%opcao%"=="5" (
    cls
    echo PROCESSANDO EMPRESAS DE lojas_oficiais_parcial.json
    echo ==================================================
    echo.
    
    :: Verificar se o arquivo existe
    if not exist lojas_oficiais_parcial.json (
        echo [ERRO] Arquivo lojas_oficiais_parcial.json nao encontrado!
        echo Crie o arquivo ou execute a opcao 1 primeiro para extrair a lista de lojas.
        pause
        goto MENU
    )
    
    :: Executar com Unicode ativado para console
    echo Este processo vai:
    echo 1. Ler cada empresa do arquivo lojas_oficiais_parcial.json
    echo 2. Buscar cada empresa no Google
    echo 3. Extrair dados de contato (telefone, email, etc.)
    echo 4. Salvar os resultados em formato JSON
    echo.
    echo Esta operacao pode demorar dependendo do numero de empresas.
    echo.
    echo Pressione qualquer tecla para iniciar o processamento...
    pause >nul
    
    :: Chamar diretamente o script Python em vez de executar através de string
    python process_parcial_stores.py
    
    :: Verificar se o processamento foi bem-sucedido
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo Processo finalizado com sucesso!
        echo Os resultados estao em: resultados/lojas_parcial_processadas.json
    ) else (
        echo.
        echo [ERRO] Ocorreu um erro durante o processamento. Verifique o log para mais detalhes.
    )
    pause
    goto MENU
)

if "%opcao%"=="6" (
    echo.
    echo Encerrando programa...
    exit /b 0
)

:: Opcao inválida
echo.
echo Opcao invalida! Por favor, escolha uma opcao entre 1 e 6.
pause
goto MENU