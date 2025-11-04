# 🔧 Guia de Criação de Executáveis (.exe)

**Sistema DAC - Transformando os launchers em arquivos .exe**

---

## 📋 Opções Disponíveis

Criamos **3 formas diferentes** de ter executáveis para iniciar o sistema:

### ✅ Opção 1: Arquivos .BAT (Já Prontos!)

**Mais Simples e Recomendada**

Arquivos criados e prontos para uso:
- `Iniciar-Web.bat` (na raiz do projeto)
- `Iniciar-Desktop.bat` (na raiz do projeto)

**Vantagens:**
- ✅ Já funcionam nativamente no Windows
- ✅ Não precisa instalar nada
- ✅ Duplo clique e funciona
- ✅ Fácil de editar se necessário

**Como usar:**
1. Duplo clique em `Iniciar-Web.bat` ou `Iniciar-Desktop.bat`
2. Pronto! 🎉

---

### ⚙️ Opção 2: PyInstaller (Conversão Automática)

**Para quem quer arquivos .exe "de verdade"**

**Pré-requisitos:**
- Python instalado
- PyInstaller instalado

**Como criar os .exe:**

1. Execute o script de build:
   ```batch
   scripts\build\build_executables.bat
   ```

2. Aguarde a compilação (pode demorar 2-5 minutos)

3. Os arquivos serão criados na raiz:
   - `Iniciar-Web.exe`
   - `Iniciar-Desktop.exe`

**Vantagens:**
- ✅ Arquivos .exe nativos
- ✅ Ícones customizáveis (futuro)
- ✅ Processo automatizado

**Desvantagens:**
- ⚠️ Demora para compilar
- ⚠️ Arquivos grandes (~15-20 MB cada)
- ⚠️ Precisa do PyInstaller

---

### 🎨 Opção 3: Bat to Exe Converter (Manual)

**Para criar .exe com interface gráfica**

**Ferramenta recomendada:**
- [Bat to Exe Converter](http://www.f2ko.de/en/b2e.php) (Grátis)
- Ou qualquer conversor de BAT/VBS para EXE

**Como fazer:**

1. Baixe e instale o Bat to Exe Converter

2. Abra o programa

3. Converta `Iniciar-Web.bat`:
   - **File to convert:** `Iniciar-Web.bat`
   - **Save as:** `Iniciar-Web.exe`
   - **Icon:** (opcional) escolha um ícone personalizado
   - **Options:** Marque "Invisible application" se quiser sem console
   - Clique em **Convert**

4. Repita para `Iniciar-Desktop.bat`

**Vantagens:**
- ✅ Interface gráfica fácil
- ✅ Adicionar ícones personalizados
- ✅ Opções de configuração visual
- ✅ Arquivos .exe pequenos

**Desvantagens:**
- ⚠️ Precisa instalar ferramenta externa
- ⚠️ Processo manual

---

## 🚀 Método Recomendado

### Para uso imediato: **Opção 1 (BAT)**
Os arquivos `.bat` já funcionam perfeitamente e são nativos do Windows!

### Para distribuição profissional: **Opção 2 (PyInstaller)**
Use o script automático `build_executables.bat`

### Para personalização visual: **Opção 3 (Conversor)**
Use ferramenta gráfica para adicionar ícones bonitos

---

## 📁 Arquivos Criados

### Na raiz do projeto:

```
DAC_2025/
├── Iniciar-Web.bat           ← Duplo clique para rodar web
├── Iniciar-Desktop.bat       ← Duplo clique para rodar desktop
├── setup.bat                 ← Instalação automática
```

### Em scripts/inicializacao/:

```
scripts/inicializacao/
├── launcher_web.py           ← Script Python para web
├── launcher_desktop.py       ← Script Python para desktop
├── Iniciar-Web.vbs          ← VBScript alternativo
├── Iniciar-Desktop.vbs      ← VBScript alternativo
├── start-web.ps1            ← PowerShell original
└── start-desktop.ps1        ← PowerShell original
```

### Em scripts/build/:

```
scripts/build/
└── build_executables.bat    ← Cria os .exe automaticamente
```

---

## 🎯 Usando os Arquivos BAT (Recomendado)

### Passo a Passo:

1. **Localize os arquivos na raiz:**
   - `Iniciar-Web.bat`
   - `Iniciar-Desktop.bat`

2. **Duplo clique no arquivo desejado:**
   - Para versão web → `Iniciar-Web.bat`
   - Para versão desktop → `Iniciar-Desktop.bat`

3. **Aguarde a inicialização:**
   - Uma janela de comando será aberta
   - O launcher verificará os pré-requisitos
   - A aplicação será iniciada automaticamente

4. **Pronto!** 🎉

---

## 🔨 Criando .EXE com PyInstaller

### Instalação do PyInstaller:

```bash
pip install pyinstaller
```

### Compilação Automática:

```batch
cd scripts\build
build_executables.bat
```

### O que acontece:

1. ✅ Verifica Python instalado
2. ✅ Instala PyInstaller (se necessário)
3. ✅ Compila `launcher_web.py` → `Iniciar-Web.exe`
4. ✅ Compila `launcher_desktop.py` → `Iniciar-Desktop.exe`
5. ✅ Copia os .exe para a raiz do projeto
6. ✅ Limpa arquivos temporários

**Tempo estimado:** 3-5 minutos

**Tamanho dos arquivos:**
- Iniciar-Web.exe: ~15-20 MB
- Iniciar-Desktop.exe: ~15-20 MB

---

## 🎨 Adicionando Ícones Personalizados

### Com PyInstaller:

Edite `build_executables.bat` e adicione:

```batch
python -m PyInstaller --onefile ^
    --windowed ^
    --name "Iniciar-Web" ^
    --icon="caminho/para/icone.ico" ^
    ...
```

### Com Bat to Exe Converter:

1. Abra o programa
2. Selecione o arquivo BAT
3. Clique em "Icon" e escolha um arquivo .ico
4. Clique em "Convert"

### Ícones recomendados:

- Web: 🌐 (ícone de globo/navegador)
- Desktop: 🖥️ (ícone de computador)

Você pode baixar ícones grátis em:
- https://icons8.com/
- https://www.iconfinder.com/
- https://www.flaticon.com/

---

## 🧪 Testando os Executáveis

### Teste 1: Arquivo BAT

```batch
# Duplo clique em Iniciar-Web.bat
# Deve abrir uma janela e iniciar o sistema
```

**Resultado esperado:**
- ✅ Janela de comando aberta
- ✅ Mensagens de inicialização
- ✅ Navegador abre automaticamente (web)
- ✅ Janela da aplicação aparece (desktop)

### Teste 2: Arquivo EXE (se compilado)

```batch
# Duplo clique em Iniciar-Web.exe
# Deve funcionar igual ao BAT
```

**Resultado esperado:**
- ✅ Mesmo comportamento do BAT
- ✅ Possível aviso do Windows Defender (normal)
- ✅ Sistema inicia normalmente

---

## ⚠️ Problemas Comuns

### "Windows protegeu seu PC"

**Causa:** Executável não assinado digitalmente

**Solução:**
1. Clique em "Mais informações"
2. Clique em "Executar assim mesmo"

Isso é normal para executáveis criados localmente.

### "Python não encontrado"

**Causa:** Python não está no PATH

**Solução:**
1. Reinstale Python marcando "Add to PATH"
2. Ou execute `setup.bat` primeiro

### "PyInstaller falhou"

**Causa:** Dependências faltando

**Solução:**
```bash
pip install --upgrade pyinstaller
```

### Executável muito grande

**Causa:** PyInstaller inclui todas as dependências

**Solução:** Normal! O .exe é standalone (não precisa de nada instalado)

---

## 📊 Comparação das Opções

| Característica | BAT | PyInstaller | Conversor |
|----------------|-----|-------------|-----------|
| **Facilidade** | ★★★★★ | ★★★☆☆ | ★★★★☆ |
| **Velocidade** | ★★★★★ | ★★☆☆☆ | ★★★★☆ |
| **Tamanho** | Mínimo | Grande | Pequeno |
| **Personalização** | Básica | Avançada | Média |
| **Ícones** | ❌ | ✅ | ✅ |
| **Nativo** | ✅ | ✅ | ✅ |
| **Precisa Python** | ✅ | ❌ | ❌ |

---

## 🎯 Recomendação Final

### Para você (desenvolvedor):
Use os arquivos **BAT** - são rápidos e funcionam perfeitamente!

### Para o professor:
Use os arquivos **BAT** - funcionam em qualquer Windows sem instalação!

### Para distribuição pública:
Compile com **PyInstaller** - arquivos .exe profissionais que funcionam sozinhos!

### Para apresentação bonita:
Use **Bat to Exe Converter** com ícones personalizados! 🎨

---

## 📝 Checklist de Uso

- [ ] Arquivos BAT criados na raiz
- [ ] Testei duplo clique no Iniciar-Web.bat
- [ ] Testei duplo clique no Iniciar-Desktop.bat
- [ ] (Opcional) Compilei os .exe com PyInstaller
- [ ] (Opcional) Adicionei ícones personalizados
- [ ] Sistema funciona perfeitamente! 🎉

---

## 🆘 Suporte

**Problema com os launchers?**

1. Verifique se executou `setup.bat` primeiro
2. Tente rodar como Administrador
3. Verifique se Python está instalado
4. Consulte a documentação em `docs/guias/`

---

<div align="center">

## ✅ Tudo Pronto!

**Os arquivos BAT já funcionam!**  
**Use-os com duplo clique! 🖱️**

*Se quiser .exe "de verdade", use o PyInstaller.*  
*Mas os BAT já fazem tudo que você precisa!* 😉

</div>
