# Script para iniciar a versão web do Sistema DAC
# Autor: Alejandro Alexandre (RA: 197890)

$ErrorActionPreference = "Continue"

# Cores para output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

Write-ColorOutput Cyan "========================================="
Write-ColorOutput Cyan "  Sistema DAC - Versão Web"
Write-ColorOutput Cyan "  Iniciando servidores..."
Write-ColorOutput Cyan "========================================="
Write-Output ""

# Diretórios
$rootDir = "c:\Users\FenixPosts\Desktop\Nova pasta\DAC_2025"
$backendDir = "$rootDir\Versão PY\web\backend"
$frontendDir = "$rootDir\Versão Web"
$pythonExe = "$rootDir\.venv\Scripts\python.exe"

# Verificar se o ambiente virtual existe
if (-Not (Test-Path $pythonExe)) {
    Write-ColorOutput Red "Erro: Ambiente virtual Python não encontrado!"
    Write-ColorOutput Yellow "Execute primeiro: python -m venv .venv"
    exit 1
}

# Iniciar backend (FastAPI)
Write-ColorOutput Green "[1/2] Iniciando backend FastAPI na porta 8000..."
$backendJob = Start-Job -ScriptBlock {
    param($backend, $python)
    Set-Location $backend
    & $python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
} -ArgumentList $backendDir, $pythonExe

Start-Sleep -Seconds 2

# Iniciar frontend (Next.js)
Write-ColorOutput Green "[2/2] Iniciando frontend Next.js na porta 3002..."
Set-Location $frontendDir
$frontendProcess = Start-Process powershell -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "npm run start-frontend" -PassThru -NoNewWindow

Write-Output ""
Write-ColorOutput Cyan "========================================="
Write-ColorOutput Green "  Servidores iniciados!"
Write-ColorOutput Cyan "========================================="
Write-Output ""
Write-ColorOutput Yellow "Backend (API):     http://localhost:8000"
Write-ColorOutput Yellow "Frontend (Web):    http://localhost:3002"
Write-ColorOutput Yellow "Documentação API:  http://localhost:8000/docs"
Write-Output ""
Write-ColorOutput Cyan "Pressione Ctrl+C para encerrar os servidores"
Write-Output ""

# Aguardar
try {
    Wait-Job $backendJob
} finally {
    Write-ColorOutput Red "`nEncerrando servidores..."
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Stop-Process -Id $frontendProcess.Id -ErrorAction SilentlyContinue
    Write-ColorOutput Green "Servidores encerrados."
}
