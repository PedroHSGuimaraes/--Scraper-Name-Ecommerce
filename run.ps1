Write-Host "Iniciando sistema de scraper em arquitetura limpa..." -ForegroundColor Green

# Verificar se o ambiente virtual Python existe
if (-not (Test-Path -Path "venv")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
}

# Ativar ambiente virtual
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Instalar dependências
Write-Host "Instalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt

# Garantir que a estrutura de diretórios existe
if (-not (Test-Path -Path "resultados")) {
    New-Item -ItemType Directory -Path "resultados" | Out-Null
    Write-Host "Diretório 'resultados' criado." -ForegroundColor Yellow
}

# Executar aplicação
Write-Host "Iniciando aplicação..." -ForegroundColor Green
python main.py $args

Write-Host "`nExecução concluída." -ForegroundColor Green
Write-Host "Pressione qualquer tecla para continuar..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
