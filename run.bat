@echo off
echo Iniciando sistema de scraper em arquitetura limpa...

REM Verificar se o ambiente virtual Python existe
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar dependências
echo Instalando dependências...
pip install -r requirements.txt

REM Garantir que a estrutura de diretórios existe
if not exist resultados mkdir resultados

REM Executar aplicação
echo Iniciando aplicação...
python main.py %*

echo.
echo Execução concluída.
pause
