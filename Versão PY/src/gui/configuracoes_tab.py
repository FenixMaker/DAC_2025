"""
Aba de configurações do sistema DAC.
Interface gráfica para gerenciar todas as configurações do sistema.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from pathlib import Path
from typing import Dict, Any, Optional
import threading
from datetime import datetime

# Importa o módulo de configurações
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config_manager import ConfigManager, test_database_connection


class ConfiguracoesTab(ttk.Frame):
    """Aba de configurações principal."""
    
    def __init__(self, parent, *args, **kwargs):
        # Callback opcional para notificar mudança de banco de dados (SQLite)
        self.on_database_changed = kwargs.pop('on_database_changed', None)
        super().__init__(parent, *args, **kwargs)
        
        # Inicializa o gerenciador de configurações
        self.config_manager = ConfigManager()
        
        # Cache das configurações atuais
        self.current_configs = {}
        
        # Variáveis de controle para indicadores de mudança
        self.has_changes = False
        
        # Configura o layout principal
        self.setup_ui()
        
        # Carrega todas as configurações
        self.load_all_configs()
    
    def setup_ui(self):
        """Configura a interface da aba de configurações."""
        # Frame principal com notebook (abas)
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cria o notebook com as abas de configuração
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Cria as abas individuais
        self.create_database_tab()
        self.create_appearance_tab()
        self.create_performance_tab()
        self.create_reports_tab()
        self.create_logs_tab()
        
        # Frame de botões na parte inferior
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Botões de ação
        self.save_button = ttk.Button(
            button_frame, 
            text="Salvar Todas as Alterações", 
            command=self.save_all_configs,
            style='Accent.TButton'
        )
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        self.cancel_button = ttk.Button(
            button_frame, 
            text="Cancelar", 
            command=self.cancel_changes
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=5)
        
        self.reset_button = ttk.Button(
            button_frame, 
            text="Redefinir para Padrões", 
            command=self.reset_to_defaults
        )
        self.reset_button.pack(side=tk.RIGHT, padx=5)
        
        self.export_button = ttk.Button(
            button_frame, 
            text="Exportar Configurações", 
            command=self.export_configs
        )
        self.export_button.pack(side=tk.RIGHT, padx=5)
        
        self.import_button = ttk.Button(
            button_frame, 
            text="Importar Configurações", 
            command=self.import_configs
        )
        self.import_button.pack(side=tk.RIGHT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Pronto")
        self.status_bar = ttk.Label(
            main_frame, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Bind para detectar mudanças
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def create_database_tab(self):
        """Cria a aba de configurações do banco de dados."""
        db_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(db_frame, text="Banco de Dados")
        
        # Frame principal com scrollbar
        canvas = tk.Canvas(db_frame)
        scrollbar = ttk.Scrollbar(db_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Seletor de tipo de banco de dados
        ttk.Label(scrollable_frame, text="Tipo de Banco:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.db_type_var = tk.StringVar()
        self.db_type_combo = ttk.Combobox(scrollable_frame, textvariable=self.db_type_var,
                                         values=['PostgreSQL', 'SQLite'], state='readonly', width=37)
        self.db_type_combo.grid(row=0, column=1, sticky='ew', pady=5, padx=(0, 10))
        self.db_type_combo.bind('<<ComboboxSelected>>', self.on_db_type_changed)
        self.db_type_combo.bind('<<ComboboxSelected>>', self.on_config_changed)
        
        # Frame para configurações PostgreSQL
        self.postgresql_frame = ttk.LabelFrame(scrollable_frame, text="Configurações PostgreSQL", padding=10)
        self.postgresql_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)
        
        ttk.Label(self.postgresql_frame, text="Host:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.db_host_var = tk.StringVar()
        self.db_host_entry = ttk.Entry(self.postgresql_frame, textvariable=self.db_host_var, width=35)
        self.db_host_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(0, 10))
        self.db_host_entry.bind('<KeyRelease>', self.on_config_changed)
        
        ttk.Label(self.postgresql_frame, text="Porta:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        self.db_port_var = tk.StringVar()
        self.db_port_entry = ttk.Entry(self.postgresql_frame, textvariable=self.db_port_var, width=35)
        self.db_port_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(0, 10))
        self.db_port_entry.bind('<KeyRelease>', self.on_config_changed)
        
        ttk.Label(self.postgresql_frame, text="Banco de Dados:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        self.db_name_var = tk.StringVar()
        self.db_name_entry = ttk.Entry(self.postgresql_frame, textvariable=self.db_name_var, width=35)
        self.db_name_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=(0, 10))
        self.db_name_entry.bind('<KeyRelease>', self.on_config_changed)
        
        # Frame para configurações SQLite
        self.sqlite_frame = ttk.LabelFrame(scrollable_frame, text="Configurações SQLite", padding=10)
        self.sqlite_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)
        
        # Caminho do arquivo SQLite
        ttk.Label(self.sqlite_frame, text="Arquivo do Banco:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        self.sqlite_path_var = tk.StringVar()
        self.sqlite_path_entry = ttk.Entry(self.sqlite_frame, textvariable=self.sqlite_path_var, width=30, state='readonly')
        self.sqlite_path_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(0, 5))
        
        self.sqlite_browse_button = ttk.Button(self.sqlite_frame, text="Procurar...", command=self.browse_sqlite_file)
        self.sqlite_browse_button.grid(row=0, column=2, padx=(5, 0))
        
        # Informações do banco atual
        self.sqlite_info_frame = ttk.LabelFrame(self.sqlite_frame, text="Informações do Banco", padding=10)
        self.sqlite_info_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=10)
        
        self.sqlite_info_label = ttk.Label(self.sqlite_info_frame, text="Nenhum banco selecionado", font=('Arial', 9))
        self.sqlite_info_label.pack(anchor='w', pady=5)

        # Lista de tabelas do SQLite
        tables_frame = ttk.Frame(self.sqlite_info_frame)
        tables_frame.pack(fill='both', expand=True)
        self.sqlite_tables_tree = ttk.Treeview(tables_frame, columns=("table", "rows"), show='headings', height=6)
        self.sqlite_tables_tree.heading("table", text="Tabela")
        self.sqlite_tables_tree.heading("rows", text="Linhas")
        self.sqlite_tables_tree.column("table", width=240, anchor='w')
        self.sqlite_tables_tree.column("rows", width=80, anchor='center')
        scroll = ttk.Scrollbar(tables_frame, orient='vertical', command=self.sqlite_tables_tree.yview)
        self.sqlite_tables_tree.configure(yscrollcommand=scroll.set)
        self.sqlite_tables_tree.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')
        
        # Campos comuns (usuário e senha para PostgreSQL)
        ttk.Label(scrollable_frame, text="Usuário:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=5)
        self.db_user_var = tk.StringVar()
        self.db_user_entry = ttk.Entry(scrollable_frame, textvariable=self.db_user_var, width=40)
        self.db_user_entry.grid(row=3, column=1, sticky='ew', pady=5, padx=(0, 10))
        self.db_user_entry.bind('<KeyRelease>', self.on_config_changed)
        
        ttk.Label(scrollable_frame, text="Senha:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=5)
        self.db_password_var = tk.StringVar()
        self.db_password_entry = ttk.Entry(scrollable_frame, textvariable=self.db_password_var, show="*", width=40)
        self.db_password_entry.grid(row=4, column=1, sticky='ew', pady=5, padx=(0, 10))
        self.db_password_entry.bind('<KeyRelease>', self.on_config_changed)
        
        self.db_user_label = ttk.Label(scrollable_frame, text="Usuário:", font=('Arial', 10, 'bold'))
        self.db_user_label.grid(row=3, column=0, sticky='w', pady=5)
        self.db_user_var = tk.StringVar()
        self.db_user_entry = ttk.Entry(scrollable_frame, textvariable=self.db_user_var, width=40)
        self.db_user_entry.grid(row=3, column=1, sticky='ew', pady=5, padx=(0, 10))
        self.db_user_entry.bind('<KeyRelease>', self.on_config_changed)
        
        self.db_password_label = ttk.Label(scrollable_frame, text="Senha:", font=('Arial', 10, 'bold'))
        self.db_password_label.grid(row=4, column=0, sticky='w', pady=5)
        self.db_password_var = tk.StringVar()
        self.db_password_entry = ttk.Entry(scrollable_frame, textvariable=self.db_password_var, show="*", width=40)
        self.db_password_entry.grid(row=4, column=1, sticky='ew', pady=5, padx=(0, 10))
        self.db_password_entry.bind('<KeyRelease>', self.on_config_changed)
        
        self.db_ssl_label = ttk.Label(scrollable_frame, text="SSL Mode:", font=('Arial', 10, 'bold'))
        self.db_ssl_label.grid(row=5, column=0, sticky='w', pady=5)
        self.db_ssl_var = tk.StringVar()
        self.db_ssl_combo = ttk.Combobox(scrollable_frame, textvariable=self.db_ssl_var, 
                                         values=['disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full'],
                                         state='readonly', width=37)
        self.db_ssl_combo.grid(row=5, column=1, sticky='ew', pady=5, padx=(0, 10))
        self.db_ssl_combo.bind('<<ComboboxSelected>>', self.on_config_changed)
        
        self.db_pool_label = ttk.Label(scrollable_frame, text="Tamanho do Pool:", font=('Arial', 10, 'bold'))
        self.db_pool_label.grid(row=6, column=0, sticky='w', pady=5)
        self.db_pool_var = tk.StringVar()
        self.db_pool_entry = ttk.Entry(scrollable_frame, textvariable=self.db_pool_var, width=40)
        self.db_pool_entry.grid(row=6, column=1, sticky='ew', pady=5, padx=(0, 10))
        self.db_pool_entry.bind('<KeyRelease>', self.on_config_changed)
        
        self.db_timeout_label = ttk.Label(scrollable_frame, text="Timeout (ms):", font=('Arial', 10, 'bold'))
        self.db_timeout_label.grid(row=7, column=0, sticky='w', pady=5)
        self.db_timeout_var = tk.StringVar()
        self.db_timeout_entry = ttk.Entry(scrollable_frame, textvariable=self.db_timeout_var, width=40)
        self.db_timeout_entry.grid(row=7, column=1, sticky='ew', pady=5, padx=(0, 10))
        self.db_timeout_entry.bind('<KeyRelease>', self.on_config_changed)
        
        self.db_retry_label = ttk.Label(scrollable_frame, text="Tentativas de Reconexão:", font=('Arial', 10, 'bold'))
        self.db_retry_label.grid(row=8, column=0, sticky='w', pady=5)
        self.db_retry_var = tk.StringVar()
        self.db_retry_entry = ttk.Entry(scrollable_frame, textvariable=self.db_retry_var, width=40)
        self.db_retry_entry.grid(row=8, column=1, sticky='ew', pady=5, padx=(0, 10))
        self.db_retry_entry.bind('<KeyRelease>', self.on_config_changed)
        
        # Botão de teste de conexão
        test_frame = ttk.Frame(scrollable_frame)
        test_frame.grid(row=9, column=0, columnspan=2, pady=20)
        
        self.test_button = ttk.Button(
            test_frame,
            text="Testar Conexão",
            command=self.test_database_connection,
            style='Accent.TButton'
        )
        self.test_button.pack(side=tk.LEFT, padx=5)
        
        self.test_result_label = ttk.Label(test_frame, text="", font=('Arial', 10))
        self.test_result_label.pack(side=tk.LEFT, padx=10)
        
        # Configura o grid para expandir e reduzir espaço em branco
        scrollable_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(1, weight=1)
        
        # Empacota os widgets de scroll
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Salva referência para atualização
        self.db_frame = scrollable_frame
    
    def create_appearance_tab(self):
        """Cria a aba de configurações de aparência."""
        appearance_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(appearance_frame, text="Aparência")
        
        # Tema
        ttk.Label(appearance_frame, text="Tema:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=10)
        self.theme_var = tk.StringVar()
        self.theme_combo = ttk.Combobox(appearance_frame, textvariable=self.theme_var,
                                        values=['light', 'dark', 'system'], state='readonly', width=30)
        self.theme_combo.grid(row=0, column=1, sticky='w', pady=10, padx=(0, 10))
        self.theme_combo.bind('<<ComboboxSelected>>', self.on_config_changed)
        
        # Tamanho da fonte
        ttk.Label(appearance_frame, text="Tamanho da Fonte:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=10)
        self.font_size_var = tk.StringVar()
        self.font_size_spin = ttk.Spinbox(appearance_frame, from_=8, to=24, textvariable=self.font_size_var, width=28)
        self.font_size_spin.grid(row=1, column=1, sticky='w', pady=10, padx=(0, 10))
        self.font_size_spin.bind('<KeyRelease>', self.on_config_changed)
        
        # Escala da UI
        ttk.Label(appearance_frame, text="Escala da Interface:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=10)
        self.ui_scale_var = tk.StringVar()
        self.ui_scale_spin = ttk.Spinbox(appearance_frame, from_=0.5, to=3.0, increment=0.1,
                                        textvariable=self.ui_scale_var, width=28)
        self.ui_scale_spin.grid(row=2, column=1, sticky='w', pady=10, padx=(0, 10))
        self.ui_scale_spin.bind('<KeyRelease>', self.on_config_changed)
        
        # Variante do logo
        ttk.Label(appearance_frame, text="Variante do Logo:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=10)
        self.logo_variant_var = tk.StringVar()
        self.logo_variant_combo = ttk.Combobox(appearance_frame, textvariable=self.logo_variant_var,
                                              values=['simplified', 'color', 'mono-black', 'mono-white'],
                                              state='readonly', width=27)
        self.logo_variant_combo.grid(row=3, column=1, sticky='w', pady=10, padx=(0, 10))
        self.logo_variant_combo.bind('<<ComboboxSelected>>', self.on_config_changed)
        
        # Animações
        self.animations_var = tk.BooleanVar()
        self.animations_check = ttk.Checkbutton(appearance_frame, text="Ativar Animações",
                                               variable=self.animations_var,
                                               command=self.on_config_changed)
        self.animations_check.grid(row=4, column=0, columnspan=2, sticky='w', pady=10)
        
        # Densidade da tabela
        ttk.Label(appearance_frame, text="Densidade das Tabelas:", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky='w', pady=10)
        self.table_density_var = tk.StringVar()
        self.table_density_combo = ttk.Combobox(appearance_frame, textvariable=self.table_density_var,
                                               values=['compact', 'normal', 'comfortable'], state='readonly', width=27)
        self.table_density_combo.grid(row=5, column=1, sticky='w', pady=10, padx=(0, 10))
        self.table_density_combo.bind('<<ComboboxSelected>>', self.on_config_changed)
        
        # Preview do tema (placeholder)
        preview_frame = ttk.LabelFrame(appearance_frame, text="Preview do Tema", padding=10)
        preview_frame.grid(row=6, column=0, columnspan=2, sticky='ew', pady=20)
        
        preview_label = ttk.Label(preview_frame, text="O preview do tema será aplicado ao reiniciar a aplicação.",
                                 font=('Arial', 9, 'italic'))
        preview_label.pack(pady=20)
        
        # Salva referência
        self.appearance_frame = appearance_frame
    
    def create_performance_tab(self):
        """Cria a aba de configurações de desempenho."""
        perf_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(perf_frame, text="Desempenho")
        
        # Máximo de linhas por consulta
        ttk.Label(perf_frame, text="Máximo de Linhas por Consulta:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=10)
        self.max_rows_var = tk.StringVar()
        self.max_rows_spin = ttk.Spinbox(perf_frame, from_=1000, to=100000, increment=1000,
                                         textvariable=self.max_rows_var, width=30)
        self.max_rows_spin.grid(row=0, column=1, sticky='w', pady=10, padx=(0, 10))
        self.max_rows_spin.bind('<KeyRelease>', self.on_config_changed)
        
        # Timeout de consulta
        ttk.Label(perf_frame, text="Timeout de Consulta (segundos):", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=10)
        self.query_timeout_var = tk.StringVar()
        self.query_timeout_spin = ttk.Spinbox(perf_frame, from_=5, to=300, increment=5,
                                             textvariable=self.query_timeout_var, width=30)
        self.query_timeout_spin.grid(row=1, column=1, sticky='w', pady=10, padx=(0, 10))
        self.query_timeout_spin.bind('<KeyRelease>', self.on_config_changed)
        
        # Qualidade dos gráficos
        ttk.Label(perf_frame, text="Qualidade dos Gráficos:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=10)
        self.chart_quality_var = tk.StringVar()
        self.chart_quality_combo = ttk.Combobox(perf_frame, textvariable=self.chart_quality_var,
                                                 values=['low', 'medium', 'high'], state='readonly', width=27)
        self.chart_quality_combo.grid(row=2, column=1, sticky='w', pady=10, padx=(0, 10))
        self.chart_quality_combo.bind('<<ComboboxSelected>>', self.on_config_changed)
        
        # Intervalo de atualização automática
        ttk.Label(perf_frame, text="Atualização Automática (segundos):", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=10)
        self.auto_refresh_var = tk.StringVar()
        self.auto_refresh_spin = ttk.Spinbox(perf_frame, from_=10, to=3600, increment=10,
                                            textvariable=self.auto_refresh_var, width=30)
        self.auto_refresh_spin.grid(row=3, column=1, sticky='w', pady=10, padx=(0, 10))
        self.auto_refresh_spin.bind('<KeyRelease>', self.on_config_changed)
        
        # Limite de memória
        ttk.Label(perf_frame, text="Limite de Memória (MB):", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=10)
        self.memory_limit_var = tk.StringVar()
        self.memory_limit_spin = ttk.Spinbox(perf_frame, from_=128, to=4096, increment=128,
                                            textvariable=self.memory_limit_var, width=30)
        self.memory_limit_spin.grid(row=4, column=1, sticky='w', pady=10, padx=(0, 10))
        self.memory_limit_spin.bind('<KeyRelease>', self.on_config_changed)
        
        # Informações de desempenho atuais
        info_frame = ttk.LabelFrame(perf_frame, text="Informações do Sistema", padding=10)
        info_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=20)
        
        # Labels para informações (serão atualizadas dinamicamente)
        self.memory_usage_label = ttk.Label(info_frame, text="Uso de Memória: --")
        self.memory_usage_label.pack(anchor='w', pady=2)
        
        self.cpu_usage_label = ttk.Label(info_frame, text="Uso de CPU: --")
        self.cpu_usage_label.pack(anchor='w', pady=2)
        
        self.active_connections_label = ttk.Label(info_frame, text="Conexões Ativas: --")
        self.active_connections_label.pack(anchor='w', pady=2)
        
        # Botão para atualizar informações
        self.update_info_button = ttk.Button(
            info_frame,
            text="Atualizar Informações",
            command=self.update_system_info
        )
        self.update_info_button.pack(pady=10)
        
        # Salva referência
        self.perf_frame = perf_frame
    
    def create_reports_tab(self):
        """Cria a aba de configurações de relatórios."""
        reports_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(reports_frame, text="Relatórios")
        
        # Período padrão
        ttk.Label(reports_frame, text="Período Padrão (dias):", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=10)
        self.default_period_var = tk.StringVar()
        self.default_period_spin = ttk.Spinbox(reports_frame, from_=1, to=365, increment=1,
                                              textvariable=self.default_period_var, width=30)
        self.default_period_spin.grid(row=0, column=1, sticky='w', pady=10, padx=(0, 10))
        self.default_period_spin.bind('<KeyRelease>', self.on_config_changed)
        
        # Casas decimais
        ttk.Label(reports_frame, text="Casas Decimais:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=10)
        self.decimal_places_var = tk.StringVar()
        self.decimal_places_spin = ttk.Spinbox(reports_frame, from_=0, to=10, increment=1,
                                              textvariable=self.decimal_places_var, width=30)
        self.decimal_places_spin.grid(row=1, column=1, sticky='w', pady=10, padx=(0, 10))
        self.decimal_places_spin.bind('<KeyRelease>', self.on_config_changed)
        
        # Formato de porcentagem
        ttk.Label(reports_frame, text="Formato de Porcentagem:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=10)
        self.percentage_format_var = tk.StringVar()
        self.percentage_format_combo = ttk.Combobox(reports_frame, textvariable=self.percentage_format_var,
                                                   values=['0%', '0.0%', '0.00%', '0.000%'], state='readonly', width=27)
        self.percentage_format_combo.grid(row=2, column=1, sticky='w', pady=10, padx=(0, 10))
        self.percentage_format_combo.bind('<<ComboboxSelected>>', self.on_config_changed)
        
        # Formato de exportação
        ttk.Label(reports_frame, text="Formato de Exportação:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=10)
        self.export_format_var = tk.StringVar()
        self.export_format_combo = ttk.Combobox(reports_frame, textvariable=self.export_format_var,
                                             values=['png', 'pdf', 'svg', 'csv', 'xlsx'], state='readonly', width=27)
        self.export_format_combo.grid(row=3, column=1, sticky='w', pady=10, padx=(0, 10))
        self.export_format_combo.bind('<<ComboboxSelected>>', self.on_config_changed)
        
        # Resolução DPI
        ttk.Label(reports_frame, text="Resolução DPI:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=10)
        self.resolution_dpi_var = tk.StringVar()
        self.resolution_dpi_spin = ttk.Spinbox(reports_frame, from_=72, to=600, increment=72,
                                             textvariable=self.resolution_dpi_var, width=30)
        self.resolution_dpi_spin.grid(row=4, column=1, sticky='w', pady=10, padx=(0, 10))
        self.resolution_dpi_spin.bind('<KeyRelease>', self.on_config_changed)
        
        # Incluir metadados
        self.include_metadata_var = tk.BooleanVar()
        self.include_metadata_check = ttk.Checkbutton(reports_frame, text="Incluir Metadados nos Relatórios",
                                                    variable=self.include_metadata_var,
                                                    command=self.on_config_changed)
        self.include_metadata_check.grid(row=5, column=0, columnspan=2, sticky='w', pady=10)
        
        # Template de relatório
        template_frame = ttk.LabelFrame(reports_frame, text="Template de Relatório", padding=10)
        template_frame.grid(row=6, column=0, columnspan=2, sticky='ew', pady=20)
        
        ttk.Label(template_frame, text="Cabeçalho:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.report_header_text = tk.Text(template_frame, height=3, width=50)
        self.report_header_text.pack(fill=tk.X, pady=(0, 10))
        self.report_header_text.bind('<KeyRelease>', self.on_config_changed)
        
        ttk.Label(template_frame, text="Rodapé:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        self.report_footer_text = tk.Text(template_frame, height=3, width=50)
        self.report_footer_text.pack(fill=tk.X)
        self.report_footer_text.bind('<KeyRelease>', self.on_config_changed)
        
        # Salva referência
        self.reports_frame = reports_frame
    
    def create_logs_tab(self):
        """Cria a aba de configurações de logs."""
        logs_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(logs_frame, text="Logs")
        
        # Nível de log
        ttk.Label(logs_frame, text="Nível de Log:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=10)
        self.log_level_var = tk.StringVar()
        self.log_level_combo = ttk.Combobox(logs_frame, textvariable=self.log_level_var,
                                          values=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                                          state='readonly', width=30)
        self.log_level_combo.grid(row=0, column=1, sticky='w', pady=10, padx=(0, 10))
        self.log_level_combo.bind('<<ComboboxSelected>>', self.on_config_changed)
        
        # Caminho do arquivo de log
        ttk.Label(logs_frame, text="Arquivo de Log:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=10)
        self.log_file_var = tk.StringVar()
        self.log_file_entry = ttk.Entry(logs_frame, textvariable=self.log_file_var, width=40)
        self.log_file_entry.grid(row=1, column=1, sticky='ew', pady=10, padx=(0, 10))
        self.log_file_entry.bind('<KeyRelease>', self.on_config_changed)
        
        self.browse_log_button = ttk.Button(logs_frame, text="Procurar...", command=self.browse_log_file)
        self.browse_log_button.grid(row=1, column=2, padx=(5, 0))
        
        # Tamanho máximo do arquivo
        ttk.Label(logs_frame, text="Tamanho Máximo (MB):", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=10)
        self.max_size_var = tk.StringVar()
        self.max_size_spin = ttk.Spinbox(logs_frame, from_=1, to=100, increment=1,
                                        textvariable=self.max_size_var, width=30)
        self.max_size_spin.grid(row=2, column=1, sticky='w', pady=10, padx=(0, 10))
        self.max_size_spin.bind('<KeyRelease>', self.on_config_changed)
        
        # Número de backups
        ttk.Label(logs_frame, text="Número de Backups:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=10)
        self.backup_count_var = tk.StringVar()
        self.backup_count_spin = ttk.Spinbox(logs_frame, from_=0, to=20, increment=1,
                                           textvariable=self.backup_count_var, width=30)
        self.backup_count_spin.grid(row=3, column=1, sticky='w', pady=10, padx=(0, 10))
        self.backup_count_spin.bind('<KeyRelease>', self.on_config_changed)
        
        # Saída no console
        self.console_output_var = tk.BooleanVar()
        self.console_output_check = ttk.Checkbutton(logs_frame, text="Exibir Logs no Console",
                                                   variable=self.console_output_var,
                                                   command=self.on_config_changed)
        self.console_output_check.grid(row=4, column=0, columnspan=2, sticky='w', pady=10)
        
        # Formato do log
        ttk.Label(logs_frame, text="Formato do Log:", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky='w', pady=10)
        self.log_format_text = tk.Text(logs_frame, height=3, width=50)
        self.log_format_text.grid(row=5, column=1, columnspan=2, sticky='ew', pady=10, padx=(0, 10))
        self.log_format_text.bind('<KeyRelease>', self.on_config_changed)
        
        # Frame de visualização de logs
        log_view_frame = ttk.LabelFrame(logs_frame, text="Visualização de Logs", padding=10)
        log_view_frame.grid(row=6, column=0, columnspan=3, sticky='nsew', pady=20)
        
        # Text widget com scrollbar para mostrar logs
        self.log_text = tk.Text(log_view_frame, height=10, width=70, state='disabled')
        log_scrollbar = ttk.Scrollbar(log_view_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky='nsew')
        log_scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Botões de controle
        log_control_frame = ttk.Frame(log_view_frame)
        log_control_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.refresh_log_button = ttk.Button(log_control_frame, text="Atualizar Logs",
                                           command=self.refresh_log_display)
        self.refresh_log_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_log_button = ttk.Button(log_control_frame, text="Limpar Logs",
                                         command=self.clear_logs)
        self.clear_log_button.pack(side=tk.LEFT, padx=5)
        
        self.open_log_button = ttk.Button(log_control_frame, text="Abrir Arquivo de Log",
                                        command=self.open_log_file)
        self.open_log_button.pack(side=tk.LEFT, padx=5)
        
        # Configura o grid
        log_view_frame.grid_columnconfigure(0, weight=1)
        log_view_frame.grid_rowconfigure(0, weight=1)
        logs_frame.grid_columnconfigure(1, weight=1)
        logs_frame.grid_rowconfigure(6, weight=1)
        
        # Salva referência
        self.logs_frame = logs_frame
    
    def load_all_configs(self):
        """Carrega todas as configurações nos campos da interface."""
        try:
            # Carrega configurações do banco de dados
            db_config = self.config_manager.load_config('database')
            self.db_type_var.set(db_config.get('type', 'PostgreSQL'))
            self.db_host_var.set(db_config.get('host', 'localhost'))
            self.db_port_var.set(str(db_config.get('port', 5432)))
            self.db_name_var.set(db_config.get('database', 'dac_db'))
            self.db_user_var.set(db_config.get('user', 'postgres'))
            self.db_password_var.set(db_config.get('password', ''))
            self.db_ssl_var.set(db_config.get('sslmode', 'prefer'))
            self.db_pool_var.set(str(db_config.get('pool_size', 10)))
            self.db_timeout_var.set(str(db_config.get('timeout_ms', 30000)))
            self.db_retry_var.set(str(db_config.get('retry_count', 3)))
            # Usa o caminho padrão vindo do ConfigManager (Versão PY/data/dac_database.db)
            default_sqlite_path = self.config_manager.get_default_config('database').get('sqlite_path')
            self.sqlite_path_var.set(db_config.get('sqlite_path', default_sqlite_path))
            
            # Atualiza a interface baseada no tipo de banco de dados
            self.on_db_type_changed()
            
            # Se for SQLite, atualiza as informações do arquivo
            if self.db_type_var.get() == 'SQLite' and self.sqlite_path_var.get():
                self.update_sqlite_info(self.sqlite_path_var.get())
            
            # Carrega configurações de aparência
            appearance_config = self.config_manager.load_config('appearance')
            self.theme_var.set(appearance_config.get('theme', 'system'))
            self.font_size_var.set(str(appearance_config.get('font_size', 12)))
            self.ui_scale_var.set(str(appearance_config.get('ui_scale', 1.0)))
            self.logo_variant_var.set(appearance_config.get('logo_variant', 'simplified'))
            self.animations_var.set(appearance_config.get('animations_enabled', True))
            self.table_density_var.set(appearance_config.get('table_density', 'normal'))
            
            # Carrega configurações de desempenho
            perf_config = self.config_manager.load_config('performance')
            self.max_rows_var.set(str(perf_config.get('max_query_rows', 10000)))
            self.query_timeout_var.set(str(perf_config.get('query_timeout_seconds', 30)))
            self.chart_quality_var.set(perf_config.get('chart_quality', 'high'))
            self.auto_refresh_var.set(str(perf_config.get('auto_refresh_interval', 60)))
            self.memory_limit_var.set(str(perf_config.get('memory_limit_mb', 512)))
            
            # Carrega configurações de relatórios
            reports_config = self.config_manager.load_config('reports')
            self.default_period_var.set(str(reports_config.get('default_period_days', 30)))
            self.decimal_places_var.set(str(reports_config.get('decimal_places', 2)))
            self.percentage_format_var.set(reports_config.get('percentage_format', '0.1%'))
            self.export_format_var.set(reports_config.get('export_format', 'png'))
            self.resolution_dpi_var.set(str(reports_config.get('resolution_dpi', 300)))
            self.include_metadata_var.set(reports_config.get('include_metadata', True))
            
            # Template de relatório
            header = reports_config.get('header_template', '')
            footer = reports_config.get('footer_template', '')
            self.report_header_text.delete('1.0', tk.END)
            self.report_header_text.insert('1.0', header)
            self.report_footer_text.delete('1.0', tk.END)
            self.report_footer_text.insert('1.0', footer)
            
            # Carrega configurações de logs
            logs_config = self.config_manager.load_config('logging')
            self.log_level_var.set(logs_config.get('level', 'INFO'))
            self.log_file_var.set(logs_config.get('file_path', 'logs/dac.log'))
            self.max_size_var.set(str(logs_config.get('max_size_mb', 10)))
            self.backup_count_var.set(str(logs_config.get('backup_count', 5)))
            self.console_output_var.set(logs_config.get('console_output', True))
            
            # Formato do log
            log_format = logs_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            self.log_format_text.delete('1.0', tk.END)
            self.log_format_text.insert('1.0', log_format)
            
            # Atualiza informações do sistema
            self.update_system_info()
            
            self.status_var.set("Configurações carregadas com sucesso")
            self.has_changes = False
            
        except Exception as e:
            self.status_var.set(f"Erro ao carregar configurações: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao carregar configurações:\n{str(e)}")
    
    def save_all_configs(self):
        """Salva todas as configurações alteradas com validação completa."""
        try:
            self.status_var.set("Validando configurações...")
            
            # Validações específicas por tipo de banco de dados
            if self.db_type_var.get() == 'PostgreSQL':
                if not self.db_host_var.get().strip():
                    self.status_var.set("Erro: Host do PostgreSQL não pode estar vazio")
                    messagebox.showerror("Erro de Validação", "Host do banco de dados PostgreSQL não pode estar vazio")
                    return
                
                if not self.db_name_var.get().strip():
                    self.status_var.set("Erro: Nome do banco PostgreSQL não pode estar vazio")
                    messagebox.showerror("Erro de Validação", "Nome do banco de dados PostgreSQL não pode estar vazio")
                    return
                
                if not self.db_user_var.get().strip():
                    self.status_var.set("Erro: Usuário do PostgreSQL não pode estar vazio")
                    messagebox.showerror("Erro de Validação", "Usuário do banco de dados PostgreSQL não pode estar vazio")
                    return
            
            if self.db_type_var.get() == 'SQLite':
                if not self.sqlite_path_var.get().strip():
                    self.status_var.set("Erro: Arquivo SQLite não selecionado")
                    messagebox.showerror("Erro de Validação", "Por favor, selecione um arquivo SQLite")
                    return
                
                # Verifica se o arquivo existe
                if not os.path.exists(self.sqlite_path_var.get()):
                    self.status_var.set("Erro: Arquivo SQLite não encontrado")
                    messagebox.showerror("Erro de Validação", f"Arquivo SQLite não encontrado:\n{self.sqlite_path_var.get()}")
                    return
            
            # Validações de desempenho
            try:
                max_rows = int(self.max_rows_var.get())
                if max_rows <= 0:
                    raise ValueError("Deve ser positivo")
            except ValueError:
                self.status_var.set("Erro: Máximo de linhas deve ser um número positivo")
                messagebox.showerror("Erro de Validação", "Máximo de linhas por consulta deve ser um número positivo")
                return
            
            try:
                timeout = int(self.query_timeout_var.get())
                if timeout <= 0:
                    raise ValueError("Deve ser positivo")
            except ValueError:
                self.status_var.set("Erro: Timeout deve ser um número positivo")
                messagebox.showerror("Erro de Validação", "Timeout de consulta deve ser um número positivo")
                return
            
            # Validações de relatórios
            try:
                decimal_places = int(self.decimal_places_var.get())
                if decimal_places < 0 or decimal_places > 10:
                    raise ValueError("Deve estar entre 0 e 10")
            except ValueError:
                self.status_var.set("Erro: Casas decimais devem estar entre 0 e 10")
                messagebox.showerror("Erro de Validação", "Casas decimais devem estar entre 0 e 10")
                return
            
            try:
                dpi = int(self.resolution_dpi_var.get())
                if dpi < 72 or dpi > 600:
                    raise ValueError("Deve estar entre 72 e 600")
            except ValueError:
                self.status_var.set("Erro: DPI deve estar entre 72 e 600")
                messagebox.showerror("Erro de Validação", "Resolução DPI deve estar entre 72 e 600")
                return
            
            self.status_var.set("Salvando configurações...")
            
            # Coleta e valida configurações do banco de dados
            db_config = {
                'type': self.db_type_var.get(),
                'host': self.db_host_var.get(),
                'port': int(self.db_port_var.get()),
                'database': self.db_name_var.get(),
                'user': self.db_user_var.get(),
                'password': self.db_password_var.get(),
                'sslmode': self.db_ssl_var.get(),
                'pool_size': int(self.db_pool_var.get()),
                'timeout_ms': int(self.db_timeout_var.get()),
                'retry_count': int(self.db_retry_var.get()),
                'sqlite_path': self.sqlite_path_var.get()
            }
            
            is_valid, errors = self.config_manager.validate_config('database', db_config)
            if not is_valid:
                self.status_var.set("Erro: Configurações do banco de dados inválidas")
                messagebox.showerror("Erro de Validação", "Configurações do banco de dados inválidas:\n" + "\n".join(errors))
                return
            
            # Salva configurações do banco de dados
            self.config_manager.save_config('database', db_config)

            # Notifica aplicação principal se houver troca de banco SQLite
            try:
                if self.db_type_var.get() == 'SQLite' and self.sqlite_path_var.get() and self.on_database_changed:
                    self.on_database_changed(self.sqlite_path_var.get())
            except Exception:
                pass
            
            # Salva configurações de aparência
            appearance_config = {
                'theme': self.theme_var.get(),
                'font_size': float(self.font_size_var.get()),
                'ui_scale': float(self.ui_scale_var.get()),
                'logo_variant': self.logo_variant_var.get(),
                'animations_enabled': self.animations_var.get(),
                'table_density': self.table_density_var.get()
            }
            self.config_manager.save_config('appearance', appearance_config)
            
            # Salva configurações de desempenho
            perf_config = {
                'max_query_rows': int(self.max_rows_var.get()),
                'query_timeout_seconds': int(self.query_timeout_var.get()),
                'chart_quality': self.chart_quality_var.get(),
                'auto_refresh_interval': int(self.auto_refresh_var.get()),
                'memory_limit_mb': int(self.memory_limit_var.get())
            }
            self.config_manager.save_config('performance', perf_config)
            
            # Salva configurações de relatórios
            reports_config = {
                'default_period_days': int(self.default_period_var.get()),
                'decimal_places': int(self.decimal_places_var.get()),
                'percentage_format': self.percentage_format_var.get(),
                'export_format': self.export_format_var.get(),
                'resolution_dpi': int(self.resolution_dpi_var.get()),
                'include_metadata': self.include_metadata_var.get(),
                'header_template': self.report_header_text.get('1.0', tk.END).strip(),
                'footer_template': self.report_footer_text.get('1.0', tk.END).strip()
            }
            self.config_manager.save_config('reports', reports_config)
            
            # Salva configurações de logs
            logs_config = {
                'level': self.log_level_var.get(),
                'file_path': self.log_file_var.get(),
                'max_size_mb': int(self.max_size_var.get()),
                'backup_count': int(self.backup_count_var.get()),
                'console_output': self.console_output_var.get(),
                'format': self.log_format_text.get('1.0', tk.END).strip()
            }
            self.config_manager.save_config('logging', logs_config)
            
            self.has_changes = False
            self.status_var.set("✓ Configurações salvas com sucesso")
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            
        except ValueError as e:
            self.status_var.set("Erro: Valor inválido")
            messagebox.showerror("Erro", f"Valor inválido:\n{str(e)}")
        except Exception as e:
            self.status_var.set("Erro: Falha ao salvar configurações")
            messagebox.showerror("Erro", f"Erro ao salvar configurações:\n{str(e)}")
    
    def on_db_type_changed(self, event=None):
        """Manipula a mudança de tipo de banco de dados."""
        db_type = self.db_type_var.get()
        
        if db_type == 'SQLite':
            self.postgresql_frame.grid_remove()
            self.sqlite_frame.grid()
            # Desabilita campos de usuário/senha para SQLite
            self.db_user_entry.config(state='disabled')
            self.db_password_entry.config(state='disabled')
            # Oculta campos específicos de PostgreSQL
            self.db_user_label.grid_remove()
            self.db_password_label.grid_remove()
            self.db_ssl_label.grid_remove()
            self.db_ssl_combo.grid_remove()
            self.db_pool_label.grid_remove()
            self.db_pool_entry.grid_remove()
            self.db_timeout_label.grid_remove()
            self.db_timeout_entry.grid_remove()
            self.db_retry_label.grid_remove()
            self.db_retry_entry.grid_remove()
        else:  # PostgreSQL
            self.sqlite_frame.grid_remove()
            self.postgresql_frame.grid()
            self.db_user_entry.config(state='normal')
            self.db_password_entry.config(state='normal')
            # Restaura campos específicos de PostgreSQL
            self.db_user_label.grid()
            self.db_password_label.grid()
            self.db_ssl_label.grid()
            self.db_ssl_combo.grid()
            self.db_pool_label.grid()
            self.db_pool_entry.grid()
            self.db_timeout_label.grid()
            self.db_timeout_entry.grid()
            self.db_retry_label.grid()
            self.db_retry_entry.grid()
    
    def browse_sqlite_file(self):
        """Abre diálogo para selecionar arquivo SQLite."""
        current_file = self.sqlite_path_var.get()
        
        # Define o diretório inicial
        if current_file and Path(current_file).exists():
            initial_dir = Path(current_file).parent
        else:
            # Fallback: diretório padrão do projeto (Versão PY/data)
            try:
                default_sqlite_path = self.config_manager.get_default_config('database').get('sqlite_path')
                initial_dir = str(Path(default_sqlite_path).parent)
            except Exception:
                # Último recurso: raiz da pasta Versão PY
                initial_dir = str(Path(__file__).resolve().parents[2])
        
        filename = filedialog.askopenfilename(
            title="Selecionar Arquivo SQLite",
            initialdir=initial_dir,
            filetypes=[
                ("Arquivos SQLite", "*.db *.sqlite *.sqlite3"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if filename:
            self.sqlite_path_var.set(filename)
            # Garante que o tipo esteja como SQLite e atualiza layout
            if self.db_type_var.get() != 'SQLite':
                self.db_type_var.set('SQLite')
                self.on_db_type_changed()
            # Atualiza informações e testa automaticamente a conexão
            self.update_sqlite_info(filename)
            self.on_config_changed()
            # Dispara o teste de conexão automático
            try:
                self.test_sqlite_connection()
            except Exception:
                # Falha silenciosa para não interromper UI em casos inesperados
                pass
    
    def update_sqlite_info(self, filepath):
        """Atualiza as informações do banco SQLite."""
        try:
            import sqlite3
            
            # Testa a conexão
            conn = sqlite3.connect(filepath)
            cursor = conn.cursor()
            
            # Obtém informações
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name ASC;")
            tables = [row[0] for row in cursor.fetchall()]
            table_count = len(tables)
            
            # Obtém contagem de linhas por tabela (limita para desempenho)
            table_rows = []
            for name in tables[:50]:  # limita a 50 tabelas para não travar
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM '{name}'")
                    cnt = cursor.fetchone()[0]
                except Exception:
                    cnt = '-'
                table_rows.append((name, cnt))
            
            # Versão do SQLite
            cursor.execute("SELECT sqlite_version()")
            sqlite_version = cursor.fetchone()[0]
            
            # Obtém o tamanho do arquivo
            file_size = Path(filepath).stat().st_size
            size_mb = file_size / (1024 * 1024)
            mod_time = datetime.fromtimestamp(Path(filepath).stat().st_mtime).strftime('%d/%m/%Y %H:%M:%S')
            
            info_text = f"""
Caminho: {filepath}
Tabelas: {table_count}
Tamanho: {size_mb:.2f} MB
Modificado: {mod_time}
SQLite: v{sqlite_version}
Status: Conectado com sucesso
"""
            
            conn.close()
            self.sqlite_info_label.config(text=info_text.strip(), foreground='green')
            
            # Popular tabela de tabelas
            # Limpa dados antigos
            for item in self.sqlite_tables_tree.get_children():
                self.sqlite_tables_tree.delete(item)
            for name, cnt in table_rows:
                self.sqlite_tables_tree.insert('', 'end', values=(name, cnt))
            
        except Exception as e:
            self.sqlite_info_label.config(text=f"Erro ao acessar banco: {str(e)}", foreground='red')
            # Limpa tabela em caso de erro
            if hasattr(self, 'sqlite_tables_tree'):
                for item in self.sqlite_tables_tree.get_children():
                    self.sqlite_tables_tree.delete(item)
    
    def test_database_connection(self):
        """Testa a conexão com o banco de dados configurado com validações."""
        db_type = self.db_type_var.get()
        
        self.status_var.set("Testando conexão com banco de dados...")
        
        if db_type == 'SQLite':
            # Testa conexão SQLite
            self.test_sqlite_connection()
        else:
            # Testa conexão PostgreSQL
            self.test_postgresql_connection()
    
    def test_sqlite_connection(self):
        """Testa conexão com SQLite com validações completas."""
        filepath = self.sqlite_path_var.get()
        
        if not filepath:
            self.status_var.set("Erro: Arquivo SQLite não selecionado")
            self.test_result_label.config(text="Por favor, selecione um arquivo SQLite", foreground='red')
            return
        
        if not os.path.exists(filepath):
            self.status_var.set("Erro: Arquivo SQLite não encontrado")
            self.test_result_label.config(text=f"Arquivo SQLite não encontrado:\n{filepath}", foreground='red')
            return
        
        # Desabilita o botão durante o teste
        self.test_button.config(state='disabled')
        self.test_result_label.config(text="Testando conexão...", foreground='blue')
        self.status_var.set("Conectando ao SQLite...")
        
        def test_connection():
            try:
                import sqlite3
                conn = sqlite3.connect(filepath)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
                # Testa se é um banco de dados válido verificando as tabelas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
                tables = cursor.fetchall()
                conn.close()
                
                if result and result[0] == 1:
                    if tables:
                        success = True
                        message = f"Conexão SQLite estabelecida com sucesso!\n{len(tables)} tabela(s) encontrada(s)"
                    else:
                        success = True
                        message = "Conexão SQLite estabelecida, mas banco parece estar vazio"
                else:
                    success = False
                    message = "Conexão estabelecida mas teste falhou"
                
                # Atualiza status
                self.after(0, lambda: self.status_var.set("✓ Conexão SQLite testada com sucesso" if success else "Erro: Teste de conexão falhou"))
                
            except sqlite3.Error as e:
                success = False
                message = f"Erro SQLite: {str(e)}"
                self.after(0, lambda: self.status_var.set("Erro: Falha na conexão SQLite"))
            except Exception as e:
                success = False
                message = f"Erro na conexão SQLite: {str(e)}"
                self.after(0, lambda: self.status_var.set("Erro: Exceção ao conectar SQLite"))
            
            # Atualiza a interface na thread principal
            self.after(0, lambda: self.update_test_result(success, message))
        
        thread = threading.Thread(target=test_connection)
        thread.daemon = True
        thread.start()
    
    def test_postgresql_connection(self):
        """Testa conexão com PostgreSQL com validações completas."""
        # Validações básicas antes de tentar conectar
        host = self.db_host_var.get().strip()
        if not host:
            self.status_var.set("Erro: Host PostgreSQL não pode estar vazio")
            self.test_result_label.config(text="Host PostgreSQL não pode estar vazio", foreground='red')
            return
        
        database = self.db_name_var.get().strip()
        if not database:
            self.status_var.set("Erro: Nome do banco PostgreSQL não pode estar vazio")
            self.test_result_label.config(text="Nome do banco PostgreSQL não pode estar vazio", foreground='red')
            return
        
        user = self.db_user_var.get().strip()
        if not user:
            self.status_var.set("Erro: Usuário PostgreSQL não pode estar vazio")
            self.test_result_label.config(text="Usuário PostgreSQL não pode estar vazio", foreground='red')
            return
        
        # Coleta as configurações atuais da aba de banco de dados
        db_config = {
            'host': host,
            'port': int(self.db_port_var.get() or 5432),
            'database': database,
            'user': user,
            'password': self.db_password_var.get(),
            'sslmode': self.db_ssl_var.get(),
            'pool_size': int(self.db_pool_var.get() or 5),
            'timeout_ms': int(self.db_timeout_var.get() or 30000),
            'max_retries': int(self.db_retry_var.get() or 3)
        }
        
        # Desabilita o botão durante o teste
        self.test_button.config(state='disabled')
        self.test_result_label.config(text="Testando conexão...", foreground='blue')
        self.status_var.set("Conectando ao PostgreSQL...")
        
        # Executa o teste em uma thread separada
        def test_connection():
            try:
                import psycopg2
                
                # Testa conexão
                conn = psycopg2.connect(
                    host=db_config['host'],
                    port=db_config['port'],
                    database=db_config['database'],
                    user=db_config['user'],
                    password=db_config['password']
                )
                cursor = conn.cursor()
                cursor.execute("SELECT version()")
                version = cursor.fetchone()
                cursor.execute("SELECT current_database(), current_user")
                db_info = cursor.fetchone()
                conn.close()
                
                if version and db_info:
                    version_info = version[0].split()[0:2]  # Pega PostgreSQL e versão
                    success = True
                    message = f"Conexão PostgreSQL estabelecida com sucesso!\n{' '.join(version_info)}\nBanco: {db_info[0]}\nUsuário: {db_info[1]}"
                else:
                    success = False
                    message = "Conexão estabelecida mas teste falhou"
                
                # Atualiza status
                self.after(0, lambda: self.status_var.set("✓ Conexão PostgreSQL testada com sucesso" if success else "Erro: Teste de conexão PostgreSQL falhou"))
                
            except ImportError:
                success = False
                message = "Biblioteca psycopg2 não instalada"
                self.after(0, lambda: self.status_var.set("Erro: psycopg2 não instalado"))
            except psycopg2.OperationalError as e:
                error_msg = str(e)
                success = False
                if "could not connect" in error_msg:
                    message = f"Não foi possível conectar ao servidor PostgreSQL\nVerifique host e porta"
                elif "authentication failed" in error_msg:
                    message = f"Falha na autenticação\nVerifique usuário e senha"
                elif "does not exist" in error_msg:
                    message = f"Banco de dados não existe"
                else:
                    message = f"Erro de conexão PostgreSQL: {error_msg}"
                self.after(0, lambda: self.status_var.set("Erro: Falha na conexão PostgreSQL"))
            except Exception as e:
                success = False
                message = f"Erro na conexão PostgreSQL: {str(e)}"
                self.after(0, lambda: self.status_var.set("Erro: Exceção ao conectar PostgreSQL"))
            
            # Atualiza a interface na thread principal
            self.after(0, lambda: self.update_test_result(success, message))
        
        thread = threading.Thread(target=test_connection)
        thread.daemon = True
        thread.start()
    
    def update_test_result(self, success: bool, message: str):
        """Atualiza o resultado do teste de conexão."""
        if success:
            self.test_result_label.config(text="✓ Conexão bem-sucedida!", foreground='green')
        else:
            self.test_result_label.config(text=f"✗ {message}", foreground='red')
        
        self.test_button.config(state='normal', text="Testar Conexão")

        # Se sucesso com SQLite, aciona callback de troca de banco (se fornecido)
        try:
            if success and self.db_type_var.get() == 'SQLite' and self.sqlite_path_var.get() and self.on_database_changed:
                self.on_database_changed(self.sqlite_path_var.get())
        except Exception:
            pass
    
    def on_config_changed(self, event=None):
        """Chamado quando qualquer configuração é alterada."""
        self.has_changes = True
        self.status_var.set("Configurações modificadas (não salvas)")
    
    def on_tab_changed(self, event=None):
        """Chamado quando a aba é alterada."""
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if self.has_changes:
            self.status_var.set(f"Aba: {current_tab} (mudanças não salvas)")
        else:
            self.status_var.set(f"Aba: {current_tab}")
    
    def cancel_changes(self):
        """Cancela as alterações não salvas e recarrega as configurações atuais."""
        if self.has_changes:
            if messagebox.askyesno("Confirmar", "Deseja descartar as alterações não salvas?"):
                try:
                    # Recarrega as configurações atuais do arquivo
                    self.load_all_configs()
                    self.has_changes = False
                    self.status_var.set("Alterações canceladas - configurações recarregadas")
                    messagebox.showinfo("Sucesso", "Alterações canceladas com sucesso!")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao cancelar alterações:\n{str(e)}")
        else:
            messagebox.showinfo("Informação", "Não há alterações para cancelar.")
    
    def reset_to_defaults(self):
        """Redefine todas as configurações para os valores padrão."""
        if messagebox.askyesno("Confirmar", "Deseja realmente redefinir todas as configurações para os valores padrão?"):
            try:
                # Carrega configurações padrão para cada tipo
                for config_type in self.config_manager.config_files.keys():
                    default_config = self.config_manager.get_default_config(config_type)
                    self.config_manager.save_config(config_type, default_config)
                
                # Recarrega a interface
                self.load_all_configs()
                
                self.status_var.set("Configurações redefinidas para padrão")
                messagebox.showinfo("Sucesso", "Configurações redefinidas com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao redefinir configurações:\n{str(e)}")
    
    def export_configs(self):
        """Exporta todas as configurações para um arquivo."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Exportar Configurações"
        )
        
        if file_path:
            success = self.config_manager.export_config(file_path)
            if success:
                self.status_var.set("Configurações exportadas com sucesso")
                messagebox.showinfo("Sucesso", f"Configurações exportadas para:\n{file_path}")
            else:
                messagebox.showerror("Erro", "Erro ao exportar configurações")
    
    def import_configs(self):
        """Importa configurações de um arquivo."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Importar Configurações"
        )
        
        if file_path:
            success, errors = self.config_manager.import_config(file_path)
            if success:
                # Recarrega a interface
                self.load_all_configs()
                self.status_var.set("Configurações importadas com sucesso")
                
                if errors:
                    messagebox.showwarning("Aviso", f"Configurações importadas com avisos:\n" + "\n".join(errors))
                else:
                    messagebox.showinfo("Sucesso", "Configurações importadas com sucesso!")
            else:
                messagebox.showerror("Erro", f"Erro ao importar configurações:\n" + "\n".join(errors))
    
    def browse_log_file(self):
        """Abre diálogo para selecionar arquivo de log."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
            title="Selecionar Arquivo de Log"
        )
        
        if file_path:
            self.log_file_var.set(file_path)
            self.on_config_changed()
    
    def update_system_info(self):
        """Atualiza informações do sistema."""
        try:
            import psutil
            
            # Uso de memória
            memory = psutil.virtual_memory()
            self.memory_usage_label.config(text=f"Uso de Memória: {memory.percent:.1f}% ({memory.used // 1024 // 1024} MB)")
            
            # Uso de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage_label.config(text=f"Uso de CPU: {cpu_percent:.1f}%")
            
            # Conexões de rede (simulado)
            self.active_connections_label.config(text="Conexões Ativas: --")
            
        except ImportError:
            self.memory_usage_label.config(text="Uso de Memória: psutil não instalado")
            self.cpu_usage_label.config(text="Uso de CPU: psutil não instalado")
            self.active_connections_label.config(text="Conexões Ativas: psutil não instalado")
        except Exception:
            self.memory_usage_label.config(text="Uso de Memória: Erro ao obter")
            self.cpu_usage_label.config(text="Uso de CPU: Erro ao obter")
            self.active_connections_label.config(text="Conexões Ativas: Erro ao obter")
    
    def refresh_log_display(self):
        """Atualiza a exibição dos logs."""
        # Implementação básica - pode ser expandida
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.insert('1.0', "Logs serão exibidos aqui...\n")
        self.log_text.config(state='disabled')
    
    def clear_logs(self):
        """Limpa os logs."""
        if messagebox.askyesno("Confirmar", "Deseja realmente limpar os logs?"):
            try:
                log_file = self.log_file_var.get()
                if os.path.exists(log_file):
                    open(log_file, 'w').close()
                self.refresh_log_display()
                messagebox.showinfo("Sucesso", "Logs limpos com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao limpar logs:\n{str(e)}")
    
    def open_log_file(self):
        """Abre o arquivo de log no editor padrão."""
        try:
            log_file = self.log_file_var.get()
            if os.path.exists(log_file):
                if sys.platform.startswith('win'):
                    os.startfile(log_file)
                elif sys.platform.startswith('darwin'):
                    os.system(f'open "{log_file}"')
                else:
                    os.system(f'xdg-open "{log_file}"')
            else:
                messagebox.showinfo("Informação", "Arquivo de log não encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir arquivo de log:\n{str(e)}")


# Função auxiliar para testar a aba
def test_configuracoes_tab():
    """Função de teste para a aba de configurações."""
    root = tk.Tk()
    root.title("Teste da Aba de Configurações")
    root.geometry("800x600")
    
    # Cria o notebook
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Adiciona a aba de configurações
    config_tab = ConfiguracoesTab(notebook)
    notebook.add(config_tab, text="Configurações")
    
    root.mainloop()


if __name__ == "__main__":
    test_configuracoes_tab()