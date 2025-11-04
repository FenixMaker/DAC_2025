# 📁 Estrutura do Projeto DAC - Organização Completa

**Sistema DAC - Digital Analysis and Control**  
**Autor:** Alejandro Alexandre (RA: 197890)  
**Data de Organização:** 04 de novembro de 2025  
**Versão:** 1.0.0

---

## 🎯 Princípios de Organização

### 1. **Separação de Responsabilidades**
- Scripts de setup separados dos scripts de execução
- Documentação organizada por propósito
- Código fonte isolado em módulos específicos

### 2. **Facilidade de Navegação**
- Atalhos convenientes na raiz do projeto
- Índice de documentação centralizado
- Estrutura de pastas intuitiva

### 3. **Boas Práticas**
- `.gitignore` completo
- Ambiente virtual isolado
- Configurações separadas do código

---

## 📂 Estrutura Detalhada

```
DAC_2025/                                 # 🏠 RAIZ DO PROJETO
│
├─── 📄 README.md                         # Visão geral do projeto
├─── 📄 CONTRIBUTING.md                   # Guia de contribuição
├─── 📄 SECURITY.md                       # Política de segurança
├─── 📄 .gitignore                        # Arquivos ignorados pelo Git
│
├─── 📄 setup.bat                         # ✨ Atalho: Setup automático (BAT)
├─── 📄 setup.ps1                         # ✨ Atalho: Setup automático (PowerShell)
│
│    # Os atalhos acima apontam para scripts/setup/
│
├─── 📁 docs/                             # 📚 DOCUMENTAÇÃO CENTRALIZADA
│    │
│    ├─── 📄 INDICE_DOCUMENTACAO.md      # Índice completo da documentação
│    ├─── 📄 DOCUMENTACAO_GERAL_PROJETO_DAC.md  # Doc técnica geral
│    │
│    ├─── 📁 guias/                       # Guias práticos de uso
│    │    ├─── 📄 INSTALACAO_RAPIDA.md   # Como instalar em 5 minutos
│    │    └─── 📄 MANUAL_EXECUCAO.md     # Como executar (detalhado)
│    │
│    └─── 📁 relatorios/                  # Relatórios e análises
│         ├─── 📄 TESTE_VERSOES.md       # Testes funcionais realizados
│         └─── 📄 SETUP_AUTOMATICO_RESUMO.md  # Resumo do sistema de setup
│
├─── 📁 scripts/                          # 🔧 SCRIPTS DE AUTOMAÇÃO
│    │
│    ├─── 📁 setup/                       # Scripts de configuração inicial
│    │    ├─── 📄 setup.bat              # Script de setup (Windows BAT)
│    │    └─── 📄 setup.ps1              # Script de setup (PowerShell)
│    │
│    └─── 📁 inicializacao/               # Scripts para iniciar o sistema
│         ├─── 📄 start-web.ps1          # Inicia versão web
│         ├─── 📄 Iniciar-Web.bat        # (gerado automaticamente)
│         ├─── 📄 Iniciar-Desktop.bat    # (gerado automaticamente)
│         └─── 📄 Parar-Servidores.bat   # (gerado automaticamente)
│
├─── 📁 Versão PY/                        # 🐍 APLICAÇÃO PYTHON DESKTOP
│    │
│    ├─── 📄 main.py                      # 🚀 Ponto de entrada principal
│    ├─── 📄 requirements.txt             # Dependências Python
│    ├─── 📄 README.md                    # README específico da versão PY
│    ├─── 📄 CONTRIBUTING.md              # Guia de contribuição
│    │
│    ├─── 📁 src/                         # Código fonte principal
│    │    │
│    │    ├─── 📄 __init__.py
│    │    │
│    │    ├─── 📁 database/               # Gerenciamento de banco de dados
│    │    │    ├─── __init__.py
│    │    │    ├─── database_manager.py
│    │    │    ├─── models.py            # Modelos ORM
│    │    │    ├─── estatisticas_models.py
│    │    │    └─── optimized_queries.py
│    │    │
│    │    ├─── 📁 modules/                # Módulos de processamento
│    │    │    ├─── __init__.py
│    │    │    ├─── data_importer.py     # Importação de dados
│    │    │    ├─── image_processor.py   # Processamento de imagens
│    │    │    ├─── pdf_processor.py     # Processamento de PDF
│    │    │    ├─── query_engine.py      # Motor de consultas
│    │    │    └─── importador_dados_dac.py
│    │    │
│    │    ├─── 📁 ui/                     # Interface Tkinter
│    │    │    ├─── __init__.py
│    │    │    ├─── main_window.py       # Janela principal
│    │    │    ├─── components.py        # Componentes reutilizáveis
│    │    │    ├─── db_status_window.py  # Status do banco
│    │    │    └─── icons.py             # Ícones e recursos visuais
│    │    │
│    │    └─── 📁 utils/                  # Utilitários
│    │         ├─── __init__.py
│    │         ├─── logger.py            # Sistema de logs
│    │         └─── validators.py        # Validadores
│    │
│    ├─── 📁 data/                        # Dados locais
│    │    ├─── 📄 dac_database.db        # Banco SQLite (gerado)
│    │    └─── 📄 db_integrity_report.json
│    │
│    ├─── 📁 logs/                        # Logs da aplicação
│    │    ├─── 📄 dac_structured_20251031.json
│    │    └─── 📄 dac_structured_20251101.json
│    │
│    ├─── 📁 web/                         # Backend Web (FastAPI)
│    │    └─── 📁 backend/
│    │         ├─── 📄 __init__.py
│    │         ├─── 📄 requirements.txt  # Dependências do backend
│    │         │
│    │         └─── 📁 app/               # Aplicação FastAPI
│    │              ├─── 📄 main.py      # Ponto de entrada
│    │              ├─── 📁 routes/      # Rotas da API
│    │              ├─── 📁 services/    # Serviços de negócio
│    │              └─── 📁 models/      # Modelos de dados
│    │
│    ├─── 📁 tests/                       # Testes automatizados
│    │    ├─── 📄 __init__.py
│    │    ├─── 📁 unit/                  # Testes unitários
│    │    ├─── 📁 integration/           # Testes de integração
│    │    ├─── 📁 performance/           # Testes de performance
│    │    ├─── 📁 fixtures/              # Fixtures de teste
│    │    └─── 📁 utils/                 # Utilitários de teste
│    │
│    └─── 📁 recursos/                    # Recursos locais
│         ├─── 📁 configuracoes/
│         ├─── 📁 dados/
│         └─── 📁 imagens/
│
├─── 📁 Versão Web/                       # 🌐 APLICAÇÃO WEB (NEXT.JS)
│    │
│    ├─── 📄 package.json                 # Dependências Node.js
│    ├─── 📄 next.config.mjs              # Configuração Next.js
│    ├─── 📄 tsconfig.json                # Configuração TypeScript
│    ├─── 📄 components.json              # Configuração de componentes
│    ├─── 📄 postcss.config.mjs           # Configuração PostCSS
│    ├─── 📄 next-env.d.ts                # Types do Next.js
│    ├─── 📄 .env.local                   # Variáveis de ambiente (gerado)
│    │
│    ├─── 📁 app/                         # App Router (Next.js 13+)
│    │    ├─── 📄 globals.css            # Estilos globais
│    │    ├─── 📄 layout.tsx             # Layout raiz
│    │    ├─── 📄 page.tsx               # Página inicial (dashboard)
│    │    │
│    │    ├─── 📁 api/                   # API Routes
│    │    ├─── 📁 consultas/             # Página de consultas
│    │    ├─── 📁 relatorios/            # Página de relatórios
│    │    └─── 📁 status-banco/          # Status do banco
│    │
│    ├─── 📁 components/                  # Componentes React
│    │    ├─── 📄 charts-section.tsx
│    │    ├─── 📄 consultas-filters.tsx
│    │    ├─── 📄 consultas-table.tsx
│    │    ├─── 📄 dashboard-header.tsx
│    │    ├─── 📄 db-status.tsx
│    │    ├─── 📄 relatorios-charts.tsx
│    │    ├─── 📄 relatorios-insights.tsx
│    │    ├─── 📄 stats-cards.tsx
│    │    ├─── 📄 theme-provider.tsx
│    │    │
│    │    └─── 📁 ui/                    # Componentes UI base
│    │         ├─── button.tsx
│    │         ├─── card.tsx
│    │         ├─── table.tsx
│    │         └─── ... (40+ componentes)
│    │
│    ├─── 📁 hooks/                       # Custom React Hooks
│    │    ├─── 📄 use-mobile.ts
│    │    └─── 📄 use-toast.ts
│    │
│    ├─── 📁 lib/                         # Bibliotecas e utilitários
│    │    ├─── 📄 db.ts                  # Cliente de banco
│    │    └─── 📄 utils.ts               # Funções utilitárias
│    │
│    ├─── 📁 public/                      # Arquivos estáticos
│    │    ├─── favicon.ico
│    │    └─── images/
│    │
│    └─── 📁 styles/                      # Estilos adicionais
│         └─── 📄 globals.css
│
├─── 📁 Banco de dados/                   # 💾 BANCO COMPARTILHADO
│    ├─── 📄 dac_database.db             # SQLite principal (gerado)
│    └─── 📄 db_integrity_report.json    # Relatório de integridade
│
├─── 📁 recursos/                         # 🔧 RECURSOS GLOBAIS
│    │
│    ├─── 📁 configuracoes/               # Arquivos de configuração
│    │    ├─── 📄 cache_config.json
│    │    ├─── 📄 database_config.json
│    │    ├─── 📄 error_monitoring.json
│    │    └─── 📄 logging_config.json
│    │
│    └─── 📁 dados/                       # Dados globais
│         ├─── 📁 amostras/              # Dados de exemplo
│         │    └─── 📄 DADOS DAC 2024 -.csv
│         ├─── 📁 database/              # Backups de banco
│         └─── 📁 scripts/               # Scripts SQL
│
├─── 📁 documentacao/                     # 📖 DOCS ADICIONAIS
│    ├─── 📄 ESTRUTURA_PROJETO.md
│    ├─── 📄 OBJETIVOS.md
│    │
│    ├─── 📁 metodologia/
│    │    └─── 📄 METODOLOGIA.md
│    │
│    ├─── 📁 referencias/
│    │    └─── 📄 BIBLIOGRAFIA.md
│    │
│    └─── 📁 resultados/
│         └─── 📄 CONCLUSOES.md
│
├─── 📁 .venv/                            # ⚙️ AMBIENTE VIRTUAL PYTHON
│    │                                    # (gerado automaticamente)
│    ├─── 📁 Scripts/
│    │    ├─── python.exe
│    │    ├─── pip.exe
│    │    └─── activate.bat
│    │
│    └─── 📁 Lib/
│         └─── 📁 site-packages/         # Bibliotecas instaladas
│
├─── 📁 .git/                             # 🔀 CONTROLE DE VERSÃO GIT
│    └─── (arquivos do Git)
│
└─── 📁 .pytest_cache/                    # ⚡ CACHE DO PYTEST
     └─── (cache de testes)
```

---

## 📊 Estatísticas do Projeto

### Linhas de Código (Estimativa)

| Componente | Linguagem | Linhas |
|------------|-----------|--------|
| Versão Desktop | Python | ~5.000 |
| Backend Web | Python | ~2.000 |
| Frontend Web | TypeScript/JavaScript | ~8.000 |
| Scripts de Setup | Batch/PowerShell | ~700 |
| Documentação | Markdown | ~3.000 |
| **TOTAL** | - | **~18.700** |

### Arquivos por Tipo

| Tipo | Quantidade |
|------|------------|
| Python (.py) | ~50 |
| TypeScript (.tsx/.ts) | ~80 |
| Markdown (.md) | ~15 |
| JSON (.json) | ~10 |
| Scripts (.bat/.ps1) | ~10 |
| **TOTAL** | **~165 arquivos** |

---

## 🎯 Navegação Rápida

### Para Desenvolvedores

| Tarefa | Localização |
|--------|-------------|
| Instalar o projeto | `setup.bat` ou `setup.ps1` (raiz) |
| Código Python Desktop | `Versão PY/src/` |
| Código Backend API | `Versão PY/web/backend/app/` |
| Código Frontend | `Versão Web/app/` e `Versão Web/components/` |
| Testes | `Versão PY/tests/` |
| Configurações | `recursos/configuracoes/` |

### Para Documentação

| Tipo | Localização |
|------|-------------|
| Início Rápido | `README.md` (raiz) |
| Instalação | `docs/guias/INSTALACAO_RAPIDA.md` |
| Manual Completo | `docs/guias/MANUAL_EXECUCAO.md` |
| Índice Completo | `docs/INDICE_DOCUMENTACAO.md` |
| Relatórios | `docs/relatorios/` |

---

## 🔐 Arquivos Importantes

### Não Versionados (.gitignore)

```
.venv/                  # Ambiente virtual
node_modules/           # Dependências Node.js
*.db                    # Bancos de dados SQLite
*.log                   # Logs
__pycache__/            # Cache Python
.next/                  # Build Next.js
.env*.local             # Variáveis de ambiente
```

### Versionados

```
src/                    # Todo código fonte
docs/                   # Toda documentação
scripts/                # Scripts de automação
recursos/configuracoes/ # Configurações (sem secrets)
README.md               # Visão geral
.gitignore              # Regras do Git
```

---

## 🔄 Fluxos de Trabalho

### 1. Novo Desenvolvedor

```
1. Clone: git clone https://github.com/FenixMaker/DAC_2025.git
2. Entre: cd DAC_2025
3. Setup: setup.bat
4. Leia: docs/INDICE_DOCUMENTACAO.md
5. Code: Versão PY/src/ ou Versão Web/
```

### 2. Executar o Sistema

```
# Versão Web
Iniciar-Web.bat

# Versão Desktop
Iniciar-Desktop.bat
```

### 3. Fazer Alterações

```
1. Crie branch: git checkout -b feature/nova-funcionalidade
2. Faça mudanças no código
3. Atualize documentação relacionada
4. Teste: python -m pytest (se Python)
5. Commit: git commit -m "Descrição"
6. Push: git push origin feature/nova-funcionalidade
7. PR: Crie Pull Request
```

---

## 📝 Convenções de Nomenclatura

### Pastas
- **snake_case** para pastas Python: `src/`, `utils/`
- **PascalCase** para pastas principais: `Versão PY/`, `Versão Web/`
- **kebab-case** para pastas web: `status-banco/`

### Arquivos
- **snake_case.py** - Arquivos Python
- **PascalCase.tsx** - Componentes React
- **kebab-case.tsx** - Arquivos TypeScript utilitários
- **UPPER_CASE.md** - Documentação importante
- **kebab-case.md** - Documentação secundária

### Código
- **PascalCase** - Classes: `DatabaseManager`
- **snake_case** - Funções/variáveis Python: `get_user_data()`
- **camelCase** - Funções/variáveis TypeScript: `getUserData()`
- **UPPER_SNAKE_CASE** - Constantes: `API_BASE_URL`

---

## 🎓 Benefícios da Organização

### 1. **Manutenibilidade**
- ✅ Fácil encontrar arquivos
- ✅ Estrutura lógica e previsível
- ✅ Separação clara de responsabilidades

### 2. **Colaboração**
- ✅ Novos desenvolvedores entendem rapidamente
- ✅ Documentação centralizada e acessível
- ✅ Padrões consistentes

### 3. **Escalabilidade**
- ✅ Fácil adicionar novos módulos
- ✅ Estrutura suporta crescimento
- ✅ Separação permite trabalho paralelo

### 4. **Profissionalismo**
- ✅ Segue padrões da indústria
- ✅ Pronto para apresentação
- ✅ Facilita auditoria e revisão

---

**Organizado por:** Alejandro Alexandre (RA: 197890)  
**Data:** 04 de novembro de 2025  
**Status:** ✅ Estrutura completa e documentada
