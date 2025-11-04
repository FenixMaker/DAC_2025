@echo off
:: ============================================================================
:: Iniciar Versao Web - Sistema DAC
:: Atalho simplificado para iniciar a versao web
:: ============================================================================

title Sistema DAC - Iniciar Web

echo ============================================================================
echo   Sistema DAC - Iniciando Versao Web
echo ============================================================================
echo.

:: Navega para a pasta de scripts
cd /d "%~dp0"
cd scripts\inicializacao

:: Executa o launcher Python
python launcher_web.py

pause
