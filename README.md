# 🏛️ Sistema DAC — Análise de Exclusão Digital no Brasil

<div align="center">

**Sistema Acadêmico para Análise de Exclusão Digital no Brasil**

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)

**Autor:** Alejandro Alexandre (RA: 197890)  
**Curso:** Análise e Desenvolvimento de Sistemas  
**Ano:** 2025

</div>

---

## Índice

- [📋 Sobre o Projeto](#-sobre-o-projeto)
- [🚀 Instalação Rápida](#-instalação-rápida)
- [🖱️ Executáveis Prontos para Uso](#️-executáveis-prontos-para-uso)
- [⚙️ Configuração](#️-configuração)
- [▶️ Uso](#️-uso)
- [🤝 Contribuição](#-contribuição)
- [📚 Documentação](#-documentação)
- [📄 Licença](#-licença)
- [📞 Contato e Suporte](#-contato-e-suporte)
- [🗃️ Banco de Dados e Filtros](#️-banco-de-dados-e-filtros)

## 📋 Sobre o Projeto

O **Sistema DAC** é uma aplicação completa desenvolvida para análise de dados relacionados à exclusão digital no Brasil, reunindo ferramentas de importação, processamento, validação, análise estatística e geração de relatórios.

### 🎯 Propósito
Apoiar decisões estratégicas por meio de dados confiáveis e relatórios consistentes sobre acesso digital no Brasil.

### ✨ Características Principais

- 📊 **Análise de Dados Completa**
  - Importação de múltiplos formatos (CSV, Excel, PDF)
  - Limpeza e validação automática
  - Métricas estatísticas avançadas
  
- 📈 **Visualizações e Relatórios**
  - Gráficos interativos
  - Exportação em PDF, CSV, XLSX, JSON
  - Dashboard web moderno
  
- 🖥️ **Duas Versões Disponíveis**
  - **Desktop:** Interface Tkinter standalone
  - **Web:** Next.js + FastAPI (frontend moderno + API REST)
  
- 💾 **Gerenciamento de Dados**
  - Suporte a SQLite e PostgreSQL
  - Sistema de backup e migração
  - Otimizações de performance

### 🛠️ Stack Tecnológica

**Backend & Desktop:**
- Python 3.13+
- Tkinter (UI Desktop)
- FastAPI (API REST)
- SQLAlchemy (ORM)
- Pandas, NumPy (Análise de dados)
- Matplotlib, Seaborn (Visualização)

**Frontend Web:**
- Next.js 16 (React 19)
- TypeScript
- TailwindCSS
- Radix UI
- Recharts

**Banco de Dados:**
- SQLite (desenvolvimento)
- PostgreSQL (produção)

---

## 🚀 Instalação Rápida

### Pré-requisitos

- [Python 3.13+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [Git](https://git-scm.com/)

### Setup Automático (Recomendado)

```bash
# 1. Clonar o repositório
git clone https://github.com/FenixMaker/DAC_2025.git
cd DAC_2025

# 2. Executar setup automático
setup.bat
```

**O script irá:**
- ✅ Verificar pré-requisitos
- ✅ Criar ambiente virtual Python
- ✅ Instalar todas as dependências (Python + Node.js)
- ✅ Configurar estrutura de diretórios
- ✅ Criar scripts de atalho

**Tempo estimado:** 10-15 minutos

📖 **Guias disponíveis:**
- [Instalação Rápida](docs/guias/INSTALACAO_RAPIDA.md) - Setup em 5 minutos
- [Manual de Execução](docs/guias/MANUAL_EXECUCAO.md) - Guia completo e detalhado
- [Índice de Documentação](docs/INDICE_DOCUMENTACAO.md) - Navegação completa

---

## 🖱️ Executáveis Prontos para Uso

### Iniciar o Sistema (Duplo Clique!)

Após executar o `setup.bat`, você terá arquivos prontos na raiz do projeto:

**Versão Web:**
```
Iniciar-Web.bat       ← Duplo clique para iniciar versão web
```
- Inicia backend (FastAPI) automaticamente
- Inicia frontend (Next.js) automaticamente  
- Abre navegador em http://localhost:3002

**Versão Desktop:**
```
Iniciar-Desktop.bat   ← Duplo clique para iniciar versão desktop
```
- Inicia aplicação Tkinter
- Interface gráfica nativa do Windows

### 🔧 Criar Executáveis .EXE (Opcional)

Se preferir arquivos `.exe` ao invés de `.bat`:

```bash
# Método 1: Compilação automática com PyInstaller
cd scripts\build
build_executables.bat

# Resultado:
# - Iniciar-Web.exe (na raiz)
# - Iniciar-Desktop.exe (na raiz)
```

📖 **Guia completo:** [Como Criar Executáveis](docs/guias/CRIAR_EXECUTAVEIS.md)

---

## ⚙️ Configuração

### 🚀 Instalação Automática (Recomendado)

**Após clonar do GitHub, execute:**

```bash
# Windows - Opção 1 (BAT)
setup.bat

# Windows - Opção 2 (PowerShell)
powershell -ExecutionPolicy Bypass -File setup.ps1
```

O script automático irá:
- ✅ Verificar pré-requisitos (Python, Node.js, npm)
- ✅ Criar ambiente virtual Python
- ✅ Instalar todas as dependências (Python + Node.js)
- ✅ Configurar estrutura de diretórios
- ✅ Criar scripts de atalho para iniciar o sistema

**Tempo estimado:** 10-15 minutos

📖 **Guia completo:** Consulte [`INSTALACAO_RAPIDA.md`](INSTALACAO_RAPIDA.md)

### Requisitos do sistema
- Python `3.13+` ⚠️ **Obrigatório**
- Node.js `18+` (para versão web)
- `pip` e `venv`
- Git
- PostgreSQL (opcional, para produção)

### Instalação Manual (Desktop/Python)

```bash
# 1) Clonar o repositório
git clone https://github.com/FenixMaker/DAC_2025.git
cd DAC_2025

# 2) Criar e ativar o ambiente virtual
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
# source .venv/bin/activate

# 3) Instalar dependências Python
cd "Versão PY"
pip install -r requirements.txt

# 4) Instalar dependências do Backend (se usar versão web)
cd web\backend
pip install -r requirements.txt
cd ..\..

# 5) Instalar dependências do Frontend (se usar versão web)
cd "Versão Web"
npm install --legacy-peer-deps
cd ..
```

### Configurações do sistema
- Banco de dados: `config/database_config.json`
- Cache: `config/cache_config.json`
- Logs: `config/logging_config.json`
- Monitoramento de erros: `config/error_monitoring.json`

Exemplo de `config/database_config.json`:
```json
{
  "default_engine": "sqlite",
  "sqlite": {
    "database_path": "data/dac_database.db"
  },
  "postgresql": {
    "host": "localhost",
    "port": 5432,
    "database": "dac_db",
    "user": "dac_user"
}
```

### Configuração da Versão Web (opcional)
```bash
cd "Versão Web"
npm install --legacy-peer-deps
```

**Arquivo `.env.local`** (criado automaticamente pelo setup):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Sistema DAC
NEXT_PUBLIC_APP_VERSION=1.0.0
```

## ▶️ Uso

### 🚀 Início Rápido (Após Setup Automático)

#### Versão Web (Recomendado)
```bash
# Windows - BAT
Iniciar-Web.bat

# Windows - PowerShell
.\Iniciar-Web.ps1
```

Acesse: http://localhost:3002

**URLs Disponíveis:**
- Frontend: http://localhost:3002
- Backend API: http://localhost:8000
- Documentação API: http://localhost:8000/docs

#### Versão Desktop
```bash
# Windows - BAT
Iniciar-Desktop.bat

# Windows - PowerShell
.\Iniciar-Desktop.ps1
```

#### Parar Servidores
```bash
# Windows - BAT
Parar-Servidores.bat

# Windows - PowerShell
.\Parar-Servidores.ps1
```

### Execução Manual

#### Versão Desktop (UI Tkinter)
```bash
# Dentro do ambiente virtual
cd "Versão PY"
..\\.venv\Scripts\python.exe main.py
```
- O sistema carrega a interface principal do DAC.
- Logs e saídas ficam disponíveis conforme configurado em `config/logging_config.json`.

#### Versão Web (Manual)

**Terminal 1 - Backend:**
```bash
cd "Versão PY\web\backend"
..\..\..\\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd "Versão Web"
npm run start-frontend
```

### Executar testes
```bash
# Todos os testes
python -m pytest tests/

# Grupos específicos
python -m pytest tests/unit/
python -m pytest tests/integration/
python -m pytest tests/performance/
```

### Exemplos e saída
- Relatórios gerados são salvos em `reports/` (PDF/CSV/XLSX).
- Bancos e dados de trabalho ficam em `data/`.

## 🤝 Contribuição

### Diretrizes para contribuidores
- Siga PEP 8 e mantenha o código documentado.
- Inclua testes unitários/integração quando alterar lógica de negócios.
- Abra uma issue quando propor mudanças maiores.

### Padrões de código e commit
Use Conventional Commits:
```
tipo(escopo): descrição

feat(ui): adicionar janela de relatórios
fix(db): corrigir conexão PostgreSQL
docs(readme): atualizar instruções de instalação
```

### Processo de submissão
- Faça um fork e crie uma branch baseada em `main`.
- Implemente a mudança e garanta que os testes passam.
- Abra um Pull Request com descrição clara e referência às issues.

---

## 📚 Documentação

### 📖 Documentação Completa

O projeto possui documentação abrangente organizada em [`docs/`](docs/):

| Documento | Descrição | Link |
|-----------|-----------|------|
| **Índice de Documentação** | Mapa completo de toda documentação | [📑 Ver](docs/INDICE_DOCUMENTACAO.md) |
| **Estrutura Detalhada** | Organização completa do projeto | [📋 Ver](docs/ESTRUTURA_DETALHADA.md) |
| **Árvore Visual** | Visualização rápida da estrutura | [🌳 Ver](docs/ARVORE_VISUAL.md) |
| **Instalação Rápida** | Guia de instalação em 5 minutos | [⚡ Ver](docs/guias/INSTALACAO_RAPIDA.md) |
| **Manual de Execução** | Guia completo de uso | [📖 Ver](docs/guias/MANUAL_EXECUCAO.md) |
| **Testes de Versões** | Relatório de testes funcionais | [✅ Ver](docs/relatorios/TESTE_VERSOES.md) |
| **Sistema de Setup** | Como funciona o setup automático | [🔧 Ver](docs/relatorios/SETUP_AUTOMATICO_RESUMO.md) |

### 🗂️ Navegação Rápida

**Para Novos Usuários:**
1. Leia este README
2. Execute [`setup.bat`](setup.bat)
3. Consulte o [Manual de Execução](docs/guias/MANUAL_EXECUCAO.md)

**Para Desenvolvedores:**
1. Veja a [Estrutura Detalhada](docs/ESTRUTURA_DETALHADA.md)
2. Leia [CONTRIBUTING.md](CONTRIBUTING.md)
3. Explore o [Índice de Documentação](docs/INDICE_DOCUMENTACAO.md)

**Para Professores/Avaliadores:**
1. Leia a [Documentação Geral](docs/DOCUMENTACAO_GERAL_PROJETO_DAC.md)
2. Veja os [Testes Realizados](docs/relatorios/TESTE_VERSOES.md)
3. Entenda o [Sistema de Setup](docs/relatorios/SETUP_AUTOMATICO_RESUMO.md)

---

## 📄 Licença
Este projeto utiliza a MIT License. Consulte `LICENSE`.

---

## 📞 Contato e Suporte

**Desenvolvedor:** Alejandro Alexandre  
**RA:** 197890  
**Curso:** Análise e Desenvolvimento de Sistemas  
**Ano:** 2025  

**Repositório:** [DAC_2025](https://github.com/FenixMaker/DAC_2025)  
**Issues:** [Reportar Problema](https://github.com/FenixMaker/DAC_2025/issues)
**Email:** fenixposts@gmail.com  
**GitHub:** fenixmaker

---

## 🗃️ Banco de Dados e Filtros

### Configuração do Banco

- Desenvolvimento: SQLite (`sqlite:///dac_dev.db`)
- Produção: PostgreSQL (`postgresql+psycopg2://<user>:<pass>@<host>:<port>/<db>`) com `DB_SSLMODE=require`
- Pool (SQLAlchemy): `pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`, `pool_recycle=1800`

### Endpoint com Filtros (FastAPI)

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

router = APIRouter(prefix="/api")

@router.get("/households")
def list_households(region: str | None = Query(None), has_internet: bool | None = Query(None), limit: int = 20, offset: int = 0, orderby: str | None = None, db: Session = Depends(get_session)):
  q = db.query(Household)
  if region:
    q = q.filter(Household.region.ilike(f"%{region}%"))
  if has_internet is not None:
    q = q.filter(Household.has_internet == has_internet)
  if orderby:
    field, direction = orderby.split(":")
    col = Household.region if field == "region" else Household.has_internet
    q = q.order_by(asc(col) if direction == "asc" else desc(col))
  return {"items": q.limit(limit).offset(offset).all()}
```

### Exemplo Frontend (Next.js)

```typescript
const res = await fetch("http://localhost:8000/api/households?region=Sudeste&has_internet=true&limit=10&orderby=region:asc");
const { items } = await res.json();
```

<div align="center">

**⭐ Sistema DAC - Análise de Exclusão Digital no Brasil ⭐**

Desenvolvido com ❤️ por Alejandro Alexandre

</div>
