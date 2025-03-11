Write-Host "Removendo arquivos obsoletos após implementação da Clean Architecture..." -ForegroundColor Yellow

# Lista de arquivos a serem removidos
$files_to_remove = @(
    # Sistema JavaScript antigo
    "scraper.js",
    "utils\dataProcessor.js",
    "index.js",
    
    # Scripts Python antigos
    "scraper_integrado.py",
    "api_google.py",
    
    # Scripts de configuração temporários
    "setup_structure.sh",
    
    # Arquivos auxiliares
    "criar_arquivo_teste.py",
    "run.sh"
)

# Remover cada arquivo
foreach ($file in $files_to_remove) {
    $full_path = Join-Path -Path $PSScriptRoot -ChildPath $file
    
    if (Test-Path $full_path) {
        Write-Host "Removendo: $file" -ForegroundColor Red
        Remove-Item -Path $full_path -Force
    } else {
        Write-Host "Arquivo não encontrado: $file" -ForegroundColor Gray
    }
}

Write-Host "`nLimpeza concluída. O projeto agora contém apenas os arquivos necessários para a Clean Architecture." -ForegroundColor Green

# Mostrar estrutura final de diretórios
Write-Host "`nEstrutura atual do projeto:" -ForegroundColor Cyan
Get-ChildItem -Directory | ForEach-Object { Write-Host "/$($_.Name)" -ForegroundColor Cyan }
