# 🚀 Guia de Instalação Rápida - Sistema DAC

**Autor:** Alejandro Alexandre (RA: 197890)  
**Sistema:** DAC - Digital Analysis and Control  
**Versão:** 1.0.0

---

## 📦 Instalação Automática (Recomendado)

### Para Usuários Windows

Após clonar o repositório do GitHub, execute **UM** dos seguintes scripts:

#### Opção 1: Script BAT (Compatível com todos os Windows)

```cmd
setup.bat
```

**Como executar:**
1. Clique duas vezes no arquivo `setup.bat`
2. Aguarde a instalação completa
3. Escolha se deseja iniciar o sistema imediatamente

#### Opção 2: Script PowerShell (Recomendado - Mais recursos)

```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
```

**Como executar:**
1. Clique com botão direito no arquivo `setup.ps1`
2. Selecione "Executar com PowerShell"
3. Aguarde a instalação completa
4. Escolha se deseja iniciar o sistema imediatamente

---

## 🔧 O que o Script de Setup Faz?

### Etapa 1: Verificação de Pré-requisitos ✅
- Verifica se Python 3.13+ está instalado
- Verifica se Node.js 18+ está instalado
- Verifica se npm está disponível
- Verifica se pip está disponível

### Etapa 2: Ambiente Virtual Python 🐍
- Cria ambiente virtual isolado em `.venv/`
- Evita conflitos com outros projetos Python
- Garante versões corretas das bibliotecas

### Etapa 3: Dependências Python 📚
- Instala todas as bibliotecas necessárias:
  - pandas, numpy (processamento de dados)
  - matplotlib, seaborn (visualização)
  - sqlalchemy (banco de dados)
  - fastapi, uvicorn (web backend)
  - opencv, pillow (processamento de imagens)
  - E muito mais...

### Etapa 4: Dependências Node.js 📦
- Instala Next.js 16 e React 19
- Instala componentes UI (Radix UI)
- Instala TailwindCSS
- Instala bibliotecas de gráficos (Recharts)
- Total: ~269 pacotes

### Etapa 5: Configuração Final ⚙️
- Cria diretórios necessários
- Cria arquivo de configuração `.env.local`
- Cria scripts de atalho:
  - `Iniciar-Web.bat` / `Iniciar-Web.ps1`
  - `Iniciar-Desktop.bat` / `Iniciar-Desktop.ps1`
  - `Parar-Servidores.bat` / `Parar-Servidores.ps1`

---

## ⚡ Após a Instalação

### Scripts Criados Automaticamente

#### 1. Iniciar Versão Web

**Windows (BAT):**
```cmd
Iniciar-Web.bat
```

**Windows (PowerShell):**
```powershell
.\Iniciar-Web.ps1
```

**O que faz:**
- Inicia backend FastAPI na porta 8000
- Inicia frontend Next.js na porta 3002
- Abre navegador automaticamente em http://localhost:3002

#### 2. Iniciar Versão Desktop

**Windows (BAT):**
```cmd
Iniciar-Desktop.bat
```

**Windows (PowerShell):**
```powershell
.\Iniciar-Desktop.ps1
```

**O que faz:**
- Inicia aplicação Python com interface Tkinter
- Abre janela automaticamente

#### 3. Parar Servidores

**Windows (BAT):**
```cmd
Parar-Servidores.bat
```

**Windows (PowerShell):**
```powershell
.\Parar-Servidores.ps1
```

**O que faz:**
- Encerra processos na porta 8000 (backend)
- Encerra processos na porta 3002 (frontend)
- Limpa recursos

---

## 📋 Pré-requisitos (Instalar ANTES do Setup)

### 1. Python 3.13 ou superior

**Download:** https://www.python.org/downloads/

**Importante durante a instalação:**
- ✅ Marque a opção "Add Python to PATH"
- ✅ Marque "Install pip"

**Verificar instalação:**
```cmd
python --version
```

### 2. Node.js 18 ou superior

**Download:** https://nodejs.org/

**Recomendado:** Instalar a versão LTS (Long Term Support)

**Verificar instalação:**
```cmd
node --version
npm --version
```

### 3. Git (Para clonar o repositório)

**Download:** https://git-scm.com/downloads

**Verificar instalação:**
```cmd
git --version
```

---

## 🌐 Clonando do GitHub

### Passo 1: Clonar Repositório

```bash
git clone https://github.com/FenixMaker/DAC_2025.git
cd DAC_2025
```

### Passo 2: Executar Setup

```cmd
setup.bat
```

**OU**

```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1
```

### Passo 3: Aguardar Instalação

A instalação pode levar de **5 a 15 minutos** dependendo da velocidade da internet e do computador.

**Progresso esperado:**
```
[1/5] Verificando pré-requisitos...     (30 segundos)
[2/5] Criando ambiente virtual...       (1 minuto)
[3/5] Instalando deps Python...         (3-5 minutos)
[4/5] Instalando deps Node.js...        (5-10 minutos)
[5/5] Configurando estrutura...         (30 segundos)
```

### Passo 4: Usar o Sistema

Após a instalação, execute:

**Versão Web:**
```cmd
Iniciar-Web.bat
```

**Versão Desktop:**
```cmd
Iniciar-Desktop.bat
```

---

## 🔍 Troubleshooting

### Problema: "Python não encontrado"

**Solução:**
1. Instale Python de https://www.python.org/downloads/
2. Durante instalação, marque "Add Python to PATH"
3. Reinicie o terminal/prompt
4. Execute `setup.bat` novamente

### Problema: "Node.js não encontrado"

**Solução:**
1. Instale Node.js de https://nodejs.org/
2. Reinicie o terminal/prompt
3. Execute `setup.bat` novamente

### Problema: "Falha ao instalar dependências"

**Solução 1 - Limpar cache:**
```cmd
# Python
.\.venv\Scripts\python.exe -m pip cache purge

# Node.js
cd "Versão Web"
npm cache clean --force
cd ..
```

**Solução 2 - Reinstalar:**
```cmd
# Deletar pastas
rmdir /s /q .venv
rmdir /s /q "Versão Web\node_modules"

# Executar setup novamente
setup.bat
```

### Problema: "Porta já em uso"

**Solução:**
```cmd
# Parar servidores existentes
Parar-Servidores.bat

# Ou manualmente
netstat -ano | findstr :8000
taskkill /F /PID [número_do_PID]

netstat -ano | findstr :3002
taskkill /F /PID [número_do_PID]
```

### Problema: "Execution Policy" (PowerShell)

**Solução:**
```powershell
# Opção 1: Bypass temporário
powershell -ExecutionPolicy Bypass -File setup.ps1

# Opção 2: Usar o .bat ao invés
setup.bat
```

---

## 📊 Estrutura Após Instalação

```
DAC_2025/
├── 📁 .venv/                    # Ambiente virtual Python (CRIADO)
│   ├── Scripts/
│   │   └── python.exe
│   └── Lib/
│
├── 📁 Versão Web/
│   ├── 📁 node_modules/         # Dependências Node.js (CRIADO)
│   ├── .env.local               # Configurações (CRIADO)
│   └── ...
│
├── 📁 Versão PY/
│   ├── 📁 data/                 # Banco de dados (CRIADO)
│   ├── 📁 logs/                 # Logs da aplicação (CRIADO)
│   └── ...
│
├── 📁 Banco de dados/           # Banco compartilhado (CRIADO)
│
├── setup.bat                    # Script de instalação BAT
├── setup.ps1                    # Script de instalação PowerShell
│
├── Iniciar-Web.bat              # Atalho web BAT (CRIADO)
├── Iniciar-Web.ps1              # Atalho web PS (CRIADO)
├── Iniciar-Desktop.bat          # Atalho desktop BAT (CRIADO)
├── Iniciar-Desktop.ps1          # Atalho desktop PS (CRIADO)
├── Parar-Servidores.bat         # Parar servidores BAT (CRIADO)
├── Parar-Servidores.ps1         # Parar servidores PS (CRIADO)
│
├── INSTALACAO_RAPIDA.md         # Este arquivo
├── MANUAL_EXECUCAO.md           # Manual completo
└── README.md                    # Visão geral
```

---

## ⏱️ Tempo Estimado de Instalação

| Componente | Tempo Estimado |
|------------|----------------|
| Verificação de pré-requisitos | 30 segundos |
| Criação do ambiente virtual | 1 minuto |
| Dependências Python (Desktop) | 2-3 minutos |
| Dependências Python (Backend) | 1 minuto |
| Dependências Node.js | 5-10 minutos |
| Configuração final | 30 segundos |
| **TOTAL** | **10-15 minutos** |

*Tempo pode variar de acordo com velocidade de internet e hardware*

---

## 🎯 Checklist de Instalação

- [ ] Python 3.13+ instalado
- [ ] Node.js 18+ instalado
- [ ] Git instalado
- [ ] Repositório clonado do GitHub
- [ ] `setup.bat` ou `setup.ps1` executado
- [ ] Todas as 5 etapas concluídas com sucesso
- [ ] Scripts de atalho criados
- [ ] Testado `Iniciar-Web.bat` ou `Iniciar-Desktop.bat`
- [ ] Sistema funcionando corretamente

---

## 📞 Suporte

Se encontrar problemas durante a instalação:

1. Consulte a seção [Troubleshooting](#troubleshooting) acima
2. Verifique o arquivo `MANUAL_EXECUCAO.md` para detalhes técnicos
3. Verifique os logs em `Versão PY\logs\`
4. Consulte o arquivo `README.md`

---

## 🎓 Para Apresentação Acadêmica

Este sistema de instalação automatizada demonstra:

✅ **Automação de DevOps** - Scripts de setup reduzem erro humano  
✅ **Gerenciamento de Dependências** - Ambiente isolado e reproduzível  
✅ **Experiência do Usuário** - Instalação com 1 clique  
✅ **Documentação Completa** - Guias para todos os níveis  
✅ **Boas Práticas** - Verificações de pré-requisitos e tratamento de erros  

---

**Desenvolvido por:** Alejandro Alexandre (RA: 197890)  
**Curso:** Análise e Desenvolvimento de Sistemas  
**Ano:** 2025  
**Licença:** MIT
