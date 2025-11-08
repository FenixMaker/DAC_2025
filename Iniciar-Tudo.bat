@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
:: ============================================================================
:: Iniciar Tudo - Sistema DAC
:: Lança um verificador simples: se faltar algo, roda setup.bat automaticamente
:: e depois pergunta se você quer iniciar a Versão Web ou Desktop.
:: ============================================================================

title Sistema DAC - Iniciar Tudo

echo ==============================================================================
echo   Sistema DAC - Iniciar Tudo
echo ==============================================================================
echo.

:: Garante que estamos na raiz do projeto
cd /d "%~dp0"

:: Verificação de pré-requisitos
echo 🔍 Verificando pré-requisitos...

setlocal EnableDelayedExpansion
set VENV_OK=
set NODE_OK=0

:: Checa venv em duas possíveis localizações
if exist ".venv\Scripts\python.exe" set VENV_OK=1
if exist "Versão PY\.venv\Scripts\python.exe" set VENV_OK=1

:: Checa dependências do Node.js (pasta node_modules)
if exist "Versão Web\node_modules" set NODE_OK=1

if not defined VENV_OK (
    echo   • Ambiente virtual Python nao encontrado.
)
if %NODE_OK%==0 (
    echo   • Dependencias do Node.js nao instaladas.
)

:: Se algo faltar, executa setup.bat automaticamente
if not defined VENV_OK (
    echo.
    echo ▶ Executando setup.bat para criar o ambiente Python...
    if exist setup.bat (
        call setup.bat
    ) else (
        echo ❌ Arquivo setup.bat nao encontrado na raiz do projeto.
        echo    Verifique o repositorio e tente novamente.
        pause
        exit /b 1
    )
)

if %NODE_OK%==0 (
    echo.
    echo ▶ Executando setup.bat para instalar dependencias do Node.js...
    if exist setup.bat (
        call setup.bat
    ) else (
        echo ❌ Arquivo setup.bat nao encontrado na raiz do projeto.
        echo    Verifique o repositorio e tente novamente.
        pause
        exit /b 1
    )
)

:: Revalida após setup
set VENV_OK=
set NODE_OK=0
if exist ".venv\Scripts\python.exe" set VENV_OK=1
if exist "Versão PY\.venv\Scripts\python.exe" set VENV_OK=1
if exist "Versão Web\node_modules" set NODE_OK=1

if not defined VENV_OK (
    echo.
    echo ❌ Ambiente virtual Python ainda nao foi criado.
    echo    Abra setup.bat manualmente e verifique possiveis erros.
    pause
    exit /b 1
)

if %NODE_OK%==0 (
    echo.
    echo ❌ Dependencias do Node.js ainda nao foram instaladas.
    echo    Abra setup.bat manualmente e verifique possiveis erros.
    pause
    exit /b 1
)

echo.
echo ✅ Tudo pronto! Ambiente configurado com sucesso.
echo.

:: Escolha de modo
echo O que voce deseja iniciar?
echo   [W] Versao Web (Frontend + Backend)
echo   [D] Versao Desktop
choice /C WD /N /M "Selecione W ou D: "
if errorlevel 2 goto start_desktop
if errorlevel 1 goto start_web

:start_web
call Iniciar-Web.bat
goto end

:start_desktop
call Iniciar-Desktop.bat
goto end

:end
echo.
echo ✅ Processo concluido. Esta janela permanecera aberta.
echo.
pause
endlocal
exit /b 0
