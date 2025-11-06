"""
Launcher executável para a Versão Web do Sistema DAC
Inicia automaticamente o backend (FastAPI) e frontend (Next.js)
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path
import ctypes

def is_admin():
    """Verifica se está executando como administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def show_message(title, message, icon=0):
    """Mostra mensagem do Windows"""
    ctypes.windll.user32.MessageBoxW(0, message, title, icon)

def find_project_root():
    """Encontra a raiz do projeto DAC_2025"""
    current = Path(__file__).resolve().parent
    
    # Subir até encontrar a pasta raiz
    while current.name != "DAC_2025" and current.parent != current:
        current = current.parent
    
    if current.name == "DAC_2025":
        return current
    
    # Se não encontrou, tenta a partir do script
    return Path(__file__).resolve().parent.parent.parent

def check_prerequisites():
    """Verifica se os pré-requisitos estão instalados"""
    project_root = find_project_root()
    web_path = project_root / "Versão Web"
    py_path = project_root / "Versão PY"
    
    errors = []
    
    # Verifica se as pastas existem
    if not web_path.exists():
        errors.append(f"Pasta 'Versão Web' não encontrada em:\n{web_path}")
    
    if not py_path.exists():
        errors.append(f"Pasta 'Versão PY' não encontrada em:\n{py_path}")
    
    # Verifica node_modules
    if web_path.exists() and not (web_path / "node_modules").exists():
        errors.append("Dependências do Node.js não instaladas!\n\nExecute primeiro: setup.bat")
    
    # Verifica venv Python (tenta na raiz primeiro)
    venv_exists = False
    if (project_root / ".venv").exists():
        venv_exists = True
    elif py_path.exists() and (py_path / ".venv").exists():
        venv_exists = True
    
    if not venv_exists:
        errors.append("Ambiente virtual Python não criado!\n\nExecute primeiro: setup.bat")
    
    return errors

def kill_processes():
    """Mata processos anteriores nas portas 8000 e 3002"""
    try:
        # Mata processos na porta 8000 (backend)
        subprocess.run('netstat -ano | findstr ":8000" | findstr "LISTENING"', 
                      shell=True, capture_output=True, text=True)
        result = subprocess.run('for /f "tokens=5" %a in (\'netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"\') do taskkill /F /PID %a', 
                               shell=True, capture_output=True, text=True)
        
        # Mata processos na porta 3002 (frontend)
        subprocess.run('netstat -ano | findstr ":3002" | findstr "LISTENING"', 
                      shell=True, capture_output=True, text=True)
        result = subprocess.run('for /f "tokens=5" %a in (\'netstat -ano ^| findstr ":3002" ^| findstr "LISTENING"\') do taskkill /F /PID %a', 
                               shell=True, capture_output=True, text=True)
        
        time.sleep(1)
    except:
        pass  # Ignora erros se não houver processos

def start_backend(project_root):
    """Inicia o backend FastAPI"""
    backend_path = project_root / "Versão PY" / "web" / "backend"
    
    # Tenta encontrar o ambiente virtual
    venv_paths = [
        project_root / ".venv" / "Scripts" / "python.exe",  # .venv na raiz
        project_root / "Versão PY" / ".venv" / "Scripts" / "python.exe",  # .venv na Versão PY
    ]
    
    venv_python = None
    for path in venv_paths:
        if path.exists():
            venv_python = path
            break
    
    if not venv_python:
        print(f"   ⚠️  Ambiente virtual Python não encontrado!")
        print(f"   Tentando usar Python do sistema...")
        venv_python = "python"
    
    os.chdir(str(backend_path))
    
    # Inicia o backend em uma nova janela
    cmd = f'start "DAC Backend (FastAPI)" cmd /k "{venv_python}" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000'
    subprocess.Popen(cmd, shell=True)
    
    return True

def start_frontend(project_root):
    """Inicia o frontend Next.js"""
    web_path = project_root / "Versão Web"
    
    os.chdir(str(web_path))
    
    # Inicia o frontend em uma nova janela - usando dev:frontend que não tenta iniciar o backend
    cmd = 'start "DAC Frontend (Next.js)" cmd /k npm run dev:frontend'
    subprocess.Popen(cmd, shell=True)
    
    return True

def open_browser():
    """Abre o navegador após alguns segundos"""
    time.sleep(8)  # Aguarda servidores iniciarem
    webbrowser.open('http://localhost:3002')

def main():
    """Função principal"""
    try:
        # Título da janela
        ctypes.windll.kernel32.SetConsoleTitleW("🌐 Sistema DAC - Launcher Web")
        
        print("=" * 60)
        print("  🌐 Sistema DAC - Launcher Versão Web")
        print("=" * 60)
        print()
        
        # Encontra a raiz do projeto
        print("📁 Localizando projeto...")
        project_root = find_project_root()
        print(f"   ✓ Projeto encontrado: {project_root}")
        print()
        
        # Verifica pré-requisitos
        print("🔍 Verificando pré-requisitos...")
        errors = check_prerequisites()
        
        if errors:
            print("   ❌ ERROS ENCONTRADOS:\n")
            for error in errors:
                print(f"   • {error}\n")
            
            show_message(
                "Erro - Sistema DAC",
                "Pré-requisitos não atendidos!\n\n" + "\n\n".join(errors) + 
                "\n\nExecute setup.bat primeiro!",
                16  # Ícone de erro
            )
            input("\nPressione ENTER para sair...")
            return 1
        
        print("   ✓ Todos os pré-requisitos OK")
        print()
        
        # Mata processos anteriores
        print("🔄 Limpando processos anteriores...")
        kill_processes()
        print("   ✓ Portas liberadas")
        print()
        
        # Inicia backend
        print("🚀 Iniciando Backend (FastAPI)...")
        if start_backend(project_root):
            print("   ✓ Backend iniciando na porta 8000")
        print()
        
        # Aguarda um pouco
        time.sleep(2)
        
        # Inicia frontend
        print("🎨 Iniciando Frontend (Next.js)...")
        if start_frontend(project_root):
            print("   ✓ Frontend iniciando na porta 3002")
        print()
        
        # Instruções
        print("=" * 60)
        print("  ✅ SERVIDORES INICIADOS COM SUCESSO!")
        print("=" * 60)
        print()
        print("📍 URLs de Acesso:")
        print("   • Frontend: http://localhost:3002")
        print("   • Backend:  http://localhost:8000")
        print("   • API Docs: http://localhost:8000/docs")
        print()
        print("⚠️  IMPORTANTE:")
        print("   • Duas janelas foram abertas (Backend e Frontend)")
        print("   • NÃO feche essas janelas!")
        print("   • O navegador abrirá automaticamente")
        print("   • Para parar: feche as janelas ou use Parar-Servidores.ps1")
        print()
        print("=" * 60)
        
        # Abre navegador
        print("🌐 Abrindo navegador em 8 segundos...")
        open_browser()
        
        print()
        print("✨ Sistema rodando! Você já pode usar a aplicação.")
        print()
        input("Pressione ENTER para fechar este launcher (os servidores continuarão rodando)...")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}\n")
        show_message("Erro - Sistema DAC", f"Erro ao iniciar:\n\n{str(e)}", 16)
        input("\nPressione ENTER para sair...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
