Write-Host "===== INICIANDO SCRAPER DE MERCADO LIVRE =====" -ForegroundColor Cyan
Write-Host ""

# Ativar ambiente virtual se existir
if (Test-Path -Path "venv\Scripts\Activate.ps1") {
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
}

# Criar diretório de resultados se não existir
if (-not (Test-Path -Path "resultados")) {
    New-Item -ItemType Directory -Path "resultados" | Out-Null
    Write-Host "Diretório 'resultados' criado." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Selecione o tipo de scraper que deseja executar:" -ForegroundColor Green
Write-Host ""
Write-Host "1) Scraper de lojas (extrai lista de lojas oficiais)" -ForegroundColor White
Write-Host "2) Scraper de contatos (extrai contatos das lojas)" -ForegroundColor White
Write-Host "3) Scraper completo (extrai lojas e depois contatos)" -ForegroundColor White
Write-Host ""

$opcao = Read-Host "Digite a opção (1, 2 ou 3)"

switch ($opcao) {
    "1" {
        Write-Host "`nIniciando scraper de lojas oficiais..." -ForegroundColor Cyan
        python main.py
    }
    "2" {
        Write-Host "`nIniciando scraper de contatos..." -ForegroundColor Cyan
        python execute_scraper_service.py
    }
    "3" {
        Write-Host "`nIniciando scraper completo (lojas + contatos)..." -ForegroundColor Cyan
        python main.py
        Write-Host "`nAgora iniciando extração de contatos..." -ForegroundColor Cyan
        python execute_scraper_service.py
    }
    default {
        Write-Host "`nOpção inválida. Por favor execute novamente e escolha 1, 2 ou 3." -ForegroundColor Red
        Write-Host "Pressione qualquer tecla para sair..."
        $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
        exit 1
    }
}

Write-Host ""
Write-Host "Scraping concluído! Verifique a pasta 'resultados' para os arquivos gerados." -ForegroundColor Green
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
