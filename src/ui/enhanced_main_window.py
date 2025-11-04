
# -*- coding: utf-8 -*-
"""
Janela principal aprimorada da aplicação DAC com interface intuitiva e acessível
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import datetime

from ..database.database_manager import DatabaseManager
from ..utils.logger import get_logger
from .import_window import ImportWindow
from .query_window import QueryWindow
from .reports_window import ReportsWindow
from .icons import get_icon, create_icon_label, create_icon_button
from .tooltip_system import HelpSystem, create_enhanced_tooltip, add_contextual_help

class EnhancedMainWindow:
    """Janela principal aprimorada com interface intuitiva e acessível"""
    
    def __init__(self, db_manager=None):
        self.logger = get_logger(__name__)
        self.db_manager = db_manager if db_manager else DatabaseManager()
        
        # Configurar janela principal
        self.root = tk.Tk()
        self.root.title("📊 DAC - Sistema de Análise Digital")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Configurar tema moderno e acessível
        self.root.configure(bg='#F8FAFC')
        
        # Configurar estilo
        self.setup_styles()
        
        # Criar interface
        self.create_widgets()
        
        # Configurar tooltips e ajuda
        self.setup_help_system()
        
        # Configurar protocolo de fechamento
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_styles(self):
        """Configura os estilos da interface com foco em acessibilidade"""
        style = ttk.Style()
        
        # Configurar tema base
        style.theme_use('clam')
        
        # Paleta de cores acessível com alto contraste
        self.colors = {
            'bg_primary': '#F8FAFC',      # Fundo principal claro
            'bg_secondary': '#F1F5F9',    # Fundo secundário
            'bg_card': '#FFFFFF',         # Fundo dos cards
            'accent_blue': '#2563EB',     # Azul principal
            'accent_green': '#059669',    # Verde para sucesso
            'accent_orange': '#D97706',   # Laranja para atenção
            'accent_red': '#DC2626',      # Vermelho para erro
            'text_primary': '#1E293B',    # Texto principal
            'text_secondary': '#64748B',  # Texto secundário
            'text_muted': '#94A3B8',      # Texto esmaecido
            'border': '#E2E8F0',          # Bordas
            'shadow': '#0F172A20'         # Sombras
        }
        
        # Configurar estilos base com melhor contraste
        style.configure('TLabel', 
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        
        style.configure('TFrame', 
                       background=self.colors['bg_primary'])
        
        # Título principal com fonte maior e legível
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 28, 'bold'),
                       foreground=self.colors['text_primary'],
                       background=self.colors['bg_primary'])
        
        # Subtítulos com contraste adequado
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 14),
                       foreground=self.colors['text_secondary'],
                       background=self.colors['bg_primary'])
        
        # Cards com sombra sutil
        style.configure('Card.TFrame',
                       background=self.colors['bg_card'],
                       relief='solid',
                       borderwidth=1)
        
        # Botões principais com cores acessíveis
        style.configure('Primary.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       foreground='white',
                       background=self.colors['accent_blue'],
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Primary.TButton',
                 background=[('active', '#1D4ED8'),
                           ('pressed', '#1E40AF')])
        
        # Botões secundários
        style.configure('Secondary.TButton',
                       font=('Segoe UI', 10),
                       foreground=self.colors['text_primary'],
                       background=self.colors['bg_secondary'],
                       borderwidth=1,
                       focuscolor='none')
        
        # Sidebar com fundo diferenciado
        style.configure('Sidebar.TFrame',
                       background=self.colors['bg_secondary'])
        
    def create_widgets(self):
        """Cria a interface principal com layout intuitivo"""
        # Container principal
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Configurar grid responsivo
        main_container.columnconfigure(0, weight=0, minsize=280)  # Sidebar
        main_container.columnconfigure(1, weight=1)               # Conteúdo principal
        main_container.rowconfigure(0, weight=1)
        
        # Criar sidebar de navegação
        self.create_sidebar(main_container)
        
        # Criar área principal
        self.create_main_area(main_container)
        
    def create_sidebar(self, parent):
        """Cria sidebar com navegação intuitiva e ícones"""
        sidebar = ttk.Frame(parent, style='Sidebar.TFrame')
        sidebar.grid(row=0, column=0, sticky='nsew', padx=(0, 20))
        sidebar.configure(padding=20)
        
        # Cabeçalho da sidebar
        header_frame = ttk.Frame(sidebar, style='Sidebar.TFrame')
        header_frame.pack(fill='x', pady=(0, 30))
        
        # Logo e título com ícone aprimorado
        logo_label = create_icon_label(header_frame, 'stats', size=48,
                                      background=self.colors['bg_secondary'])
        logo_label.pack()
        
        title_label = ttk.Label(header_frame, text="DAC System",
                               font=('Segoe UI', 18, 'bold'),
                               foreground=self.colors['text_primary'],
                               background=self.colors['bg_secondary'])
        title_label.pack(pady=(5, 0))
        
        subtitle_label = ttk.Label(header_frame, text="Sistema de Análise Digital",
                                  font=('Segoe UI', 10),
                                  foreground=self.colors['text_secondary'],
                                  background=self.colors['bg_secondary'])
        subtitle_label.pack()
        
        # Menu de navegação com ícones e descrições
        nav_frame = ttk.Frame(sidebar, style='Sidebar.TFrame')
        nav_frame.pack(fill='x', pady=(0, 20))
        
        # Botões de navegação principais com ícones aprimorados
        nav_buttons = [
            ("import", "Importar Dados", "Importar arquivos CSV com dados", self.open_import_window),
            ("search", "Consultar Dados", "Filtrar e consultar informações", self.open_query_window),
            ("reports", "Relatórios", "Gerar relatórios e análises", self.open_reports_window),
            ("settings", "Configurações", "Configurar sistema e preferências", self.open_settings)
        ]
        
        for icon_name, title, description, command in nav_buttons:
            btn_frame = ttk.Frame(nav_frame, style='Sidebar.TFrame')
            btn_frame.pack(fill='x', pady=8)
            
            # Container para ícone e texto
            btn_container = ttk.Frame(btn_frame, style='Sidebar.TFrame')
            btn_container.pack(fill='x')
            
            # Ícone
            icon_label = create_icon_label(btn_container, icon_name, size=20,
                                         background=self.colors['bg_secondary'])
            icon_label.pack(side='left', padx=(0, 10))
            
            # Botão principal
            btn = ttk.Button(btn_container, text=title,
                           style='Secondary.TButton',
                           command=command)
            btn.pack(side='left', fill='x', expand=True)
            
            # Tooltip com descrição aprimorado
            HelpSystem.create_tooltip(btn, custom_text=description)
            
            # Descrição visual
            desc_label = ttk.Label(btn_frame, text=description,
                                  font=('Segoe UI', 8),
                                  foreground=self.colors['text_muted'],
                                  background=self.colors['bg_secondary'])
            desc_label.pack(pady=(2, 0))
        
        # Seção de ajuda com sistema aprimorado
        help_frame = ttk.Frame(sidebar, style='Sidebar.TFrame')
        help_frame.pack(fill='x', side='bottom', pady=(20, 0))
        
        # Container para ícone e texto de ajuda
        help_header = ttk.Frame(help_frame, style='Sidebar.TFrame')
        help_header.pack(fill='x')
        
        help_icon = create_icon_label(help_header, 'help', size=16,
                                     background=self.colors['bg_secondary'])
        help_icon.pack(side='left', padx=(0, 5))
        
        help_label = ttk.Label(help_header, text="Precisa de ajuda?",
                              font=('Segoe UI', 10, 'bold'),
                              foreground=self.colors['text_primary'],
                              background=self.colors['bg_secondary'])
        help_label.pack(side='left')
        
        # Botão de ajuda contextual
        help_btn, self.help_panel = add_contextual_help(help_frame, 'main')
        help_btn.configure(text="💡 Guia Rápido", style='Secondary.TButton')
        help_btn.pack(fill='x', pady=(5, 0))
        
        # Botão para documentação completa
        doc_btn = create_icon_button(help_frame, 'help', "Documentação Completa",
                                    style='Secondary.TButton',
                                    command=self.show_help)
        doc_btn.pack(fill='x', pady=(2, 0))
        HelpSystem.create_tooltip(doc_btn, 'help_btn')
        
    def create_main_area(self, parent):
        """Cria área principal com dashboard e informações"""
        main_area = ttk.Frame(parent)
        main_area.grid(row=0, column=1, sticky='nsew')
        main_area.configure(padding=20)
        
        # Cabeçalho principal
        header_frame = ttk.Frame(main_area)
        header_frame.pack(fill='x', pady=(0, 30))
        
        welcome_label = ttk.Label(header_frame, text="Bem-vindo ao DAC System",
                                 style='Title.TLabel')
        welcome_label.pack(anchor='w')
        
        date_label = ttk.Label(header_frame, 
                              text=f"📅 {datetime.datetime.now().strftime('%d/%m/%Y - %H:%M')}",
                              style='Subtitle.TLabel')
        date_label.pack(anchor='w', pady=(5, 0))
        
        # Cards de estatísticas
        self.create_stats_cards(main_area)
        
        # Seção de primeiros passos
        self.create_getting_started(main_area)
        
    def create_stats_cards(self, parent):
        """Cria cards com estatísticas do sistema"""
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill='x', pady=(0, 30))
        
        # Configurar grid para cards
        for i in range(3):
            stats_frame.columnconfigure(i, weight=1)
        
        # Card 1: Total de registros
        card1 = ttk.Frame(stats_frame, style='Card.TFrame')
        card1.grid(row=0, column=0, sticky='ew', padx=(0, 10), pady=10)
        card1.configure(padding=20)
        
        icon1 = create_icon_label(card1, 'stats', size=32,
                                 background=self.colors['bg_card'])
        icon1.pack()
        
        title1 = ttk.Label(card1, text="Total de Registros",
                          font=('Segoe UI', 12, 'bold'),
                          foreground=self.colors['text_primary'],
                          background=self.colors['bg_card'])
        title1.pack(pady=(5, 0))
        
        try:
            total_records = self.get_total_records()
            value1 = ttk.Label(card1, text=f"{total_records:,}",
                              font=('Segoe UI', 20, 'bold'),
                              foreground=self.colors['accent_blue'],
                              background=self.colors['bg_card'])
        except:
            value1 = ttk.Label(card1, text="0",
                              font=('Segoe UI', 20, 'bold'),
                              foreground=self.colors['accent_blue'],
                              background=self.colors['bg_card'])
        value1.pack()
        
        # Card 2: Status do banco
        card2 = ttk.Frame(stats_frame, style='Card.TFrame')
        card2.grid(row=0, column=1, sticky='ew', padx=5, pady=10)
        card2.configure(padding=20)
        
        icon2 = create_icon_label(card2, 'database', size=32,
                                 background=self.colors['bg_card'])
        icon2.pack()
        
        title2 = ttk.Label(card2, text="Status do Banco",
                          font=('Segoe UI', 12, 'bold'),
                          foreground=self.colors['text_primary'],
                          background=self.colors['bg_card'])
        title2.pack(pady=(5, 0))
        
        try:
            db_status = "✅ Conectado" if self.db_manager.test_connection() else "❌ Desconectado"
            status_color = self.colors['accent_green'] if "Conectado" in db_status else self.colors['accent_red']
        except:
            db_status = "❌ Erro"
            status_color = self.colors['accent_red']
            
        value2 = ttk.Label(card2, text=db_status,
                          font=('Segoe UI', 14, 'bold'),
                          foreground=status_color,
                          background=self.colors['bg_card'])
        value2.pack()
        
        # Card 3: Última atualização
        card3 = ttk.Frame(stats_frame, style='Card.TFrame')
        card3.grid(row=0, column=2, sticky='ew', padx=(10, 0), pady=10)
        card3.configure(padding=20)
        
        icon3 = create_icon_label(card3, 'time', size=32,
                                 background=self.colors['bg_card'])
        icon3.pack()
        
        title3 = ttk.Label(card3, text="Última Atualização",
                          font=('Segoe UI', 12, 'bold'),
                          foreground=self.colors['text_primary'],
                          background=self.colors['bg_card'])
        title3.pack(pady=(5, 0))
        
        value3 = ttk.Label(card3, text="Agora",
                          font=('Segoe UI', 14, 'bold'),
                          foreground=self.colors['accent_orange'],
                          background=self.colors['bg_card'])
        value3.pack()
        
    def create_getting_started(self, parent):
        """Cria seção de primeiros passos para novos usuários"""
        getting_started_frame = ttk.Frame(parent, style='Card.TFrame')
        getting_started_frame.pack(fill='both', expand=True)
        getting_started_frame.configure(padding=30)
        
        # Título da seção com ícone
        title_frame = ttk.Frame(getting_started_frame, style='Card.TFrame')
        title_frame.pack(fill='x', pady=(0, 20))
        
        rocket_icon = create_icon_label(title_frame, 'home', size=24,
                                       background=self.colors['bg_card'])
        rocket_icon.pack(side='left', padx=(0, 10))
        
        title = ttk.Label(title_frame, text="Primeiros Passos",
                         font=('Segoe UI', 18, 'bold'),
                         foreground=self.colors['text_primary'],
                         background=self.colors['bg_card'])
        title.pack(side='left')
        
        # Lista de passos com ícones apropriados
        steps = [
            ("import", "1. Importar Dados", "Comece importando seus arquivos CSV com os dados para análise"),
            ("search", "2. Explorar Dados", "Use a ferramenta de consulta para filtrar e explorar as informações"),
            ("reports", "3. Gerar Relatórios", "Crie relatórios personalizados com gráficos e estatísticas")
        ]
        
        for icon_name, step_title, description in steps:
            step_frame = ttk.Frame(getting_started_frame, style='Card.TFrame')
            step_frame.pack(fill='x', pady=10)
            
            # Container horizontal para ícone e texto
            content_frame = ttk.Frame(step_frame, style='Card.TFrame')
            content_frame.pack(fill='x')
            
            # Ícone
            icon_label = create_icon_label(content_frame, icon_name, size=28,
                                          background=self.colors['bg_card'])
            icon_label.pack(side='left', padx=(0, 15))
            
            # Texto
            text_frame = ttk.Frame(content_frame, style='Card.TFrame')
            text_frame.pack(side='left', fill='x', expand=True)
            
            step_label = ttk.Label(text_frame, text=step_title,
                                  font=('Segoe UI', 14, 'bold'),
                                  foreground=self.colors['text_primary'],
                                  background=self.colors['bg_card'])
            step_label.pack(anchor='w')
            
            desc_label = ttk.Label(text_frame, text=description,
                                  font=('Segoe UI', 11),
                                  foreground=self.colors['text_secondary'],
                                  background=self.colors['bg_card'])
            desc_label.pack(anchor='w', pady=(2, 0))
        
        # Botões de ação principais
        action_frame = ttk.Frame(getting_started_frame, style='Card.TFrame')
        action_frame.pack(fill='x', pady=(20, 0))
        
        # Botão principal de início
        start_btn = create_icon_button(action_frame, 'import', "Começar Importando Dados",
                                      style='Primary.TButton',
                                      command=self.open_import_window)
        start_btn.pack(pady=(0, 10))
        HelpSystem.create_tooltip(start_btn, 'import_btn')
        
        # Botão de ajuda para primeiros passos
        help_getting_started = ttk.Button(action_frame, text="❓ Precisa de ajuda para começar?",
                                         style='Secondary.TButton',
                                         command=lambda: self.show_getting_started_help())
        help_getting_started.pack()
        HelpSystem.create_tooltip(help_getting_started, 
                                 custom_text="Clique para ver instruções detalhadas sobre como começar")
        
    def setup_help_system(self):
        """Configura sistema de ajuda e tooltips"""
        # Inicializa o sistema de ajuda
        self.help_panels = {}
        
    def show_getting_started_help(self):
        """Mostra ajuda específica para primeiros passos"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Guia de Primeiros Passos")
        help_window.geometry("500x400")
        help_window.configure(bg=self.colors['bg_primary'])
        
        # Centralizar janela
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Título
        title_frame = ttk.Frame(help_window)
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        title_label = ttk.Label(title_frame, text="🚀 Como Começar",
                               font=('Segoe UI', 16, 'bold'),
                               foreground=self.colors['text_primary'])
        title_label.pack()
        
        # Conteúdo scrollável
        canvas = tk.Canvas(help_window, bg=self.colors['bg_primary'])
        scrollbar = ttk.Scrollbar(help_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Instruções detalhadas
        instructions = [
            ("1. Preparar seus dados", 
             "Certifique-se de que seus arquivos CSV estão formatados corretamente com cabeçalhos nas primeiras linhas."),
            ("2. Importar dados", 
             "Clique em 'Importar Dados' na barra lateral e selecione seus arquivos CSV. O sistema processará automaticamente."),
            ("3. Explorar dados", 
             "Use 'Consultar Dados' para filtrar e visualizar informações específicas usando os critérios disponíveis."),
            ("4. Gerar relatórios", 
             "Acesse 'Relatórios' para criar análises personalizadas e exportar resultados em diferentes formatos."),
            ("5. Configurar sistema", 
             "Ajuste preferências em 'Configurações' para personalizar a experiência de uso.")
        ]
        
        for title, description in instructions:
            # Frame para cada instrução
            inst_frame = ttk.Frame(scrollable_frame, style='Card.TFrame')
            inst_frame.pack(fill='x', padx=20, pady=10)
            
            # Título da instrução
            title_label = ttk.Label(inst_frame, text=title,
                                   font=('Segoe UI', 12, 'bold'),
                                   foreground=self.colors['text_primary'])
            title_label.pack(anchor='w', pady=(10, 5))
            
            # Descrição
            desc_label = ttk.Label(inst_frame, text=description,
                                  font=('Segoe UI', 10),
                                  foreground=self.colors['text_secondary'],
                                  wraplength=400)
            desc_label.pack(anchor='w', padx=(20, 10), pady=(0, 10))
        
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=(0, 20))
        scrollbar.pack(side="right", fill="y", padx=(0, 20), pady=(0, 20))
        
        # Botão para fechar
        close_btn = ttk.Button(help_window, text="Entendi!",
                              style='Primary.TButton',
                              command=help_window.destroy)
        close_btn.pack(pady=20)
        
    def create_tooltip(self, widget, text):
        """Cria tooltip aprimorado para um widget"""
        return create_enhanced_tooltip(widget, text)
        
    def get_total_records(self):
        """Obtém o total de registros no banco de dados"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM individuals")
                return cursor.fetchone()[0]
        except:
            return 0
            
    def open_import_window(self):
        """Abre janela de importação de dados"""
        try:
            import_window = ImportWindow(self.root, self.db_manager)
            import_window.show()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir janela de importação: {str(e)}")
            
    def open_query_window(self):
        """Abre janela de consulta de dados"""
        try:
            query_window = QueryWindow(self.root, self.db_manager)
            query_window.show()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir janela de consulta: {str(e)}")
            
    def open_reports_window(self):
        """Abre janela de relatórios"""
        try:
            reports_window = ReportsWindow(self.root, self.db_manager)
            reports_window.show()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir janela de relatórios: {str(e)}")
            
    def open_settings(self):
        """Abre janela de configurações"""
        messagebox.showinfo("Configurações", "Funcionalidade em desenvolvimento")
        
    def show_help(self):
        """Mostra ajuda do sistema"""
        help_text = """
🔹 GUIA RÁPIDO DO DAC SYSTEM 🔹

📥 IMPORTAR DADOS:
• Clique em 'Importar Dados' na barra lateral
• Selecione seus arquivos CSV
• Aguarde a importação ser concluída

🔍 CONSULTAR DADOS:
• Use 'Consultar Dados' para filtrar informações
• Aplique filtros por região, idade, etc.
• Visualize os resultados em tabela

📊 RELATÓRIOS:
• Gere relatórios personalizados
• Exporte em diferentes formatos
• Visualize gráficos e estatísticas

💡 DICAS:
• Mantenha seus dados organizados
• Use filtros para análises específicas
• Exporte relatórios para compartilhar
        """
        
        messagebox.showinfo("Guia do Usuário", help_text)
        
    def on_closing(self):
        """Manipula o fechamento da aplicação"""
        if messagebox.askokcancel("Sair", "Deseja realmente sair do DAC System?"):
            self.root.destroy()
            
    def run(self):
        """Inicia a aplicação"""
        self.root.mainloop()
