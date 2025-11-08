# COMANDOS MANUAIS — Sistema DAC (Windows PowerShell)

Este guia lista apenas comandos manuais para baixar, configurar e iniciar o projeto DAC, sem usar scripts automatizados. Execute-os na pasta do projeto: `c:\Users\FenixPosts\Desktop\DAC_2025`.

Observação: Use o PowerShell. Se usar CMD, a maioria dos comandos funciona igual.

---

## 1) Verificar pré-requisitos
- Verifica versões instaladas.

```
python --version
python -m pip --version
node --version
npm --version
```

Se algum não existir, instale:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/

---

## 2) Criar ambiente virtual Python
- Cria a venv dentro de `Versão PY` (onde o app espera).

```
Set-Location "c:\Users\FenixPosts\Desktop\DAC_2025\Versão PY"
python -m venv .venv
```

- Atualiza o `pip` dentro da venv:

```
".venv\Scripts\python.exe" -m pip install --upgrade pip
```

---

## 3) Instalar dependências Python
- Desktop (arquivo `requirements.txt`):

```
".venv\Scripts\python.exe" -m pip install -r "c:\Users\FenixPosts\Desktop\DAC_2025\Versão PY\requirements.txt"
```

- Backend Web (FastAPI):

```
".venv\Scripts\python.exe" -m pip install -r "c:\Users\FenixPosts\Desktop\DAC_2025\Versão PY\web\backend\requirements.txt"
```

---

## 4) Instalar dependências do Frontend (Next.js)

```
Set-Location "c:\Users\FenixPosts\Desktop\DAC_2025\Versão Web"
npm install --legacy-peer-deps
```

---

## 5) Criar arquivo de configuração do Frontend (`.env.local`)
- Cria/atualiza o arquivo com variáveis padrão.

```
@"
# Configuracao do Sistema DAC - Versao Web
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Sistema DAC
NEXT_PUBLIC_APP_VERSION=1.0.0
"@ | Set-Content "c:\Users\FenixPosts\Desktop\DAC_2025\Versão Web\.env.local"
```

---

## 6) Iniciar Versão Web (Backend + Frontend)
Abra duas janelas do PowerShell:

- Janela 1 — Backend API (porta 8000):
```
Set-Location "c:\Users\FenixPosts\Desktop\DAC_2025\Versão PY\web\backend"
"..\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- Janela 2 — Frontend (porta 3002):
```
Set-Location "c:\Users\FenixPosts\Desktop\DAC_2025\Versão Web"
npm run start-frontend
```

Acesse: `http://localhost:3002` e documentação API: `http://localhost:8000/docs`.

---

## 7) Iniciar Versão Desktop

```
Set-Location "c:\Users\FenixPosts\Desktop\DAC_2025\Versão PY"
".venv\Scripts\python.exe" "main.py"
```

---

## 8) Verificar instalação manual (checks rápidos)

- Venv existe e funciona:
```
Test-Path "c:\Users\FenixPosts\Desktop\DAC_2025\Versão PY\.venv\Scripts\python.exe"
"c:\Users\FenixPosts\Desktop\DAC_2025\Versão PY\.venv\Scripts\python.exe" --version
```

- Principais libs Python:
```
"c:\Users\FenixPosts\Desktop\DAC_2025\Versão PY\.venv\Scripts\python.exe" -c "import tkinter, sqlalchemy, matplotlib"
"c:\Users\FenixPosts\Desktop\DAC_2025\Versão PY\.venv\Scripts\python.exe" -c "import fastapi, uvicorn"
```

- Node e `node_modules`:
```
node --version
Test-Path "c:\Users\FenixPosts\Desktop\DAC_2025\Versão Web\node_modules"
```

---

## 9) Testar .gitignore e versionar bancos de dados

- Escolha automático do arquivo alvo (ajuste se necessário):
```
$DBFILE = "c:\Users\FenixPosts\Desktop\DAC_2025\Versão PY\data\dac_database.db"
if (!(Test-Path $DBFILE)) { $DBFILE = "c:\Users\FenixPosts\Desktop\DAC_2025\Banco de dados\dac_database.db" }
```

- Verificar se está sendo ignorado:
```
Set-Location "c:\Users\FenixPosts\Desktop\DAC_2025"
git check-ignore -v "$DBFILE"
```

- Testar adição (dry-run):
```
git add -n "$DBFILE"
```

- Status:
```
git status --porcelain
```

- Adicionar e commitar bancos (exemplo):
```
git add "c:\Users\FenixPosts\Desktop\DAC_2025\Versão PY\data\dac_database.db" "c:\Users\FenixPosts\Desktop\DAC_2025\Banco de dados\dac_database.db"
git commit -m "Versiona banco de dados academico"
```

---

## 10) Parar servidores (opcional)
- Encerrar processos em portas conhecidas.

```
# Porta 8000 (Backend)
Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

# Porta 3002 (Frontend)
Get-NetTCPConnection -LocalPort 3002 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

---

## Dúvidas comuns
- Se `npm install` falhar, tente novamente com `--legacy-peer-deps` (já incluído acima).
- Se a venv não ativar, use o caminho absoluto do Python da venv nos comandos.
- Se o Frontend iniciar em outra porta, verifique o `package.json` e logs.

Pronto! Com estes comandos, você substitui o uso dos `.bat` e controla tudo manualmente.