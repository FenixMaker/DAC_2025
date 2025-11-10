"""
Launcher executável para a Versão Desktop do Sistema DAC
Inicia automaticamente a aplicação Tkinter
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path
import ctypes
import time

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
    py_path = project_root / "Versão PY"
    
    errors = []
    
    # Verifica se a pasta existe
    if not py_path.exists():
        errors.append(f"Pasta 'Versão PY' não encontrada em:\n{py_path}")
        return errors
    
    # Verifica main.py
    if not (py_path / "main.py").exists():
        errors.append(f"Arquivo main.py não encontrado em:\n{py_path}")
    
    return errors

def _venv_python_path(py_path: Path) -> Path:
    return py_path / ".venv" / "Scripts" / "python.exe"

def _is_venv_working(venv_python: Path) -> bool:
    try:
        if not venv_python.exists():
            return False
        res = subprocess.run([str(venv_python), "-V"], capture_output=True, text=True, timeout=10)
        return res.returncode == 0
    except Exception:
        return False

def _recreate_venv(py_path: Path) -> Path:
    """Recria o ambiente virtual usando o Python atual e instala requirements, se existir."""
    print("\n⚠️ Ambiente virtual inválido ou corrompido. Recriando automaticamente...")
    # Remove venv antiga, se existir
    try:
        shutil.rmtree(py_path / ".venv", ignore_errors=True)
    except Exception:
        pass

    # Cria nova venv com o Python atual
    subprocess.check_call([sys.executable, "-m", "venv", str(py_path / ".venv")])
    venv_python = _venv_python_path(py_path)

    # Atualiza pip e instala requisitos, se arquivo existir
    try:
        subprocess.check_call([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], cwd=str(py_path))
        req = py_path / "requirements.txt"
        if req.exists():
            print("📦 Instalando dependências da aplicação (requirements.txt)...")
            subprocess.check_call([str(venv_python), "-m", "pip", "install", "-r", str(req)], cwd=str(py_path))
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Falha ao instalar dependências: {e}\n")
        raise

    return venv_python

def _ensure_venv_ready(py_path: Path) -> Path:
    venv_python = _venv_python_path(py_path)
    if _is_venv_working(venv_python):
        return venv_python

    # Se a venv existe mas está quebrada (ex: copiada de outro PC), oferecer recriação automática
    print("\n⚠️ Detecção: Ambiente virtual parece inválido (talvez copiado de outro computador).")
    choice = input("Deseja recriar automaticamente agora? [S/n]: ").strip().lower()
    if choice in ("", "s", "sim", "y", "yes"):
        return _recreate_venv(py_path)
    else:
        raise RuntimeError(
            "Ambiente virtual inválido. Execute setup.bat ou aceite recriar automaticamente."
        )

def start_desktop_app(project_root):
    """Inicia a aplicação desktop"""
    py_path = project_root / "Versão PY"
    main_script = py_path / "main.py"

    # Garante venv válida
    venv_python = _ensure_venv_ready(py_path)

    # Muda para o diretório da aplicação
    os.chdir(str(py_path))

    # Inicia a aplicação (SEM cmd, diretamente)
    process = subprocess.Popen(
        [str(venv_python), str(main_script)],
        cwd=str(py_path)
    )

    return process

def main():
    """Função principal"""
    try:
        # Título da janela
        ctypes.windll.kernel32.SetConsoleTitleW("🖥️ Sistema DAC - Launcher Desktop")
        
        print("=" * 60)
        print("  🖥️  Sistema DAC - Launcher Versão Desktop")
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
                "Pré-requisitos não atendidos!\n\n" + "\n\n".join(errors),
                16  # Ícone de erro
            )
            input("\nPressione ENTER para sair...")
            return 1
        
        print("   ✓ Todos os pré-requisitos OK")
        print()
        
        # Inicia aplicação
        print("🚀 Iniciando aplicação Desktop...")
        print()
        process = start_desktop_app(project_root)
        
        print("=" * 60)
        print("  ✅ APLICAÇÃO INICIADA COM SUCESSO!")
        print("=" * 60)
        print()
        print("📍 Informações:")
        print("   • A janela da aplicação foi aberta")
        print("   • Use a interface gráfica normalmente")
        print("   • Feche a janela da aplicação para encerrar")
        print()
        print("=" * 60)
        print()
        print("Aguardando fechamento da aplicação...")
        
        # Aguarda a aplicação fechar
        process.wait()
        
        print("\n✅ Aplicação encerrada normalmente.")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário.")
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}\n")
        show_message("Erro - Sistema DAC", f"Erro ao iniciar:\n\n{str(e)}", 16)
        input("\nPressione ENTER para sair...")
        return 1

if __name__ == "__main__":
    sys.exit(main())
