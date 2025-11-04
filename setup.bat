@echo off
REM ============================================================================
REM Sistema DAC - Atalho para Setup
REM Este arquivo e um atalho conveniente na raiz do projeto
REM O script real esta em: scripts\setup\setup.bat
REM ============================================================================

echo Iniciando configuracao do Sistema DAC...
echo.

call "%~dp0scripts\setup\setup.bat" %*
