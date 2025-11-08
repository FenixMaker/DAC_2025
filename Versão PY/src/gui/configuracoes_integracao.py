"""
Módulo de integração da aba de configurações ao menu principal.
Fornece funções para adicionar e gerenciar a aba de configurações na aplicação principal.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from gui.configuracoes_tab import ConfiguracoesTab


class ConfiguracoesIntegracao:
    """Classe responsável por integrar a aba de configurações à aplicação principal."""
    
    def __init__(self, main_window, notebook_principal):
        """
        Inicializa a integração.
        
        Args:
            main_window: Janela principal da aplicação
            notebook_principal: Notebook principal onde as abas são adicionadas
        """
        self.main_window = main_window
        self.notebook_principal = notebook_principal
        self.config_tab = None
        self.config_menu_items = []
    
    def adicionar_aba_configuracoes(self):
        """Adiciona a aba de configurações ao notebook principal."""
        try:
            # Cria a aba de configurações
            self.config_tab = ConfiguracoesTab(self.notebook_principal)
            
            # Adiciona ao notebook principal
            self.notebook_principal.add(self.config_tab, text="⚙️ Configurações")
            
            print("Aba de configurações adicionada com sucesso!")
            return True
            
        except Exception as e:
            print(f"Erro ao adicionar aba de configurações: {e}")
            messagebox.showerror("Erro", f"Erro ao adicionar aba de configurações:\n{str(e)}")
            return False
    
    def adicionar_menu_configuracoes(self, menu_bar):
        """
        Adiciona itens de menu relacionados às configurações.
        
        Args:
            menu_bar: MenuBar principal da aplicação
        """
        try:
            # Cria ou obtém o menu de ferramentas/opções
            if 'Ferramentas' not in [menu_bar.entrycget(i, 'label') for i in range(menu_bar.index('end') + 1)]:
                ferramentas_menu = tk.Menu(menu_bar, tearoff=0)
                menu_bar.add_cascade(label="Ferramentas", menu=ferramentas_menu)
            else:
                # Encontra o menu de ferramentas existente
                for i in range(menu_bar.index('end') + 1):
                    if menu_bar.entrycget(i, 'label') == 'Ferramentas':
                        ferramentas_menu = menu_bar.nametowidget(menu_bar.entrycget(i, 'menu'))
                        break
            
            # Adiciona separador se já houver itens
            if ferramentas_menu.index('end') is not None:
                ferramentas_menu.add_separator()
            
            # Adiciona itens de configuração
            ferramentas_menu.add_command(
                label="Configurações Gerais...",
                command=self.abrir_configuracoes,
                accelerator="Ctrl+Alt+C",
                image=self.get_menu_icon('config'),
                compound=tk.LEFT
            )
            
            ferramentas_menu.add_command(
                label="Testar Conexão com Banco",
                command=self.testar_conexao_banco,
                image=self.get_menu_icon('database'),
                compound=tk.LEFT
            )
            
            ferramentas_menu.add_separator()
            
            ferramentas_menu.add_command(
                label="Exportar Configurações",
                command=self.exportar_configuracoes,
                image=self.get_menu_icon('export'),
                compound=tk.LEFT
            )
            
            ferramentas_menu.add_command(
                label="Importar Configurações",
                command=self.importar_configuracoes,
                image=self.get_menu_icon('import'),
                compound=tk.LEFT
            )
            
            # Configura atalho de teclado
            self.main_window.bind_all("<Control-Alt-c>", lambda e: self.abrir_configuracoes())
            
            # Adiciona ao menu de contexto (clique direito) se existir
            self.adicionar_context_menu_configuracoes()
            
            print("Menu de configurações adicionado com sucesso!")
            return True
            
        except Exception as e:
            print(f"Erro ao adicionar menu de configurações: {e}")
            return False
    
    def adicionar_context_menu_configuracoes(self):
        """Adiciona opções de configuração ao menu de contexto."""
        try:
            # Cria menu de contexto para a janela principal
            self.context_menu = tk.Menu(self.main_window, tearoff=0)
            
            # Adiciona opções de configuração
            self.context_menu.add_command(
                label="Configurações...",
                command=self.abrir_configuracoes
            )
            
            self.context_menu.add_separator()
            
            self.context_menu.add_command(
                label="Recarregar Configurações",
                command=self.recarregar_configuracoes
            )
            
            # Bind do clique direito
            self.main_window.bind("<Button-3>", self.show_context_menu)
            
        except Exception as e:
            print(f"Erro ao adicionar menu de contexto: {e}")
    
    def show_context_menu(self, event):
        """Mostra o menu de contexto."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def get_menu_icon(self, icon_type):
        """
        Retorna ícone para o menu (placeholder - pode ser substituído por ícones reais).
        
        Args:
            icon_type: Tipo do ícone ('config', 'database', 'export', 'import')
            
        Returns:
            PhotoImage ou None se não houver ícone
        """
        # Por enquanto retorna None - pode ser implementado com ícones reais depois
        return None
    
    def abrir_configuracoes(self):
        """Abre a aba de configurações."""
        try:
            # Se a aba já existe, seleciona ela
            if self.config_tab and self.config_tab.winfo_exists():
                # Encontra a aba de configurações
                for i in range(self.notebook_principal.index('end')):
                    if self.notebook_principal.tab(i, 'text') == '⚙️ Configurações':
                        self.notebook_principal.select(i)
                        break
            else:
                # Se não existe, cria e adiciona
                self.adicionar_aba_configuracoes()
            
            # Foca na janela principal
            self.main_window.focus_force()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir configurações:\n{str(e)}")
    
    def testar_conexao_banco(self):
        """Testa a conexão com o banco de dados."""
        try:
            from utils.config_manager import config_manager, test_database_connection
            
            # Carrega configurações do banco
            db_config = config_manager.load_config('database')
            
            # Testa a conexão
            success, message = test_database_connection(db_config)
            
            if success:
                messagebox.showinfo("Sucesso", f"Conexão bem-sucedida!\n{message}")
            else:
                messagebox.showerror("Erro", f"Falha na conexão:\n{message}")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao testar conexão:\n{str(e)}")
    
    def exportar_configuracoes(self):
        """Exporta as configurações atuais."""
        try:
            from tkinter import filedialog
            from utils.config_manager import config_manager
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Exportar Configurações"
            )
            
            if file_path:
                success = config_manager.export_config(file_path)
                if success:
                    messagebox.showinfo("Sucesso", f"Configurações exportadas para:\n{file_path}")
                else:
                    messagebox.showerror("Erro", "Erro ao exportar configurações")
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar configurações:\n{str(e)}")
    
    def importar_configuracoes(self):
        """Importa configurações de um arquivo."""
        try:
            from tkinter import filedialog
            from utils.config_manager import config_manager
            
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Importar Configurações"
            )
            
            if file_path:
                success, errors = config_manager.import_config(file_path)
                if success:
                    # Recarrega a aba se existir
                    if self.config_tab and self.config_tab.winfo_exists():
                        self.config_tab.load_all_configs()
                    
                    if errors:
                        messagebox.showwarning("Aviso", f"Configurações importadas com avisos:\n" + "\n".join(errors))
                    else:
                        messagebox.showinfo("Sucesso", "Configurações importadas com sucesso!")
                else:
                    messagebox.showerror("Erro", f"Erro ao importar configurações:\n" + "\n".join(errors))
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar configurações:\n{str(e)}")
    
    def recarregar_configuracoes(self):
        """Recarrega as configurações da aba."""
        try:
            if self.config_tab and self.config_tab.winfo_exists():
                self.config_tab.load_all_configs()
                messagebox.showinfo("Sucesso", "Configurações recarregadas com sucesso!")
            else:
                messagebox.showinfo("Informação", "A aba de configurações não está aberta.")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao recarregar configurações:\n{str(e)}")
    
    def obter_configuracao(self, config_type: str, key: str, default=None):
        """
        Obtém uma configuração específica.
        
        Args:
            config_type: Tipo de configuração ('database', 'appearance', etc.)
            key: Chave da configuração
            default: Valor padrão se não encontrar
            
        Returns:
            Valor da configuração ou default
        """
        try:
            from utils.config_manager import config_manager
            config = config_manager.load_config(config_type)
            return config.get(key, default)
        except Exception:
            return default
    
    def definir_configuracao(self, config_type: str, key: str, value):
        """
        Define uma configuração específica.
        
        Args:
            config_type: Tipo de configuração
            key: Chave da configuração
            value: Valor a ser definido
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            from utils.config_manager import config_manager
            config = config_manager.load_config(config_type)
            config[key] = value
            return config_manager.save_config(config_type, config)
        except Exception:
            return False


# Função auxiliar para facilitar a integração
def integrar_configuracoes(main_window, notebook_principal, menu_bar=None):
    """
    Função de conveniência para integrar as configurações à aplicação.
    
    Args:
        main_window: Janela principal da aplicação
        notebook_principal: Notebook principal
        menu_bar: MenuBar opcional
        
    Returns:
        Instância da ConfiguracoesIntegracao
    """
    integracao = ConfiguracoesIntegracao(main_window, notebook_principal)
    
    # Adiciona a aba de configurações
    integracao.adicionar_aba_configuracoes()
    
    # Adiciona ao menu se fornecido
    if menu_bar:
        integracao.adicionar_menu_configuracoes(menu_bar)
    
    return integracao


# Exemplo de uso em uma aplicação principal
if __name__ == "__main__":
    # Cria janela de teste
    root = tk.Tk()
    root.title("Teste de Integração de Configurações")
    root.geometry("1000x700")
    
    # Cria menu
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # Cria notebook principal
    main_notebook = ttk.Notebook(root)
    main_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Adiciona algumas abas de exemplo
    exemplo_frame = ttk.Frame(main_notebook)
    main_notebook.add(exemplo_frame, text="Exemplo")
    
    ttk.Label(exemplo_frame, text="Aba de exemplo - clique na aba Configurações", 
              font=('Arial', 14)).pack(pady=50)
    
    # Integra as configurações
    integracao = integrar_configuracoes(root, main_notebook, menubar)
    
    root.mainloop()