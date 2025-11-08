# -*- coding: utf-8 -*-
"""
Janela de geração de relatórios - Sistema DAC
Versão aprimorada com visualizações interativas e análises avançadas
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime
import json
import os
from typing import Dict, List, Optional, Any, Tuple
from ..utils.logger import get_logger
from ..database.models import Individual, Household, Region, DeviceUsage
from .icons import get_icon, get_icon_color

class ReportsWindow:
    """Janela para geração de relatórios com visualizações avançadas e análises interativas"""
    
    def __init__(self, parent, db_manager, filtered_data: Optional[List] = None):
        self.parent = parent
        self.db_manager = db_manager
        self.filtered_data = filtered_data
        self.logger = get_logger(__name__)
        
        # Configurações de visualização com tema moderno - GRÁFICOS MENORES
        self.chart_config = {
            'figure_size': (4.5, 3),  # Ainda menor para caber melhor
            'dpi': 80,  # Reduzido ainda mais
            'style': 'seaborn-v0_8',
            'color_palette': ['#00D4FF', '#8B5CF6', '#EC4899', '#F59E0B', '#10B981']
        }
        
        # Paleta de cores moderna atualizada
        self.colors = {
            'bg_primary': '#0D1117',      # Fundo principal escuro atualizado
            'bg_secondary': '#161B22',    # Fundo secundário
            'bg_card': '#21262D',         # Fundo dos cards
            'bg_hover': '#30363D',        # Fundo hover
            'accent_blue': '#238CF5',     # Azul moderno
            'accent_purple': '#8B5CF6',   # Roxo vibrante
            'accent_pink': '#F472B6',     # Rosa vibrante
            'accent_orange': '#FB923C',   # Laranja vibrante
            'accent_green': '#34D399',    # Verde vibrante
            'text_primary': '#F0F6FC',    # Texto principal
            'text_secondary': '#8B949E',  # Texto secundário
            'text_muted': '#6E7681',      # Texto esmaecido
            'border': '#30363D'           # Bordas
        }
        
        # Cache de dados processados
        self.processed_data: Dict[str, Any] = {}
        self.statistics: Dict[str, Any] = {}
        
        # Variáveis de controle
        self.data: List = []
        self.export_format = tk.StringVar(value="PDF")
        self.chart_type = tk.StringVar(value="bar")
        
        # Criar janela com estilo moderno
        self.window = tk.Toplevel(parent)
        self.window.title("� Relatórios Avançados - Sistema DAC")
        # Tamanho aumentado para melhor visualização
        self.window.geometry("1350x800")
        # Tornar redimensionável e definir um tamanho mínimo para evitar cortes
        try:
            self.window.minsize(1100, 700)
        except Exception:
            pass
        self.window.resizable(True, True)
        self.window.configure(bg=self.colors['bg_primary'])
        self.window.transient(parent)
        self.window.grab_set()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configurar estilos modernos
        self.setup_modern_styles()
        
        # Configurar estilo matplotlib
        self.setup_matplotlib_style()
        
        # Centralizar janela
        self.center_window()
        
        # Configurar atalhos de teclado
        self.setup_keyboard_shortcuts()
        
        # Criar widgets
        self.create_widgets()
        
        # Carregar dados e gerar relatórios
        self.load_data_and_generate_reports()

    def _bind_resize_redraw(self, frame, redraw_fn):
        """Associa evento de redimensionamento para redesenhar o gráfico no frame."""
        try:
            def _on_resize(event):
                # Regerar gráfico ao mudar tamanho, mantendo funcionalidades
                for widget in frame.winfo_children():
                    widget.destroy()
                try:
                    redraw_fn()
                except Exception:
                    # Evitar quebra em resize
                    pass
            frame.bind("<Configure>", _on_resize)
        except Exception:
            pass

    def _get_dynamic_figsize(self, frame, base: Tuple[float, float] = (8, 6), padding_px: int = 24) -> Tuple[float, float]:
        """Calcula figsize (em polegadas) com base no tamanho atual do frame.
        Aplica limites mínimos e máximos para manter legibilidade.
        """
        try:
            frame.update_idletasks()
            dpi = float(plt.rcParams.get('figure.dpi', 100))
            width_px = max(frame.winfo_width() - padding_px, 300)
            height_px = max(frame.winfo_height() - padding_px, 240)

            width_in = width_px / dpi
            height_in = height_px / dpi

            # Limites para legibilidade
            min_w, min_h = 5.5, 4.0
            max_w, max_h = 16.0, 10.0

            width_in = min(max(width_in, min_w), max_w)
            height_in = min(max(height_in, min_h), max_h)

            # Se tamanho ainda é muito pequeno (ex: primeira renderização), usar base
            if width_px <= 320 or height_px <= 260:
                return base

            return (width_in, height_in)
        except Exception:
            return base
    
    def show(self):
        """Exibe a janela de relatórios"""
        try:
            self.window.deiconify()  # Mostra a janela se estiver minimizada
            self.window.lift()       # Traz a janela para frente
            self.window.focus_set()  # Define o foco na janela
            self.logger.info("Janela de relatórios exibida")
        except Exception as e:
            self.logger.error(f"Erro ao exibir janela de relatórios: {e}")
        
    def setup_modern_styles(self):
        """Configura os estilos modernos da interface"""
        style = ttk.Style()
        
        # Configurar tema base
        style.theme_use('clam')
        
        # Configurar estilos base
        style.configure('TLabel', 
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'])
        
        style.configure('TFrame', 
                       background=self.colors['bg_primary'])
        
        # Título principal
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 20, 'bold'),
                       foreground=self.colors['text_primary'],
                       background=self.colors['bg_primary'])
        
        # Subtítulos
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 12, 'normal'),
                       foreground=self.colors['text_secondary'],
                       background=self.colors['bg_primary'])
        
        # Cards modernos
        style.configure('Card.TFrame',
                       background=self.colors['bg_card'],
                       relief='flat',
                       borderwidth=0)
        
        style.configure('Card.TLabelFrame',
                       background=self.colors['bg_card'],
                       relief='flat',
                       borderwidth=1,
                       lightcolor=self.colors['border'],
                       darkcolor=self.colors['border'])
        
        style.configure('Card.TLabelFrame.Label',
                       font=('Segoe UI', 12, 'bold'),
                       foreground=self.colors['text_primary'],
                       background=self.colors['bg_card'])
        
        # Botões modernos
        style.configure('Modern.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(15, 10),
                       relief='flat',
                       background=self.colors['accent_blue'],
                       foreground='white',
                       borderwidth=0)
        
        style.map('Modern.TButton',
                 background=[('active', self.colors['accent_purple']),
                           ('pressed', self.colors['accent_pink'])],
                 foreground=[('active', 'white'),
                           ('pressed', 'white')])
        
        # Notebook (abas)
        style.configure('TNotebook',
                       background=self.colors['bg_primary'],
                       borderwidth=0)
        
        style.configure('TNotebook.Tab',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_secondary'],
                       padding=(20, 10),
                       font=('Segoe UI', 10, 'normal'))
        
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['bg_card']),
                           ('active', self.colors['accent_blue'])],
                 foreground=[('selected', self.colors['text_primary']),
                           ('active', 'white')])
    
    def setup_matplotlib_style(self):
        """Configura o estilo do matplotlib com tema escuro"""
        try:
            plt.style.use('dark_background')
        except OSError:
            plt.style.use('default')
        
        # Configurações globais para tema escuro
        plt.rcParams.update({
            'figure.facecolor': self.colors['bg_card'],
            'axes.facecolor': self.colors['bg_card'],
            'axes.edgecolor': self.colors['border'],
            'axes.linewidth': 1,
            'axes.grid': True,
            'grid.color': self.colors['border'],
            'grid.alpha': 0.3,
            'text.color': self.colors['text_primary'],
            'axes.labelcolor': self.colors['text_primary'],
            'xtick.color': self.colors['text_secondary'],
            'ytick.color': self.colors['text_secondary'],
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9
        })
    
    def setup_keyboard_shortcuts(self):
        """Configura atalhos de teclado"""
        self.window.bind('<Control-s>', lambda e: self.export_pdf_report())
        self.window.bind('<Control-e>', lambda e: self.export_excel_report())
        self.window.bind('<F5>', lambda e: self.refresh_reports())
        self.window.bind('<Escape>', lambda e: self.window.destroy())
    
    def on_closing(self):
        """Trata o fechamento da janela"""
        try:
            # Limpar figuras matplotlib para liberar memória
            plt.close('all')
            self.window.destroy()
        except Exception as e:
            self.logger.error(f"Erro ao fechar janela de relatórios: {e}")
            self.window.destroy()
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.window.update_idletasks()
        width = 1280
        height = 750
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Cria os widgets da interface com design moderno"""
        # Frame principal com padding maior
        main_frame = ttk.Frame(self.window, padding="25")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid responsivo
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Cabeçalho moderno com mais destaque
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        # Título com estilo moderno e maior
        title_label = ttk.Label(header_frame, text="� Relatórios Avançados - Sistema DAC", 
                               style='Title.TLabel',
                               font=('Segoe UI', 20, 'bold'))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Status dos dados com estilo moderno e destaque
        self.status_label = ttk.Label(header_frame, text="🔄 Carregando dados...", 
                                     style='Subtitle.TLabel',
                                     font=('Segoe UI', 11))
        self.status_label.grid(row=0, column=1, sticky=tk.E)
        
        # Frame de controles com padding e espaçamento maior
        controls_frame = ttk.LabelFrame(main_frame, text="🎛️ Controles de Visualização", 
                                       padding="18")
        controls_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        controls_frame.columnconfigure(3, weight=1)
        
        # Tipo de gráfico com labels maiores
        ttk.Label(controls_frame, text="📊 Tipo de Gráfico:", 
                 font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, padx=(0, 10))
        chart_combo = ttk.Combobox(controls_frame, textvariable=self.chart_type, 
                                  values=["bar", "pie", "line", "scatter"], 
                                  state="readonly", width=14, font=('Segoe UI', 10))
        chart_combo.grid(row=0, column=1, padx=(0, 35))
        chart_combo.bind('<<ComboboxSelected>>', self.on_chart_type_changed)
        
        # Formato de exportação
        ttk.Label(controls_frame, text="💾 Formato:", 
                 font=('Segoe UI', 10, 'bold')).grid(row=0, column=2, padx=(0, 10))
        format_combo = ttk.Combobox(controls_frame, textvariable=self.export_format,
                                   values=["PDF", "Excel", "PNG", "SVG"], 
                                   state="readonly", width=14, font=('Segoe UI', 10))
        format_combo.grid(row=0, column=3, padx=(0, 35))
        
        # Botões de controle maiores
        ttk.Button(controls_frame, text="🔄 Atualizar (F5)", 
                  style='Modern.TButton',
                  command=self.refresh_reports).grid(row=0, column=4, padx=(0, 15))
        
        ttk.Button(controls_frame, text="⚙️ Configurações", 
                  style='Modern.TButton',
                  command=self.show_settings).grid(row=0, column=5)
        
        # Notebook para abas com tabs maiores
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        
        # Criar abas
        self.create_overview_tab()
        self.create_statistics_tab()
        self.create_demographics_tab()
        self.create_digital_access_tab()
        self.create_regional_tab()
        self.create_analysis_tab()
        
        # Frame de botões com mais espaço
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, pady=(8, 0))
        
        # Guardar referência aos botões para controlar estado habilitado/desabilitado
        self.export_pdf_btn = ttk.Button(
            buttons_frame,
            text="📄 PDF",
            style='Modern.TButton',
            command=self.export_pdf_report
        )
        self.export_pdf_btn.grid(row=0, column=0, padx=(0, 10))

        self.export_excel_btn = ttk.Button(
            buttons_frame,
            text="📊 Excel",
            style='Modern.TButton',
            command=self.export_excel_report
        )
        self.export_excel_btn.grid(row=0, column=1, padx=(0, 10))

        # Inicialmente desabilitado até dados carregarem
        self.export_pdf_btn.configure(state='disabled')
        self.export_excel_btn.configure(state='disabled')

        ttk.Button(
            buttons_frame,
            text="💾 Salvar",
            style='Modern.TButton',
            command=self.save_settings
        ).grid(row=0, column=2, padx=(0, 10))

        ttk.Button(
            buttons_frame,
            text="❌ Fechar",
            style='Modern.TButton',
            command=self.window.destroy
        ).grid(row=0, column=3)
    
    def create_overview_tab(self):
        """Cria a aba de visão geral com resumo executivo"""
        # Container principal SEM scroll, usando grid responsivo
        container = ttk.Frame(self.notebook)
        self.notebook.add(container, text="📊 Visão Geral")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=0)
        container.rowconfigure(1, weight=1)
        
        # Frame para métricas principais
        metrics_frame = ttk.LabelFrame(container, text="📈 Métricas", 
                                      padding="8", style='Card.TLabelframe')
        metrics_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        # Cards de métricas
        self.create_metric_cards(metrics_frame)
        
        # Frame para gráfico de resumo - COMPACTO
        summary_chart_frame = ttk.LabelFrame(container, text="Resumo Visual", padding="5")
        summary_chart_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=3)
        
        self.overview_chart_frame = summary_chart_frame
        # Redesenhar ao redimensionar
        self._bind_resize_redraw(self.overview_chart_frame, self.generate_overview_chart)
    
    def create_metric_cards(self, parent):
        """Cria cards com métricas principais"""
        # Frame para os cards compactos
        cards_frame = ttk.Frame(parent)
        cards_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=3)
        
        # Card 1 - Total de registros compacto
        self.total_card = ttk.LabelFrame(cards_frame, text="📊 Total", 
                                        padding="8", style='Card.TLabelframe')
        self.total_card.grid(row=0, column=0, padx=5, pady=3)
        self.total_value = ttk.Label(self.total_card, text="0", 
                                     font=('Segoe UI', 18, 'bold'), foreground='#238CF5')
        self.total_value.grid(row=0, column=0)
        
        # Card 2 - Acesso à Internet compacto
        self.internet_card = ttk.LabelFrame(cards_frame, text="🌐 Internet", 
                                           padding="8", style='Card.TLabelframe')
        self.internet_card.grid(row=0, column=1, padx=5, pady=3)
        self.internet_value = ttk.Label(self.internet_card, text="0%", 
                                       font=('Segoe UI', 18, 'bold'), foreground='#34D399')
        self.internet_value.grid(row=0, column=0)
        
        # Card 3 - Pessoas com Deficiência compacto
        self.disability_card = ttk.LabelFrame(cards_frame, text="♿ Deficiência", 
                                             padding="8", style='Card.TLabelframe')
        self.disability_card.grid(row=0, column=2, padx=5, pady=3)
        self.disability_value = ttk.Label(self.disability_card, text="0%", 
                                         font=('Segoe UI', 18, 'bold'), foreground='#FB923C')
        self.disability_value.grid(row=0, column=0)
        
        # Card 4 - Idade Média compacto
        self.age_card = ttk.LabelFrame(cards_frame, text="👥 Idade", 
                                      padding="8", style='Card.TLabelframe')
        self.age_card.grid(row=0, column=3, padx=5, pady=3)
        self.age_value = ttk.Label(self.age_card, text="0", 
                                  font=('Segoe UI', 18, 'bold'), foreground='#8B5CF6')
        self.age_value.grid(row=0, column=0)
    
    def on_chart_type_changed(self, event=None):
        """Callback para mudança do tipo de gráfico"""
        try:
            self.refresh_current_tab()
        except Exception as e:
            self.logger.error(f"Erro ao alterar tipo de gráfico: {e}")
    
    def refresh_reports(self):
        """Atualiza todos os relatórios"""
        try:
            self.status_label.config(text="Atualizando relatórios...", foreground='orange')
            self.window.update()
            
            # Recarregar dados
            self.load_data_and_generate_reports()
            
            self.status_label.config(text="Relatórios atualizados com sucesso!", foreground='green')
            self.window.after(3000, lambda: self.status_label.config(text="Pronto", foreground='blue'))
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar relatórios: {e}")
            self.status_label.config(text="Erro na atualização", foreground='red')
            messagebox.showerror("Erro", f"Erro ao atualizar relatórios: {e}")
    
    def refresh_current_tab(self):
        """Atualiza apenas a aba atual"""
        try:
            current_tab = self.notebook.select()
            tab_text = self.notebook.tab(current_tab, "text")
            
            if "Visão Geral" in tab_text:
                self.generate_overview_chart()
            elif "Estatísticas" in tab_text:
                self.generate_gender_chart()
            elif "Demografia" in tab_text:
                self.generate_age_chart()
                self.generate_income_chart()
            elif "Acesso Digital" in tab_text:
                self.generate_internet_chart()
                self.generate_devices_chart()
            elif "Regional" in tab_text:
                self.generate_regional_chart()
            elif "Análise" in tab_text:
                self.generate_correlation_analysis()
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar aba atual: {e}")
    
    def show_settings(self):
        """Mostra janela de configurações com estilo moderno"""
        settings_window = tk.Toplevel(self.window)
        settings_window.title("⚙️ Configurações de Relatórios")
        settings_window.geometry("500x400")
        settings_window.configure(bg='#2B2B2B')
        settings_window.transient(self.window)
        settings_window.grab_set()
        settings_window.resizable(False, False)
        
        # Centralizar janela
        x = self.window.winfo_x() + 50
        y = self.window.winfo_y() + 50
        settings_window.geometry(f"500x400+{x}+{y}")
        
        # Aplicar estilos modernos à janela de configurações
        style = ttk.Style()
        
        # Conteúdo das configurações
        main_frame = ttk.Frame(settings_window, padding="30")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título principal
        ttk.Label(main_frame, text="Configurações de Visualização", 
                 style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Seção de cores
        colors_frame = ttk.LabelFrame(main_frame, text="🎨 Aparência", padding="15")
        colors_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(colors_frame, text="Paleta de Cores:").grid(row=0, column=0, sticky=tk.W, pady=5)
        color_var = tk.StringVar(value="Padrão")
        color_combo = ttk.Combobox(colors_frame, textvariable=color_var,
                                  values=["Padrão", "Vibrante", "Pastel", "Monocromático"],
                                  state="readonly", width=20)
        color_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(colors_frame, text="Tamanho dos Gráficos:").grid(row=1, column=0, sticky=tk.W, pady=5)
        size_var = tk.StringVar(value="Médio")
        size_combo = ttk.Combobox(colors_frame, textvariable=size_var,
                                 values=["Pequeno", "Médio", "Grande"],
                                 state="readonly", width=20)
        size_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Seção de exportação
        export_frame = ttk.LabelFrame(main_frame, text="📊 Exportação", padding="15")
        export_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(export_frame, text="Formato Padrão:").grid(row=0, column=0, sticky=tk.W, pady=5)
        format_var = tk.StringVar(value="PDF")
        format_combo = ttk.Combobox(export_frame, textvariable=format_var,
                                   values=["PDF", "Excel", "PNG", "SVG"],
                                   state="readonly", width=20)
        format_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Botões com estilo moderno
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=(30, 0))
        
        ttk.Button(buttons_frame, text="✅ Aplicar", 
                  style='Modern.TButton',
                  command=lambda: self.apply_settings(color_var.get(), size_var.get(), format_var.get(), settings_window)).grid(row=0, column=0, padx=(0, 15))
        ttk.Button(buttons_frame, text="❌ Cancelar", 
                  style='Modern.TButton',
                  command=settings_window.destroy).grid(row=0, column=1)
    
    def apply_settings(self, color_palette, chart_size, export_format, settings_window):
        """Aplica as configurações selecionadas"""
        try:
            # Atualizar configurações de cores
            if color_palette == "Vibrante":
                self.chart_config['color_palette'] = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            elif color_palette == "Pastel":
                self.chart_config['color_palette'] = ['#FFB3BA', '#BAFFC9', '#BAE1FF', '#FFFFBA', '#FFD1FF']
            elif color_palette == "Monocromático":
                self.chart_config['color_palette'] = ['#2C3E50', '#34495E', '#5D6D7E', '#85929E', '#AEB6BF']
            else:  # Padrão
                self.chart_config['color_palette'] = ['#3498DB', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6']
            
            # Atualizar tamanho dos gráficos
            if chart_size == "Pequeno":
                self.chart_config['figure_size'] = (8, 5)
            elif chart_size == "Grande":
                self.chart_config['figure_size'] = (12, 8)
            else:  # Médio
                self.chart_config['figure_size'] = (10, 6)
            
            # Salvar formato de exportação padrão
            self.default_export_format = export_format.lower()
            
            # Atualizar gráficos com novas configurações
            self.refresh_current_tab()
            
            settings_window.destroy()
            messagebox.showinfo("✅ Sucesso", "Configurações aplicadas com sucesso!")
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar configurações: {e}")
            messagebox.showerror("❌ Erro", f"Erro ao aplicar configurações: {e}")
    
    def save_settings(self):
        """Salva as configurações atuais"""
        try:
            settings = {
                'chart_config': self.chart_config,
                'export_format': self.export_format.get(),
                'chart_type': self.chart_type.get(),
                'timestamp': datetime.now().isoformat()
            }
            
            # Criar diretório de configurações se não existir
            config_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'config')
            os.makedirs(config_dir, exist_ok=True)
            
            # Salvar configurações
            config_file = os.path.join(config_dir, 'reports_settings.json')
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            self.logger.info("Configurações de relatórios salvas")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")
    
    def create_analysis_tab(self):
        """Cria a aba de análise avançada"""
        # Container principal sem scroll, com grid
        container = ttk.Frame(self.notebook)
        self.notebook.add(container, text="🔍 Análise Avançada")
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)
        
        # Frame para análise de correlação - COMPACTO
        correlation_frame = ttk.LabelFrame(container, text="Análise de Correlação", padding="5")
        correlation_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=3, pady=3)
        
        self.correlation_chart_frame = correlation_frame
        
        # Frame para tendências - COMPACTO
        trends_frame = ttk.LabelFrame(container, text="Análise de Tendências", padding="5")
        trends_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=3, pady=3)
        
        self.trends_chart_frame = trends_frame
    
    def create_statistics_tab(self):
        """Cria a aba de estatísticas gerais"""
        # Container principal sem scroll
        container = ttk.Frame(self.notebook)
        self.notebook.add(container, text="📈 Estatísticas Gerais")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=0)
        container.rowconfigure(1, weight=1)
        
        # Frame para estatísticas numéricas - COMPACTO
        numbers_frame = ttk.LabelFrame(container, text="📊 Resumo", 
                                      padding="3", style='Card.TLabelframe')
        numbers_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=3, pady=2)
        
        self.stats_text = tk.Text(numbers_frame, height=4, width=90, 
                                 font=('Consolas', 8), bg='#21262D', fg='#F0F6FC',
                                 relief='flat', borderwidth=0)
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=2, pady=2)
        
        # Scrollbar para o texto
        stats_scrollbar = ttk.Scrollbar(numbers_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        stats_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Frame para gráfico de pizza - COMPACTO
        self.stats_chart_frame = ttk.LabelFrame(container, text="👥 Distribuição por Gênero", 
                                               padding="3", style='Card.TLabelframe')
        self.stats_chart_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                                    padx=3, pady=2)
        # Redesenhar ao redimensionar
        self._bind_resize_redraw(self.stats_chart_frame, self.generate_gender_chart)
    
    def create_demographics_tab(self):
        """Cria a aba de dados demográficos"""
        # Container principal sem scroll, com grid responsivo
        container = ttk.Frame(self.notebook)
        self.notebook.add(container, text="👥 Demografia")
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)
        
        # Frame para gráfico de idade - COMPACTO
        self.age_chart_frame = ttk.LabelFrame(container, text="📅 Faixa Etária", 
                                             padding="5", style='Card.TLabelframe')
        self.age_chart_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=3, pady=3)
        # Redesenhar ao redimensionar
        self._bind_resize_redraw(self.age_chart_frame, self.generate_age_chart)
        
        # Frame para gráfico de renda - COMPACTO
        self.income_chart_frame = ttk.LabelFrame(container, text="💰 Renda", 
                                                padding="5", style='Card.TLabelframe')
        self.income_chart_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=3, pady=3)
        # Redesenhar ao redimensionar
        self._bind_resize_redraw(self.income_chart_frame, self.generate_income_chart)
    
    def create_digital_access_tab(self):
        """Cria a aba de acesso digital"""
        # Container principal sem scroll, com grid responsivo
        container = ttk.Frame(self.notebook)
        self.notebook.add(container, text="Acesso Digital")
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)
        
        # Frame para gráfico de internet - COMPACTO
        self.internet_chart_frame = ttk.LabelFrame(container, text="Acesso à Internet", padding="5")
        self.internet_chart_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=3, pady=3)
        # Redesenhar ao redimensionar
        self._bind_resize_redraw(self.internet_chart_frame, self.generate_internet_chart)
        
        # Frame para gráfico de dispositivos - COMPACTO
        self.devices_chart_frame = ttk.LabelFrame(container, text="Uso de Dispositivos", padding="5")
        self.devices_chart_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=3, pady=3)
        # Redesenhar ao redimensionar
        self._bind_resize_redraw(self.devices_chart_frame, self.generate_devices_chart)
    
    def create_regional_tab(self):
        """Cria a aba de análise regional"""
        # Container principal sem scroll
        container = ttk.Frame(self.notebook)
        self.notebook.add(container, text="Análise Regional")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)
        
        # Frame para gráfico regional - COMPACTO
        self.regional_chart_frame = ttk.LabelFrame(container, text="Distribuição por Região", padding="5")
        self.regional_chart_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=3)
        # Redesenhar ao redimensionar
        self._bind_resize_redraw(self.regional_chart_frame, self.generate_regional_chart)
    
    def load_data_and_generate_reports(self, filtered_data=None):
        """Carrega dados e gera relatórios com tratamento robusto de erros"""
        try:
            # Verificar se o gerenciador de banco está disponível
            if not self.db_manager:
                self.logger.error("Gerenciador de banco de dados não disponível")
                messagebox.showerror("Erro", "Sistema de banco de dados não está disponível.")
                return
            
            if filtered_data:
                # Usar dados filtrados passados como parâmetro
                self.data = filtered_data
                self.logger.info(f"Carregados {len(filtered_data)} registros filtrados")
            elif self.filtered_data:
                # Usar dados filtrados da instância
                self.data = self.filtered_data
            else:
                # Carregar todos os dados do banco com eager loading
                try:
                    with self.db_manager.get_session() as session:
                        from sqlalchemy.orm import joinedload
                        query_result = session.query(Individual)\
                            .options(joinedload(Individual.household)\
                                    .joinedload(Household.region))\
                            .options(joinedload(Individual.household)\
                                    .joinedload(Household.region))\
                            .options(joinedload(Individual.device_usage))\
                            .all()
                        
                        if not query_result:
                            self.logger.warning("Nenhum dado encontrado no banco")
                            messagebox.showwarning("Aviso", "Nenhum dado encontrado no banco de dados.")
                            self.data = []
                            return
                        
                        # Fazer uma cópia dos dados para uso fora da sessão
                        data_copy = []
                        errors_count = 0
                        
                        for individual in query_result:
                            try:
                                # Acessar todos os atributos necessários enquanto na sessão
                                household_data = {
                                    'income_range': None,
                                    'has_internet': False,
                                    'region_name': 'N/A',
                                    'devices': []
                                }
                                
                                if hasattr(individual, 'household') and individual.household:
                                    household_data['income_range'] = getattr(individual.household, 'income_range', None)
                                    household_data['has_internet'] = getattr(individual.household, 'has_internet', False)
                                    
                                    # Região
                                    if hasattr(individual.household, 'region') and individual.household.region:
                                        household_data['region_name'] = getattr(individual.household.region, 'name', 'N/A')
                                    
                                    # Dispositivos do indivíduo
                                    if hasattr(individual, 'device_usage') and individual.device_usage:
                                        try:
                                            devices = [d.device_type for d in individual.device_usage if hasattr(d, 'device_type')]
                                            household_data['devices'] = devices
                                        except Exception:
                                            household_data['devices'] = []
                                
                                individual_data = {
                                    'id': getattr(individual, 'id', None),
                                    'age': getattr(individual, 'age', None),
                                    'gender': getattr(individual, 'gender', None),
                                    'has_disability': getattr(individual, 'has_disability', False),
                                    'household': household_data
                                }
                                data_copy.append(individual_data)
                                
                            except Exception as process_error:
                                self.logger.error(f"Erro ao processar registro individual: {process_error}")
                                errors_count += 1
                                continue
                        
                        self.data = data_copy
                        self.logger.info(f"Carregados {len(data_copy)} registros do banco")
                        
                        if errors_count > 0:
                            self.logger.warning(f"{errors_count} registros tiveram problemas no processamento")
                            messagebox.showwarning("Aviso", f"{errors_count} registros tiveram problemas e foram ignorados.")
                        
                except Exception as db_error:
                    self.logger.error(f"Erro ao consultar banco de dados: {db_error}")
                    messagebox.showerror("Erro", f"Erro ao acessar banco de dados: {db_error}")
                    return
            
            if not self.data:
                self.logger.warning("Nenhum dado válido para gerar relatórios")
                messagebox.showwarning("Aviso", "Nenhum dado válido encontrado para gerar relatórios.")
                # Desabilitar exportações
                self._update_export_buttons(enabled=False)
                return
            
            # Gerar estatísticas e gráficos
            self.logger.info("Iniciando geração de relatórios")
            try:
                self.generate_statistics()
                self.generate_gender_chart()
                self.generate_age_chart()
                self.generate_income_chart()
                self.generate_internet_chart()
                self.generate_devices_chart()
                self.generate_regional_chart()
                self.logger.info("Relatórios gerados com sucesso")
                # Habilitar exportações pois há dados carregados e gráficos gerados
                self._update_export_buttons(enabled=True)
            except Exception as chart_error:
                self.logger.error(f"Erro ao gerar gráficos: {chart_error}")
                messagebox.showerror("Erro", f"Erro ao gerar gráficos: {chart_error}")
            
        except Exception as e:
            self.logger.error(f"Erro geral ao carregar dados: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")
            self._update_export_buttons(enabled=False)

    def _update_export_buttons(self, enabled: bool):
        """Ativa ou desativa botões de exportação conforme disponibilidade de dados."""
        state = 'normal' if enabled else 'disabled'
        try:
            if hasattr(self, 'export_pdf_btn'):
                self.export_pdf_btn.configure(state=state)
            if hasattr(self, 'export_excel_btn'):
                self.export_excel_btn.configure(state=state)
            # Atualizar texto de status
            if enabled:
                self.status_label.configure(text="Pronto para exportar", foreground='green')
            else:
                self.status_label.configure(text="Sem dados para exportação", foreground='orange')
        except Exception:
            pass
    
    def generate_statistics(self):
        """Gera estatísticas dos dados com tratamento robusto de erros"""
        if not self.data:
            self.logger.warning("Nenhum dado disponível para gerar estatísticas")
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, "Nenhum dado disponível para gerar estatísticas.")
            return
        
        try:
            total = len(self.data)
            errors_count = 0
            
            # Estatísticas por gênero
            gender_counts = {}
            for individual in self.data:
                try:
                    if isinstance(individual, dict):
                        gender = individual.get('gender') or 'Não informado'
                    else:
                        gender = getattr(individual, 'gender', None) or 'Não informado'
                    gender_counts[gender] = gender_counts.get(gender, 0) + 1
                except Exception as e:
                    self.logger.error(f"Erro ao processar gênero: {e}")
                    errors_count += 1
                    gender_counts['Não informado'] = gender_counts.get('Não informado', 0) + 1
            
            # Estatísticas por idade
            ages = []
            for individual in self.data:
                try:
                    if isinstance(individual, dict):
                        age = individual.get('age')
                    else:
                        age = getattr(individual, 'age', None)
                    
                    if age is not None and isinstance(age, (int, float)) and 0 <= age <= 150:
                        ages.append(age)
                except Exception as e:
                    self.logger.error(f"Erro ao processar idade: {e}")
                    errors_count += 1
            
            avg_age = sum(ages) / len(ages) if ages else 0
            
            # Estatísticas por deficiência
            disability_count = 0
            for individual in self.data:
                try:
                    if isinstance(individual, dict):
                        has_disability = individual.get('has_disability', False)
                    else:
                        has_disability = getattr(individual, 'has_disability', False)
                    
                    if has_disability:
                        disability_count += 1
                except Exception as e:
                    self.logger.error(f"Erro ao processar deficiência: {e}")
                    errors_count += 1
            
            # Estatísticas de internet
            internet_count = 0
            for individual in self.data:
                try:
                    if isinstance(individual, dict):
                        has_internet = individual.get('household', {}).get('has_internet', False)
                    else:
                        household = getattr(individual, 'household', None)
                        has_internet = getattr(household, 'has_internet', False) if household else False
                    
                    if has_internet:
                        internet_count += 1
                except Exception as e:
                    self.logger.error(f"Erro ao processar internet: {e}")
                    errors_count += 1
            
            # Estatísticas por renda
            income_counts = {}
            for individual in self.data:
                try:
                    if isinstance(individual, dict):
                        income = individual.get('household', {}).get('income_range') or 'Não informado'
                    else:
                        household = getattr(individual, 'household', None)
                        income = getattr(household, 'income_range', None) if household else None
                        income = income or 'Não informado'
                    
                    income_counts[income] = income_counts.get(income, 0) + 1
                except Exception as e:
                    self.logger.error(f"Erro ao processar renda: {e}")
                    errors_count += 1
                    income_counts['Não informado'] = income_counts.get('Não informado', 0) + 1
            
            # Montar texto das estatísticas
            stats_text = f"""RELATÓRIO ESTATÍSTICO - SISTEMA DAC
{'='*50}

TOTAL DE REGISTROS: {total}
"""
            
            if errors_count > 0:
                stats_text += f"REGISTROS COM PROBLEMAS: {errors_count}\n"
            
            stats_text += f"""\nDISTRIBUIÇÃO POR GÊNERO:
{'-'*30}
"""
            
            for gender, count in gender_counts.items():
                try:
                    percentage = (count / total) * 100 if total > 0 else 0
                    stats_text += f"{gender}: {count} ({percentage:.1f}%)\n"
                except Exception as e:
                    self.logger.error(f"Erro ao calcular percentual de gênero: {e}")
                    stats_text += f"{gender}: {count} (erro no cálculo)\n"
            
            stats_text += f"""\nESTATÍSTICAS DE IDADE:
{'-'*30}
Idade média: {avg_age:.1f} anos
Total com idade válida: {len(ages)}
Total sem idade: {total - len(ages)}

PESSOAS COM DEFICIÊNCIA:
{'-'*30}"""
            
            try:
                disability_percentage = (disability_count/total)*100 if total > 0 else 0
                no_disability_percentage = ((total-disability_count)/total)*100 if total > 0 else 0
                stats_text += f"""Com deficiência: {disability_count} ({disability_percentage:.1f}%)
Sem deficiência: {total-disability_count} ({no_disability_percentage:.1f}%)
"""
            except Exception as e:
                self.logger.error(f"Erro ao calcular percentuais de deficiência: {e}")
                stats_text += f"""Com deficiência: {disability_count}
Sem deficiência: {total-disability_count}
"""
            
            stats_text += f"""\nACESSO À INTERNET:
{'-'*30}"""
            
            try:
                internet_percentage = (internet_count/total)*100 if total > 0 else 0
                no_internet_percentage = ((total-internet_count)/total)*100 if total > 0 else 0
                stats_text += f"""Com internet: {internet_count} ({internet_percentage:.1f}%)
Sem internet: {total-internet_count} ({no_internet_percentage:.1f}%)
"""
            except Exception as e:
                self.logger.error(f"Erro ao calcular percentuais de internet: {e}")
                stats_text += f"""Com internet: {internet_count}
Sem internet: {total-internet_count}
"""
            
            stats_text += f"""\nDISTRIBUIÇÃO POR RENDA:
{'-'*30}
"""
            
            for income, count in income_counts.items():
                try:
                    percentage = (count / total) * 100 if total > 0 else 0
                    stats_text += f"{income}: {count} ({percentage:.1f}%)\n"
                except Exception as e:
                    self.logger.error(f"Erro ao calcular percentual de renda: {e}")
                    stats_text += f"{income}: {count} (erro no cálculo)\n"
            
            # Atualizar o widget de texto
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, stats_text)
            
            if errors_count > 0:
                self.logger.warning(f"Estatísticas geradas com {errors_count} erros")
            else:
                self.logger.info("Estatísticas geradas com sucesso")
                
        except Exception as e:
            self.logger.error(f"Erro geral ao gerar estatísticas: {e}")
            error_text = f"""ERRO AO GERAR ESTATÍSTICAS
{'='*50}

Ocorreu um erro ao processar os dados:
{str(e)}

Verifique os logs para mais detalhes."""
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, error_text)
            messagebox.showerror("Erro", f"Erro ao gerar estatísticas: {e}")
    
    def generate_gender_chart(self):
        """Gera gráfico de distribuição por gênero com formatação melhorada"""
        if not self.data:
            return
        
        # Usar método de formatação padronizada
        gender_counts = {}
        for individual in self.data:
            gender = self._format_gender_value(individual)
            gender_counts[gender] = gender_counts.get(gender, 0) + 1
        
        if gender_counts:
            # Figsize dinâmico e formato quadrado para pizza
            w, h = self._get_dynamic_figsize(self.stats_chart_frame, base=(8, 6))
            size = min(w, h)
            fig, ax = plt.subplots(figsize=(size, size))
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            wedges, texts, autotexts = ax.pie(gender_counts.values(), labels=gender_counts.keys(), 
                                            autopct='%1.1f%%', colors=colors[:len(gender_counts)],
                                            startangle=90, textprops={'fontsize': 10})
            
            # Melhorar aparência do título
            ax.set_title('Distribuição por Gênero', fontweight='bold', fontsize=14, pad=20)
            
            # Adicionar legenda interna para evitar overflow lateral
            legend_labels = [f'{gender}: {count:,} pessoas' for gender, count in gender_counts.items()]
            ax.legend(wedges, legend_labels, title="Detalhes", loc="upper right")
            
            canvas = FigureCanvasTkAgg(fig, self.stats_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _show_no_data_message(self, parent_frame, message):
        """Exibe mensagem quando não há dados disponíveis"""
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        message_frame = ttk.Frame(parent_frame)
        message_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(message_frame, text="📊 Sem Dados", 
                 font=('Arial', 16, 'bold')).pack(pady=(50, 10))
        ttk.Label(message_frame, text=message, 
                 font=('Arial', 12), foreground='gray').pack(pady=10)
    
    def _show_error_message(self, parent_frame, message):
        """Exibe mensagem de erro"""
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        error_frame = ttk.Frame(parent_frame)
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(error_frame, text="⚠️ Erro", 
                 font=('Arial', 16, 'bold'), foreground='red').pack(pady=(50, 10))
        ttk.Label(error_frame, text=message, 
                 font=('Arial', 12), foreground='red').pack(pady=10)
    
    def generate_age_chart(self):
        """Gera gráfico de distribuição por faixa etária com tratamento de erros"""
        try:
            if not self.data:
                self._show_no_data_message(self.age_chart_frame, "Nenhum dado disponível para análise de idades")
                return
            
            # Usar método de validação melhorado
            ages = []
            invalid_ages = 0
            
            for individual in self.data:
                age = self._get_valid_age(individual)
                if age is not None:
                    ages.append(age)
                else:
                    invalid_ages += 1
            
            if not ages:
                self._show_no_data_message(self.age_chart_frame, 
                    f"Dados de idade não disponíveis ou inválidos\n({invalid_ages} registros com idades inválidas)")
                return
            
            # Limpar frame anterior
            for widget in self.age_chart_frame.winfo_children():
                widget.destroy()
            
            # Definir faixas etárias
            age_ranges = {'0-17': 0, '18-29': 0, '30-49': 0, '50-64': 0, '65+': 0}
            
            for age in ages:
                if age < 18:
                    age_ranges['0-17'] += 1
                elif age < 30:
                    age_ranges['18-29'] += 1
                elif age < 50:
                    age_ranges['30-49'] += 1
                elif age < 65:
                    age_ranges['50-64'] += 1
                else:
                    age_ranges['65+'] += 1
            
            figsize = self._get_dynamic_figsize(self.age_chart_frame, base=(8, 6))
            fig, ax = plt.subplots(figsize=figsize)
            bars = ax.bar(age_ranges.keys(), age_ranges.values(), color='#45B7D1', alpha=0.8)
            
            # Melhorar aparência
            ax.set_title('Distribuição por Faixa Etária', fontweight='bold', fontsize=14, pad=20)
            ax.set_xlabel('Faixa Etária (anos)', fontsize=12)
            ax.set_ylabel('Quantidade de Pessoas', fontsize=12)
            ax.grid(True, alpha=0.3, axis='y')
            
            # Adicionar valores nas barras com formatação melhorada
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{int(height):,}', ha='center', va='bottom', fontweight='bold')
            
            # Adicionar informações sobre qualidade dos dados
            total_records = len(self.data)
            valid_percentage = (len(ages) / total_records) * 100
            
            info_text = f'Dados válidos: {len(ages):,}/{total_records:,} ({valid_percentage:.1f}%)'
            if invalid_ages > 0:
                info_text += f'\nDados inválidos: {invalid_ages:,}'
            
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            plt.xticks(rotation=0)
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.age_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar gráfico de idades: {e}")
            self._show_error_message(self.age_chart_frame, f"Erro ao gerar gráfico: {str(e)}")
    
    def generate_income_chart(self):
        """Gera gráfico de distribuição por renda com tratamento de erros"""
        try:
            if not self.data:
                self._show_no_data_message(self.income_chart_frame, "Nenhum dado disponível para análise de renda")
                return
            
            income_counts = {}
            invalid_income = 0
            
            for individual in self.data:
                try:
                    if isinstance(individual, dict):
                        income = individual.get('household', {}).get('income_range')
                    else:
                        income = getattr(individual.household, 'income_range', None) if hasattr(individual, 'household') and individual.household else None
                    
                    if income and income.strip():
                        income_counts[income] = income_counts.get(income, 0) + 1
                    else:
                        income_counts['Não Informado'] = income_counts.get('Não Informado', 0) + 1
                        invalid_income += 1
                except (AttributeError, KeyError):
                    income_counts['Não Informado'] = income_counts.get('Não Informado', 0) + 1
                    invalid_income += 1
            
            if not income_counts:
                self._show_no_data_message(self.income_chart_frame, "Dados de renda não disponíveis")
                return
            
            # Limpar frame anterior
            for widget in self.income_chart_frame.winfo_children():
                widget.destroy()
            
            # Ordenar por ordem lógica de renda (se possível)
            income_order = ['Até 1 SM', '1-2 SM', '2-3 SM', '3-5 SM', '5-10 SM', 'Acima de 10 SM', 'Não Informado']
            sorted_income = {}
            
            # Primeiro, adicionar itens na ordem preferida
            for income in income_order:
                if income in income_counts:
                    sorted_income[income] = income_counts[income]
            
            # Depois, adicionar qualquer item restante
            for income, count in income_counts.items():
                if income not in sorted_income:
                    sorted_income[income] = count
            
            figsize = self._get_dynamic_figsize(self.income_chart_frame, base=(10, 6))
            fig, ax = plt.subplots(figsize=figsize)
            colors = plt.cm.Set3(range(len(sorted_income)))
            bars = ax.bar(range(len(sorted_income)), list(sorted_income.values()), color=colors, alpha=0.8)
            
            # Melhorar aparência
            ax.set_title('Distribuição por Faixa de Renda Familiar', fontweight='bold', fontsize=14, pad=20)
            ax.set_xlabel('Faixa de Renda (Salários Mínimos)', fontsize=12)
            ax.set_ylabel('Quantidade de Famílias', fontsize=12)
            ax.set_xticks(range(len(sorted_income)))
            ax.set_xticklabels(list(sorted_income.keys()), rotation=45, ha='right')
            ax.grid(True, alpha=0.3, axis='y')
            
            # Adicionar valores nas barras com formatação melhorada
            for i, bar in enumerate(bars):
                height = bar.get_height()
                percentage = (height / len(self.data)) * 100
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{int(height):,}\n({percentage:.1f}%)', ha='center', va='bottom', fontweight='bold')
            
            # Adicionar informações sobre qualidade dos dados
            total_records = len(self.data)
            valid_records = total_records - invalid_income
            valid_percentage = (valid_records / total_records) * 100
            
            info_text = f'Dados válidos: {valid_records:,}/{total_records:,} ({valid_percentage:.1f}%)'
            if invalid_income > 0:
                info_text += f'\nDados não informados: {invalid_income:,}'
            
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.income_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar gráfico de renda: {e}")
            self._show_error_message(self.income_chart_frame, f"Erro ao gerar gráfico: {str(e)}")
    
    def generate_internet_chart(self):
        """Gera gráfico de acesso à internet com formatação melhorada"""
        if not self.data:
            return
        
        # Usar método de formatação padronizada
        internet_counts = {'Com Internet': 0, 'Sem Internet': 0, 'Não Informado': 0}
        for individual in self.data:
            internet_status = self._format_internet_access(individual)
            internet_counts[internet_status] += 1
        
        # Remover categoria "Não Informado" se for zero
        if internet_counts['Não Informado'] == 0:
            del internet_counts['Não Informado']
        
        # Figsize dinâmico e formato quadrado para pizza
        w, h = self._get_dynamic_figsize(self.internet_chart_frame, base=(7, 5))
        size = min(w, h)
        fig, ax = plt.subplots(figsize=(size, size))
        colors = ['#4ECDC4', '#FF6B6B', '#FFA500'][:len(internet_counts)]
        wedges, texts, autotexts = ax.pie(internet_counts.values(), labels=internet_counts.keys(), 
                                        autopct='%1.1f%%', colors=colors,
                                        startangle=90, textprops={'fontsize': 10})
        
        # Melhorar aparência do título
        ax.set_title('Acesso à Internet', fontweight='bold', fontsize=14, pad=20)
        
        # Adicionar legenda interna para evitar overflow
        legend_labels = [f'{status}: {count:,} pessoas' for status, count in internet_counts.items()]
        ax.legend(wedges, legend_labels, title="Detalhes", loc="upper right")
        
        canvas = FigureCanvasTkAgg(fig, self.internet_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def generate_devices_chart(self):
        """Gera gráfico de dispositivos com tratamento de erros"""
        try:
            if not self.data:
                self._show_no_data_message(self.devices_chart_frame, "Nenhum dado disponível para análise de dispositivos")
                return
            
            device_counts = {}
            households_without_devices = 0
            households_with_errors = 0
            
            for individual in self.data:
                try:
                    if isinstance(individual, dict):
                        devices = individual.get('household', {}).get('devices')
                    else:
                        devices = getattr(individual.household, 'devices', None) if hasattr(individual, 'household') and individual.household else None
                    
                    # Tratar dispositivos como lista ou string
                    if isinstance(devices, list):
                        if devices:
                            # Se é uma lista, contar cada dispositivo
                            for device in devices:
                                if device and str(device).strip():
                                    device_str = str(device).strip()
                                    device_counts[device_str] = device_counts.get(device_str, 0) + 1
                                else:
                                    device_counts['Não Especificado'] = device_counts.get('Não Especificado', 0) + 1
                        else:
                            device_counts['Nenhum Dispositivo'] = device_counts.get('Nenhum Dispositivo', 0) + 1
                            households_without_devices += 1
                    elif devices and str(devices).strip():
                        # Se é string válida
                        device_str = str(devices).strip()
                        device_counts[device_str] = device_counts.get(device_str, 0) + 1
                    else:
                        # Se é None ou string vazia
                        device_counts['Não Informado'] = device_counts.get('Não Informado', 0) + 1
                        households_without_devices += 1
                        
                except (AttributeError, KeyError, TypeError) as e:
                    device_counts['Erro nos Dados'] = device_counts.get('Erro nos Dados', 0) + 1
                    households_with_errors += 1
            
            if not device_counts:
                self._show_no_data_message(self.devices_chart_frame, "Dados de dispositivos não disponíveis")
                return
            
            # Limpar frame anterior
            for widget in self.devices_chart_frame.winfo_children():
                widget.destroy()
            
            # Ordenar dispositivos por quantidade (decrescente)
            sorted_devices = dict(sorted(device_counts.items(), key=lambda x: x[1], reverse=True))
            
            figsize = self._get_dynamic_figsize(self.devices_chart_frame, base=(12, 8))
            fig, ax = plt.subplots(figsize=figsize)
            colors = plt.cm.tab20(range(len(sorted_devices)))
            bars = ax.bar(range(len(sorted_devices)), list(sorted_devices.values()), color=colors, alpha=0.8)
            
            # Melhorar aparência
            ax.set_title('Distribuição de Dispositivos por Domicílio', fontweight='bold', fontsize=14, pad=20)
            ax.set_xlabel('Tipo de Dispositivo', fontsize=12)
            ax.set_ylabel('Quantidade de Domicílios', fontsize=12)
            ax.set_xticks(range(len(sorted_devices)))
            ax.set_xticklabels(list(sorted_devices.keys()), rotation=45, ha='right')
            ax.grid(True, alpha=0.3, axis='y')
            
            # Adicionar valores nas barras com formatação melhorada
            for i, bar in enumerate(bars):
                height = bar.get_height()
                percentage = (height / len(self.data)) * 100
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{int(height):,}\n({percentage:.1f}%)', ha='center', va='bottom', fontweight='bold', fontsize=9)
            
            # Adicionar informações sobre qualidade dos dados
            total_records = len(self.data)
            valid_records = total_records - households_with_errors
            valid_percentage = (valid_records / total_records) * 100
            
            info_text = f'Total de domicílios: {total_records:,}\n'
            info_text += f'Dados válidos: {valid_records:,} ({valid_percentage:.1f}%)'
            if households_without_devices > 0:
                info_text += f'\nSem dispositivos: {households_without_devices:,}'
            if households_with_errors > 0:
                info_text += f'\nErros nos dados: {households_with_errors:,}'
            
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                   verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
            
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.devices_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar gráfico de dispositivos: {e}")
            self._show_error_message(self.devices_chart_frame, f"Erro ao gerar gráfico: {str(e)}")
    
    def generate_regional_chart(self):
        """Gera gráfico de distribuição regional"""
        if not self.data:
            return
        
        regional_counts = {}
        for individual in self.data:
            if isinstance(individual, dict):
                region = individual.get('household', {}).get('region_name') or 'Não informado'
            else:
                region = individual.household.region.name if individual.household.region else 'Não informado'
            regional_counts[region] = regional_counts.get(region, 0) + 1
        
        if regional_counts:
            figsize = self._get_dynamic_figsize(self.regional_chart_frame, base=(10, 6))
            fig, ax = plt.subplots(figsize=figsize)
            bars = ax.bar(range(len(regional_counts)), list(regional_counts.values()), color='#A8E6CF')
            ax.set_title('Distribuição por Região')
            ax.set_xlabel('Região')
            ax.set_ylabel('Quantidade de Pessoas')
            ax.set_xticks(range(len(regional_counts)))
            ax.set_xticklabels(list(regional_counts.keys()), rotation=45, ha='right')
            
            # Adicionar valores nas barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}', ha='center', va='bottom')
            
            fig.tight_layout()
            
            canvas = FigureCanvasTkAgg(fig, self.regional_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def export_pdf_report(self):
        """Exporta relatório em PDF com tratamento robusto de erros"""
        try:
            # Verificar se há dados para exportar
            if not self.data:
                self.logger.warning("Tentativa de exportar PDF sem dados")
                messagebox.showwarning("Aviso", "Nenhum dado disponível para exportar.")
                return
            
            # Verificar se as estatísticas foram geradas
            stats_content = self.stats_text.get(1.0, tk.END).strip()
            if not stats_content or stats_content == "Nenhum dado disponível para gerar estatísticas.":
                self.logger.warning("Tentativa de exportar PDF sem estatísticas geradas")
                messagebox.showwarning("Aviso", "Gere as estatísticas antes de exportar o relatório.")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Salvar relatório como"
            )
            
            if not filename:
                self.logger.info("Exportação de PDF cancelada pelo usuário")
                return
            
            # Criar PDF usando reportlab
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from datetime import datetime
            import tempfile
            import os
            
            try:
                doc = SimpleDocTemplate(filename, pagesize=A4)
                styles = getSampleStyleSheet()
                story = []
                
                # Título do relatório
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=18,
                    spaceAfter=30,
                    alignment=1  # Center
                )
                story.append(Paragraph("RELATÓRIO ESTATÍSTICO - SISTEMA DAC", title_style))
                story.append(Spacer(1, 12))
                
                # Data de geração
                date_style = ParagraphStyle(
                    'DateStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    alignment=1
                )
                story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", date_style))
                story.append(Spacer(1, 20))
                
                # Conteúdo das estatísticas
                content_style = ParagraphStyle(
                    'ContentStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    fontName='Courier'
                )
                
                # Dividir o conteúdo em parágrafos
                stats_lines = stats_content.split('\n')
                for line in stats_lines:
                    if line.strip():
                        story.append(Paragraph(line.replace(' ', '&nbsp;'), content_style))
                    else:
                        story.append(Spacer(1, 6))
                
                # Construir o PDF
                doc.build(story)
                
                self.logger.info(f"Relatório PDF exportado com sucesso: {filename}")
                messagebox.showinfo("Sucesso", f"Relatório exportado com sucesso!\n{filename}")
                
            except ImportError as import_error:
                self.logger.error(f"Biblioteca reportlab não encontrada: {import_error}")
                messagebox.showerror("Erro", "Biblioteca reportlab não está instalada.\nInstale com: pip install reportlab")
            except Exception as pdf_error:
                self.logger.error(f"Erro ao criar PDF: {pdf_error}")
                messagebox.showerror("Erro", f"Erro ao criar PDF: {pdf_error}")
                
        except Exception as e:
            self.logger.error(f"Erro geral na exportação de PDF: {e}")
            messagebox.showerror("Erro", f"Erro ao exportar relatório: {e}")
    
    def export_excel_report(self):
        """Exporta relatório em Excel com tratamento robusto de erros"""
        try:
            # Verificar se há dados para exportar
            if not self.data:
                self.logger.warning("Tentativa de exportar Excel sem dados")
                messagebox.showwarning("Aviso", "Nenhum dado disponível para exportar.")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Salvar relatório como"
            )
            
            if not filename:
                self.logger.info("Exportação de Excel cancelada pelo usuário")
                return
            
            try:
                import pandas as pd
                
                # Preparar dados para exportação
                export_data = []
                for individual in self.data:
                    try:
                        if isinstance(individual, dict):
                            row = {
                                'ID': individual.get('id', ''),
                                'Idade': individual.get('age', ''),
                                'Gênero': individual.get('gender', ''),
                                'Tem Deficiência': 'Sim' if individual.get('has_disability', False) else 'Não',
                                'Faixa de Renda': individual.get('household', {}).get('income_range', ''),
                                'Tem Internet': 'Sim' if individual.get('household', {}).get('has_internet', False) else 'Não',
                                'Região': individual.get('household', {}).get('region_name', '')
                            }
                        else:
                            row = {
                                'ID': getattr(individual, 'id', ''),
                                'Idade': getattr(individual, 'age', ''),
                                'Gênero': getattr(individual, 'gender', ''),
                                'Tem Deficiência': 'Sim' if getattr(individual, 'has_disability', False) else 'Não',
                                'Faixa de Renda': getattr(individual.household, 'income_range', '') if hasattr(individual, 'household') and individual.household else '',
                                'Tem Internet': 'Sim' if (hasattr(individual, 'household') and individual.household and getattr(individual.household, 'has_internet', False)) else 'Não',
                                'Região': getattr(individual.household.region, 'name', '') if (hasattr(individual, 'household') and individual.household and hasattr(individual.household, 'region') and individual.household.region) else ''
                            }
                        export_data.append(row)
                    except Exception as row_error:
                        self.logger.error(f"Erro ao processar linha para exportação: {row_error}")
                        continue
                
                # Criar DataFrame e exportar
                df = pd.DataFrame(export_data)
                
                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    # Aba com dados brutos
                    df.to_excel(writer, sheet_name='Dados', index=False)
                    
                    # Aba com estatísticas resumidas
                    stats_data = []
                    
                    # Estatísticas por gênero
                    gender_counts = df['Gênero'].value_counts()
                    for gender, count in gender_counts.items():
                        percentage = (count / len(df)) * 100
                        stats_data.append(['Gênero', gender, count, f'{percentage:.1f}%'])
                    
                    # Estatísticas por faixa etária
                    age_ranges = {'0-17': 0, '18-29': 0, '30-49': 0, '50-64': 0, '65+': 0}
                    for age in df['Idade'].dropna():
                        try:
                            age = int(age)
                            if age < 18:
                                age_ranges['0-17'] += 1
                            elif age < 30:
                                age_ranges['18-29'] += 1
                            elif age < 50:
                                age_ranges['30-49'] += 1
                            elif age < 65:
                                age_ranges['50-64'] += 1
                            else:
                                age_ranges['65+'] += 1
                        except:
                            continue
                    
                    for age_range, count in age_ranges.items():
                        percentage = (count / len(df)) * 100 if len(df) > 0 else 0
                        stats_data.append(['Faixa Etária', age_range, count, f'{percentage:.1f}%'])
                    
                    # Outras estatísticas
                    internet_counts = df['Tem Internet'].value_counts()
                    for status, count in internet_counts.items():
                        percentage = (count / len(df)) * 100
                        stats_data.append(['Internet', status, count, f'{percentage:.1f}%'])
                    
                    disability_counts = df['Tem Deficiência'].value_counts()
                    for status, count in disability_counts.items():
                        percentage = (count / len(df)) * 100
                        stats_data.append(['Deficiência', status, count, f'{percentage:.1f}%'])
                    
                    stats_df = pd.DataFrame(stats_data, columns=['Categoria', 'Valor', 'Quantidade', 'Percentual'])
                    stats_df.to_excel(writer, sheet_name='Estatísticas', index=False)
                
                self.logger.info(f"Relatório Excel exportado com sucesso: {filename}")
                messagebox.showinfo("Sucesso", f"Relatório exportado com sucesso!\n{filename}")
                
            except ImportError as import_error:
                self.logger.error(f"Bibliotecas pandas/openpyxl não encontradas: {import_error}")
                messagebox.showerror("Erro", "Bibliotecas necessárias não estão instaladas.\nInstale com: pip install pandas openpyxl")
            except Exception as excel_error:
                self.logger.error(f"Erro ao criar Excel: {excel_error}")
                messagebox.showerror("Erro", f"Erro ao criar Excel: {excel_error}")
                
        except Exception as e:
            self.logger.error(f"Erro geral na exportação de Excel: {e}")
            messagebox.showerror("Erro", f"Erro ao exportar relatório: {e}")
    
    def generate_overview_chart(self):
        """Gera gráfico de visão geral com formatação melhorada"""
        try:
            if not self.data:
                return
            
            # Limpar frame anterior
            for widget in self.overview_chart_frame.winfo_children():
                widget.destroy()
            
            # Atualizar cards de métricas
            self.update_metric_cards()
            
            # Criar gráfico de resumo com tamanho dinâmico para evitar overflow
            base_size = self.chart_config.get('figure_size', (8, 5))
            w, h = self._get_dynamic_figsize(self.overview_chart_frame, base=base_size)
            # Para grid 2x2, garantir altura suficiente
            h = max(h, w * 0.75)
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(w, h))
            
            # Gráfico 1: Distribuição por gênero com formatação melhorada
            gender_counts = {}
            for individual in self.data:
                gender = self._format_gender_value(individual)
                gender_counts[gender] = gender_counts.get(gender, 0) + 1
            
            if gender_counts:
                # Garantir que color_palette seja uma lista válida
                color_palette = self.chart_config.get('color_palette', ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83'])
                if not isinstance(color_palette, list):
                    color_palette = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#592E83']
                
                # Usar apenas as cores necessárias
                colors_needed = min(len(gender_counts), len(color_palette))
                chart_colors = color_palette[:colors_needed] if colors_needed > 0 else ['#2E86AB']
                
                # Formatação melhorada do gráfico de pizza
                wedges, texts, autotexts = ax1.pie(gender_counts.values(), labels=gender_counts.keys(), 
                                                  autopct='%1.1f%%', colors=chart_colors,
                                                  startangle=90, textprops={'fontsize': 9})
                ax1.set_title('Distribuição por Gênero', fontweight='bold', pad=20)
            
            # Gráfico 2: Acesso à Internet com formatação melhorada
            internet_counts = {'Com Internet': 0, 'Sem Internet': 0, 'Não Informado': 0}
            for individual in self.data:
                internet_status = self._format_internet_access(individual)
                internet_counts[internet_status] += 1
            
            # Remover categoria "Não Informado" se for zero
            if internet_counts['Não Informado'] == 0:
                del internet_counts['Não Informado']
            
            bars = ax2.bar(internet_counts.keys(), internet_counts.values(), 
                          color=['#4ECDC4', '#FF6B6B', '#FFA500'][:len(internet_counts)])
            ax2.set_title('Acesso à Internet', fontweight='bold', pad=20)
            ax2.set_ylabel('Quantidade de Pessoas')
            
            # Adicionar valores nas barras
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{int(height)}', ha='center', va='bottom', fontsize=9)
            
            # Gráfico 3: Faixas etárias com formatação melhorada
            ages = []
            for individual in self.data:
                age = self._get_valid_age(individual)
                if age is not None:
                    ages.append(age)
            
            if ages:
                n, bins, patches = ax3.hist(ages, bins=10, color='#45B7D1', alpha=0.7, 
                                          edgecolor='black', linewidth=0.5)
                ax3.set_title('Distribuição de Idades', fontweight='bold', pad=20)
                ax3.set_xlabel('Idade (anos)')
                ax3.set_ylabel('Quantidade de Pessoas')
                ax3.grid(True, alpha=0.3)
                ax3.set_ylabel('Frequência')
            
            # Gráfico 4: Pessoas com deficiência
            disability_counts = {'Com Deficiência': 0, 'Sem Deficiência': 0}
            for individual in self.data:
                has_disability = individual.get('has_disability', False) if isinstance(individual, dict) else getattr(individual, 'has_disability', False)
                disability_counts['Com Deficiência' if has_disability else 'Sem Deficiência'] += 1
            
            ax4.bar(disability_counts.keys(), disability_counts.values(), color=['#FFA07A', '#98FB98'])
            ax4.set_title('Pessoas com Deficiência')
            ax4.set_ylabel('Quantidade')
            plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45)
            
            plt.tight_layout()
            
            # Adicionar ao frame
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, self.overview_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Gerar insights automáticos
            self.generate_insights()
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar gráfico de visão geral: {e}")
    
    def _format_gender_value(self, individual):
        """Formata o valor de gênero com tratamento de dados incompletos"""
        if isinstance(individual, dict):
            gender = individual.get('gender', '')
        else:
            gender = getattr(individual, 'gender', '')
        
        # Normalizar valores de gênero
        if not gender or str(gender).strip().lower() in ['', 'null', 'none', 'nan']:
            return 'Não Informado'
        
        gender_str = str(gender).strip().lower()
        if gender_str in ['m', 'masculino', 'male', 'homem']:
            return 'Masculino'
        elif gender_str in ['f', 'feminino', 'female', 'mulher']:
            return 'Feminino'
        else:
            return gender.title() if gender else 'Não Informado'
    
    def _format_internet_access(self, individual):
        """Formata o status de acesso à internet"""
        if isinstance(individual, dict):
            has_internet = individual.get('household', {}).get('has_internet')
        else:
            has_internet = (getattr(individual.household, 'has_internet', None) 
                          if hasattr(individual, 'household') and individual.household 
                          else None)
        
        if has_internet is None or str(has_internet).lower() in ['null', 'none', 'nan', '']:
            return 'Não Informado'
        
        return 'Com Internet' if has_internet else 'Sem Internet'
    
    def _get_valid_age(self, individual):
        """Obtém idade válida com validação"""
        if isinstance(individual, dict):
            age = individual.get('age')
        else:
            age = getattr(individual, 'age', None)
        
        if age is None or str(age).lower() in ['null', 'none', 'nan', '']:
            return None
        
        try:
            age_int = int(float(age))
            # Validar faixa etária razoável
            if 0 <= age_int <= 120:
                return age_int
        except (ValueError, TypeError):
            pass
        
        return None
    
    def _format_disability_status(self, individual):
        """Formata o status de deficiência"""
        if isinstance(individual, dict):
            has_disability = individual.get('has_disability')
        else:
            has_disability = getattr(individual, 'has_disability', None)
        
        if has_disability is None or str(has_disability).lower() in ['null', 'none', 'nan', '']:
            return 'Não Informado'
        
        return 'Sim' if has_disability else 'Não'
    
    def update_metric_cards(self):
        """Atualiza os cards de métricas principais com formatação melhorada"""
        try:
            if not self.data:
                return
            
            total = len(self.data)
            
            # Total de registros com formatação
            self.total_value.config(text=f"{total:,}")
            
            # Percentual com internet com tratamento de dados incompletos
            internet_count = 0
            valid_internet_data = 0
            
            for individual in self.data:
                internet_status = self._format_internet_access(individual)
                if internet_status != 'Não Informado':
                    valid_internet_data += 1
                    if internet_status == 'Com Internet':
                        internet_count += 1
            
            internet_percentage = (internet_count / valid_internet_data * 100) if valid_internet_data > 0 else 0
            self.internet_value.config(text=f"{internet_percentage:.1f}%")
            
            # Percentual com deficiência com tratamento melhorado
            disability_count = 0
            valid_disability_data = 0
            
            for individual in self.data:
                disability_status = self._format_disability_status(individual)
                if disability_status != 'Não Informado':
                    valid_disability_data += 1
                    if disability_status == 'Sim':
                        disability_count += 1
            
            disability_percentage = (disability_count / valid_disability_data * 100) if valid_disability_data > 0 else 0
            self.disability_value.config(text=f"{disability_percentage:.1f}%")
            
            # Idade média com validação melhorada
            ages = []
            for individual in self.data:
                age = self._get_valid_age(individual)
                if age is not None:
                    ages.append(age)
            
            avg_age = sum(ages) / len(ages) if ages else 0
            self.age_value.config(text=f"{avg_age:.1f} anos")
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar cards de métricas: {e}")
    
    def generate_insights(self):
        """Gera insights automáticos baseados nos dados"""
        try:
            if not self.data:
                self.insights_text.delete(1.0, tk.END)
                self.insights_text.insert(1.0, "Nenhum dado disponível para gerar insights.")
                return
            
            insights = []
            total = len(self.data)
            
            # Análise de gênero
            gender_counts = {}
            for individual in self.data:
                gender = individual.get('gender', 'Não informado') if isinstance(individual, dict) else getattr(individual, 'gender', 'Não informado')
                gender_counts[gender] = gender_counts.get(gender, 0) + 1
            
            if gender_counts:
                dominant_gender = max(gender_counts, key=gender_counts.get)
                percentage = (gender_counts[dominant_gender] / total) * 100
                insights.append(f"• O gênero predominante é {dominant_gender} ({percentage:.1f}% dos registros).")
            
            # Análise de internet
            internet_count = sum(1 for ind in self.data if (ind.get('household', {}).get('has_internet', False) if isinstance(ind, dict) else getattr(ind.household, 'has_internet', False) if hasattr(ind, 'household') and ind.household else False))
            internet_percentage = (internet_count / total) * 100 if total > 0 else 0
            
            if internet_percentage > 70:
                insights.append(f"• Boa conectividade: {internet_percentage:.1f}% da população tem acesso à internet.")
            elif internet_percentage < 30:
                insights.append(f"• Baixa conectividade: apenas {internet_percentage:.1f}% da população tem acesso à internet.")
            else:
                insights.append(f"• Conectividade moderada: {internet_percentage:.1f}% da população tem acesso à internet.")
            
            # Análise de idade
            ages = [ind.get('age') if isinstance(ind, dict) else getattr(ind, 'age', None) for ind in self.data]
            valid_ages = [age for age in ages if age is not None and isinstance(age, (int, float))]
            
            if valid_ages:
                avg_age = sum(valid_ages) / len(valid_ages)
                young_count = sum(1 for age in valid_ages if age < 30)
                young_percentage = (young_count / len(valid_ages)) * 100
                
                insights.append(f"• A idade média da população é {avg_age:.1f} anos.")
                
                if young_percentage > 50:
                    insights.append(f"• População jovem: {young_percentage:.1f}% tem menos de 30 anos.")
                elif young_percentage < 20:
                    insights.append(f"• População envelhecida: apenas {young_percentage:.1f}% tem menos de 30 anos.")
            
            # Análise de deficiência
            disability_count = sum(1 for ind in self.data if (ind.get('has_disability', False) if isinstance(ind, dict) else getattr(ind, 'has_disability', False)))
            disability_percentage = (disability_count / total) * 100 if total > 0 else 0
            
            if disability_percentage > 15:
                insights.append(f"• Alta incidência de deficiência: {disability_percentage:.1f}% da população.")
            else:
                insights.append(f"• {disability_percentage:.1f}% da população possui alguma deficiência.")
            
            # Análise regional (se disponível)
            regional_counts = {}
            for individual in self.data:
                region = individual.get('household', {}).get('region_name', 'Não informado') if isinstance(individual, dict) else getattr(individual.household.region, 'name', 'Não informado') if hasattr(individual, 'household') and individual.household and hasattr(individual.household, 'region') and individual.household.region else 'Não informado'
                regional_counts[region] = regional_counts.get(region, 0) + 1
            
            if len(regional_counts) > 1 and 'Não informado' not in regional_counts:
                dominant_region = max(regional_counts, key=regional_counts.get)
                percentage = (regional_counts[dominant_region] / total) * 100
                insights.append(f"• A região com maior concentração é {dominant_region} ({percentage:.1f}%).")
            
            # Exibir insights
            insights_text = "\n".join(insights) if insights else "Nenhum insight específico identificado nos dados atuais."
            self.insights_text.delete(1.0, tk.END)
            self.insights_text.insert(1.0, insights_text)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar insights: {e}")
            self.insights_text.delete(1.0, tk.END)
            self.insights_text.insert(1.0, f"Erro ao gerar insights: {e}")
    
    def generate_correlation_analysis(self):
        """Gera análise de correlação avançada"""
        try:
            if not self.data:
                return
            
            # Limpar frames anteriores
            for widget in self.correlation_chart_frame.winfo_children():
                widget.destroy()
            for widget in self.trends_chart_frame.winfo_children():
                widget.destroy()
            
            # Preparar dados para análise
            analysis_data = []
            for individual in self.data:
                try:
                    if isinstance(individual, dict):
                        row = {
                            'age': individual.get('age', 0) if individual.get('age') is not None else 0,
                            'has_disability': 1 if individual.get('has_disability', False) else 0,
                            'has_internet': 1 if individual.get('household', {}).get('has_internet', False) else 0,
                            'gender_numeric': 1 if individual.get('gender') == 'Masculino' else 0
                        }
                    else:
                        row = {
                            'age': getattr(individual, 'age', 0) if getattr(individual, 'age', None) is not None else 0,
                            'has_disability': 1 if getattr(individual, 'has_disability', False) else 0,
                            'has_internet': 1 if (hasattr(individual, 'household') and individual.household and getattr(individual.household, 'has_internet', False)) else 0,
                            'gender_numeric': 1 if getattr(individual, 'gender', None) == 'Masculino' else 0
                        }
                    analysis_data.append(row)
                except Exception as row_error:
                    self.logger.error(f"Erro ao processar linha para análise: {row_error}")
                    continue
            
            if not analysis_data:
                return
            
            # Gráfico de correlação
            fig1, ax1 = plt.subplots(figsize=(6, 5))
            
            # Análise simples de correlação idade vs internet
            ages = [row['age'] for row in analysis_data if row['age'] > 0]
            internet_by_age = [row['has_internet'] for row in analysis_data if row['age'] > 0]
            
            if ages and internet_by_age:
                ax1.scatter(ages, internet_by_age, alpha=0.6, color='#4ECDC4')
                ax1.set_xlabel('Idade')
                ax1.set_ylabel('Tem Internet (0=Não, 1=Sim)')
                ax1.set_title('Relação entre Idade e Acesso à Internet')
                ax1.grid(True, alpha=0.3)
            
            canvas1 = FigureCanvasTkAgg(fig1, self.correlation_chart_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Gráfico de tendências
            fig2, ax2 = plt.subplots(figsize=(6, 5))
            
            # Análise de faixas etárias vs acesso digital
            age_ranges = {'0-17': [], '18-29': [], '30-49': [], '50-64': [], '65+': []}
            
            for row in analysis_data:
                age = row['age']
                internet = row['has_internet']
                
                if age < 18:
                    age_ranges['0-17'].append(internet)
                elif age < 30:
                    age_ranges['18-29'].append(internet)
                elif age < 50:
                    age_ranges['30-49'].append(internet)
                elif age < 65:
                    age_ranges['50-64'].append(internet)
                else:
                    age_ranges['65+'].append(internet)
            
            # Calcular percentuais de acesso à internet por faixa etária
            internet_percentages = []
            labels = []
            
            for age_range, internet_list in age_ranges.items():
                if internet_list:
                    percentage = (sum(internet_list) / len(internet_list)) * 100
                    internet_percentages.append(percentage)
                    labels.append(age_range)
            
            if internet_percentages:
                bars = ax2.bar(labels, internet_percentages, color='#45B7D1')
                ax2.set_xlabel('Faixa Etária')
                ax2.set_ylabel('% com Acesso à Internet')
                ax2.set_title('Acesso à Internet por Faixa Etária')
                ax2.set_ylim(0, 100)
                
                # Adicionar valores nas barras
                for bar, percentage in zip(bars, internet_percentages):
                    ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 1,
                           f'{percentage:.1f}%', ha='center', va='bottom')
            
            canvas2 = FigureCanvasTkAgg(fig2, self.trends_chart_frame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar análise de correlação: {e}")
    
    def export_excel_report(self):
        """Exporta dados em Excel com tratamento robusto de erros"""
        if not self.data:
            self.logger.warning("Tentativa de exportar Excel sem dados")
            messagebox.showwarning("Aviso", "Nenhum dado disponível para exportar.")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                title="Salvar dados como"
            )
            
            if not filename:
                self.logger.info("Exportação de Excel cancelada pelo usuário")
                return
            
            # Verificar se o diretório de destino existe e é gravável
            import os
            dest_dir = os.path.dirname(filename)
            if not os.path.exists(dest_dir):
                self.logger.error(f"Diretório de destino não existe: {dest_dir}")
                messagebox.showerror("Erro", f"Diretório de destino não existe: {dest_dir}")
                return
            
            if not os.access(dest_dir, os.W_OK):
                self.logger.error(f"Sem permissão de escrita no diretório: {dest_dir}")
                messagebox.showerror("Erro", f"Sem permissão de escrita no diretório: {dest_dir}")
                return
            
            # Preparar dados para exportação
            export_data = []
            errors_count = 0
            
            for individual in self.data:
                try:
                    # Processar dados do indivíduo
                    if isinstance(individual, dict):
                        # Dados já processados (dicionário)
                        individual_id = individual.get('id', 'N/A')
                        age = individual.get('age', 'N/A')
                        gender = individual.get('gender', 'N/A')
                        has_disability = individual.get('has_disability', False)
                        
                        household_data = individual.get('household', {})
                        region_name = household_data.get('region_name', 'N/A')
                        income_range = household_data.get('income_range', 'N/A')
                        has_internet = household_data.get('has_internet', False)
                        devices = household_data.get('devices', 'Nenhum')
                        
                    else:
                        # Objeto SQLAlchemy
                        individual_id = getattr(individual, 'id', 'N/A')
                        age = getattr(individual, 'age', 'N/A')
                        gender = getattr(individual, 'gender', 'N/A')
                        has_disability = getattr(individual, 'has_disability', False)
                        
                        # Dados do domicílio
                        household = getattr(individual, 'household', None)
                        if household:
                            region = getattr(household, 'region', None)
                            region_name = getattr(region, 'name', 'N/A') if region else 'N/A'
                            income_range = getattr(household, 'income_range', 'N/A')
                            has_internet = getattr(household, 'has_internet', False)
                            
                            # Dispositivos do indivíduo
                            device_usage = getattr(individual, 'device_usage', [])
                            if device_usage:
                                try:
                                    device_list = [getattr(d, 'device_type', 'Desconhecido') for d in device_usage]
                                    devices = ', '.join(device_list) if device_list else 'Nenhum'
                                except Exception:
                                    devices = 'Erro ao processar'
                            else:
                                devices = 'Nenhum'
                        else:
                            region_name = 'N/A'
                            income_range = 'N/A'
                            has_internet = False
                            devices = 'Nenhum'
                    
                    # Validar e formatar dados
                    export_row = {
                        'ID': str(individual_id) if individual_id is not None else 'N/A',
                        'Região': str(region_name) if region_name else 'N/A',
                        'Idade': str(age) if age is not None else 'N/A',
                        'Gênero': str(gender) if gender else 'N/A',
                        'Renda': str(income_range) if income_range else 'N/A',
                        'Deficiência': 'Sim' if has_disability else 'Não',
                        'Internet': 'Sim' if has_internet else 'Não',
                        'Dispositivos': str(devices) if devices else 'Nenhum'
                    }
                    
                    export_data.append(export_row)
                    
                except Exception as process_error:
                    self.logger.error(f"Erro ao processar registro para Excel: {process_error}")
                    errors_count += 1
                    # Adicionar registro com erro
                    export_data.append({
                        'ID': 'ERRO',
                        'Região': 'Erro no processamento',
                        'Idade': 'N/A',
                        'Gênero': 'N/A',
                        'Renda': 'N/A',
                        'Deficiência': 'N/A',
                        'Internet': 'N/A',
                        'Dispositivos': 'N/A'
                    })
            
            if not export_data:
                self.logger.error("Nenhum dado válido para exportar")
                messagebox.showerror("Erro", "Nenhum dado válido encontrado para exportar.")
                return
            
            try:
                # Criar DataFrame e salvar
                import pandas as pd
                df = pd.DataFrame(export_data)
                
                # Salvar com tratamento de erros
                df.to_excel(filename, index=False, sheet_name='Dados DAC', engine='openpyxl')
                
                # Verificar se o arquivo foi criado com sucesso
                if os.path.exists(filename) and os.path.getsize(filename) > 0:
                    success_msg = f"Dados exportados com sucesso para:\n{filename}\n\nRegistros exportados: {len(export_data)}"
                    if errors_count > 0:
                        success_msg += f"\nRegistros com problemas: {errors_count}"
                    
                    self.logger.info(f"Excel exportado com sucesso: {len(export_data)} registros, {errors_count} erros")
                    messagebox.showinfo("Sucesso", success_msg)
                else:
                    self.logger.error("Arquivo Excel não foi criado corretamente")
                    messagebox.showerror("Erro", "Arquivo Excel não foi criado corretamente.")
                    
            except ImportError as import_error:
                self.logger.error(f"Erro de importação para Excel: {import_error}")
                messagebox.showerror("Erro", "Bibliotecas necessárias para Excel não estão disponíveis.\nInstale: pip install openpyxl")
            except PermissionError as perm_error:
                self.logger.error(f"Erro de permissão ao salvar Excel: {perm_error}")
                messagebox.showerror("Erro", f"Sem permissão para salvar o arquivo:\n{filename}\n\nVerifique se o arquivo não está aberto em outro programa.")
            except Exception as excel_error:
                self.logger.error(f"Erro específico ao gerar Excel: {excel_error}")
                messagebox.showerror("Erro", f"Erro ao gerar Excel: {excel_error}")
                
        except Exception as e:
            self.logger.error(f"Erro geral ao exportar Excel: {e}")
            messagebox.showerror("Erro", f"Erro ao exportar Excel: {e}")