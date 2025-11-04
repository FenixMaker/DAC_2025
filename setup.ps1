# ============================================================================
# Sistema DAC - Atalho para Setup
# Este arquivo é um atalho conveniente na raiz do projeto
# O script real está em: scripts\setup\setup.ps1
# ============================================================================

Write-Host "Iniciando configuração do Sistema DAC..." -ForegroundColor Cyan
Write-Host ""

$scriptPath = Join-Path $PSScriptRoot "scripts\setup\setup.ps1"
& $scriptPath @args
