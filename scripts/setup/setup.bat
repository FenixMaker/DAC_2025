@echo off
setlocal enabledelayedexpansion

REM ==============================================
REM  Sistema DAC - Setup
REM  Prepara ambiente Python (venv) e Node.js
REM ==============================================

REM Determina a raiz do projeto a partir desta pasta
for %%I in ("%~dp0..\..") do set ROOT=%%~fI
set PY_DIR=%ROOT%\Versão PY
set WEB_DIR=%ROOT%\Versão Web

echo ==============================================
echo   Sistema DAC - Setup de Dependencias
echo ==============================================
echo.
echo Raiz do projeto: %ROOT%
echo PY DIR: %PY_DIR%
echo WEB DIR: %WEB_DIR%
echo.

REM ----------------------------------------------
REM 1) Preparar venv Python em "Versão PY\\.venv"
REM ----------------------------------------------
if not exist "%PY_DIR%" (
  echo [ERRO] Pasta "Versão PY" nao encontrada em: %PY_DIR%
  echo.
  goto :END
)

echo [Python] Verificando venv em "%PY_DIR%\.venv"...
if not exist "%PY_DIR%\.venv\Scripts\python.exe" (
  echo [Python] Venv nao encontrada. Criando...
  python -m venv "%PY_DIR%\.venv"
  if errorlevel 1 (
    echo [ERRO] Falha ao criar venv. Certifique-se que o Python esta instalado e no PATH.
    echo.
    goto :END
  )
) else (
  echo [Python] Venv existente encontrada.
)

set VENV_PY="%PY_DIR%\.venv\Scripts\python.exe"

echo [Python] Atualizando pip...
%VENV_PY% -m pip install --upgrade pip
if exist "%PY_DIR%\requirements.txt" (
  echo [Python] Instalando dependencias de requirements.txt...
  %VENV_PY% -m pip install -r "%PY_DIR%\requirements.txt"
) else (
  echo [Python] Arquivo requirements.txt nao encontrado em "%PY_DIR%". Pulando instalacao.
)
if exist "%PY_DIR%\web\backend\requirements.txt" (
  echo [Python] Instalando dependencias do Backend (FastAPI)...
  %VENV_PY% -m pip install -r "%PY_DIR%\web\backend\requirements.txt"
)
echo.

REM ----------------------------------------------
REM 2) Preparar dependencias Node.js em "Versão Web"
REM ----------------------------------------------
if exist "%WEB_DIR%\package.json" (
  echo [Node] package.json encontrado.
  if not exist "%WEB_DIR%\node_modules" (
    echo [Node] node_modules ausente. Instalando com npm install...
    pushd "%WEB_DIR%"
    npm install
    if errorlevel 1 (
      echo [AVISO] Falha ao instalar dependencias Node. Verifique se o Node.js esta instalado.
    )
    popd
  ) else (
    echo [Node] node_modules ja existente. Pulando instalacao.
  )
) else (
  echo [Node] package.json nao encontrado em "%WEB_DIR%". Pulando etapa do frontend.
)
echo.

echo ==============================================
echo   Setup concluido.
echo   Venv pronta em: %PY_DIR%\.venv
echo ==============================================
echo.
goto :EOF

:END
echo Setup finalizado com erros. Corrija as mensagens acima e execute novamente.
exit /b 1
