# 📚 Manual Completo de Execução - Sistema DAC 2025

**Autor:** Alejandro Alexandre (RA: 197890)  
**Curso:** Análise e Desenvolvimento de Sistemas  
**Data:** 04 de novembro de 2025  
**Versão do Sistema:** 1.0.0

---

## 📑 Índice

1. [Visão Geral do Sistema](#visão-geral-do-sistema)
2. [Pré-requisitos](#pré-requisitos)
3. [Arquitetura do Sistema](#arquitetura-do-sistema)
4. [Versão Web - Como Funciona](#versão-web---como-funciona)
5. [Versão Python Desktop - Como Funciona](#versão-python-desktop---como-funciona)
6. [Guia de Inicialização Passo a Passo](#guia-de-inicialização-passo-a-passo)
7. [Troubleshooting](#troubleshooting)
8. [Explicação Técnica Detalhada](#explicação-técnica-detalhada)

---

## 🎯 Visão Geral do Sistema

O **Sistema DAC (Digital Analysis and Control)** é uma aplicação acadêmica desenvolvida para análise de dados relacionados à exclusão digital no Brasil. O sistema foi desenvolvido em **duas versões completamente funcionais**:

### 1. **Versão Web** (Aplicação Moderna)
- **Frontend:** Next.js 16 (React) com TypeScript
- **Backend:** FastAPI (Python) - API REST
- **Banco de Dados:** SQLite (compartilhado)
- **Propósito:** Acesso via navegador, multiplataforma

### 2. **Versão Python Desktop** (Aplicação Standalone)
- **Interface:** Tkinter (Python GUI)
- **Backend:** Integrado na aplicação
- **Banco de Dados:** SQLite (local)
- **Propósito:** Execução local sem necessidade de servidor web

---

## 🔧 Pré-requisitos

### Software Necessário

| Software | Versão Mínima | Verificação | Propósito |
|----------|---------------|-------------|-----------|
| **Python** | 3.13.x | `python --version` | Executar backend e aplicação desktop |
| **Node.js** | 18.x ou superior | `node --version` | Executar frontend Next.js |
| **NPM** | 9.x ou superior | `npm --version` | Gerenciar dependências JavaScript |
| **PowerShell** | 5.1 ou superior | `$PSVersionTable` | Executar scripts de inicialização |

### Dependências Python (requirements.txt)

```python
# Processamento de Dados
pandas>=1.5.0              # Manipulação de dados tabulares
numpy>=1.21.0              # Operações matemáticas e arrays

# Banco de Dados
sqlalchemy>=1.4.0          # ORM para acesso ao banco de dados
psycopg2-binary>=2.9.9     # Driver PostgreSQL (suporte futuro)

# Visualização
matplotlib>=3.5.0          # Geração de gráficos
seaborn>=0.11.0            # Gráficos estatísticos avançados

# Processamento de Documentos
openpyxl>=3.0.0           # Leitura/escrita de arquivos Excel
pdfplumber>=0.7.0         # Extração de dados de PDF
reportlab>=3.6.0          # Geração de relatórios PDF

# Processamento de Imagens
opencv-python>=4.8.0      # Visão computacional
Pillow>=10.0.0            # Manipulação de imagens
pytesseract>=0.3.10       # OCR (reconhecimento de texto)
```

### Dependências Web Backend (FastAPI)

```python
fastapi==0.111.0          # Framework web assíncrono
uvicorn[standard]==0.30.0 # Servidor ASGI
jinja2==3.1.4             # Template engine
python-multipart==0.0.9   # Upload de arquivos
httpx==0.27.2             # Cliente HTTP assíncrono
```

### Dependências Frontend (package.json)

```json
{
  "next": "16.0.0",           // Framework React
  "react": "19.2.0",          // Biblioteca UI
  "@radix-ui/*": "...",       // Componentes UI acessíveis
  "recharts": "...",          // Biblioteca de gráficos
  "tailwindcss": "...",       // CSS utility-first
  "lucide-react": "..."       // Ícones
}
```

---

## 🏗️ Arquitetura do Sistema

### Estrutura de Diretórios

```
DAC_2025/
│
├─── 📁 Banco de dados/          # Banco compartilhado (versão web)
│    └── dac_database.db         # SQLite database
│
├─── 📁 Versão Web/              # Aplicação Web (Next.js)
│    ├── app/                    # Páginas e rotas Next.js
│    ├── components/             # Componentes React
│    ├── lib/                    # Utilitários e configurações
│    ├── package.json            # Dependências Node.js
│    └── next.config.mjs         # Configuração Next.js
│
├─── 📁 Versão PY/               # Aplicação Desktop Python
│    ├── main.py                 # Ponto de entrada principal
│    ├── requirements.txt        # Dependências Python
│    ├── data/                   # Banco de dados local
│    │   └── dac_database.db     # SQLite database
│    ├── src/                    # Código fonte
│    │   ├── database/           # Gerenciamento de BD
│    │   ├── modules/            # Módulos de processamento
│    │   ├── ui/                 # Interface Tkinter
│    │   └── utils/              # Utilitários
│    └── web/                    # Backend FastAPI
│        └── backend/
│            ├── app/            # Aplicação FastAPI
│            └── requirements.txt
│
├─── 📁 .venv/                   # Ambiente virtual Python
│    └── Scripts/
│        └── python.exe          # Interpretador Python isolado
│
├─── start-web.ps1               # Script de inicialização web
└─── MANUAL_EXECUCAO.md          # Este documento
```

---

## 🌐 Versão Web - Como Funciona

### Arquitetura Client-Server

A versão web utiliza uma **arquitetura de três camadas**:

```
┌─────────────────────────────────────────────────────────────┐
│                    NAVEGADOR DO USUÁRIO                      │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Frontend Next.js (Porta 3002)              │    │
│  │  • React Components                                 │    │
│  │  • TailwindCSS Styling                             │    │
│  │  • Recharts para visualizações                     │    │
│  │  • Client-side rendering                           │    │
│  └─────────────────┬──────────────────────────────────┘    │
└────────────────────┼───────────────────────────────────────┘
                     │ HTTP/JSON
                     │ (API Requests)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend FastAPI (Porta 8000)                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │         API REST (FastAPI + Uvicorn)               │    │
│  │  • Endpoints: /api/estatisticas/*                  │    │
│  │  • Processamento assíncrono                        │    │
│  │  • Validação de dados (Pydantic)                   │    │
│  │  • CORS habilitado                                 │    │
│  └─────────────────┬──────────────────────────────────┘    │
└────────────────────┼───────────────────────────────────────┘
                     │ SQL Queries
                     │ (SQLAlchemy ORM)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           Banco de Dados SQLite                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  📊 dac_database.db                                │    │
│  │  • Tabelas normalizadas                            │    │
│  │  • Índices otimizados                              │    │
│  │  • Transações ACID                                 │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de Inicialização - Versão Web

#### 1️⃣ **Fase 1: Preparação do Ambiente**

```powershell
# O sistema primeiro prepara o ambiente virtual Python
cd "c:\Users\FenixPosts\Desktop\Nova pasta\DAC_2025"
python -m venv .venv
```

**O que acontece:**
- Python cria um ambiente isolado em `.venv/`
- Isso garante que as dependências não conflitem com outros projetos
- Um interpretador Python dedicado é instalado em `.venv/Scripts/python.exe`

#### 2️⃣ **Fase 2: Instalação de Dependências**

**Backend Python:**
```powershell
.\.venv\Scripts\python.exe -m pip install -r "Versão PY\web\backend\requirements.txt"
```

**O que é instalado:**
- `fastapi` → Framework web moderno e rápido
- `uvicorn` → Servidor ASGI para executar FastAPI
- `jinja2` → Templates HTML (se necessário)
- `python-multipart` → Upload de arquivos
- `httpx` → Cliente HTTP assíncrono

**Frontend Node.js:**
```powershell
cd "Versão Web"
npm install --legacy-peer-deps
```

**O que é instalado:**
- Next.js 16 + React 19
- Componentes UI (@radix-ui/*)
- TailwindCSS para estilização
- Recharts para gráficos
- ~269 pacotes no total

#### 3️⃣ **Fase 3: Inicialização do Backend (FastAPI)**

```powershell
cd "Versão PY\web\backend"
..\..\..\\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Processo de inicialização do backend:**

```python
# 1. Uvicorn carrega o módulo app.main
# 2. FastAPI inicializa a aplicação
from fastapi import FastAPI
app = FastAPI()

# 3. DatabaseManager conecta ao banco
from app.services.db import DatabaseManager
db_manager = DatabaseManager()
db_manager.initialize()
# Output: "Banco de dados inicializado com otimizações"

# 4. Rotas são registradas
@app.get("/api/estatisticas/resumo")
async def get_resumo():
    # Retorna estatísticas do banco
    
# 5. CORS é configurado
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, ...)

# 6. Servidor começa a escutar na porta 8000
# Output: "Uvicorn running on http://0.0.0.0:8000"
```

**Logs visíveis:**
```
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
2025-11-04 16:00:29 - INFO - Otimização da estrutura do banco concluída
2025-11-04 16:00:29 - INFO - Banco de dados inicializado com otimizações
2025-11-04 16:00:29 - INFO - DatabaseManager inicializado para Web API
```

**O que cada linha significa:**
- `Started server process [PID]` → Processo do servidor foi criado
- `Application startup complete` → FastAPI pronto para receber requisições
- `Uvicorn running on...` → Servidor escutando conexões
- `Banco de dados inicializado` → Conexão com SQLite estabelecida
- `DatabaseManager inicializado` → ORM pronto para queries

#### 4️⃣ **Fase 4: Inicialização do Frontend (Next.js)**

```powershell
cd "Versão Web"
npm run start-frontend
# Que executa: next dev --port 3002
```

**Processo de inicialização do frontend:**

```javascript
// 1. Next.js carrega configuração (next.config.mjs)
const config = {
  reactStrictMode: true,
  // ... outras configurações
}

// 2. Turbopack (bundler) compila o código TypeScript
// - Páginas em app/
// - Componentes em components/
// - Estilos TailwindCSS

// 3. Servidor de desenvolvimento inicia
// Output: "▲ Next.js 16.0.0 (Turbopack)"

// 4. Aplicação fica disponível
// Output: "✓ Ready in 439ms"

// 5. Rotas são mapeadas
// - / → página principal (dashboard)
// - /consultas → página de consultas
// - /relatorios → página de relatórios
// - /status-banco → status do banco de dados
```

**Logs visíveis:**
```
▲ Next.js 16.0.0 (Turbopack)
- Local:        http://localhost:3002
- Network:      http://192.168.0.154:3002
- Environments: .env.local

✓ Starting...
✓ Ready in 439ms
```

**O que cada linha significa:**
- `Next.js 16.0.0 (Turbopack)` → Versão e motor de build
- `Local: http://localhost:3002` → URL para acesso local
- `Network: http://192.168...` → URL para acesso na rede local
- `Ready in 439ms` → Tempo que levou para inicializar

#### 5️⃣ **Fase 5: Comunicação Frontend ↔ Backend**

```javascript
// Frontend faz requisição
// File: app/page.tsx
async function fetchDados() {
  const response = await fetch('http://localhost:8000/api/estatisticas/resumo');
  const data = await response.json();
  return data;
}
```

```python
# Backend processa requisição
# File: app/main.py
@app.get("/api/estatisticas/resumo")
async def get_resumo():
    query = """
        SELECT COUNT(*) as total,
               AVG(velocidade) as media_velocidade
        FROM dados_dac
    """
    result = db_manager.execute(query)
    return {"total": result.total, "media": result.media_velocidade}
```

**Logs da comunicação:**
```
# Frontend
GET /api/estatisticas/resumo 200 in 253ms (compile: 193ms, render: 60ms)

# Backend
INFO: 127.0.0.1:64651 - "GET /api/estatisticas/resumo HTTP/1.1" 200 OK
```

---

## 🖥️ Versão Python Desktop - Como Funciona

### Arquitetura Monolítica

A versão desktop usa uma **arquitetura monolítica integrada**:

```
┌─────────────────────────────────────────────────────────────┐
│               APLICAÇÃO DESKTOP (main.py)                    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           Interface Gráfica (Tkinter)              │    │
│  │  ┌──────────────────────────────────────────┐     │    │
│  │  │  MainWindow (Janela Principal)           │     │    │
│  │  │  • Menu superior                         │     │    │
│  │  │  • Painel de estatísticas               │     │    │
│  │  │  • Botões de ação                       │     │    │
│  │  └──────────────────────────────────────────┘     │    │
│  │  ┌──────────────────────────────────────────┐     │    │
│  │  │  ConsultaWindow (Consultas)              │     │    │
│  │  │  • Filtros de busca                     │     │    │
│  │  │  • Tabela de resultados                 │     │    │
│  │  │  • Paginação                            │     │    │
│  │  └──────────────────────────────────────────┘     │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │ Eventos / Callbacks                     │
│                   ▼                                         │
│  ┌────────────────────────────────────────────────────┐    │
│  │        Módulos de Negócio (src/modules/)           │    │
│  │  • DataImporter (importação de dados)              │    │
│  │  • QueryEngine (motor de consultas)                │    │
│  │  • ImageProcessor (processamento de imagens)       │    │
│  │  • PDFProcessor (geração de relatórios)            │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │ SQL Queries                             │
│                   ▼                                         │
│  ┌────────────────────────────────────────────────────┐    │
│  │      DatabaseManager (src/database/)               │    │
│  │  • Connection Pool                                 │    │
│  │  • ORM (SQLAlchemy)                               │    │
│  │  • Modelos de dados                               │    │
│  └────────────────┬───────────────────────────────────┘    │
└────────────────────┼───────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Banco de Dados SQLite Local                     │
│  📊 Versão PY/data/dac_database.db                          │
└─────────────────────────────────────────────────────────────┘
```

### Fluxo de Inicialização - Versão Desktop

#### 1️⃣ **Fase 1: Execução do Script Principal**

```powershell
cd "Versão PY"
..\\.venv\Scripts\python.exe main.py
```

**O que acontece:**
```python
# File: main.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 1. Importações básicas
import sys
import os
from pathlib import Path

# 2. Configuração do path para imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 3. Importações da aplicação
from src.ui.main_window import MainWindow
from src.database.database_manager import DatabaseManager
from src.utils.logger import setup_logger

# 4. Função principal
def main():
    """Ponto de entrada principal da aplicação"""
    
    # 5. Configuração de logging
    logger = setup_logger('DAC_Enhanced')
    logger.info("Iniciando aplicação DAC")
    
    # 6. Inicialização do banco de dados
    logger.info("Inicializando banco de dados...")
    db_manager = DatabaseManager()
    
    # 7. Criação da interface gráfica
    logger.info("Iniciando interface gráfica...")
    app = MainWindow(db_manager)
    
    # 8. Loop principal da aplicação
    logger.info("Iniciando interface principal")
    app.mainloop()
    
    # 9. Finalização
    logger.info("Finalizando aplicação DAC")

if __name__ == "__main__":
    main()
```

#### 2️⃣ **Fase 2: Inicialização do Logger**

```python
# File: src/utils/logger.py

def setup_logger(name):
    """
    Configura sistema de logging estruturado
    Logs são salvos em: logs/dac_structured_YYYYMMDD.json
    """
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Handler para arquivo JSON
    file_handler = logging.FileHandler(
        f'logs/dac_structured_{datetime.now():%Y%m%d}.json'
    )
    
    # Handler para console
    console_handler = logging.StreamHandler()
    
    # Formato: YYYY-MM-DD HH:MM:SS - NAME - LEVEL - MESSAGE
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return logger
```

**Output:**
```
2025-11-04 15:59:33 - DAC_Enhanced - INFO - Iniciando aplicação DAC
```

#### 3️⃣ **Fase 3: Inicialização do Banco de Dados**

```python
# File: src/database/database_manager.py

class DatabaseManager:
    def __init__(self):
        """Inicializa gerenciador de banco de dados"""
        
        # 1. Define caminho do banco
        self.db_path = Path(__file__).parent.parent.parent / 'data' / 'dac_database.db'
        
        # 2. Cria engine SQLAlchemy
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        
        # 3. Cria sessão
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # 4. Cria tabelas se não existirem
        Base.metadata.create_all(self.engine)
        
        # 5. Otimiza banco de dados
        self._optimize_database()
        
        logger.info(f"Banco de dados inicializado: {self.db_path}")
    
    def _optimize_database(self):
        """Aplica otimizações no SQLite"""
        
        optimizations = [
            "PRAGMA journal_mode=WAL",        # Write-Ahead Logging
            "PRAGMA synchronous=NORMAL",      # Sincronização moderada
            "PRAGMA cache_size=10000",        # Cache maior
            "PRAGMA temp_store=MEMORY",       # Temp em memória
        ]
        
        for opt in optimizations:
            self.session.execute(text(opt))
        
        logger.info("Otimização da estrutura do banco concluída")
```

**Output:**
```
2025-11-04 15:59:33 - DAC_Enhanced - INFO - Inicializando banco de dados...
2025-11-04 15:59:33 - DAC_Enhanced - INFO - Otimização da estrutura do banco concluída
2025-11-04 15:59:33 - DAC_Enhanced - INFO - Banco de dados inicializado: C:\...\data\dac_database.db
2025-11-04 15:59:33 - DAC_Enhanced - INFO - Banco de dados inicializado com sucesso
2025-11-04 15:59:33 - DAC_Enhanced - INFO - Verificação de integridade do banco: OK
```

#### 4️⃣ **Fase 4: Criação da Interface Gráfica (Tkinter)**

```python
# File: src/ui/main_window.py

class MainWindow(tk.Tk):
    def __init__(self, db_manager):
        """Inicializa janela principal"""
        
        super().__init__()
        
        # 1. Configurações da janela
        self.title("Sistema DAC - Análise de Exclusão Digital")
        self.geometry("1200x800")
        
        # 2. Armazena referência ao banco
        self.db_manager = db_manager
        
        # 3. Cria menu superior
        self._create_menu()
        
        # 4. Cria painel de estatísticas
        self._create_stats_panel()
        
        # 5. Cria botões de ação
        self._create_action_buttons()
        
        # 6. Carrega dados iniciais
        self._load_statistics()
        
        logger.info("Interface criada com sucesso")
    
    def _create_menu(self):
        """Cria barra de menu"""
        menubar = tk.Menu(self)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Importar Dados", command=self.import_data)
        file_menu.add_command(label="Exportar", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        
        # Menu Consultas
        query_menu = tk.Menu(menubar, tearoff=0)
        query_menu.add_command(label="Nova Consulta", command=self.open_query_window)
        menubar.add_cascade(label="Consultas", menu=query_menu)
        
        self.config(menu=menubar)
    
    def _create_stats_panel(self):
        """Cria painel de estatísticas"""
        stats_frame = tk.Frame(self, bg='#f0f0f0')
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cards de estatísticas
        self.total_label = tk.Label(stats_frame, text="Total: 0", font=('Arial', 16))
        self.total_label.pack()
        
        # ... outros widgets
    
    def _load_statistics(self):
        """Carrega estatísticas do banco"""
        query = "SELECT COUNT(*) as total FROM dados_dac"
        result = self.db_manager.execute(query)
        
        self.total_label.config(text=f"Total: {result.total}")
        
        logger.info("Estatísticas atualizadas com sucesso")
```

**Output:**
```
2025-11-04 15:59:33 - DAC_Enhanced - INFO - Iniciando interface gráfica...
2025-11-04 15:59:33 - DAC_Enhanced - INFO - Estatísticas atualizadas com sucesso
2025-11-04 15:59:33 - DAC_Enhanced - INFO - Interface criada com sucesso
2025-11-04 15:59:33 - DAC_Enhanced - INFO - Iniciando interface principal
```

#### 5️⃣ **Fase 5: Loop Principal da Aplicação**

```python
# File: main.py (continuação)

# 8. Loop principal da aplicação
app.mainloop()

# O mainloop() do Tkinter:
# - Mantém a janela aberta
# - Processa eventos (cliques, teclas, etc.)
# - Atualiza a interface
# - Aguarda até que a janela seja fechada
```

**O que acontece no loop:**

1. **Eventos de Mouse/Teclado** → Capturados pelo Tkinter
2. **Callbacks** → Funções Python são executadas
3. **Atualização de UI** → Widgets são redesenhados
4. **Queries ao Banco** → Dados são buscados/salvos
5. **Processamento** → Módulos executam lógica de negócio

**Exemplo de interação:**
```python
# Usuário clica em "Nova Consulta"
def open_query_window(self):
    logger.info("Abrindo janela de consulta")
    
    # Cria nova janela
    query_window = ConsultaWindow(self, self.db_manager)
    
    # Janela é exibida modalmente
    query_window.wait_window()
```

**Output:**
```
2025-11-04 15:59:41 - DAC_Enhanced - INFO - Consulta executada: página 1, 22 registros exibidos
```

#### 6️⃣ **Fase 6: Finalização**

```python
# Quando o usuário fecha a janela
def on_closing(self):
    logger.info("Fechando janela principal")
    
    # Fecha conexão com banco
    self.db_manager.close()
    logger.info("Conexão com banco de dados fechada")
    
    # Fecha a aplicação
    self.destroy()

# Output final
logger.info("Finalizando aplicação DAC")
```

**Output:**
```
2025-11-04 15:59:43 - DAC_Enhanced - INFO - Fechando janela de consulta
2025-11-04 15:59:44 - DAC_Enhanced - INFO - Conexão com banco de dados fechada
2025-11-04 15:59:44 - DAC_Enhanced - INFO - Finalizando aplicação DAC
```

---

## 🚀 Guia de Inicialização Passo a Passo

### 📋 Checklist Pré-Inicialização

- [ ] Python 3.13.x instalado
- [ ] Node.js 18+ instalado
- [ ] NPM 9+ instalado
- [ ] PowerShell disponível
- [ ] Permissões de execução configuradas

### 🌐 Iniciar Versão Web

#### Método 1: Script Automático (Recomendado)

```powershell
# 1. Navegar até a pasta do projeto
cd "c:\Users\FenixPosts\Desktop\Nova pasta\DAC_2025"

# 2. Executar script PowerShell
powershell -ExecutionPolicy Bypass -File .\start-web.ps1
```

**O que o script faz:**
1. ✅ Verifica ambiente virtual Python
2. ✅ Inicia backend FastAPI em job separado
3. ✅ Inicia frontend Next.js
4. ✅ Exibe URLs de acesso
5. ✅ Gerencia encerramento limpo com Ctrl+C

#### Método 2: Manual (Passo a Passo)

**Terminal 1 - Backend:**

```powershell
# Passo 1: Navegar para a pasta do backend
cd "c:\Users\FenixPosts\Desktop\Nova pasta\DAC_2025\Versão PY\web\backend"

# Passo 2: Ativar ambiente virtual e iniciar servidor
..\..\..\\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Aguarde ver:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [PID] using WatchFiles
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Terminal 2 - Frontend:**

```powershell
# Passo 1: Navegar para a pasta do frontend
cd "c:\Users\FenixPosts\Desktop\Nova pasta\DAC_2025\Versão Web"

# Passo 2: Iniciar Next.js
powershell -ExecutionPolicy Bypass -Command "npm run start-frontend"
```

**Aguarde ver:**
```
▲ Next.js 16.0.0 (Turbopack)
- Local:        http://localhost:3002
✓ Ready in 439ms
```

#### Acessar a Aplicação

1. **Frontend (Interface):** http://localhost:3002
2. **Backend API:** http://localhost:8000
3. **Documentação API:** http://localhost:8000/docs
4. **Rede Local:** http://[seu-ip]:3002

### 🖥️ Iniciar Versão Desktop

#### Método Único

```powershell
# Passo 1: Navegar para a pasta da versão Python
cd "c:\Users\FenixPosts\Desktop\Nova pasta\DAC_2025\Versão PY"

# Passo 2: Executar com Python do ambiente virtual
..\\.venv\Scripts\python.exe main.py
```

**Aguarde ver:**
```
2025-11-04 15:59:33 - DAC_Enhanced - INFO - Iniciando aplicação DAC
2025-11-04 15:59:33 - DAC_Enhanced - INFO - Inicializando banco de dados...
2025-11-04 15:59:33 - DAC_Enhanced - INFO - Banco de dados inicializado com sucesso
2025-11-04 15:59:33 - DAC_Enhanced - INFO - Interface criada com sucesso
```

**A janela da aplicação será aberta automaticamente**

---

## 🔍 Troubleshooting

### Problema 1: "Python não reconhecido"

**Erro:**
```
'python' não é reconhecido como um comando interno ou externo
```

**Solução:**
```powershell
# Use o caminho completo para o Python do ambiente virtual
.\.venv\Scripts\python.exe main.py
```

### Problema 2: "Porta já em uso"

**Erro:**
```
Error: listen EADDRINUSE: address already in use :::3002
```

**Solução:**
```powershell
# Encontrar processo usando a porta
netstat -ano | findstr :3002

# Matar processo (substitua [PID] pelo número retornado)
taskkill /F /PID [PID]
```

### Problema 3: "Module not found"

**Erro:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solução:**
```powershell
# Reinstalar dependências Python
cd "Versão PY\web\backend"
..\..\..\\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Problema 4: "NPM packages not installed"

**Erro:**
```
Error: Cannot find module 'next'
```

**Solução:**
```powershell
# Reinstalar dependências Node.js
cd "Versão Web"
npm install --legacy-peer-deps
```

### Problema 5: "Execution Policy"

**Erro:**
```
não pode ser carregado porque a execução de scripts foi desabilitada
```

**Solução:**
```powershell
# Executar com bypass de política
powershell -ExecutionPolicy Bypass -File .\start-web.ps1
```

---

## 📊 Explicação Técnica Detalhada

### Por que Ambiente Virtual Python?

```
SEM Ambiente Virtual:
┌─────────────────────────────────┐
│   Sistema Operacional           │
│   ┌─────────────────────────┐  │
│   │  Python Global (3.13)   │  │
│   │  ├─ pandas 1.5.0        │  │ ← Projeto A precisa
│   │  ├─ pandas 2.3.0        │  │ ← Projeto B precisa
│   │  └─ CONFLITO! ❌        │  │
│   └─────────────────────────┘  │
└─────────────────────────────────┘

COM Ambiente Virtual:
┌─────────────────────────────────┐
│   Sistema Operacional           │
│                                 │
│   ┌─────────────┐  ┌──────────┐│
│   │ Projeto A   │  │ Projeto B││
│   │ .venv/      │  │ .venv/   ││
│   │ pandas 1.5  │  │pandas 2.3││
│   │ ✅          │  │ ✅       ││
│   └─────────────┘  └──────────┘│
└─────────────────────────────────┘
```

### Como FastAPI Processa Requisições

```python
# 1. Cliente faz requisição
GET http://localhost:8000/api/estatisticas/resumo

# 2. Uvicorn recebe na porta 8000
# 3. FastAPI roteia para o handler correto
@app.get("/api/estatisticas/resumo")
async def get_resumo():
    
    # 4. Função assíncrona executa
    # 5. DatabaseManager faz query ao SQLite
    data = await db_manager.query("""
        SELECT * FROM dados_dac
    """)
    
    # 6. Dados são serializados para JSON
    return JSONResponse(data)

# 7. Response é enviada ao cliente
HTTP/1.1 200 OK
Content-Type: application/json
{
  "total": 1234,
  "media": 56.7
}
```

### Como Next.js Renderiza Páginas

```javascript
// 1. Usuário acessa http://localhost:3002
// 2. Next.js procura app/page.tsx

// 3. Componente é renderizado
export default function Dashboard() {
  // 4. useEffect dispara ao montar
  useEffect(() => {
    // 5. Fetch busca dados da API
    fetch('http://localhost:8000/api/estatisticas/resumo')
      .then(res => res.json())
      .then(data => {
        // 6. State é atualizado
        setStats(data);
        
        // 7. React re-renderiza componente
      });
  }, []);
  
  // 8. JSX é convertido para HTML
  return (
    <div>
      <h1>Dashboard</h1>
      <StatsCard data={stats} />
    </div>
  );
}

// 9. HTML é enviado ao navegador
// 10. CSS (TailwindCSS) é aplicado
// 11. JavaScript hidrata a página (torna interativa)
```

### Como Tkinter Gerencia Eventos

```python
# 1. Aplicação inicia mainloop()
app.mainloop()

# 2. Loop infinito processa eventos
while True:
    # 3. Aguarda evento
    event = wait_for_event()  # Clique, tecla, etc.
    
    # 4. Identifica widget alvo
    widget = find_widget(event)
    
    # 5. Chama callback associado
    if event.type == 'Button-1':  # Clique esquerdo
        widget.command()  # Executa função
    
    # 6. Atualiza interface
    redraw_widgets()
    
    # 7. Repete até quit()
    if should_quit:
        break
```

### Otimizações do SQLite

```sql
-- WAL Mode (Write-Ahead Logging)
PRAGMA journal_mode=WAL;
/* 
  Permite leituras simultâneas enquanto escreve
  Aumenta performance em 70-100%
*/

-- Cache Size
PRAGMA cache_size=10000;
/*
  10.000 páginas × 4KB = 40MB de cache
  Reduz I/O de disco
*/

-- Temp Store
PRAGMA temp_store=MEMORY;
/*
  Tabelas temporárias em RAM
  Mais rápido que disco
*/

-- Synchronous
PRAGMA synchronous=NORMAL;
/*
  Sincronização moderada
  Balance entre segurança e performance
*/
```

---

## 📈 Fluxo de Dados Completo

### Exemplo: Usuário Consulta Estatísticas na Versão Web

```
1. USUÁRIO                           2. NAVEGADOR
   └─> Acessa localhost:3002           └─> Renderiza página
           │                                     │
           ▼                                     ▼
   [Clica em Dashboard]              [React component mount]
           │                                     │
           ▼                                     ▼
3. FRONTEND (Next.js)               4. JAVASCRIPT
   └─> useEffect dispara               └─> fetch() chamado
           │                                     │
           ▼                                     ▼
   GET /api/estatisticas/resumo ────────────────┘
           │
           │ HTTP Request
           ▼
5. BACKEND (FastAPI)
   └─> Uvicorn recebe requisição
           │
           ▼
   @app.get("/api/estatisticas/resumo")
   async def get_resumo():
           │
           ▼
6. DATABASE MANAGER
   └─> SQLAlchemy ORM
           │
           ▼
   session.query(DadosDAC).all()
           │
           ▼
7. SQLITE
   └─> Executa query SQL
           │
           ▼
   SELECT * FROM dados_dac
   WHERE condicao = true;
           │
           ▼
8. RESULT SET
   └─> Linhas retornadas
           │
           ▼
9. SERIALIZAÇÃO
   └─> Python dict → JSON
           │
           ▼
10. HTTP RESPONSE
    └─> 200 OK + JSON
            │
            ▼
11. FRONTEND RECEBE
    └─> .then(data => ...)
            │
            ▼
12. STATE UPDATE
    └─> setStats(data)
            │
            ▼
13. RE-RENDER
    └─> React atualiza DOM
            │
            ▼
14. NAVEGADOR
    └─> Exibe dados atualizados
            │
            ▼
15. USUÁRIO
    └─> Vê estatísticas na tela
```

---

## 🎓 Pontos para Explicar ao Professor

### 1. **Arquitetura Moderna vs Tradicional**

**Versão Web (Moderna):**
- ✅ Separação de responsabilidades (Frontend/Backend)
- ✅ API RESTful reutilizável
- ✅ Escalável (pode adicionar apps mobile)
- ✅ Tecnologias atuais (React, FastAPI)

**Versão Desktop (Tradicional):**
- ✅ Monolítica, mais simples de entender
- ✅ Não requer servidor web
- ✅ Funciona offline
- ✅ Menor complexidade de deploy

### 2. **Escolhas Tecnológicas Justificadas**

| Tecnologia | Por Que Foi Escolhida |
|------------|----------------------|
| **FastAPI** | Framework Python moderno, rápido, com validação automática e documentação |
| **Next.js** | Framework React com SSR, otimizado, muito usado na indústria |
| **SQLite** | Banco leve, sem necessidade de servidor, perfeito para protótipos |
| **Tkinter** | Biblioteca padrão Python, não requer instalações extras |
| **TailwindCSS** | CSS utility-first, desenvolvimento rápido, design consistente |

### 3. **Boas Práticas Implementadas**

```python
# Logging Estruturado
logger.info("Operação executada", extra={
    "user_id": 123,
    "operation": "query",
    "duration_ms": 45
})

# Gerenciamento de Contexto
with db_manager.session() as session:
    # Conexão é fechada automaticamente
    pass

# Type Hints (Python)
def get_stats() -> Dict[str, Any]:
    return {"total": 100}

# Async/Await (Performance)
async def fetch_data():
    data = await db.query()
    return data
```

### 4. **Segurança**

```python
# Proteção contra SQL Injection
# MAU (vulnerável):
query = f"SELECT * FROM users WHERE id = {user_input}"

# BOM (seguro):
query = text("SELECT * FROM users WHERE id = :id")
session.execute(query, {"id": user_input})

# CORS configurado corretamente
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3002"],  # Apenas origem confiável
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 5. **Performance**

```python
# Indexação do banco
class DadosDAC(Base):
    __tablename__ = 'dados_dac'
    
    id = Column(Integer, primary_key=True, index=True)  # Index automático
    estado = Column(String, index=True)  # Index para filtros
    cidade = Column(String, index=True)  # Index para buscas

# Cache de queries
from functools import lru_cache

@lru_cache(maxsize=128)
def get_estados():
    return db.query(Estado).all()  # Cached!

# Paginação
def get_dados(page=1, per_page=50):
    offset = (page - 1) * per_page
    return db.query(DadosDAC).limit(per_page).offset(offset).all()
```

---

## 📚 Glossário Técnico

| Termo | Significado |
|-------|------------|
| **API REST** | Interface de comunicação entre sistemas usando HTTP |
| **ORM** | Object-Relational Mapping - traduz objetos para SQL |
| **ASGI** | Async Server Gateway Interface - padrão para apps Python assíncronas |
| **SSR** | Server-Side Rendering - renderização no servidor |
| **CORS** | Cross-Origin Resource Sharing - segurança HTTP |
| **Middleware** | Camada intermediária que processa requisições |
| **Callback** | Função executada em resposta a um evento |
| **Hook** | Função especial do React (useState, useEffect, etc.) |
| **ORM Query** | Consulta ao banco usando objetos ao invés de SQL |
| **Virtual Environment** | Ambiente Python isolado com dependências próprias |

---

## 📞 Suporte

**Autor:** Alejandro Alexandre  
**RA:** 197890  
**Curso:** Análise e Desenvolvimento de Sistemas  
**Ano:** 2025  

**Repositório:** DAC_2025  
**Branch:** main  

---

## ✅ Checklist de Apresentação para o Professor

- [ ] Demonstrar inicialização da versão web
- [ ] Explicar arquitetura cliente-servidor
- [ ] Mostrar comunicação Frontend ↔ Backend via DevTools
- [ ] Demonstrar inicialização da versão desktop
- [ ] Explicar diferenças arquiteturais
- [ ] Mostrar banco de dados (DB Browser for SQLite)
- [ ] Demonstrar logs estruturados
- [ ] Explicar escolhas tecnológicas
- [ ] Apresentar código-fonte organizado
- [ ] Mostrar documentação gerada (Swagger)

---

**Última atualização:** 04 de novembro de 2025  
**Versão do documento:** 1.0  
**Status:** ✅ Completo e testado
