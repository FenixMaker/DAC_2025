@echo off
REM ============================================================================
REM Script de Teste do .gitignore - Sistema DAC
REM Autor: Alejandro Alexandre (RA: 197890)
REM ============================================================================

echo.
echo ============================================
echo TESTANDO .GITIGNORE DO SISTEMA DAC
echo ============================================
echo.

REM Navegar para o diretório do projeto
pushd "%~dp0..\.."

echo [1] Verificando status do Git...
git status --porcelain
echo.

echo [2] Verificando arquivos ignorados...
git status --ignored
echo.

echo [3] Testando padrões específicos...
echo - node_modules: 
git check-ignore -v "node_modules/" 2>nul && echo   ❌ Ignorado || echo   ✅ Não ignorado

echo - .env: 
git check-ignore -v ".env" 2>nul && echo   ❌ Ignorado || echo   ✅ Não ignorado

echo - __pycache__: 
git check-ignore -v "__pycache__/" 2>nul && echo   ❌ Ignorado || echo   ✅ Não ignorado

echo - .venv: 
git check-ignore -v ".venv/" 2>nul && echo   ❌ Ignorado || echo   ✅ Não ignorado

echo.
echo [4] Verificando arquivos sensíveis...
echo Procurando arquivos .env...
where /R . *.env 2>nul | findstr /V node_modules | findstr /V .git

echo.
echo Procurando arquivos de chaves...
where /R . *.key 2>nul | findstr /V node_modules | findstr /V .git

echo.
echo [5] Verificando dependências...
echo Verificando node_modules...
if exist "node_modules" (
    echo ❌ node_modules encontrado - deveria estar ignorado!
) else (
    echo ✅ node_modules não encontrado - correto!
)

echo.
echo Verificando __pycache__...
where /R . __pycache__ 2>nul | findstr /V node_modules | findstr /V .git

echo.
echo [6] Verificando build artifacts...
echo Verificando diretórios de build...
if exist "build" (
    echo ❌ Diretório build encontrado - deveria estar ignorado!
) else (
    echo ✅ Diretório build não encontrado - correto!
)

if exist "dist" (
    echo ❌ Diretório dist encontrado - deveria estar ignorado!
) else (
    echo ✅ Diretório dist não encontrado - correto!
)

echo.
echo ============================================
echo TESTE CONCLUÍDO
echo ============================================
echo.
echo ✅ Arquivos que DEVEM estar ignorados:
echo    - node_modules/
echo    - __pycache__/
echo    - .venv/
echo    - *.env
echo    - *.log
echo    - build/
echo    - dist/
echo.
echo ⚠️  Verifique os resultados acima para garantir que:
echo    - Nenhum arquivo sensível está sendo rastreado
echo    - Os arquivos listados estão sendo ignorados corretamente
echo.

popd
pause