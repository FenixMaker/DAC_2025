# ============================================================================
# Sistema DAC - Script de Configuração Automática (PowerShell)
# Autor: Alejandro Alexandre (RA: 197890)
# Curso: Análise e Desenvolvimento de Sistemas
# Ano: 2025
# ============================================================================

#Requires -Version 5.1

$ErrorActionPreference = "Continue"

# Cores
function Write-ColorOutput {
    param(
        [string]$Message,
        [ConsoleColor]$Color = [ConsoleColor]::White
    )
    $originalColor = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $Color
    Write-Output $Message
    $host.UI.RawUI.ForegroundColor = $originalColor
}

function Write-Header {
    param([string]$Text)
    Write-ColorOutput "`n========================================================================" Cyan
    Write-ColorOutput "  $Text" Cyan
    Write-ColorOutput "========================================================================`n" Cyan
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "[OK] $Message" Green
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "[INFO] $Message" Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-ColorOutput "[ERRO] $Message" Red
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "$Message" White
}

# Banner
Clear-Host
Write-Header "SISTEMA DAC - CONFIGURAÇÃO AUTOMÁTICA"
Write-ColorOutput "  Análise de Exclusão Digital no Brasil" White
Write-ColorOutput "`n  Autor: Alejandro Alexandre (RA: 197890)" White
Write-ColorOutput "  Versão: 1.0.0" White
Write-ColorOutput "  Data: 04/11/2025`n" White

# ============================================================================
# ETAPA 1: VERIFICAÇÃO DE PRÉ-REQUISITOS
# ============================================================================

Write-Header "ETAPA 1/5: Verificando Pré-requisitos"

$hasErrors = $false

# Verifica Python
Write-Step "[1/4] Verificando Python..."
try {
    $pythonVersion = (python --version 2>&1) -replace "Python ", ""
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Python encontrado: $pythonVersion"
    } else {
        throw
    }
} catch {
    Write-Error-Custom "Python não encontrado!"
    Write-Output "`nPor favor, instale Python 3.13 ou superior:"
    Write-Output "https://www.python.org/downloads/`n"
    $hasErrors = $true
}

# Verifica pip
Write-Step "[2/4] Verificando pip..."
try {
    python -m pip --version | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "pip encontrado"
    } else {
        throw
    }
} catch {
    Write-Error-Custom "pip não encontrado!"
    $hasErrors = $true
}

# Verifica Node.js
Write-Step "[3/4] Verificando Node.js..."
try {
    $nodeVersion = (node --version 2>&1)
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Node.js encontrado: $nodeVersion"
    } else {
        throw
    }
} catch {
    Write-Error-Custom "Node.js não encontrado!"
    Write-Output "`nPor favor, instale Node.js 18 ou superior:"
    Write-Output "https://nodejs.org/`n"
    $hasErrors = $true
}

# Verifica npm
Write-Step "[4/4] Verificando npm..."
try {
    $npmVersion = (npm --version 2>&1)
    if ($LASTEXITCODE -eq 0) {
        Write-Success "npm encontrado: $npmVersion"
    } else {
        throw
    }
} catch {
    Write-Error-Custom "npm não encontrado!"
    $hasErrors = $true
}

if ($hasErrors) {
    Write-Output "`nPressione qualquer tecla para sair..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Output ""
Write-Success "Todos os pré-requisitos foram atendidos!"
Start-Sleep -Seconds 2

# ============================================================================
# ETAPA 2: CRIAÇÃO DO AMBIENTE VIRTUAL PYTHON
# ============================================================================

Write-Header "ETAPA 2/5: Criando Ambiente Virtual Python"

if (Test-Path ".venv") {
    Write-Info "Ambiente virtual já existe"
    $recreate = Read-Host "Deseja recriar? (S/N)"
    if ($recreate -eq "S" -or $recreate -eq "s") {
        Write-Info "Removendo ambiente virtual antigo..."
        Remove-Item -Recurse -Force .venv
        Write-Info "Criando novo ambiente virtual..."
        python -m venv .venv
    } else {
        Write-Info "Usando ambiente virtual existente"
    }
} else {
    Write-Info "Criando ambiente virtual Python..."
    python -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Ambiente virtual criado com sucesso!"
    } else {
        Write-Error-Custom "Falha ao criar ambiente virtual"
        exit 1
    }
}

Start-Sleep -Seconds 1

# ============================================================================
# ETAPA 3: INSTALAÇÃO DE DEPENDÊNCIAS PYTHON
# ============================================================================

Write-Header "ETAPA 3/5: Instalando Dependências Python"

Write-Info "Atualizando pip..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Success "pip atualizado"
}

Write-Output ""
Write-Info "Instalando dependências da Versão Python Desktop..."
Write-Output "       Isso pode levar alguns minutos..."

& .\.venv\Scripts\python.exe -m pip install -r "Versão PY\requirements.txt" --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Success "Dependências da versão Desktop instaladas"
} else {
    Write-Error-Custom "Falha ao instalar dependências Desktop"
    exit 1
}

Write-Output ""
Write-Info "Instalando dependências do Backend Web (FastAPI)..."

& .\.venv\Scripts\python.exe -m pip install -r "Versão PY\web\backend\requirements.txt" --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Success "Dependências do Backend instaladas"
} else {
    Write-Error-Custom "Falha ao instalar dependências do Backend"
    exit 1
}

Start-Sleep -Seconds 1

# ============================================================================
# ETAPA 4: INSTALAÇÃO DE DEPENDÊNCIAS NODE.JS
# ============================================================================

Write-Header "ETAPA 4/5: Instalando Dependências Node.js"

Push-Location "Versão Web"

if (Test-Path "node_modules") {
    Write-Info "node_modules já existe"
    $reinstall = Read-Host "Deseja reinstalar? (S/N)"
    if ($reinstall -eq "S" -or $reinstall -eq "s") {
        Write-Info "Removendo node_modules antigo..."
        Remove-Item -Recurse -Force node_modules
        Write-Info "Instalando dependências..."
        npm install --legacy-peer-deps --loglevel=error
    } else {
        Write-Info "Usando node_modules existente"
    }
} else {
    Write-Info "Instalando dependências do Frontend (Next.js)..."
    Write-Output "       Isso pode levar vários minutos...`n"
    
    npm install --legacy-peer-deps --loglevel=error
    
    if ($LASTEXITCODE -eq 0) {
        Write-Output ""
        Write-Success "Dependências do Frontend instaladas"
    } else {
        Write-Output ""
        Write-Error-Custom "Falha ao instalar dependências do Frontend"
        Pop-Location
        exit 1
    }
}

Pop-Location
Start-Sleep -Seconds 1

# ============================================================================
# ETAPA 5: CONFIGURAÇÃO DE ESTRUTURA DE ARQUIVOS
# ============================================================================

Write-Header "ETAPA 5/5: Configurando Estrutura de Arquivos"

Write-Info "Criando diretórios necessários..."

$directories = @(
    "Banco de dados",
    "Versão PY\data",
    "Versão PY\logs",
    "documentacao"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

Write-Success "Diretórios criados/verificados"

# Cria arquivo .env.local
if (-not (Test-Path "Versão Web\.env.local")) {
    Write-Info "Criando arquivo de configuração .env.local..."
    
    $envContent = @"
# Configuração do Sistema DAC - Versão Web
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Sistema DAC
NEXT_PUBLIC_APP_VERSION=1.0.0
"@
    
    $envContent | Out-File -FilePath "Versão Web\.env.local" -Encoding utf8
    Write-Success "Arquivo .env.local criado"
} else {
    Write-Info "Arquivo .env.local já existe"
}

Write-Output ""
Write-Info "Criando scripts de atalho..."

# Script para iniciar versão web (PowerShell)
$webScript = @'
# Inicia Sistema DAC - Versão Web
$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Iniciando Sistema DAC - Versão Web" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "[1/2] Iniciando Backend FastAPI..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\Versão PY\web\backend'; ..\..\..\\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Minimized

Start-Sleep -Seconds 3

Write-Host "[2/2] Iniciando Frontend Next.js..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir\Versão Web'; npm run start-frontend" -WindowStyle Minimized

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Servidores Iniciados!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API:      http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend Web:     http://localhost:3002" -ForegroundColor Yellow
Write-Host "Documentação API: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Pressione qualquer tecla para abrir o navegador..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Start-Process "http://localhost:3002"
'@

$webScript | Out-File -FilePath "Iniciar-Web.ps1" -Encoding utf8

# Script para iniciar versão desktop (PowerShell)
$desktopScript = @'
# Inicia Sistema DAC - Versão Desktop
Write-Host "Iniciando Sistema DAC - Versão Desktop..." -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$scriptDir\Versão PY"

& ..\\.venv\Scripts\python.exe main.py
'@

$desktopScript | Out-File -FilePath "Iniciar-Desktop.ps1" -Encoding utf8

# Script para parar servidores
$stopScript = @'
# Para servidores do Sistema DAC
Write-Host "Parando servidores do Sistema DAC..." -ForegroundColor Yellow
Write-Host ""

Write-Host "[INFO] Encerrando processos Python na porta 8000..." -ForegroundColor Cyan
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($port8000) {
    foreach ($conn in $port8000) {
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "[INFO] Encerrando processos Node.js na porta 3002..." -ForegroundColor Cyan
$port3002 = Get-NetTCPConnection -LocalPort 3002 -ErrorAction SilentlyContinue
if ($port3002) {
    foreach ($conn in $port3002) {
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "[OK] Servidores encerrados" -ForegroundColor Green
Write-Host ""
pause
'@

$stopScript | Out-File -FilePath "Parar-Servidores.ps1" -Encoding utf8

Write-Success "Scripts de atalho criados:"
Write-Output "         - Iniciar-Web.ps1"
Write-Output "         - Iniciar-Desktop.ps1"
Write-Output "         - Parar-Servidores.ps1"

# ============================================================================
# FINALIZAÇÃO
# ============================================================================

Write-Output ""
Write-Header "CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!"

Write-Output "[RESUMO]"
Write-Output ""
Write-Output "  Python Version:   $pythonVersion"
Write-Output "  Node.js Version:  $nodeVersion"
Write-Output "  NPM Version:      $npmVersion"
Write-Output ""
Write-Output "  Ambiente Virtual: .venv\"
Write-Output "  Dependências Python: Instaladas"
Write-Output "  Dependências Node.js: Instaladas"
Write-Output ""

Write-Header "PRÓXIMOS PASSOS"

Write-Output "  Para iniciar o Sistema DAC, execute um dos scripts:"
Write-Output ""
Write-Output "  1. VERSÃO WEB (Recomendado):"
Write-Output "     - Execute: .\Iniciar-Web.ps1"
Write-Output "     - Acesse: http://localhost:3002"
Write-Output ""
Write-Output "  2. VERSÃO DESKTOP:"
Write-Output "     - Execute: .\Iniciar-Desktop.ps1"
Write-Output ""
Write-Output "  3. Para parar os servidores:"
Write-Output "     - Execute: .\Parar-Servidores.ps1"
Write-Output ""

Write-Header "DOCUMENTAÇÃO"

Write-Output "  Consulte os seguintes arquivos para mais informações:"
Write-Output ""
Write-Output "  - MANUAL_EXECUCAO.md     (Guia completo de uso)"
Write-Output "  - README.md              (Visão geral do projeto)"
Write-Output "  - CONTRIBUTING.md        (Guia de contribuição)"
Write-Output ""

Write-ColorOutput "========================================================================`n" Cyan

# Pergunta se quer iniciar agora
$startNow = Read-Host "Deseja iniciar o Sistema DAC agora? (S/N)"

if ($startNow -eq "S" -or $startNow -eq "s") {
    Write-Output ""
    Write-Output "Qual versão deseja iniciar?"
    Write-Output ""
    Write-Output "  1. Versão Web (Frontend + Backend)"
    Write-Output "  2. Versão Desktop"
    Write-Output ""
    
    $choice = Read-Host "> "
    
    if ($choice -eq "1") {
        Write-Output ""
        Write-Info "Iniciando Versão Web..."
        & .\Iniciar-Web.ps1
    } elseif ($choice -eq "2") {
        Write-Output ""
        Write-Info "Iniciando Versão Desktop..."
        & .\Iniciar-Desktop.ps1
    }
} else {
    Write-Output ""
    Write-Info "Execute os scripts quando quiser usar o sistema"
}

Write-Output ""
Write-Output "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
