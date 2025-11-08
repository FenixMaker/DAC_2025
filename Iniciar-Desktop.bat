@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul

:: ============================================================================
:: Iniciar Versao Desktop - Sistema DAC (robusto)
:: - Usa Python do venv se existir
:: - Mantem a janela aberta e exibe mensagens de erro
:: ============================================================================

title Sistema DAC - Iniciar Desktop

:: Garante raiz do projeto
cd /d "%~dp0"

echo =============================================================
echo   Sistema DAC - Iniciando Versao Desktop
echo =============================================================
echo.

set LAUNCHER=scripts\inicializacao\launcher_desktop.py
if not exist "%LAUNCHER%" (
    echo ❌ Arquivo de launcher nao encontrado: %LAUNCHER%
    echo    Verifique se o projeto foi clonado completo.
    echo.
    pause
    exit /b 1
)

:: Descobre melhor Python para executar o launcher
set "PYTHON_EXE="
if exist "Versão PY\.venv\Scripts\python.exe" set "PYTHON_EXE=Versão PY\.venv\Scripts\python.exe"
if not defined PYTHON_EXE (
    where py >nul 2>&1 && set "PYTHON_EXE=py -3"
)
if not defined PYTHON_EXE (
    where python >nul 2>&1 && set "PYTHON_EXE=python"
)
if not defined PYTHON_EXE (
    echo ❌ Python nao encontrado no sistema.
    echo    Instale Python 3 e execute setup.bat.
    echo.
    pause
    exit /b 1
)

echo 🐍 Usando Python: %PYTHON_EXE%
echo.

:: Executa o launcher
if "%PYTHON_EXE%"=="py -3" (
    py -3 "%LAUNCHER%"
) else (
    "%PYTHON_EXE%" "%LAUNCHER%"
)
set RC=%ERRORLEVEL%

echo.
if %RC% NEQ 0 (
    echo ❌ Falha ao iniciar a Versao Desktop. Codigo: %RC%
    echo    Dica: rode primeiro setup.bat ou Iniciar-Tudo.bat.
) else (
    echo ✅ Launcher Desktop concluido.
)
echo.
pause
endlocal
exit /b %RC%
