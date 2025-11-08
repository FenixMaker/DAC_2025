@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
REM ============================================================================
REM Sistema DAC - Script de Configuracao Automatica
REM Autor: Alejandro Alexandre (RA: 197890)
REM Curso: Analise e Desenvolvimento de Sistemas
REM Ano: 2025
REM ============================================================================

setlocal enabledelayedexpansion

REM Define cores (se suportado)
color 0A

echo ========================================================================
echo   SISTEMA DAC - CONFIGURACAO AUTOMATICA
echo   Analise de Exclusao Digital no Brasil
echo ========================================================================
echo.
echo   Autor: Alejandro Alexandre (RA: 197890)
echo   Versao: 1.0.0
echo   Data: 04/11/2025
echo.
echo ========================================================================
echo.

REM Verifica se esta sendo executado como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Executando com privilegios de administrador
) else (
    echo [AVISO] Nao esta executando como administrador
    echo         Algumas operacoes podem falhar
)
echo.

REM ============================================================================
REM ETAPA 1: VERIFICACAO DE PRE-REQUISITOS
REM ============================================================================

echo ========================================================================
echo   ETAPA 1/5: Verificando Pre-requisitos
echo ========================================================================
echo.

REM Verifica Python
echo [1/4] Verificando Python...
python --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [OK] Python encontrado: !PYTHON_VERSION!
) else (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Por favor, instale Python 3.13 ou superior:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Verifica pip
echo [2/4] Verificando pip...
python -m pip --version >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] pip encontrado
) else (
    echo [ERRO] pip nao encontrado!
    pause
    exit /b 1
)

REM Verifica Node.js
echo [3/4] Verificando Node.js...
node --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=1" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo [OK] Node.js encontrado: !NODE_VERSION!
) else (
    echo [ERRO] Node.js nao encontrado!
    echo.
    echo Por favor, instale Node.js 18 ou superior:
    echo https://nodejs.org/
    echo.
    pause
    exit /b 1
)

REM Verifica npm
echo [4/4] Verificando npm...
npm --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=1" %%i in ('npm --version 2^>^&1') do set NPM_VERSION=%%i
    echo [OK] npm encontrado: !NPM_VERSION!
) else (
    echo [ERRO] npm nao encontrado!
    pause
    exit /b 1
)

echo.
echo [SUCESSO] Todos os pre-requisitos foram atendidos!
echo.
timeout /t 2 >nul

REM ============================================================================
REM ETAPA 2: CRIACAO DO AMBIENTE VIRTUAL PYTHON
REM ============================================================================

echo ========================================================================
echo   ETAPA 2/5: Criando Ambiente Virtual Python
echo ========================================================================
echo.

REM Remover ambiente virtual antigo na raiz se existir (de versoes anteriores)
if exist ".venv" (
    echo [INFO] Removendo ambiente virtual antigo da raiz...
    rmdir /s /q .venv
    echo [OK] Ambiente virtual antigo removido
    echo.
)

REM Criar ambiente virtual na pasta Versao PY (onde a aplicacao espera)
cd "Versão PY"

if exist ".venv" (
    echo [AVISO] Ambiente virtual ja existe em Versao PY
    echo         Deseja recriar? (S/N)
    set /p RECREATE="> "
    if /i "!RECREATE!"=="S" (
        echo [INFO] Removendo ambiente virtual antigo...
        rmdir /s /q .venv
        echo [INFO] Criando novo ambiente virtual...
        python -m venv .venv
        if %errorLevel% == 0 (
            echo [OK] Ambiente virtual criado com sucesso!
        ) else (
            echo [ERRO] Falha ao criar ambiente virtual
            cd ..
            pause
            exit /b 1
        )
    ) else (
        echo [INFO] Usando ambiente virtual existente
    )
) else (
    echo [INFO] Criando ambiente virtual Python em Versao PY...
    python -m venv .venv
    if %errorLevel% == 0 (
        echo [OK] Ambiente virtual criado com sucesso!
    ) else (
        echo [ERRO] Falha ao criar ambiente virtual
        cd ..
        pause
        exit /b 1
    )
)

cd ..

echo.
timeout /t 1 >nul

REM ============================================================================
REM ETAPA 3: INSTALACAO DE DEPENDENCIAS PYTHON
REM ============================================================================

echo ========================================================================
echo   ETAPA 3/5: Instalando Dependencias Python
echo ========================================================================
echo.

echo [INFO] Atualizando pip no ambiente virtual...
"Versão PY\.venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
if %errorLevel% == 0 (
    echo [OK] pip atualizado
) else (
    echo [AVISO] Nao foi possivel atualizar o pip
)

echo.
echo [INFO] Instalando dependencias da Versao Python Desktop...
echo        Isso pode levar alguns minutos...
"Versão PY\.venv\Scripts\python.exe" -m pip install -r "Versão PY\requirements.txt" --quiet
if %errorLevel% == 0 (
    echo [OK] Dependencias da versao Desktop instaladas
) else (
    echo [ERRO] Falha ao instalar dependencias Desktop
    pause
    exit /b 1
)

echo.
echo [INFO] Instalando dependencias do Backend Web (FastAPI)...
"Versão PY\.venv\Scripts\python.exe" -m pip install -r "Versão PY\web\backend\requirements.txt" --quiet
if %errorLevel% == 0 (
    echo [OK] Dependencias do Backend instaladas
) else (
    echo [ERRO] Falha ao instalar dependencias do Backend
    pause
    exit /b 1
)

echo.
timeout /t 1 >nul

REM ============================================================================
REM ETAPA 4: INSTALACAO DE DEPENDENCIAS NODE.JS
REM ============================================================================

echo ========================================================================
echo   ETAPA 4/5: Instalando Dependencias Node.js
echo ========================================================================
echo.

cd "Versão Web"

if exist "node_modules" (
    echo [AVISO] node_modules ja existe
    echo         Deseja reinstalar? (S/N)
    set /p REINSTALL="> "
    if /i "!REINSTALL!"=="S" (
        echo [INFO] Removendo node_modules antigo...
        rmdir /s /q node_modules
        echo [INFO] Instalando dependencias...
        call npm install --legacy-peer-deps --loglevel=error
    ) else (
        echo [INFO] Usando node_modules existente
    )
) else (
    echo [INFO] Instalando dependencias do Frontend (Next.js)...
    echo        Isso pode levar varios minutos...
    echo.
    call npm install --legacy-peer-deps --loglevel=error
    if %errorLevel% == 0 (
        echo.
        echo [OK] Dependencias do Frontend instaladas
    ) else (
        echo.
        echo [ERRO] Falha ao instalar dependencias do Frontend
        cd ..
        pause
        exit /b 1
    )
)

cd ..
echo.
timeout /t 1 >nul

REM ============================================================================
REM ETAPA 5: CRIACAO DE DIRETORIOS E ARQUIVOS
REM ============================================================================

echo ========================================================================
echo   ETAPA 5/5: Configurando Estrutura de Arquivos
echo ========================================================================
echo.

REM Cria diretorios necessarios
echo [INFO] Criando diretorios necessarios...

if not exist "Banco de dados" mkdir "Banco de dados"
if not exist "Versão PY\data" mkdir "Versão PY\data"
if not exist "Versão PY\logs" mkdir "Versão PY\logs"
if not exist "documentacao" mkdir "documentacao"

echo [OK] Diretorios criados/verificados

REM Cria arquivo .env.local para o frontend (se nao existir)
if not exist "Versão Web\.env.local" (
    echo [INFO] Criando arquivo de configuracao .env.local...
    (
        echo # Configuracao do Sistema DAC - Versao Web
        echo NEXT_PUBLIC_API_URL=http://localhost:8000
        echo NEXT_PUBLIC_APP_NAME=Sistema DAC
        echo NEXT_PUBLIC_APP_VERSION=1.0.0
    ) > "Versão Web\.env.local"
    echo [OK] Arquivo .env.local criado
) else (
    echo [INFO] Arquivo .env.local ja existe
)

echo.

REM ============================================================================
REM CRIACAO DE SCRIPTS DE ATALHO
REM ============================================================================

echo [INFO] Criando scripts de atalho...

REM Script para iniciar versao web
(
    echo @echo off
    echo echo Iniciando Sistema DAC - Versao Web...
    echo echo.
    echo start "DAC Backend" /min cmd /c "cd /d "%%~dp0Versão PY\web\backend" ^&^& ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    echo timeout /t 3 >nul
    echo start "DAC Frontend" /min cmd /c "cd /d "%%~dp0Versão Web" ^&^& npm run start-frontend"
    echo echo.
    echo echo ========================================
    echo echo   Servidores Iniciados!
    echo echo ========================================
    echo echo.
    echo echo Backend API:      http://localhost:8000
    echo echo Frontend Web:     http://localhost:3002
    echo echo Documentacao API: http://localhost:8000/docs
    echo echo.
    echo echo Pressione qualquer tecla para abrir o navegador...
    echo pause ^>nul
    echo start http://localhost:3002
) > "Iniciar-Web.bat"

REM Script para iniciar versao desktop
(
    echo @echo off
    echo echo Iniciando Sistema DAC - Versao Desktop...
    echo cd /d "%%~dp0Versão PY"
    echo .venv\Scripts\python.exe main.py
    echo pause
) > "Iniciar-Desktop.bat"

REM Script para parar servidores
(
    echo @echo off
    echo echo Parando servidores do Sistema DAC...
    echo.
    echo [INFO] Encerrando processos Python na porta 8000...
    echo for /f "tokens=5" %%%%a in ('netstat -ano ^| findstr :8000') do taskkill /F /PID %%%%a 2^>nul
    echo.
    echo [INFO] Encerrando processos Node.js na porta 3002...
    echo for /f "tokens=5" %%%%a in ('netstat -ano ^| findstr :3002') do taskkill /F /PID %%%%a 2^>nul
    echo.
    echo [OK] Servidores encerrados
    echo pause
) > "Parar-Servidores.bat"

echo [OK] Scripts de atalho criados:
echo      - Iniciar-Web.bat
echo      - Iniciar-Desktop.bat
echo      - Parar-Servidores.bat

echo.

REM ============================================================================
REM FINALIZACAO
REM ============================================================================

echo.
echo ========================================================================
echo   CONFIGURACAO CONCLUIDA COM SUCESSO!
echo ========================================================================
echo.
echo [RESUMO]
echo.
echo   Python Version:   !PYTHON_VERSION!
echo   Node.js Version:  !NODE_VERSION!
echo   NPM Version:      !NPM_VERSION!
echo.
echo   Ambiente Virtual: Versao PY\.venv\
echo   Dependencias Python: Instaladas
echo   Dependencias Node.js: Instaladas
echo.
echo ========================================================================
echo   PROXIMOS PASSOS
echo ========================================================================
echo.
echo   Para iniciar o Sistema DAC, execute um dos scripts:
echo.
echo   1. VERSAO WEB (Recomendado):
echo      - Clique duas vezes em: Iniciar-Web.bat
echo      - Acesse: http://localhost:3002
echo.
echo   2. VERSAO DESKTOP:
echo      - Clique duas vezes em: Iniciar-Desktop.bat
echo.
echo   3. Para parar os servidores:
echo      - Execute: Parar-Servidores.bat
echo.
echo ========================================================================
echo   DOCUMENTACAO
echo ========================================================================
echo.
echo   Consulte os seguintes arquivos para mais informacoes:
echo.
echo   - MANUAL_EXECUCAO.md     (Guia completo de uso)
echo   - README.md              (Visao geral do projeto)
echo   - CONTRIBUTING.md        (Guia de contribuicao)
echo.
echo ========================================================================
echo.
echo   Configuracao concluida em: %date% %time%
echo.
echo ========================================================================
echo.

REM Pergunta se quer iniciar agora
echo Deseja iniciar o Sistema DAC agora? (S/N)
set /p START_NOW="> "

if /i "!START_NOW!"=="S" (
    echo.
    echo Qual versao deseja iniciar?
    echo.
    echo   1. Versao Web (Frontend + Backend)
    echo   2. Versao Desktop
    echo.
    set /p VERSION_CHOICE="> "
    
    if "!VERSION_CHOICE!"=="1" (
        echo.
        echo [INFO] Iniciando Versao Web...
        call Iniciar-Web.bat
    ) else if "!VERSION_CHOICE!"=="2" (
        echo.
        echo [INFO] Iniciando Versao Desktop...
        call Iniciar-Desktop.bat
    )
) else (
    echo.
    echo [INFO] Execute os scripts de atalho quando quiser usar o sistema
)

echo.
echo Pressione qualquer tecla para sair...
pause >nul
endlocal
