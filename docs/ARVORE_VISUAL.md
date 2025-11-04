# 📁 Estrutura do Projeto - Visualização Rápida

```
DAC_2025/
│
│   ══════════════════════════════════════════════════════════════
│   📌 ARQUIVOS PRINCIPAIS (Raiz)
│   ══════════════════════════════════════════════════════════════
│
├── 📄 README.md                           ← Comece aqui!
├── 📄 CONTRIBUTING.md                     ← Como contribuir
├── 📄 SECURITY.md                         ← Política de segurança
├── 📄 .gitignore                          ← Arquivos ignorados
│
├── 📄 setup.bat                           ← ⚡ INSTALAÇÃO (Windows)
├── 📄 setup.ps1                           ← ⚡ INSTALAÇÃO (PowerShell)
│
│   ══════════════════════════════════════════════════════════════
│   📚 DOCUMENTAÇÃO (docs/)
│   ══════════════════════════════════════════════════════════════
│
├── 📁 docs/
│   │
│   ├── 📄 INDICE_DOCUMENTACAO.md         ← 🗺️ Mapa da documentação
│   ├── 📄 ESTRUTURA_DETALHADA.md         ← 📋 Estrutura completa
│   ├── 📄 ORGANIZACAO_RESUMO.md          ← ✅ Resumo da organização
│   ├── 📄 DOCUMENTACAO_GERAL_PROJETO_DAC.md
│   │
│   ├── 📁 guias/                         ← 📖 GUIAS PRÁTICOS
│   │   ├── 📄 INSTALACAO_RAPIDA.md      ← Como instalar (5 min)
│   │   └── 📄 MANUAL_EXECUCAO.md        ← Como executar (completo)
│   │
│   └── 📁 relatorios/                    ← 📊 RELATÓRIOS TÉCNICOS
│       ├── 📄 TESTE_VERSOES.md          ← Testes realizados
│       └── 📄 SETUP_AUTOMATICO_RESUMO.md ← Sistema de setup
│
│   ══════════════════════════════════════════════════════════════
│   🔧 SCRIPTS DE AUTOMAÇÃO (scripts/)
│   ══════════════════════════════════════════════════════════════
│
├── 📁 scripts/
│   │
│   ├── 📁 setup/                         ← 🛠️ INSTALAÇÃO
│   │   ├── 📄 setup.bat                 ← Setup completo (BAT)
│   │   └── 📄 setup.ps1                 ← Setup completo (PowerShell)
│   │
│   └── 📁 inicializacao/                 ← 🚀 EXECUÇÃO
│       ├── 📄 start-web.ps1             ← Inicia versão web
│       └── 📄 ... (gerados pelo setup)
│
│   ══════════════════════════════════════════════════════════════
│   🐍 VERSÃO PYTHON DESKTOP (Versão PY/)
│   ══════════════════════════════════════════════════════════════
│
├── 📁 Versão PY/
│   ├── 📄 main.py                        ← 🚀 Iniciar aqui!
│   ├── 📄 requirements.txt               ← Dependências
│   │
│   ├── 📁 src/                           ← Código fonte
│   │   ├── 📁 database/                 ← Banco de dados
│   │   ├── 📁 modules/                  ← Processamento
│   │   ├── 📁 ui/                       ← Interface Tkinter
│   │   └── 📁 utils/                    ← Utilitários
│   │
│   ├── 📁 web/backend/                   ← Backend FastAPI
│   ├── 📁 tests/                         ← Testes
│   ├── 📁 data/                          ← Dados locais
│   └── 📁 logs/                          ← Logs
│
│   ══════════════════════════════════════════════════════════════
│   🌐 VERSÃO WEB (Versão Web/)
│   ══════════════════════════════════════════════════════════════
│
├── 📁 Versão Web/
│   ├── 📄 package.json                   ← Dependências Node.js
│   ├── 📄 next.config.mjs                ← Config Next.js
│   │
│   ├── 📁 app/                           ← Páginas (Next.js 13+)
│   ├── 📁 components/                    ← Componentes React
│   ├── 📁 lib/                           ← Bibliotecas
│   └── 📁 public/                        ← Arquivos estáticos
│
│   ══════════════════════════════════════════════════════════════
│   💾 DADOS E RECURSOS
│   ══════════════════════════════════════════════════════════════
│
├── 📁 Banco de dados/                    ← BD compartilhado
├── 📁 recursos/                          ← Configs e dados
│   ├── 📁 configuracoes/
│   └── 📁 dados/
│
├── 📁 documentacao/                      ← Docs adicionais
│   ├── ESTRUTURA_PROJETO.md
│   ├── OBJETIVOS.md
│   └── ... (metodologia, refs, etc.)
│
│   ══════════════════════════════════════════════════════════════
│   ⚙️ GERADO AUTOMATICAMENTE
│   ══════════════════════════════════════════════════════════════
│
├── 📁 .venv/                             ← Ambiente virtual Python
├── 📁 .git/                              ← Controle de versão
└── 📁 .pytest_cache/                     ← Cache de testes
```

---

## 🎯 Navegação Rápida

### 🚀 Quero começar agora!
1. Leia: [`README.md`](../README.md)
2. Execute: `setup.bat`
3. Use: `Iniciar-Web.bat` ou `Iniciar-Desktop.bat`

### 📚 Quero entender o projeto
1. Índice: [`docs/INDICE_DOCUMENTACAO.md`](INDICE_DOCUMENTACAO.md)
2. Estrutura: [`docs/ESTRUTURA_DETALHADA.md`](ESTRUTURA_DETALHADA.md)
3. Docs Geral: [`docs/DOCUMENTACAO_GERAL_PROJETO_DAC.md`](DOCUMENTACAO_GERAL_PROJETO_DAC.md)

### 🔧 Quero instalar
- Guia rápido: [`docs/guias/INSTALACAO_RAPIDA.md`](guias/INSTALACAO_RAPIDA.md)

### 📖 Quero usar
- Manual: [`docs/guias/MANUAL_EXECUCAO.md`](guias/MANUAL_EXECUCAO.md)

### 👨‍💻 Quero contribuir
- Guia: [`CONTRIBUTING.md`](../CONTRIBUTING.md)

### 📊 Quero ver testes/relatórios
- Testes: [`docs/relatorios/TESTE_VERSOES.md`](relatorios/TESTE_VERSOES.md)
- Setup: [`docs/relatorios/SETUP_AUTOMATICO_RESUMO.md`](relatorios/SETUP_AUTOMATICO_RESUMO.md)

---

## 📊 Estatísticas

- **Total de arquivos:** ~165
- **Linhas de código:** ~18.700
- **Documentos .md:** 15+
- **Scripts:** 10+
- **Componentes React:** 80+
- **Módulos Python:** 50+

---

**Criado por:** Alejandro Alexandre (RA: 197890)  
**Data:** 04/11/2025  
**Versão:** 1.0.0
