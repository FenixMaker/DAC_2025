@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

REM ============================================================
REM Testar regras do .gitignore para arquivos de banco de dados
REM Projeto: DAC_2025
REM ============================================================

echo ===============================================
echo  Teste de .gitignore para bancos de dados
echo  Data/Hora: %DATE% %TIME%
echo ===============================================

echo.
echo [1/5] Verificando se o Git está instalado...
where git >nul 2>&1
if errorlevel 1 (
  echo ERRO: Git nao encontrado no PATH.
  echo Instale o Git ou execute este script em um ambiente com Git.
  goto :end
)

echo Git encontrado.

echo.
echo [2/5] Verificando se estamos em um repositório Git...
cd /d "%~dp0"
set REPO_DIR=%CD%

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
  echo ERRO: Este diretório nao é um repositório Git: %REPO_DIR%
  echo Execute 'git init' ou vá para a pasta do repositório.
  goto :end
)

echo OK: Repositório Git detectado em %REPO_DIR%

echo.
echo [3/5] Resumo de regras relacionadas no .gitignore (raiz):
if exist ".gitignore" (
  echo -- Linhas com padroes de bancos (raiz) --
  findstr /N /C:"*.db" /C:"*.sqlite" /C:"*.sqlite3" ".gitignore"
  echo -- Excecoes adicionadas para permitir bancos --
  findstr /N /C:"!/recursos/dados/database/*.db" /C:"!/recursos/dados/database/*.sqlite" ".gitignore"
  findstr /N /C:"!/Versão PY/data/*.db" /C:"!/Versão PY/data/*.sqlite" ".gitignore"
  findstr /N /C:"!/Banco de dados/*.db" /C:"!/Banco de dados/*.sqlite" ".gitignore"
) else (
  echo Aviso: .gitignore raiz nao encontrado.
)

echo.
echo [4/5] Resumo de regras relacionadas no .gitignore (Versao PY):
if exist "Versão PY\.gitignore" (
  echo -- Linhas com padroes de bancos (Versao PY) --
  findstr /N /C:"*.db" /C:"*.sqlite" /C:"*.sqlite3" "Versão PY\.gitignore"
) else (
  echo Aviso: Versao PY\.gitignore nao encontrado.
)

echo.
echo [5/5] Listando arquivos de banco de dados no projeto:
echo -- Arquivos *.db --
for /R %%F in (*.db) do echo %%F

echo -- Arquivos *.sqlite --
for /R %%F in (*.sqlite) do echo %%F

echo -- Arquivos *.sqlite3 --
for /R %%F in (*.sqlite3) do echo %%F

echo.
echo ===============================================
echo  Testando arquivo principal do projeto
set DBFILE="Versão PY\data\dac_database.db"
if not exist %DBFILE% (
  set DBFILE="Banco de dados\dac_database.db"
)
if not exist %DBFILE% (
  set DBFILE="recursos\dados\database\dac_database.db"
)

echo  Arquivo alvo: %DBFILE%
echo ===============================================

echo.
echo [A] Verificando se o arquivo está sendo ignorado (git check-ignore)...
git check-ignore -v %DBFILE%
if errorlevel 1 (
  echo Resultado: NAO ignorado pelo .gitignore.
) else (
  echo Resultado: IGNORADO pelo .gitignore.
)

echo.
echo [B] Tentando adicionar (dry-run) o arquivo ao Git:
git add -n %DBFILE%
if errorlevel 1 (
  echo Resultado: Nao foi possivel preparar 'add' (pode estar ignorado ou ocorreram erros).
) else (
  echo Resultado: Dry-run concluido. Se houver saida acima, o arquivo seria adicionado.
)

echo.
echo [C] Status do Git focado no arquivo:
git status --porcelain

echo.
echo ===============================================
echo  Dicas
echo  - Se o arquivo aparecer no 'git add -n' ele pode ser versionado.
echo  - Se 'git check-ignore' mostrar uma regra, ainda ha algo ignorando o arquivo.
echo  - Use 'git add -f %DBFILE%' para forcar a adicao caso necessario.
echo ===============================================

echo.
echo Final do teste. Pressione uma tecla para sair...
pause

:end
endlocal
exit /b 0
