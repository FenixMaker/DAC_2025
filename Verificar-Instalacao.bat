@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
REM ============================================================================
REM Sistema DAC - Script de Verificacao da Instalacao
REM Verifica se todos os componentes foram instalados corretamente
REM ============================================================================

setlocal enabledelayedexpansion

color 0B

echo ========================================================================
echo   SISTEMA DAC - VERIFICACAO DA INSTALACAO
echo ========================================================================
echo.

set ERRORS=0
set WARNINGS=0

REM ============================================================================
REM Verificar Python
REM ============================================================================

echo [1/7] Verificando Python...
python --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo   [OK] Python encontrado: !PYTHON_VERSION!
) else (
    echo   [ERRO] Python nao encontrado!
    set /a ERRORS+=1
)

REM ============================================================================
REM Verificar Ambiente Virtual
REM ============================================================================

echo [2/7] Verificando Ambiente Virtual...
if exist "Versão PY\.venv\Scripts\python.exe" (
    echo   [OK] Ambiente virtual encontrado em: Versao PY\.venv
    
    REM Verificar se o ambiente virtual funciona
    "Versão PY\.venv\Scripts\python.exe" --version >nul 2>&1
    if %errorLevel% == 0 (
        echo   [OK] Ambiente virtual funcionando corretamente
    ) else (
        echo   [ERRO] Ambiente virtual nao funciona corretamente
        set /a ERRORS+=1
    )
) else (
    echo   [ERRO] Ambiente virtual NAO encontrado!
    echo          Esperado em: Versao PY\.venv
    set /a ERRORS+=1
)

REM ============================================================================
REM Verificar Dependencias Python Desktop
REM ============================================================================

echo [3/7] Verificando dependencias Python Desktop...
if exist "Versão PY\requirements.txt" (
    "Versão PY\.venv\Scripts\python.exe" -c "import tkinter; import sqlalchemy; import matplotlib" >nul 2>&1
    if %errorLevel% == 0 (
        echo   [OK] Principais dependencias Desktop instaladas
    ) else (
        echo   [ERRO] Algumas dependencias Desktop estao faltando
        set /a ERRORS+=1
    )
) else (
    echo   [AVISO] Arquivo requirements.txt nao encontrado
    set /a WARNINGS+=1
)

REM ============================================================================
REM Verificar Dependencias Backend
REM ============================================================================

echo [4/7] Verificando dependencias Backend...
if exist "Versão PY\web\backend\requirements.txt" (
    "Versão PY\.venv\Scripts\python.exe" -c "import fastapi; import uvicorn" >nul 2>&1
    if %errorLevel% == 0 (
        echo   [OK] Principais dependencias Backend instaladas
    ) else (
        echo   [ERRO] Algumas dependencias Backend estao faltando
        set /a ERRORS+=1
    )
) else (
    echo   [AVISO] Arquivo requirements.txt do backend nao encontrado
    set /a WARNINGS+=1
)

REM ============================================================================
REM Verificar Node.js
REM ============================================================================

echo [5/7] Verificando Node.js...
node --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo   [OK] Node.js encontrado: !NODE_VERSION!
) else (
    echo   [ERRO] Node.js nao encontrado!
    set /a ERRORS+=1
)

REM ============================================================================
REM Verificar Dependencias Frontend
REM ============================================================================

echo [6/7] Verificando dependencias Frontend...
if exist "Versão Web\node_modules" (
    echo   [OK] node_modules encontrado
) else (
    echo   [ERRO] node_modules NAO encontrado!
    echo          Execute: npm install na pasta Versao Web
    set /a ERRORS+=1
)

REM ============================================================================
REM Verificar Scripts de Atalho
REM ============================================================================

echo [7/7] Verificando scripts de atalho...
set SCRIPTS_OK=0

if exist "Iniciar-Desktop.bat" (
    set /a SCRIPTS_OK+=1
) else (
    echo   [AVISO] Iniciar-Desktop.bat nao encontrado
    set /a WARNINGS+=1
)

if exist "Iniciar-Web.bat" (
    set /a SCRIPTS_OK+=1
) else (
    echo   [AVISO] Iniciar-Web.bat nao encontrado
    set /a WARNINGS+=1
)

if exist "Parar-Servidores.bat" (
    set /a SCRIPTS_OK+=1
) else (
    echo   [AVISO] Parar-Servidores.bat nao encontrado
    set /a WARNINGS+=1
)

if !SCRIPTS_OK! == 3 (
    echo   [OK] Todos os scripts de atalho encontrados
) else (
    echo   [AVISO] Alguns scripts de atalho estao faltando (!SCRIPTS_OK!/3)
)

REM ============================================================================
REM Resumo
REM ============================================================================

echo.
echo ========================================================================
echo   RESULTADO DA VERIFICACAO
echo ========================================================================
echo.

if !ERRORS! == 0 (
    if !WARNINGS! == 0 (
        echo   STATUS: [OK] TUDO PRONTO PARA USO!
        echo.
        echo   Voce pode iniciar o sistema usando:
        echo   - Iniciar-Desktop.bat (Versao Desktop)
        echo   - Iniciar-Web.bat (Versao Web)
    ) else (
        echo   STATUS: [AVISO] Instalacao OK com !WARNINGS! avisos
        echo.
        echo   O sistema deve funcionar, mas alguns componentes opcionais
        echo   podem estar faltando.
    )
) else (
    echo   STATUS: [ERRO] INSTALACAO INCOMPLETA
    echo.
    echo   Encontrados !ERRORS! erros e !WARNINGS! avisos
    echo.
    echo   SOLUCAO: Execute novamente o setup.bat
    echo.
)

echo ========================================================================
echo.

echo.
if !ERRORS! GTR 0 (
    echo ❌ Existem erros na instalacao.
    echo    Execute setup.bat e tente novamente.
    echo.
    pause
    endlocal & exit /b 1
) else (
    echo ✅ Instalacao verificada com sucesso.
    echo.
    pause
    endlocal & exit /b 0
)
