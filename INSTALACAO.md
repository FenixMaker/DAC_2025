# 🚀 Guia Rápido de Instalação - Sistema DAC

## 📋 Pré-requisitos

Antes de executar o setup, certifique-se de ter instalado:

1. **Python 3.13+** - [Download](https://www.python.org/downloads/)
   - ⚠️ **IMPORTANTE**: Marque a opção "Add Python to PATH" durante a instalação
   
2. **Node.js 18+** - [Download](https://nodejs.org/)
   - Inclui o npm automaticamente

## 🔧 Instalação (Primeira Vez)

### Passo 1: Execute o Setup

```bash
# Clique duas vezes no arquivo:
setup.bat
```

O script irá:
- ✅ Verificar se Python e Node.js estão instalados
- ✅ Criar ambiente virtual Python em `Versão PY\.venv\`
- ✅ Instalar todas as dependências Python (Desktop + Backend)
- ✅ Instalar todas as dependências Node.js (Frontend)
- ✅ Criar scripts de atalho (Iniciar-Desktop.bat, Iniciar-Web.bat, etc.)
- ✅ Configurar estrutura de diretórios

**⏱️ Tempo estimado**: 5-10 minutos (dependendo da sua conexão)

### Passo 2: Verificar Instalação (Opcional)

```bash
# Clique duas vezes no arquivo:
Verificar-Instalacao.bat
```

Este script verifica se tudo foi instalado corretamente.

## 🎯 Como Usar

Após a instalação bem-sucedida, você pode iniciar o sistema de duas formas:

### Opção 1: Versão Desktop (Tkinter)

```bash
# Clique duas vezes no arquivo:
Iniciar-Desktop.bat
```

- Interface gráfica desktop (Windows)
- Não requer navegador
- Ideal para uso local

### Opção 2: Versão Web (Next.js + FastAPI)

```bash
# Clique duas vezes no arquivo:
Iniciar-Web.bat
```

Acesse no navegador:
- **Frontend**: http://localhost:3002
- **Backend API**: http://localhost:8000
- **Documentação API**: http://localhost:8000/docs

## 🛠️ Solução de Problemas

### ❌ Erro: "Ambiente virtual Python não criado"

**Causa**: O ambiente virtual não foi criado corretamente.

**Solução**:
```bash
1. Execute novamente: setup.bat
2. Quando perguntar se quer recriar o ambiente virtual, responda: S
```

### ❌ Erro: "Python não encontrado"

**Causa**: Python não está no PATH do sistema.

**Solução**:
```bash
1. Reinstale o Python
2. MARQUE a opção "Add Python to PATH"
3. Execute setup.bat novamente
```

### ❌ Erro: "node_modules não encontrado"

**Causa**: Dependências do frontend não foram instaladas.

**Solução**:
```bash
1. Abra o PowerShell na pasta do projeto
2. cd "Versão Web"
3. npm install --legacy-peer-deps
4. cd ..
```

### ❌ Erro: "Porta 8000 ou 3002 já está em uso"

**Causa**: Outro processo está usando essas portas.

**Solução**:
```bash
# Clique duas vezes no arquivo:
Parar-Servidores.bat
```

Depois tente iniciar novamente.

### ⚠️ Ambiente virtual corrompido (após copiar projeto)

**Causa**: O ambiente virtual Python não funciona após copiar/mover o projeto.

**Solução**:
```bash
1. Delete a pasta: Versão PY\.venv
2. Execute novamente: setup.bat
```

## 📁 Estrutura de Arquivos Importantes

```
DAC_2025/
├── setup.bat                      # ← EXECUTE PRIMEIRO
├── Verificar-Instalacao.bat       # Verifica se tudo está OK
├── Iniciar-Desktop.bat            # Inicia versão desktop
├── Iniciar-Web.bat                # Inicia versão web
├── Parar-Servidores.bat           # Para servidores web
│
├── Versão PY/
│   ├── .venv/                     # ← Ambiente virtual Python (criado pelo setup)
│   ├── main.py                    # Arquivo principal desktop
│   ├── requirements.txt           # Dependências Python
│   └── web/backend/
│       └── requirements.txt       # Dependências backend
│
└── Versão Web/
    ├── node_modules/              # ← Dependências Node.js (criado pelo setup)
    └── package.json               # Configuração do projeto
```

## 🔄 Atualizar Dependências

Se você baixar uma versão atualizada do código:

```bash
# Para Python:
cd "Versão PY"
.venv\Scripts\pip install -r requirements.txt --upgrade

# Para Node.js:
cd "Versão Web"
npm install --legacy-peer-deps
```

## 📞 Precisa de Ajuda?

1. ✅ Verifique a seção "Solução de Problemas" acima
2. ✅ Execute `Verificar-Instalacao.bat` para diagnóstico
3. ✅ Consulte a documentação completa em `MANUAL_EXECUCAO.md`
4. ✅ Abra uma issue no repositório do projeto

## ✨ Resumo de Comandos

| Ação | Comando |
|------|---------|
| **Instalar pela primeira vez** | `setup.bat` |
| **Verificar instalação** | `Verificar-Instalacao.bat` |
| **Iniciar versão desktop** | `Iniciar-Desktop.bat` |
| **Iniciar versão web** | `Iniciar-Web.bat` |
| **Parar servidores** | `Parar-Servidores.bat` |

---

**Desenvolvido por**: Alejandro Alexandre (RA: 197890)  
**Curso**: Análise e Desenvolvimento de Sistemas  
**Ano**: 2025
