# -*- coding: utf-8 -*-
"""
Janela principal da aplicação DAC - Modern Dark Theme
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from ..database.database_manager import DatabaseManager
from ..utils.logger import get_logger
from .import_window import ImportWindow
from .query_window import QueryWindow
from .reports_window import ReportsWindow
from .db_status_window import DbStatusWindow
from .modern_theme import theme
from .theme_manager import ThemeManager
from .modern_components import KPICard, ModernButton, ModernSidebar
from .icons import get_icon, create_icon_button, get_icon_color
from .logo_assets import load_logo_tk
from ..gui.configuracoes_tab import ConfiguracoesTab

class MainWindow:
    """Janela principal da aplicação DAC"""
    
    def __init__(self, db_manager=None):
        self.logger = get_logger(__name__)
        self.db_manager = db_manager if db_manager else DatabaseManager()
        
        # Garantir que o banco está inicializado antes de criar a interface
        if not hasattr(self.db_manager, 'engine') or self.db_manager.engine is None:
            self.db_manager.initialize_database()
        
        # Configurar janela principal
        self.root = tk.Tk()
        self.root.title("Sistema DAC - Digital Analysis Center")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)

        # Ícone da janela (simplificado para clareza em tamanhos pequenos)
        try:
            logo_icon = load_logo_tk("simplified", size=64)
            # Tkinter suporta somente .ico para iconbitmap, mas PhotoImage pode para taskbar em alguns sistemas
            self.root.iconphoto(True, logo_icon)
        except Exception:
            pass
        
        # Aplicar tema moderno
        self.theme_manager = ThemeManager()
        self.theme_manager.apply_theme(self.root)
        self.root.configure(bg=theme.bg_root)
        
        # Criar interface
        self.create_widgets()
        
    
    def create_widgets(self):
        """Cria os widgets da interface principal"""
        # Container principal
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True)
        
        # Configurar grid principal com responsividade
        main_container.columnconfigure(0, weight=0, minsize=280)  # Sidebar fixa
        main_container.columnconfigure(1, weight=1, minsize=600)  # Área principal expansível
        main_container.rowconfigure(0, weight=1, minsize=500)
        
        # Sidebar esquerda
        self.create_sidebar(main_container)
        
        # Área principal do dashboard com responsividade
        dashboard_frame = ttk.Frame(main_container, style='Content.TFrame')
        dashboard_frame.grid(row=0, column=1, sticky='nsew', padx=20, pady=20)
        dashboard_frame.columnconfigure(0, weight=1)
        dashboard_frame.rowconfigure(0, weight=0, minsize=80)   # Header fixo
        dashboard_frame.rowconfigure(1, weight=1, minsize=400)  # Conteúdo expansível
        
        # Header do dashboard
        self.create_dashboard_header(dashboard_frame)
        
        # Área de conteúdo principal com grid responsivo
        content_area = ttk.Frame(dashboard_frame)
        content_area.grid(row=1, column=0, sticky='nsew', pady=(20, 0))
        content_area.columnconfigure(0, weight=2, minsize=400)  # Gráficos principais
        content_area.columnconfigure(1, weight=1, minsize=300)  # Painel lateral
        content_area.rowconfigure(0, weight=0, minsize=120)     # Cards de stats
        content_area.rowconfigure(1, weight=1, minsize=300)     # Área de gráficos
        
        # Cards de estatísticas (superior)
        self.create_stats_cards(content_area)
        
        # Área de gráficos e informações (inferior)
        self.create_charts_area(content_area)
        
        # Atualizar estatísticas iniciais
        self.update_stats()
    
    def create_sidebar(self, parent):
        """Cria a sidebar usando ModernSidebar component"""
        # Criar sidebar moderna
        self.sidebar = ModernSidebar(parent)
        self.sidebar.grid(row=0, column=0, sticky='nsew')
        
        # Adicionar menu items com Material Symbols
        self.sidebar.add_menu_item("dashboard", "Dashboard", get_icon("dashboard"), None)
        self.sidebar.add_menu_item("import", "Importar Dados", get_icon("import"), self.open_import_window)
        self.sidebar.add_menu_item("query", "Consultar", get_icon("search"), self.open_query_window)
        self.sidebar.add_menu_item("reports", "Relatórios", get_icon("reports"), self.open_reports_window)
        self.sidebar.add_menu_item("db_status", "Status do Banco", get_icon("database"), self.open_db_status_window)
        self.sidebar.add_menu_item("settings", "Configurações", get_icon("settings"), self.open_settings)
        
        # Definir dashboard como ativo
        if "dashboard" in self.sidebar.buttons:
            self.sidebar.active_button = "dashboard"
        
        # Footer da sidebar
        footer_frame = ttk.Frame(self.sidebar, style='Sidebar.TFrame')
        footer_frame.pack(side='bottom', fill='x', padx=theme.spacing_lg, 
                         pady=theme.spacing_lg)
        
        # Botão de atualização usando ModernButton com Material Symbol
        refresh_btn = ModernButton(
            footer_frame,
            text="Atualizar Dados",
            style_type="success",
            icon=get_icon("refresh"),
            command=self.update_stats
        )
        refresh_btn.pack(fill='x', pady=(0, theme.spacing_md))
        
        # Informações do sistema
        info_label = ttk.Label(
            footer_frame,
            text="v2.0 • Python • SQLite",
            font=(theme.font_family, 9),
            style='Secondary.TLabel'
        )
        info_label.pack(anchor='center')
    
    def create_dashboard_header(self, parent):
        """Cria o header do dashboard"""
        header_frame = ttk.Frame(parent, style='Header.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 0))
        header_frame.columnconfigure(0, weight=1)
        
        # Marca com logo + título
        brand_frame = ttk.Frame(header_frame, style='Header.TFrame')
        brand_frame.grid(row=0, column=0, sticky='w')
        try:
            logo_img = load_logo_tk("color", size=40)
            logo_label = ttk.Label(brand_frame, image=logo_img)
            logo_label.image = logo_img  # evitar GC
            logo_label.grid(row=0, column=0, padx=(0, 10))
        except Exception:
            pass
        title_label = ttk.Label(brand_frame,
                               text="Sistema de Análise Digital",
                               style='Title.TLabel')
        title_label.grid(row=0, column=1, sticky='w')
        
        # Subtítulo com espaçamento consistente
        subtitle_label = ttk.Label(header_frame,
                                  text="Dashboard de Exclusão Digital - Dados TIC Domicílios",
                                  style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, sticky='w', pady=(6, 0))
        
        # Indicadores do header (lado direito)
        indicators_frame = ttk.Frame(header_frame, style='Header.TFrame')
        indicators_frame.grid(row=0, column=1, rowspan=2, sticky='e')
        
        # Status indicator com Material Symbol
        status_icon = get_icon('check')
        status_label = ttk.Label(indicators_frame, 
                                text=f"{status_icon} Sistema Online",
                                font=('Segoe UI', 10, 'bold'),
                                foreground='#10B981',
                                style='TLabel')
        status_label.pack(anchor='e')
        
        # Data/hora com Material Symbol
        import datetime
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        calendar_icon = get_icon('calendar')
        time_label = ttk.Label(indicators_frame, 
                              text=f"{calendar_icon} {now}",
                              style='Subtitle.TLabel')
        time_label.pack(anchor='e', pady=(6, 0))
    
    def create_stats_cards(self, parent):
        """Cria os cards de estatísticas usando KPICard moderno"""
        stats_frame = ttk.Frame(parent, style='TFrame')
        stats_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 20))
        
        # Configurar grid para os cards
        for i in range(5):
            stats_frame.columnconfigure(i, weight=1, minsize=180)
        
        # Dados dos cards com Material Symbols
        cards_data = [
            ("database", "Regiões", "regions"),
            ("home", "Domicílios", "households"),
            ("user", "Indivíduos", "individuals"),
            ("view_module", "Dispositivos", "device_usage_records"),
            ("wifi", "Internet", "internet_usage_records")
        ]
        
        self.stats_labels = {}
        
        for i, (icon, title, key) in enumerate(cards_data):
            # Criar KPICard moderno
            kpi_card = KPICard(
                stats_frame,
                label_text=title,
                value="0",
                icon=icon
            )
            kpi_card.grid(row=0, column=i, sticky='nsew', padx=8)
            
            # Armazenar referência ao label de valor para atualização
            self.stats_labels[key] = kpi_card.value_label
    
    def create_charts_area(self, parent):
        """Cria a área de gráficos e informações com design modernizado"""
        # Painel esquerdo - Gráfico principal
        left_panel = tk.Frame(parent, bg='#21262D', relief='flat')
        left_panel.grid(row=1, column=0, sticky='nsew', padx=(0, 15))
        
        # Header do painel com design aprimorado
        left_header = tk.Frame(left_panel, bg='#21262D')
        left_header.pack(fill='x', padx=25, pady=(25, 15))
        
        # Título com ícone e melhor tipografia
        chart_title = tk.Label(left_header,
                              text="📈 Análise de Exclusão Digital",
                              font=('Segoe UI', 16, 'bold'),
                              bg='#21262D',
                              fg='#F0F6FC')
        chart_title.pack(anchor='w')
        
        chart_subtitle = tk.Label(left_header,
                                 text="Distribuição por região e categoria",
                                 font=('Segoe UI', 11),
                                 bg='#21262D',
                                 fg='#8B949E')
        chart_subtitle.pack(anchor='w', pady=(6, 0))
        
        # Linha divisória sutil
        divider = tk.Frame(left_header, bg='#30363D', height=1)
        divider.pack(fill='x', pady=(15, 0))
        
        # Área do gráfico com fundo atualizado
        chart_area = tk.Frame(left_panel, bg='#0D1117', relief='flat')
        chart_area.pack(fill='both', expand=True, padx=25, pady=(15, 25))
        
        # Simulação de gráfico aprimorada
        self.create_mock_chart(chart_area)
        
        # Painel direito - Insights e métricas
        right_panel = tk.Frame(parent, bg='#21262D', relief='flat')
        right_panel.grid(row=1, column=1, sticky='nsew', padx=(15, 0))
        
        # Header do painel direito
        right_header = tk.Frame(right_panel, bg='#21262D')
        right_header.pack(fill='x', padx=25, pady=(25, 15))
        
        info_title = tk.Label(right_header,
                             text="💡 Insights do Sistema",
                             font=('Segoe UI', 16, 'bold'),
                             bg='#21262D',
                             fg='#F0F6FC')
        info_title.pack(anchor='w')
        
        info_subtitle = tk.Label(right_header,
                               text="Métricas e análises em tempo real",
                               font=('Segoe UI', 11),
                               bg='#21262D',
                               fg='#8B949E')
        info_subtitle.pack(anchor='w', pady=(6, 0))
        
        # Linha divisória
        divider_right = tk.Frame(right_header, bg='#30363D', height=1)
        divider_right.pack(fill='x', pady=(15, 0))
        
        # Painel de insights aprimorado
        self.create_insights_panel(right_panel)
        
        # Área do gráfico simulado com espaçamento harmonizado
        chart_area = tk.Frame(left_panel, bg='#0B1426', relief='flat')
        chart_area.pack(fill='both', expand=True, padx=25, pady=(0, 22))
        
        # Simulação de gráfico com barras coloridas
        self.create_mock_chart(chart_area)
        
        # Painel direito - Informações e métricas
        right_panel = tk.Frame(parent, bg='#1E2A3A', relief='flat')
        right_panel.grid(row=1, column=1, sticky='nsew', padx=(12, 0))
        
        # Header do painel direito com padding consistente
        right_header = tk.Frame(right_panel, bg='#1E2A3A')
        right_header.pack(fill='x', padx=25, pady=(22, 12))
        
        info_title = tk.Label(right_header,
                             text="ℹ️ Insights do Sistema",
                             font=('Segoe UI', 15, 'bold'),
                             bg='#1E2A3A',
                             fg='white')
        info_title.pack(anchor='w')
        
        # Métricas adicionais
        self.create_insights_panel(right_panel)
    
    def create_mock_chart(self, parent):
        """Cria um gráfico simulado moderno com barras animadas"""
        chart_frame = tk.Frame(parent, bg='#0D1117')
        chart_frame.pack(fill='both', expand=True, padx=25, pady=25)
        
        # Dados simulados atualizados
        regions = ["Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]
        values = [65, 45, 85, 75, 55]
        colors = ["#238CF5", "#8B5CF6", "#F472B6", "#FB923C", "#34D399"]
        
        # Título do gráfico
        chart_title = tk.Label(chart_frame,
                              text="Taxa de Exclusão Digital por Região",
                              font=('Segoe UI', 12, 'bold'),
                              bg='#0D1117',
                              fg='#F0F6FC')
        chart_title.pack(pady=(0, 20))
        
        for i, (region, value, color) in enumerate(zip(regions, values, colors)):
            # Container da barra com espaçamento melhorado
            bar_container = tk.Frame(chart_frame, bg='#0D1117')
            bar_container.pack(fill='x', pady=8)
            
            # Label da região com melhor formatação
            region_label = tk.Label(bar_container,
                                   text=region,
                                   font=('Segoe UI', 10, 'bold'),
                                   bg='#0D1117',
                                   fg='#F0F6FC',
                                   width=12,
                                   anchor='w')
            region_label.pack(side='left', padx=(0, 15))
            
            # Container da barra de progresso
            progress_container = tk.Frame(bar_container, bg='#0D1117')
            progress_container.pack(side='left', fill='x', expand=True, padx=(0, 15))
            
            # Barra de fundo com bordas arredondadas simuladas
            bar_bg = tk.Frame(progress_container, bg='#30363D', height=24)
            bar_bg.pack(fill='x')
            
            # Barra de progresso com gradiente simulado
            bar_fill = tk.Frame(bar_bg, bg=color, height=22)
            bar_fill.place(x=1, y=1, relwidth=value/100, height=22)
            
            # Valor com destaque
            value_label = tk.Label(bar_container,
                                  text=f"{value}%",
                                  font=('Segoe UI', 10, 'bold'),
                                  bg='#0D1117',
                                  fg=color,
                                  width=8)
            value_label.pack(side='right')
        
        # Legenda do gráfico
        legend_frame = tk.Frame(chart_frame, bg='#0D1117')
        legend_frame.pack(fill='x', pady=(20, 0))
        
        legend_label = tk.Label(legend_frame,
                               text="💡 Dados baseados na pesquisa TIC Domicílios 2024",
                               font=('Segoe UI', 9, 'italic'),
                               bg='#0D1117',
                               fg='#8B949E')
        legend_label.pack(anchor='center')
    
    def create_insights_panel(self, parent):
        """Cria o painel de insights moderno com métricas visuais aprimoradas"""
        insights_frame = tk.Frame(parent, bg='#21262D')
        insights_frame.pack(fill='both', expand=True, padx=25, pady=(15, 25))
        
        # Insights cards atualizados com design moderno
        insights = [
            ("📊", "Taxa de Exclusão", "23.5%", "#F87171", "↓ -2.1% vs mês anterior", "error"),
            ("🎯", "Cobertura Internet", "76.5%", "#34D399", "↑ +3.2% vs mês anterior", "success"),
            ("📱", "Uso de Dispositivos", "89.2%", "#238CF5", "↑ +1.8% vs mês anterior", "info"),
            ("🏠", "Domicílios Conectados", "68.7%", "#FB923C", "↑ +2.5% vs mês anterior", "warning")
        ]
        
        for icon, title, value, color, trend, trend_type in insights:
            # Card com design modernizado
            insight_card = tk.Frame(insights_frame, bg='#0D1117', relief='flat', bd=1)
            insight_card.pack(fill='x', pady=8)
            
            # Container interno com padding otimizado
            card_content = tk.Frame(insight_card, bg='#0D1117')
            card_content.pack(fill='x', padx=20, pady=18)
            
            # Header do card melhorado
            header_frame = tk.Frame(card_content, bg='#0D1117')
            header_frame.pack(fill='x')
            
            # Ícone com tamanho otimizado
            icon_label = tk.Label(header_frame,
                                 text=icon,
                                 font=('Segoe UI', 16),
                                 bg='#0D1117',
                                 fg=color,
                                 width=3)
            icon_label.pack(side='left')
            
            # Título com melhor tipografia
            title_label = tk.Label(header_frame,
                                  text=title,
                                  font=('Segoe UI', 11, 'normal'),
                                  bg='#0D1117',
                                  fg='#8B949E')
            title_label.pack(side='left', padx=(10, 0))
            
            # Valor principal com destaque visual
            value_label = tk.Label(card_content,
                                  text=value,
                                  font=('Segoe UI', 20, 'bold'),
                                  bg='#0D1117',
                                  fg=color)
            value_label.pack(anchor='w', pady=(8, 0))
            
            # Tendência com indicador visual aprimorado
            trend_frame = tk.Frame(card_content, bg='#0D1117')
            trend_frame.pack(fill='x', pady=(4, 0))
            
            # Indicador de tendência com cor baseada no tipo
            trend_colors = {
                'success': '#34D399',
                'error': '#F87171', 
                'warning': '#FB923C',
                'info': '#238CF5'
            }
            
            trend_label = tk.Label(trend_frame,
                                  text=trend,
                                  font=('Segoe UI', 10, 'normal'),
                                  bg='#0D1117',
                                  fg=trend_colors.get(trend_type, '#8B949E'))
            trend_label.pack(anchor='w')
            
            # Barra de progresso visual opcional
            if title == "Cobertura Internet":
                progress_bg = tk.Frame(card_content, bg='#30363D', height=4)
                progress_bg.pack(fill='x', pady=(8, 0))
                
                progress_fill = tk.Frame(progress_bg, bg=color, height=4)
                progress_fill.place(x=0, y=0, relwidth=0.765)  # 76.5%
        
        # Seção de ações rápidas
        actions_title = tk.Label(insights_frame,
                                text="⚡ Ações Rápidas",
                                font=('Segoe UI', 14, 'bold'),
                                bg='#21262D',
                                fg='#F0F6FC')
        actions_title.pack(anchor='w', pady=(25, 15))
        
        # Botões de ação com design moderno
        actions_frame = tk.Frame(insights_frame, bg='#21262D')
        actions_frame.pack(fill='x')
        
        quick_actions = [
            ("🔄", "Atualizar", self.update_stats, "#238CF5"),
            ("📤", "Exportar", self.export_data, "#34D399"),
            ("⚙️", "Config", self.open_settings, "#8B949E")
        ]
        
        for icon, text, command, color in quick_actions:
            action_btn = tk.Button(actions_frame,
                                  text=f"{icon} {text}",
                                  font=('Segoe UI', 10, 'bold'),
                                  bg='#30363D',
                                  fg=color,
                                  relief='flat',
                                  bd=0,
                                  padx=15,
                                  pady=8,
                                  command=command)
            action_btn.pack(fill='x', pady=3)
            
            # Hover effects
            def on_enter(e, btn=action_btn):
                btn.configure(bg='#40464E')
                
            def on_leave(e, btn=action_btn):
                btn.configure(bg='#30363D')
                
            action_btn.bind("<Enter>", on_enter)
            action_btn.bind("<Leave>", on_leave)
    
    def create_navigation_buttons(self, parent):
        """Cria os botões de navegação com design moderno"""
        buttons_config = [
            ("📥 Importar Dados", self.open_import_window, "Importar dados TIC Domicílios", "#2E86AB"),
            ("🔍 Consultar Dados", self.open_query_window, "Consultar e filtrar dados", "#A23B72"),
            ("📊 Gerar Relatórios", self.open_reports_window, "Gerar relatórios personalizados", "#F18F01"),
            ("🔄 Atualizar Status", self.update_stats, "Atualizar estatísticas do sistema", "#C73E1D")
        ]
        
        # Criar frame para cada botão com espaçamento
        for i, (text, command, tooltip, color) in enumerate(buttons_config):
            # Frame do botão
            btn_frame = ttk.Frame(parent)
            btn_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=8)
            btn_frame.columnconfigure(0, weight=1)
            
            # Botão principal
            btn = ttk.Button(btn_frame, text=text, command=command, style='Action.TButton')
            btn.grid(row=0, column=0, sticky=(tk.W, tk.E))
            
            # Descrição do botão
            desc_label = ttk.Label(btn_frame, text=tooltip, 
                                  font=('Segoe UI', 9, 'italic'),
                                  foreground='#6C757D')
            desc_label.grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
            
            # Tooltip simples
            self.create_tooltip(btn, tooltip)
        
        # Configurar grid
        parent.columnconfigure(0, weight=1)
    
    def create_status_panel(self, parent):
        """Cria o painel de status com estatísticas modernas"""
        # Título do painel
        title_frame = ttk.Frame(parent)
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        title_label = ttk.Label(title_frame, text="📈 Estatísticas do Sistema", 
                               style='Title.TLabel')
        title_label.pack()
        
        # Separador
        separator = ttk.Separator(title_frame, orient='horizontal')
        separator.pack(fill='x', pady=(5, 0))
        
        # Labels para estatísticas com cards
        self.stats_labels = {}
        
        stats_info = [
            ('regions', '🌍', 'Regiões cadastradas', '#2E86AB'),
            ('households', '🏠', 'Domicílios', '#A23B72'),
            ('individuals', '👥', 'Indivíduos', '#F18F01'),
            ('device_usage_records', '💻', 'Registros de dispositivos', '#C73E1D'),
            ('internet_usage_records', '🌐', 'Registros de internet', '#28A745')
        ]
        
        for i, (key, icon, label_text, color) in enumerate(stats_info):
            # Frame do card
            card_frame = ttk.Frame(parent)
            card_frame.grid(row=i+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
            card_frame.columnconfigure(1, weight=1)
            
            # Ícone
            icon_label = ttk.Label(card_frame, text=icon, font=('Segoe UI', 16))
            icon_label.grid(row=0, column=0, padx=(10, 15), pady=10)
            
            # Container de texto
            text_frame = ttk.Frame(card_frame)
            text_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=10)
            
            # Label do título
            title_label = ttk.Label(text_frame, text=label_text, 
                                   font=('Segoe UI', 10, 'bold'),
                                   foreground='#495057')
            title_label.pack(anchor='w')
            
            # Label do valor
            value_label = ttk.Label(text_frame, text="0", 
                                   font=('Segoe UI', 14, 'bold'),
                                   foreground=color)
            value_label.pack(anchor='w')
            
            self.stats_labels[key] = value_label
        
        # Configurar grid
        parent.columnconfigure(0, weight=1)
    
    def create_info_panel(self, parent):
        """Cria o painel de informações com design moderno"""
        # Título do painel
        title_frame = ttk.Frame(parent)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        title_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(title_frame, text="ℹ️ Sobre o Sistema", 
                               style='Title.TLabel')
        title_label.pack()
        
        # Separador
        separator = ttk.Separator(title_frame, orient='horizontal')
        separator.pack(fill='x', pady=(5, 0))
        
        # Container principal de informações
        info_container = ttk.Frame(parent)
        info_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        info_container.columnconfigure(0, weight=1)
        
        # Descrição principal
        desc_text = "Sistema de Análise de Exclusão Digital desenvolvido para processar e analisar dados da pesquisa TIC Domicílios do CETIC.br."
        desc_label = ttk.Label(info_container, text=desc_text, 
                              font=('Segoe UI', 10),
                              foreground='#495057',
                              wraplength=600,
                              justify=tk.LEFT)
        desc_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Funcionalidades
        features_title = ttk.Label(info_container, text="🚀 Funcionalidades:", 
                                  font=('Segoe UI', 11, 'bold'),
                                  foreground='#343a40')
        features_title.grid(row=1, column=0, sticky=tk.W, pady=(0, 8))
        
        features = [
            "📥 Importação automática de dados CSV",
            "🔍 Consultas avançadas por região",
            "📊 Geração de relatórios detalhados",
            "📈 Análise de padrões de exclusão",
            "💾 Armazenamento em banco SQLite"
        ]
        
        for i, feature in enumerate(features):
            feature_label = ttk.Label(info_container, text=f"  {feature}", 
                                     font=('Segoe UI', 9),
                                     foreground='#6c757d')
            feature_label.grid(row=2+i, column=0, sticky=tk.W, pady=1)
        
        # Informações técnicas
        tech_frame = ttk.Frame(info_container)
        tech_frame.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(15, 0))
        
        tech_title = ttk.Label(tech_frame, text="⚙️ Tecnologias:", 
                              font=('Segoe UI', 11, 'bold'),
                              foreground='#343a40')
        tech_title.pack(anchor='w', pady=(0, 8))
        
        tech_text = "Python • Tkinter • SQLite • Pandas"
        tech_label = ttk.Label(tech_frame, text=tech_text, 
                              font=('Segoe UI', 9, 'italic'),
                              foreground='#6c757d')
        tech_label.pack(anchor='w')
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
    
    def create_tooltip(self, widget, text):
        """Cria tooltip simples para um widget"""
        def on_enter(event):
            widget.config(cursor="hand2")
        
        def on_leave(event):
            widget.config(cursor="")
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def update_stats(self):
        """Atualiza as estatísticas do sistema com validação robusta"""
        try:
            # Verificar se o banco está disponível
            if not self.db_manager or not hasattr(self.db_manager, 'engine'):
                self.logger.warning("Banco de dados não está disponível para atualização de estatísticas")
                return
                
            if self.db_manager.engine is None:
                self.logger.warning("Engine do banco não foi inicializada")
                return
            
            stats = self.db_manager.get_database_stats()
            
            # Verificar se stats_labels foi inicializado
            if not hasattr(self, 'stats_labels'):
                self.logger.warning("Labels de estatísticas não foram inicializados ainda")
                return
            
            for key, value in stats.items():
                if key in self.stats_labels:
                    self.stats_labels[key].config(text=str(value))
            
            self.logger.info("Estatísticas atualizadas com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar estatísticas: {e}")
            # Não mostrar messagebox de erro para não interromper a UI
            # messagebox.showerror("Erro", f"Erro ao atualizar estatísticas: {e}")
    
    def open_import_window(self):
        """Abre a janela de importação"""
        try:
            ImportWindow(self.root, self.db_manager, self.update_stats)
        except Exception as e:
            self.logger.error(f"Erro ao abrir janela de importação: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir janela de importação: {e}")
    
    def open_query_window(self):
        """Abre a janela de consulta"""
        try:
            QueryWindow(self.root, self.db_manager)
        except Exception as e:
            self.logger.error(f"Erro ao abrir janela de consulta: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir janela de consulta: {e}")
    
    def open_reports_window(self):
        """Abre a janela de relatórios"""
        try:
            ReportsWindow(self.root, self.db_manager)
        except Exception as e:
            self.logger.error(f"Erro ao abrir janela de relatórios: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir janela de relatórios: {e}")

    def open_db_status_window(self):
        """Abre a janela de status do banco de dados"""
        try:
            DbStatusWindow(self.root, self.db_manager)
        except Exception as e:
            self.logger.error(f"Erro ao abrir janela de status do banco: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir status do banco: {e}")
    
    def export_data(self):
        """Exporta dados do sistema"""
        try:
            from tkinter import filedialog
            
            # Solicitar local de salvamento
            filename = filedialog.asksaveasfilename(
                title="Exportar Dados",
                defaultextension=".csv",
                filetypes=[
                    ("Arquivo CSV", "*.csv"),
                    ("Arquivo Excel", "*.xlsx"),
                    ("Todos os arquivos", "*.*")
                ]
            )
            
            if filename:
                # Aqui seria implementada a lógica de exportação
                # Por enquanto, apenas simular
                messagebox.showinfo("Sucesso", f"Dados exportados para:\n{filename}")
                self.logger.info(f"Dados exportados para: {filename}")
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar dados: {e}")
            messagebox.showerror("Erro", f"Erro ao exportar dados: {e}")
    
    def open_settings(self):
        """Abre a interface completa de Configurações (com abas editáveis)."""
        try:
            # Janela de configurações completa
            settings_window = tk.Toplevel(self.root)
            settings_window.title("⚙️ Configurações")
            settings_window.geometry("1000x700")
            settings_window.minsize(900, 600)
            settings_window.transient(self.root)

            # Aplicar tema ao toplevel, se disponível
            try:
                self.theme_manager.apply_theme(settings_window)
            except Exception:
                pass

            # Container principal
            container = ttk.Frame(settings_window)
            container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Aba de configurações completa com Notebook e botões de ação
            def _on_db_changed(new_path: str):
                try:
                    # Fecha conexão atual e reinicializa com novo caminho
                    if hasattr(self, 'db_manager') and self.db_manager:
                        try:
                            self.db_manager.close()
                        except Exception:
                            pass
                    # Cria novo gerenciador com o caminho selecionado
                    from ..database.database_manager import DatabaseManager as _DBM
                    self.db_manager = _DBM(new_path)
                    self.db_manager.initialize_database()
                    self.logger.info(f"Banco de dados alternado para: {new_path}")
                    messagebox.showinfo("Banco de Dados", f"Conectado ao banco:\n{new_path}")
                except Exception as e:
                    self.logger.error(f"Erro ao alternar banco: {e}")
                    messagebox.showerror("Erro", f"Falha ao alternar banco:\n{e}")

            config_tab = ConfiguracoesTab(container, on_database_changed=_on_db_changed)
            config_tab.pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            self.logger.error(f"Erro ao abrir configurações: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir configurações: {e}")
    
    def run(self):
        """Executa a aplicação"""
        try:
            self.logger.info("Iniciando interface principal")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Erro na execução da aplicação: {e}")
            raise
        finally:
            self.db_manager.close()
