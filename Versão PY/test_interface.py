#!/usr/bin/env python3
"""
Script de teste para a interface de configuração do sistema DAC.
Verifica a funcionalidade completa da interface de configuração.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from gui.configuracoes_tab import ConfiguracoesTab
    from utils.config_manager import ConfigManager
    print("✓ Módulos importados com sucesso")
except ImportError as e:
    print(f"✗ Erro ao importar módulos: {e}")
    sys.exit(1)

def test_interface():
    """Testa a interface de configuração."""
    print("\n=== Testando Interface de Configuração ===")
    
    # Cria janela principal
    root = tk.Tk()
    root.title("Teste da Interface de Configuração - DAC")
    root.geometry("900x700")
    
    try:
        # Cria gerenciador de configurações
        config_manager = ConfigManager()
        print("✓ ConfigManager criado com sucesso")
        
        # Cria aba de configurações
        config_tab = ConfiguracoesTab(root)
        config_tab.pack(fill=tk.BOTH, expand=True)
        print("✓ ConfiguracoesTab criada com sucesso")
        
        # Verifica se os elementos principais existem
        checks = [
            ("Notebook/Abas", hasattr(config_tab, 'notebook')),
            ("Status Bar", hasattr(config_tab, 'status_var')),
            ("Botão Salvar", hasattr(config_tab, 'save_button')),
            ("Botão Cancelar", hasattr(config_tab, 'cancel_button')),
            ("Botão Testar Conexão", hasattr(config_tab, 'test_button')),
            ("Botão Resetar", hasattr(config_tab, 'reset_button')),
            ("Frame PostgreSQL", hasattr(config_tab, 'postgresql_frame')),
            ("Frame SQLite", hasattr(config_tab, 'sqlite_frame')),
            ("Variável Tipo DB", hasattr(config_tab, 'db_type_var')),
            ("Variável SQLite Path", hasattr(config_tab, 'sqlite_path_var'))
        ]
        
        print("\n=== Verificando Elementos da Interface ===")
        for name, check in checks:
            status = "✓" if check else "✗"
            print(f"{status} {name}")
        
        # Verifica abas existentes
        print("\n=== Verificando Abas ===")
        try:
            abas = config_tab.notebook.tabs()
            abas_nomes = [config_tab.notebook.tab(tab, 'text') for tab in abas]
            for nome in abas_nomes:
                print(f"✓ Aba: {nome}")
        except Exception as e:
            print(f"✗ Erro ao verificar abas: {e}")
        
        # Testa carregamento de configurações
        print("\n=== Testando Carregamento de Configurações ===")
        try:
            config_tab.load_all_configs()
            print("✓ Configurações carregadas com sucesso")
        except Exception as e:
            print(f"✗ Erro ao carregar configurações: {e}")
        
        # Testa status inicial
        print(f"\n=== Status Inicial ===")
        print(f"Status: {config_tab.status_var.get()}")
        print(f"Tipo DB: {config_tab.db_type_var.get()}")
        print(f"SQLite Path: {config_tab.sqlite_path_var.get()}")
        
        # Verifica se o arquivo SQLite padrão existe
        sqlite_path = config_tab.sqlite_path_var.get()
        if sqlite_path and os.path.exists(sqlite_path):
            print(f"✓ Arquivo SQLite encontrado: {sqlite_path}")
        else:
            print(f"⚠ Arquivo SQLite não encontrado: {sqlite_path}")
        
        print("\n=== Interface de Configuração - Teste Concluído ===")
        print("A interface foi criada com sucesso!")
        print("Você pode interagir com a interface para testar as funcionalidades.")
        print("\nPrincipais funcionalidades disponíveis:")
        print("• Alternar entre PostgreSQL e SQLite")
        print("• Selecionar arquivo SQLite")
        print("• Testar conexão com banco de dados")
        print("• Salvar/Cancelar alterações")
        print("• Resetar para padrões")
        print("• Exportar/Importar configurações")
        
        # Inicia o loop principal
        print("\nIniciando interface gráfica...")
        root.mainloop()
        
    except Exception as e:
        print(f"✗ Erro ao criar interface: {e}")
        messagebox.showerror("Erro", f"Erro ao criar interface:\n{str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("=== Teste da Interface de Configuração - DAC ===")
    success = test_interface()
    if success:
        print("\n✓ Teste concluído com sucesso!")
    else:
        print("\n✗ Teste falhou!")
        sys.exit(1)