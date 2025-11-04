# 📚 Índice de Documentação - Sistema DAC

**Sistema DAC - Digital Analysis and Control**  
**Autor:** Alejandro Alexandre (RA: 197890)  
**Última atualização:** 04 de novembro de 2025

---

## 📖 Estrutura da Documentação

### 🚀 Início Rápido

| Documento | Descrição | Localização |
|-----------|-----------|-------------|
| **README.md** | Visão geral do projeto e início rápido | `/README.md` |
| **Instalação Rápida** | Guia de instalação em 5 minutos | `/docs/guias/INSTALACAO_RAPIDA.md` |
| **Manual de Execução** | Guia completo de como executar | `/docs/guias/MANUAL_EXECUCAO.md` |

### 📋 Documentação Técnica

| Documento | Descrição | Localização |
|-----------|-----------|-------------|
| **Documentação Geral** | Visão técnica completa do projeto | `/docs/DOCUMENTACAO_GERAL_PROJETO_DAC.md` |
| **Contributing** | Guia para contribuidores | `/CONTRIBUTING.md` |
| **Security** | Política de segurança | `/SECURITY.md` |

### 📊 Relatórios e Testes

| Documento | Descrição | Localização |
|-----------|-----------|-------------|
| **Teste de Versões** | Relatório de testes funcionais | `/docs/relatorios/TESTE_VERSOES.md` |
| **Setup Automático** | Resumo do sistema de instalação | `/docs/relatorios/SETUP_AUTOMATICO_RESUMO.md` |

### 📁 Documentação Adicional

| Pasta | Conteúdo | Localização |
|-------|----------|-------------|
| **documentacao/** | Estrutura, objetivos, metodologia | `/documentacao/` |
| **recursos/** | Configurações e dados | `/recursos/` |

---

## 🗂️ Estrutura do Projeto

```
DAC_2025/
│
├─── 📄 README.md                    # Visão geral e início rápido
├─── 📄 CONTRIBUTING.md              # Guia de contribuição
├─── 📄 SECURITY.md                  # Política de segurança
├─── 📄 .gitignore                   # Arquivos ignorados pelo Git
│
├─── 📄 setup.bat                    # Atalho para instalação (BAT)
├─── 📄 setup.ps1                    # Atalho para instalação (PowerShell)
├─── 📄 Iniciar-Web.bat              # ✨ NOVO! Inicia versão web
├─── 📄 Iniciar-Desktop.bat          # ✨ NOVO! Inicia versão desktop
│
├─── 📁 docs/                        # 📚 DOCUMENTAÇÃO PRINCIPAL
│    ├─── 📄 DOCUMENTACAO_GERAL_PROJETO_DAC.md
│    ├─── 📄 INDICE_DOCUMENTACAO.md  # Este arquivo
│    ├─── 📄 ESTRUTURA_DETALHADA.md
│    ├─── � ORGANIZACAO_RESUMO.md
│    ├─── 📄 ARVORE_VISUAL.md
│    ├─── 📄 SUMARIO_EXECUTIVO.md
│    │
│    ├─── �📁 guias/                  # Guias de uso
│    │    ├─── INSTALACAO_RAPIDA.md
│    │    ├─── MANUAL_EXECUCAO.md
│    │    └─── CRIAR_EXECUTAVEIS.md  # ✨ NOVO!
│    │
│    └─── 📁 relatorios/             # Relatórios técnicos
│         ├─── TESTE_VERSOES.md
│         ├─── SETUP_AUTOMATICO_RESUMO.md
│         └─── EXECUTAVEIS_CRIADOS.md # ✨ NOVO!
│
├─── 📁 scripts/                     # 🔧 SCRIPTS DE AUTOMAÇÃO
│    ├─── 📁 setup/                  # Scripts de configuração
│    │    ├─── setup.bat
│    │    └─── setup.ps1
│    │
│    ├─── 📁 build/                  # ✨ NOVO! Scripts de build
│    │    └─── build_executables.bat # Compila .py → .exe
│    │
│    └─── 📁 inicializacao/          # Scripts de inicialização
│         ├─── start-web.ps1
│         ├─── launcher_web.py       # ✨ NOVO!
│         ├─── launcher_desktop.py   # ✨ NOVO!
│         ├─── Iniciar-Web.vbs
│         └─── Iniciar-Desktop.vbs
│
├─── 📁 Versão PY/                   # 🐍 APLICAÇÃO PYTHON DESKTOP
│    ├─── main.py                    # Ponto de entrada
│    ├─── requirements.txt           # Dependências Python
│    │
│    ├─── src/                       # Código fonte
│    │    ├─── database/             # Gerenciamento de BD
│    │    ├─── modules/              # Módulos de processamento
│    │    ├─── ui/                   # Interface Tkinter
│    │    └─── utils/                # Utilitários
│    │
│    ├─── data/                      # Dados e banco local
│    ├─── logs/                      # Logs da aplicação
│    │
│    ├─── web/                       # Backend FastAPI
│    │    └─── backend/
│    │         ├─── app/
│    │         └─── requirements.txt
│    │
│    └─── tests/                     # Testes automatizados
│         ├─── unit/
│         ├─── integration/
│         └─── performance/
│
├─── 📁 Versão Web/                  # 🌐 APLICAÇÃO WEB (NEXT.JS)
│    ├─── package.json               # Dependências Node.js
│    ├─── next.config.mjs            # Configuração Next.js
│    │
│    ├─── app/                       # Páginas e rotas
│    ├─── components/                # Componentes React
│    ├─── lib/                       # Utilitários
│    └─── public/                    # Arquivos estáticos
│
├─── 📁 Banco de dados/              # 💾 BANCO DE DADOS COMPARTILHADO
│    └─── dac_database.db
│
├─── 📁 recursos/                    # 🔧 RECURSOS E CONFIGURAÇÕES
│    ├─── configuracoes/             # Arquivos de configuração JSON
│    └─── dados/                     # Dados e amostras
│
├─── 📁 documentacao/                # 📖 DOCUMENTAÇÃO ADICIONAL
│    ├─── ESTRUTURA_PROJETO.md
│    ├─── OBJETIVOS.md
│    ├─── metodologia/
│    ├─── referencias/
│    └─── resultados/
│
└─── 📁 .venv/                       # ⚙️ AMBIENTE VIRTUAL PYTHON
     └─── Scripts/
          └─── python.exe
```

---

## 🎯 Fluxo de Documentação por Tipo de Usuário

### 👨‍💻 Desenvolvedor Novo

1. **Começar com:** [`README.md`](/README.md)
2. **Instalar:** [`docs/guias/INSTALACAO_RAPIDA.md`](/docs/guias/INSTALACAO_RAPIDA.md)
3. **Executar:** [`docs/guias/MANUAL_EXECUCAO.md`](/docs/guias/MANUAL_EXECUCAO.md)
4. **Contribuir:** [`CONTRIBUTING.md`](/CONTRIBUTING.md)

### 👨‍🏫 Professor/Avaliador

1. **Visão Geral:** [`README.md`](/README.md)
2. **Documentação Técnica:** [`docs/DOCUMENTACAO_GERAL_PROJETO_DAC.md`](/docs/DOCUMENTACAO_GERAL_PROJETO_DAC.md)
3. **Testes Realizados:** [`docs/relatorios/TESTE_VERSOES.md`](/docs/relatorios/TESTE_VERSOES.md)
4. **Sistema de Setup:** [`docs/relatorios/SETUP_AUTOMATICO_RESUMO.md`](/docs/relatorios/SETUP_AUTOMATICO_RESUMO.md)

### 👥 Usuário Final

1. **Instalação:** [`docs/guias/INSTALACAO_RAPIDA.md`](/docs/guias/INSTALACAO_RAPIDA.md)
2. **Como Usar:** [`docs/guias/MANUAL_EXECUCAO.md`](/docs/guias/MANUAL_EXECUCAO.md)

### 🔐 Security Researcher

1. **Política de Segurança:** [`SECURITY.md`](/SECURITY.md)

---

## 📝 Convenções de Documentação

### Formato dos Documentos
- **Markdown (.md):** Todos os documentos usam Markdown
- **Encoding:** UTF-8
- **Estilo:** Cabeçalhos hierárquicos, listas, tabelas, código

### Estrutura Padrão de um Documento

```markdown
# Título do Documento

**Autor:** Alejandro Alexandre (RA: 197890)
**Data:** DD/MM/AAAA
**Versão:** X.Y.Z

---

## Seção 1
Conteúdo...

## Seção 2
Conteúdo...

---

**Última atualização:** DD/MM/AAAA
```

### Emojis Utilizados

| Emoji | Significado |
|-------|-------------|
| 📚 | Documentação |
| 🚀 | Início rápido / Execução |
| 🔧 | Configuração / Scripts |
| 🐍 | Python |
| 🌐 | Web / Internet |
| 💾 | Banco de dados |
| 📊 | Relatórios / Análises |
| ✅ | Sucesso / Completo |
| ⚠️ | Aviso / Atenção |
| 🎯 | Objetivo / Meta |
| 👨‍💻 | Desenvolvedor |
| 📁 | Pasta / Diretório |
| 📄 | Arquivo |

---

## 🔄 Atualização de Documentação

### Responsabilidades

- **Autor:** Manter documentação atualizada com o código
- **Contribuidores:** Atualizar docs relacionadas às suas mudanças
- **Revisores:** Verificar consistência entre código e documentação

### Processo de Atualização

1. **Mudança no código** → Atualizar documentação relacionada
2. **Nova funcionalidade** → Criar/atualizar guia de uso
3. **Bug fix** → Atualizar troubleshooting se aplicável
4. **Release** → Atualizar changelog e versões

---

## 📞 Suporte e Contato

**Autor:** Alejandro Alexandre  
**RA:** 197890  
**Curso:** Análise e Desenvolvimento de Sistemas  
**Ano:** 2025  

**Repositório:** [DAC_2025](https://github.com/FenixMaker/DAC_2025)  
**Branch Principal:** main

---

## 🏷️ Glossário de Documentação

| Termo | Significado |
|-------|-------------|
| **Guia** | Documento passo a passo para realizar uma tarefa |
| **Manual** | Documentação completa e detalhada |
| **Relatório** | Documento sobre testes, análises ou resultados |
| **README** | Primeiro documento a ler (visão geral) |
| **CONTRIBUTING** | Regras para contribuir com o projeto |
| **SECURITY** | Políticas e práticas de segurança |
| **Changelog** | Histórico de mudanças do projeto |

---

**Última atualização:** 04/11/2025  
**Versão da Documentação:** 1.0.0  
**Status:** ✅ Completo e organizado
