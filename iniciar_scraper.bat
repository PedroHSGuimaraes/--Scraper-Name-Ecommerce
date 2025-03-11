@echo off
setlocal enabledelayedexpansion
title Scraper do Mercado Livre - Menu de Execução
color 0A

:: Criar log
echo [%date% %time%] Iniciando execucao do scraper > scraper_execucao.log

echo ===== INICIANDO SCRAPER DE MERCADO LIVRE =====
echo.

:: Verificar se o Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado! Instale o Python e adicione ao PATH.
    echo [%date% %time%] ERRO: Python nao encontrado >> scraper_execucao.log
    color 0C
    pause
    exit /b 1
)

:: Verificar ambiente virtual
if not exist venv (
    echo Ambiente virtual nao encontrado. Criando...
    echo [%date% %time%] Criando ambiente virtual >> scraper_execucao.log
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERRO] Falha ao criar ambiente virtual!
        echo [%date% %time%] ERRO: Falha ao criar ambiente virtual >> scraper_execucao.log
        color 0C
        pause
        exit /b 1
    )
    echo Ambiente virtual criado com sucesso.
)

:: Ativar ambiente virtual
echo Ativando ambiente virtual...
echo [%date% %time%] Ativando ambiente virtual >> scraper_execucao.log
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao ativar ambiente virtual!
    echo [%date% %time%] ERRO: Falha ao ativar ambiente virtual >> scraper_execucao.log
    color 0C
    pause
    exit /b 1
)

:: Verificar/instalar dependências
echo Verificando dependencias...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Algumas dependencias podem nao ter sido instaladas corretamente.
    echo [%date% %time%] AVISO: Problemas com dependencias >> scraper_execucao.log
    color 0E
)

:: Criar diretório de resultados se não existir
if not exist resultados (
    echo Criando diretorio de resultados...
    mkdir resultados
    echo [%date% %time%] Diretorio de resultados criado >> scraper_execucao.log
)

echo.
echo Selecione o tipo de scraper que deseja executar:
echo.
echo 1) Scraper de lojas (extrai lista de lojas oficiais)
echo 2) Scraper de contatos (extrai contatos das lojas)
echo 3) Scraper completo (extrai lojas e depois contatos)
echo.

set /p opcao="Digite a opção (1, 2 ou 3): "

:: Executar com tratamento de erro
if "%opcao%"=="1" (
    echo.
    echo Iniciando scraper de lojas oficiais...
    echo [%date% %time%] Iniciando scraper de lojas oficiais >> scraper_execucao.log
    python main.py
    set erro=%ERRORLEVEL%
) else if "%opcao%"=="2" (
    echo.
    echo Iniciando scraper de contatos...
    echo [%date% %time%] Iniciando scraper de contatos >> scraper_execucao.log
    
    :: Verificar se o arquivo de lojas existe
    if not exist lojas_oficiais.json (
        if not exist lojas_oficiais_parcial.json (
            echo [AVISO] Arquivo de lojas nao encontrado! Execute o scraper de lojas primeiro.
            echo [%date% %time%] AVISO: Arquivo de lojas não encontrado >> scraper_execucao.log
            color 0E
            pause
            exit /b 1
        )
    )
    
    python execute_scraper_service.py
    set erro=%ERRORLEVEL%
) else if "%opcao%"=="3" (
    echo.
    echo Iniciando scraper completo (lojas + contatos)...
    echo [%date% %time%] Iniciando scraper completo >> scraper_execucao.log
    
    :: Executar primeiro script
    python main.py
    set erro=%ERRORLEVEL%
    
    if !erro! EQU 0 (
        echo.
        echo Agora iniciando extração de contatos...
        echo [%date% %time%] Iniciando extração de contatos >> scraper_execucao.log
        python execute_scraper_service.py
        set erro=%ERRORLEVEL%
    ) else (
        echo [ERRO] O scraper de lojas falhou com código de erro !erro!
        echo [%date% %time%] ERRO: Falha no scraper de lojas, código !erro! >> scraper_execucao.log
    )
) else (
    echo.
    echo [ERRO] Opção inválida. Por favor execute novamente e escolha 1, 2 ou 3.
    echo [%date% %time%] ERRO: Opção inválida selecionada: %opcao% >> scraper_execucao.log
    color 0C
    pause
    exit /b 1
)

:: Verificar se houve erro na execução
if %erro% NEQ 0 (
    echo.
    echo [ERRO] Ocorreu um erro durante a execução do scraper (código %erro%).
    echo [%date% %time%] ERRO: Execução do scraper falhou com código %erro% >> scraper_execucao.log
    color 0C
) else (
    echo.
    echo Scraping concluído com sucesso!
    echo Verifique a pasta "resultados" para os arquivos gerados.
    echo.
    echo [%date% %time%] Execução concluída com sucesso >> scraper_execucao.log
)

:: Sugerir localização dos arquivos
echo.
echo Possíveis locais dos resultados:
echo  - Scraper de lojas: lojas_oficiais.json, lojas_oficiais.csv
echo  - Scraper de contatos: resultados/scraper_service_results.json
echo  - Outros: resultados/contatos_final.json, resultados/contatos_processados_*.json
echo.

pause
endlocal
