@echo off
:: ============================================================================
:: Iniciar Versao Desktop - Sistema DAC
:: Atalho simplificado para iniciar a versao desktop
:: ============================================================================

title Sistema DAC - Iniciar Desktop

echo ============================================================================
echo   Sistema DAC - Iniciando Versao Desktop
echo ============================================================================
echo.

:: Navega para a pasta de scripts
cd /d "%~dp0"
cd scripts\inicializacao

:: Executa o launcher Python
where py >nul 2>&1
if %errorlevel%==0 (
	py -3 launcher_desktop.py
) else (
	python launcher_desktop.py
)

pause
