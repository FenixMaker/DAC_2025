# -*- coding: utf-8 -*-
"""
Janela de importação de dados TIC Domicílios
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import time
import os
from typing import List, Optional, Callable

from ..modules.data_importer import DataImporter
from ..utils.logger import get_logger
from .icons import get_icon, get_icon_color

class ImportWindow:
    """Janela para importação de dados CSV, Excel e PDF com validação robusta"""
    
    def __init__(self, parent, db_manager, callback: Optional[Callable] = None):
        self.parent = parent
        self.db_manager = db_manager
        self.callback = callback
        self.logger = get_logger(__name__)
        
        # Configurações de importação
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.supported_extensions = {'.csv', '.xlsx', '.xls', '.pdf'}
        self.batch_size = 1000  # Registros por lote
        
        # Estatísticas de importação
        self.import_stats = {
            'total_files': 0,
            'processed_files': 0,
            'success_count': 0,
            'error_count': 0,
            'total_records': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.title("Importação de Dados - DAC System")
        # Tamanho compacto e adequado
        self.window.geometry("920x620")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Aplicar tema escuro moderno
        self.window.configure(bg='#0D1117')
        
        # Configurar estilos TTK para tema escuro
        self.setup_dark_theme()
        
        # Variáveis
        self.selected_files: List[str] = []
        self.import_thread = None
        self.status_var = tk.StringVar(value="Pronto para importação")
        
        # Centralizar janela
        self.center_window()
        
        # Criar interface
        self.create_widgets()
        # Ajustar layout em resize (somente wrap de treeview/log pela rolagem)
        self.window.bind('<Configure>', lambda e: None)
        self.setup_keyboard_shortcuts()
        
    def setup_keyboard_shortcuts(self):
        """Configurar atalhos de teclado"""
        self.window.bind('<Control-o>', lambda e: self.select_csv_files())
        self.window.bind('<Control-e>', lambda e: self.select_excel_files())
        self.window.bind('<Control-p>', lambda e: self.start_pdf_import())
        self.window.bind('<Control-i>', lambda e: self.start_import())
        self.window.bind('<Control-c>', lambda e: self.cancel_import())
        self.window.bind('<Delete>', lambda e: self.clear_selection())
        self.window.bind('<Escape>', lambda e: self.on_closing())
        self.window.bind('<F5>', lambda e: self.refresh_file_list())
    
    def on_closing(self):
        """Tratar fechamento da janela"""
        if self.import_thread is not None:
            if messagebox.askyesno("Confirmar", "Há uma importação em andamento. Deseja cancelar e fechar?"):
                self.cancel_import()
                self.window.destroy()
        else:
            self.window.destroy()
    
    def center_window(self):
        """Centralizar janela na tela"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_dark_theme(self):
        """Configurar tema escuro para a janela de importação"""
        style = ttk.Style()
        
        # Cores do tema escuro
        colors = {
            'bg_primary': '#0D1117',
            'bg_secondary': '#161B22',
            'bg_card': '#21262D',
            'bg_hover': '#30363D',
            'text_primary': '#F0F6FC',
            'text_secondary': '#8B949E',
            'accent_blue': '#238CF5',
            'accent_green': '#34D399',
            'border': '#30363D'
        }
        
        # Configurar estilos TTK
        style.configure('Dark.TFrame',
                       background=colors['bg_primary'])
        
        style.configure('Dark.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['text_primary'],
                       font=('Segoe UI', 10))
        
        style.configure('Dark.Title.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['text_primary'],
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Dark.TButton',
                       background=colors['accent_blue'],
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(15, 8),
                       relief='flat',
                       borderwidth=0)
        
        style.map('Dark.TButton',
                 background=[('active', colors['bg_hover']),
                           ('pressed', colors['accent_green'])])
        
        style.configure('Dark.Treeview',
                       background=colors['bg_card'],
                       foreground=colors['text_primary'],
                       fieldbackground=colors['bg_card'],
                       borderwidth=0,
                       font=('Segoe UI', 10))
        
        style.configure('Dark.Treeview.Heading',
                       background=colors['bg_secondary'],
                       foreground=colors['text_primary'],
                       font=('Segoe UI', 11, 'bold'))
        
        style.configure('Dark.TProgressbar',
                       background=colors['accent_blue'],
                       troughcolor=colors['bg_card'],
                       borderwidth=0)
        
        style.configure('Dark.TLabelFrame',
                       background=colors['bg_primary'],
                       relief='flat',
                       borderwidth=1,
                       lightcolor=colors['border'],
                       darkcolor=colors['border'])
        
        style.configure('Dark.TLabelFrame.Label',
                       background=colors['bg_primary'],
                       foreground=colors['text_primary'],
                       font=('Segoe UI', 12, 'bold'))
    
    def create_widgets(self):
        """Criar widgets da interface aprimorada com tema escuro"""
        # Frame principal com tema escuro (sem scroll, tamanho fixo mostra tudo)
        main_frame = ttk.Frame(self.window, padding="20", style='Dark.TFrame')
        main_frame.pack(fill='both', expand=True)

        # Configurar grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # Título e status com Material Symbols
        header_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)

        import_icon = get_icon('import')
        title_label = ttk.Label(header_frame,
                                text=f"{import_icon} Importação de Dados - DAC System",
                                style='Dark.Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)

        # Status com cor personalizada
        self.status_label = tk.Label(header_frame,
                                     textvariable=self.status_var,
                                     font=('Segoe UI', 10),
                                     bg='#0D1117',
                                     fg='#34D399')  # Verde para status
        self.status_label.grid(row=0, column=1, sticky=tk.E)

        # Seleção de arquivos com tema escuro usando tk.Frame
        files_container = tk.Frame(main_frame, bg='#0D1117')
        files_container.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20), padx=20)
        files_container.columnconfigure(0, weight=1)

        # Título da seção com Material Symbol
        folder_icon = get_icon('folder_open')
        files_title = tk.Label(files_container,
                               text=f"{folder_icon} Seleção de Arquivos",
                               font=('Segoe UI', 12, 'bold'),
                               bg='#0D1117',
                               fg='#F0F6FC')
        files_title.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

        # Frame interno para os controles
        files_frame = tk.Frame(files_container, bg='#21262D', relief='flat', bd=1)
        files_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=0, pady=0)
        files_frame.columnconfigure(1, weight=1)

        # Botões de seleção com Material Symbols
        buttons_row1 = tk.Frame(files_frame, bg='#21262D')
        buttons_row1.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E),
                          pady=(15, 15), padx=20)

        # Usar tk.Button com Material Symbols
        file_icon = get_icon('file')
        btn_csv = tk.Button(buttons_row1, text=f"{file_icon} CSV (Ctrl+O)",
                            command=self.select_csv_files,
                            bg='#238CF5', fg='white',
                            font=('Segoe UI', 10, 'bold'),
                            relief='flat', bd=0, padx=15, pady=8)
        btn_csv.grid(row=0, column=0, padx=(0, 10))

        table_icon = get_icon('table')
        btn_excel = tk.Button(buttons_row1, text=f"{table_icon} Excel (Ctrl+E)",
                              command=self.select_excel_files,
                              bg='#238CF5', fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', bd=0, padx=15, pady=8)
        btn_excel.grid(row=0, column=1, padx=(0, 10))

        delete_icon = get_icon('delete')
        btn_clear = tk.Button(buttons_row1, text=f"{delete_icon} Limpar (Del)",
                              command=self.clear_selection,
                              bg='#238CF5', fg='white',
                              font=('Segoe UI', 10, 'bold'),
                              relief='flat', bd=0, padx=15, pady=8)
        btn_clear.grid(row=0, column=2, padx=(0, 10))

        refresh_icon = get_icon('refresh')
        btn_refresh = tk.Button(buttons_row1, text=f"{refresh_icon} Atualizar (F5)",
                                command=self.refresh_file_list,
                                bg='#238CF5', fg='white',
                                font=('Segoe UI', 10, 'bold'),
                                relief='flat', bd=0, padx=15, pady=8)
        btn_refresh.grid(row=0, column=3)

        # Lista de arquivos com tema escuro
        list_frame = tk.Frame(files_frame, bg='#21262D')
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S),
                        pady=(0, 15), padx=20)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Treeview com tema escuro
        columns = ('arquivo', 'tipo', 'tamanho', 'status')
        self.files_tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                       height=8)

        # Configurar colunas da tabela com Material Symbols
        file_col_icon = get_icon('description')
        self.files_tree.heading('arquivo', text=f'{file_col_icon} Arquivo')
        type_icon = get_icon('category')
        self.files_tree.heading('tipo', text=f'{type_icon} Tipo')
        size_icon = get_icon('data_usage')
        self.files_tree.heading('tamanho', text=f'{size_icon} Tamanho')
        status_icon = get_icon('check_circle')
        self.files_tree.heading('status', text=f'{status_icon} Status')

        self.files_tree.column('arquivo', width=300)
        self.files_tree.column('tipo', width=80)
        self.files_tree.column('tamanho', width=100)
        self.files_tree.column('status', width=120)

        self.files_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbars com tema escuro
        tree_v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical",
                                         command=self.files_tree.yview)
        tree_v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.files_tree.config(yscrollcommand=tree_v_scrollbar.set)

        tree_h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal",
                                         command=self.files_tree.xview)
        tree_h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.files_tree.config(xscrollcommand=tree_h_scrollbar.set)

        # Informações de seleção com tema escuro
        info_label = tk.Label(files_frame,
                              text="📁 Arquivos suportados: CSV, Excel (.xlsx, .xls), PDF | 📏 Tamanho máximo: 100MB",
                              font=('Segoe UI', 10),
                              bg='#21262D',
                              fg='#8B949E')
        info_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=20, pady=(0, 15))

        # Progresso e estatísticas com tema escuro
        progress_container = tk.Frame(main_frame, bg='#0D1117')
        progress_container.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20), padx=20)
        progress_container.columnconfigure(0, weight=1)

        # Título da seção de progresso
        progress_title = tk.Label(progress_container,
                                  text="⏱️ Progresso da Importação",
                                  font=('Segoe UI', 12, 'bold'),
                                  bg='#0D1117',
                                  fg='#F0F6FC')
        progress_title.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

        # Frame do progresso
        progress_frame = tk.Frame(progress_container, bg='#21262D', relief='flat', bd=1)
        progress_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=0, pady=0)
        progress_frame.columnconfigure(0, weight=1)

        # Barra de progresso com tema escuro
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                            maximum=100, length=500)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(15, 15), padx=20)

        # Estatísticas em tempo real com tema escuro
        stats_frame = tk.Frame(progress_frame, bg='#21262D')
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=20, pady=(0, 15))

        self.stats_labels = {}
        stats_info = [
            ('processed', '📊 Processados: 0/0'),
            ('success', '✅ Sucessos: 0'),
            ('errors', '❌ Erros: 0'),
            ('records', '📋 Registros: 0'),
            ('time', '⏱️ Tempo: 00:00')
        ]

        for i, (key, text) in enumerate(stats_info):
            label = tk.Label(stats_frame, text=text,
                             font=('Segoe UI', 10),
                             bg='#21262D',
                             fg='#F0F6FC')
            label.grid(row=0, column=i, padx=(0, 25), sticky=tk.W)
            self.stats_labels[key] = label

        # Log de mensagens com tema escuro
        log_container = tk.Frame(main_frame, bg='#0D1117')
        log_container.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20), padx=20)
        log_container.columnconfigure(0, weight=1)
        log_container.rowconfigure(1, weight=1)

        # Título da seção de log
        log_title = tk.Label(log_container,
                             text="📝 Log de Importação",
                             font=('Segoe UI', 12, 'bold'),
                             bg='#0D1117',
                             fg='#F0F6FC')
        log_title.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

        # Frame do log
        log_frame = tk.Frame(log_container, bg='#21262D', relief='flat', bd=1)
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=0, pady=0)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # Text widget para log com tema escuro
        self.log_text = tk.Text(log_frame, height=12, wrap=tk.WORD,
                                font=('JetBrains Mono', 9),
                                bg='#21262D', fg='#F0F6FC',
                                insertbackground='#F0F6FC',
                                selectbackground='#30363D')
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=15, pady=15)

        # Configurar tags para cores no tema escuro
        self.log_text.tag_config('success', foreground='#34D399')  # Verde
        self.log_text.tag_config('error', foreground='#F87171')    # Vermelho
        self.log_text.tag_config('warning', foreground='#FB923C')  # Laranja
        self.log_text.tag_config('info', foreground='#238CF5')     # Azul

        # Scrollbar para log
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=(0, 15), pady=15)
        self.log_text.config(yscrollcommand=log_scrollbar.set)

        # Botões de ação com tema escuro
        buttons_frame = tk.Frame(main_frame, bg='#0D1117')
        buttons_frame.grid(row=4, column=0, pady=(15, 0), padx=20)

        self.import_button = tk.Button(buttons_frame, text="📥 Importar Arquivos (Ctrl+I)",
                                       command=self.start_import, state='disabled',
                                       bg='#238CF5', fg='white',
                                       font=('Segoe UI', 11, 'bold'),
                                       relief='flat', bd=0, padx=20, pady=10)
        self.import_button.grid(row=0, column=0, padx=(0, 10))

        self.import_pdf_button = tk.Button(buttons_frame, text="📄 Processar PDFs (Ctrl+P)",
                                           command=self.start_pdf_import,
                                           bg='#238CF5', fg='white',
                                           font=('Segoe UI', 11, 'bold'),
                                           relief='flat', bd=0, padx=20, pady=10)
        self.import_pdf_button.grid(row=0, column=1, padx=(0, 10))

        self.cancel_button = tk.Button(buttons_frame, text="❌ Cancelar (Ctrl+C)",
                                       command=self.cancel_import, state='disabled',
                                       bg='#F87171', fg='white',
                                       font=('Segoe UI', 11, 'bold'),
                                       relief='flat', bd=0, padx=20, pady=10)
        self.cancel_button.grid(row=0, column=2, padx=(0, 10))

        close_button = tk.Button(buttons_frame, text="🚪 Fechar (Esc)",
                                 command=self.on_closing,
                                 bg='#8B949E', fg='white',
                                 font=('Segoe UI', 11, 'bold'),
                                 relief='flat', bd=0, padx=20, pady=10)
        close_button.grid(row=0, column=3)
    
    def select_csv_files(self):
        """Seleciona arquivos CSV"""
        try:
            files = filedialog.askopenfilenames(
                title="Selecionar arquivos CSV",
                filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
            )
            if files:
                self.add_files(files, "CSV")
        except Exception as e:
            self.logger.error(f"Erro ao selecionar arquivos CSV: {e}")
            messagebox.showerror("Erro", f"Erro ao selecionar arquivos CSV: {str(e)}")
    
    def select_excel_files(self):
        """Seleciona arquivos Excel"""
        try:
            files = filedialog.askopenfilenames(
                title="Selecionar arquivos Excel",
                filetypes=[("Arquivos Excel", "*.xlsx *.xls"), ("Todos os arquivos", "*.*")]
            )
            if files:
                self.add_files(files, "Excel")
        except Exception as e:
            self.logger.error(f"Erro ao selecionar arquivos Excel: {e}")
            messagebox.showerror("Erro", f"Erro ao selecionar arquivos Excel: {str(e)}")
    
    def add_files(self, files, file_type):
        """Adiciona arquivos à lista com validação robusta"""
        added_count = 0
        error_count = 0
        
        for file_path in files:
            try:
                # Validar se o arquivo existe
                if not Path(file_path).exists():
                    self.logger.warning(f"Arquivo não encontrado: {file_path}")
                    error_count += 1
                    continue
                
                # Validar tamanho do arquivo (máximo 100MB)
                file_size = Path(file_path).stat().st_size
                if file_size > 100 * 1024 * 1024:  # 100MB
                    self.logger.warning(f"Arquivo muito grande (>100MB): {file_path}")
                    messagebox.showwarning("Aviso", f"Arquivo muito grande: {Path(file_path).name}\nTamanho máximo: 100MB")
                    error_count += 1
                    continue
                
                # Validar extensão do arquivo
                file_ext = Path(file_path).suffix.lower()
                valid_extensions = {
                    'CSV': ['.csv'],
                    'Excel': ['.xlsx', '.xls']
                }
                
                if file_ext not in valid_extensions.get(file_type, []):
                    self.logger.warning(f"Extensão inválida para {file_type}: {file_path}")
                    messagebox.showwarning("Aviso", f"Extensão inválida para {file_type}: {file_ext}")
                    error_count += 1
                    continue
                
                # Verificar se já foi adicionado
                if file_path not in [f[0] for f in self.selected_files]:
                    self.selected_files.append((file_path, file_type))
                    
                    # Adicionar à treeview com informações detalhadas
                    file_name = Path(file_path).name
                    formatted_size = self.format_file_size(file_size)
                    
                    self.files_tree.insert('', 'end', values=(
                        file_name,
                        file_type,
                        formatted_size,
                        'Pronto'
                    ))
                    
                    added_count += 1
                    self.logger.info(f"Arquivo adicionado: {file_path}")
                
            except Exception as e:
                self.logger.error(f"Erro ao processar arquivo {file_path}: {e}")
                error_count += 1
        
        # Feedback ao usuário
        if added_count > 0:
            self.log_message(f"✓ {added_count} arquivo(s) adicionado(s) com sucesso", 'success')
        
        if error_count > 0:
            self.log_message(f"✗ {error_count} arquivo(s) com problemas", 'error')
        
        # Atualizar status
        self.status_var.set(f"{len(self.selected_files)} arquivo(s) selecionado(s)")
        self.update_import_button()
    
    def format_file_size(self, size_bytes):
        """Formatar tamanho do arquivo em formato legível"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def refresh_file_list(self):
        """Atualizar lista de arquivos verificando se ainda existem"""
        if not self.selected_files:
            self.log_message("Nenhum arquivo para atualizar", 'info')
            return
        
        self.log_message("Atualizando lista de arquivos...", 'info')
        
        # Limpar treeview
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        
        # Revalidar arquivos
        valid_files = []
        for file_path, file_type in self.selected_files[:]:
            try:
                if Path(file_path).exists():
                    file_size = Path(file_path).stat().st_size
                    if file_size > 0 and file_size <= self.max_file_size:
                        valid_files.append((file_path, file_type))
                        
                        file_name = Path(file_path).name
                        formatted_size = self.format_file_size(file_size)
                        
                        self.files_tree.insert('', 'end', values=(
                            file_name,
                            file_type,
                            formatted_size,
                            'Pronto'
                        ))
                    else:
                        self.log_message(f"✗ Arquivo removido (inválido): {Path(file_path).name}", 'warning')
                else:
                    self.log_message(f"✗ Arquivo removido (não encontrado): {Path(file_path).name}", 'warning')
            except Exception as e:
                self.log_message(f"✗ Erro ao validar arquivo: {Path(file_path).name}", 'error')
        
        self.selected_files = valid_files
        self.status_var.set(f"{len(self.selected_files)} arquivo(s) válido(s)")
        self.update_import_button()
        
        self.log_message(f"Lista atualizada: {len(valid_files)} arquivo(s) válido(s)", 'success')
    
    def clear_selection(self):
        """Limpa a seleção de arquivos"""
        self.selected_files.clear()
        
        # Limpar treeview
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
        
        self.status_var.set("Pronto para importação")
        self.log_message("Seleção de arquivos limpa", 'info')
        self.update_import_button()
    
    def update_import_button(self):
        """Atualiza o estado do botão de importação"""
        if self.selected_files and self.import_thread is None:
            self.import_button.config(state=tk.NORMAL)
        else:
            self.import_button.config(state=tk.DISABLED)
    
    def log_message(self, message, tag='info'):
        """Adiciona mensagem ao log com formatação por cores"""
        self.log_text.config(state=tk.NORMAL)
        
        # Adicionar timestamp
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        # Inserir com tag apropriada
        self.log_text.insert(tk.END, full_message, tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.window.update_idletasks()
    
    def start_import(self):
        """Iniciar importação de arquivos com validação e estatísticas"""
        if not self.selected_files:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado!")
            return
        
        # Verificar conexão com banco
        if not self.db_manager:
            messagebox.showerror("Erro", "Conexão com banco de dados não disponível!")
            return
        
        # Resetar estatísticas
        self.import_stats = {
            'total_files': len(self.selected_files),
            'processed_files': 0,
            'success_count': 0,
            'error_count': 0,
            'total_records': 0,
            'start_time': time.time(),
            'end_time': None
        }
        
        # Configurar interface para importação
        self.import_button.config(state='disabled')
        self.import_pdf_button.config(state='disabled')
        self.cancel_button.config(state='normal')
        self.progress_var.set(0)
        self.status_var.set("Importando arquivos...")
        
        # Atualizar status dos arquivos na treeview
        for item in self.files_tree.get_children():
            self.files_tree.set(item, 'status', 'Aguardando...')
        
        # Iniciar thread de importação
        self.import_thread = threading.Thread(target=self.import_files_thread)
        self.import_thread.daemon = True
        self.import_thread.start()
    
    def start_pdf_import(self):
        """Iniciar importação de PDFs com seleção automática"""
        # Verificar conexão com banco
        if not self.db_manager:
            messagebox.showerror("Erro", "Conexão com banco de dados não disponível!")
            return
        
        # Resetar estatísticas
        self.import_stats = {
            'total_files': 0,  # Será definido após seleção
            'processed_files': 0,
            'success_count': 0,
            'error_count': 0,
            'total_records': 0,
            'start_time': time.time(),
            'end_time': None
        }
        
        # Configurar interface
        self.import_button.config(state='disabled')
        self.import_pdf_button.config(state='disabled')
        self.cancel_button.config(state='normal')
        self.progress_var.set(0)
        self.status_var.set("Processando PDFs...")
        
        # Iniciar thread de importação de PDF
        self.import_thread = threading.Thread(target=self.import_pdf_thread)
        self.import_thread.daemon = True
        self.import_thread.start()
        
        self.log_message("Iniciando processamento de PDFs...", 'info')
    
    def import_files_thread(self):
        """Thread para importação de arquivos com estatísticas em tempo real"""
        try:
            total_files = len(self.selected_files)
            self.log_message(f"Iniciando importação de {total_files} arquivo(s)...", 'info')
            
            # Criar instância do importador
            importer = DataImporter(self.db_manager)
            
            # Obter itens da treeview para atualização de status
            tree_items = list(self.files_tree.get_children())
            
            # Processar cada arquivo
            for i, (file_path, file_type) in enumerate(self.selected_files):
                if self.import_thread is None:  # Cancelado
                    self.log_message("⚠ Importação cancelada pelo usuário", 'warning')
                    break
                
                file_name = Path(file_path).name
                self.log_message(f"Processando [{i+1}/{total_files}]: {file_name}", 'info')
                
                # Atualizar status na treeview
                if i < len(tree_items):
                    self.files_tree.set(tree_items[i], 'status', 'Processando...')
                
                try:
                    # Validação final do arquivo
                    validation_result = self.validate_file_for_import(file_path)
                    if not validation_result['valid']:
                        raise ValueError(validation_result['error'])
                    
                    # Callback para progresso do arquivo
                    def file_progress(current, total):
                        if total > 0:
                            file_percent = (current / total) * 100
                            overall_percent = ((i + (current / total)) / total_files) * 100
                            self.progress_var.set(overall_percent)
                            
                            # Atualizar estatísticas em tempo real
                            self.update_import_stats()
                    
                    # Importar arquivo
                    result = importer.import_file(file_path, progress_callback=file_progress)
                    
                    if result and result.get('success', False):
                        records_imported = result.get('records_imported', 0)
                        self.import_stats['success_count'] += 1
                        self.import_stats['total_records'] += records_imported
                        
                        # Atualizar status na treeview
                        if i < len(tree_items):
                            self.files_tree.set(tree_items[i], 'status', f'✓ {records_imported} registros')
                        
                        self.log_message(f"✓ Sucesso: {records_imported} registro(s) importado(s)", 'success')
                    else:
                        error_msg = result.get('error', 'Falha desconhecida') if result else 'Falha na importação'
                        self.import_stats['error_count'] += 1
                        
                        # Atualizar status na treeview
                        if i < len(tree_items):
                            self.files_tree.set(tree_items[i], 'status', '✗ Erro')
                        
                        self.log_message(f"✗ Falha: {error_msg}", 'error')
                
                except FileNotFoundError:
                    self.import_stats['error_count'] += 1
                    if i < len(tree_items):
                        self.files_tree.set(tree_items[i], 'status', '✗ Não encontrado')
                    self.log_message(f"✗ Arquivo não encontrado: {file_name}", 'error')
                
                except PermissionError:
                    self.import_stats['error_count'] += 1
                    if i < len(tree_items):
                        self.files_tree.set(tree_items[i], 'status', '✗ Sem permissão')
                    self.log_message(f"✗ Sem permissão para acessar: {file_name}", 'error')
                
                except ValueError as e:
                    self.import_stats['error_count'] += 1
                    if i < len(tree_items):
                        self.files_tree.set(tree_items[i], 'status', '✗ Dados inválidos')
                    self.log_message(f"✗ Dados inválidos: {str(e)}", 'error')
                
                except Exception as e:
                    self.import_stats['error_count'] += 1
                    if i < len(tree_items):
                        self.files_tree.set(tree_items[i], 'status', '✗ Erro inesperado')
                    self.log_message(f"✗ Erro inesperado: {str(e)}", 'error')
                    self.logger.error(f"Erro inesperado na importação de {file_path}: {e}")
                
                # Atualizar progresso e estatísticas
                self.import_stats['processed_files'] += 1
                progress = (self.import_stats['processed_files'] / total_files) * 100
                self.progress_var.set(progress)
                self.update_import_stats()
            
            # Finalizar importação
            self.import_stats['end_time'] = time.time()
            
            # Relatório final
            if self.import_thread is not None:
                duration = self.import_stats['end_time'] - self.import_stats['start_time']
                self.log_message("\n=== Importação Concluída ===", 'info')
                self.log_message(f"✓ Sucessos: {self.import_stats['success_count']}", 'success')
                self.log_message(f"✗ Erros: {self.import_stats['error_count']}", 'error')
                self.log_message(f"📊 Total processado: {self.import_stats['processed_files']}/{total_files}", 'info')
                self.log_message(f"📈 Registros importados: {self.import_stats['total_records']}", 'info')
                self.log_message(f"⏱ Tempo total: {duration:.1f}s", 'info')
                
                # Atualizar estatísticas na janela principal
                if self.callback and self.import_stats['success_count'] > 0:
                    self.window.after(100, self.callback)
        
        except Exception as e:
            self.log_message(f"✗ Erro crítico no processo de importação: {str(e)}", 'error')
            self.logger.error(f"Erro crítico na importação: {e}")
            self.import_stats['error_count'] = len(self.selected_files)
        
        finally:
            # Restaurar interface
            import_success = (self.import_stats['success_count'] > 0 and 
                            self.import_stats['error_count'] == 0)
            self.window.after(100, lambda: self.import_finished(import_success, "arquivos"))
    
    def validate_file_for_import(self, file_path):
        """Validar arquivo antes da importação"""
        try:
            path = Path(file_path)
            
            # Verificar se existe
            if not path.exists():
                return {'valid': False, 'error': f'Arquivo não encontrado: {path.name}'}
            
            # Verificar se não está vazio
            if path.stat().st_size == 0:
                return {'valid': False, 'error': f'Arquivo vazio: {path.name}'}
            
            # Verificar tamanho máximo
            if path.stat().st_size > self.max_file_size:
                return {'valid': False, 'error': f'Arquivo muito grande: {path.name}'}
            
            # Verificar extensão
            if path.suffix.lower() not in self.supported_extensions:
                return {'valid': False, 'error': f'Extensão não suportada: {path.suffix}'}
            
            return {'valid': True, 'error': None}
            
        except Exception as e:
            return {'valid': False, 'error': f'Erro na validação: {str(e)}'}
    
    def update_import_stats(self):
        """Atualizar estatísticas em tempo real na interface"""
        try:
            # Atualizar labels de estatísticas
            self.stats_labels['processed'].config(
                text=f"Processados: {self.import_stats['processed_files']}/{self.import_stats['total_files']}"
            )
            self.stats_labels['success'].config(
                text=f"Sucessos: {self.import_stats['success_count']}"
            )
            self.stats_labels['errors'].config(
                text=f"Erros: {self.import_stats['error_count']}"
            )
            self.stats_labels['records'].config(
                text=f"Registros: {self.import_stats['total_records']}"
            )
            
            # Calcular tempo decorrido
            if self.import_stats['start_time']:
                elapsed = time.time() - self.import_stats['start_time']
                minutes = int(elapsed // 60)
                seconds = int(elapsed % 60)
                self.stats_labels['time'].config(
                    text=f"Tempo: {minutes:02d}:{seconds:02d}"
                )
            
            self.window.update_idletasks()
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar estatísticas: {e}")
    
    def cancel_import(self):
        """Cancela a importação"""
        if self.import_thread:
            self.import_thread = None
            self.log_message("\n=== Importação cancelada ===")
            self.import_finished()
    
    def import_pdf_thread(self):
        """Thread para importação de PDFs com estatísticas em tempo real"""
        try:
            total_files = len(self.selected_files)
            self.log_message(f"Iniciando importação de {total_files} arquivo(s) PDF...", 'info')
            
            # Criar instância do extrator de PDF
            from ..modules.pdf_processor import PDFProcessor
            processor = PDFProcessor()
            
            # Obter itens da treeview para atualização de status
            tree_items = list(self.files_tree.get_children())
            
            # Processar cada arquivo PDF
            for i, (file_path, file_type) in enumerate(self.selected_files):
                if self.import_thread is None:  # Cancelado
                    self.log_message("⚠ Importação cancelada pelo usuário", 'warning')
                    break
                
                file_name = Path(file_path).name
                self.log_message(f"Processando PDF [{i+1}/{total_files}]: {file_name}", 'info')
                
                # Atualizar status na treeview
                if i < len(tree_items):
                    self.files_tree.set(tree_items[i], 'status', 'Extraindo dados...')
                
                try:
                    # Validação final do arquivo
                    validation_result = self.validate_file_for_import(file_path)
                    if not validation_result['valid']:
                        raise ValueError(validation_result['error'])
                    
                    # Callback para progresso da extração
                    def extraction_progress(current, total):
                        if total > 0:
                            file_percent = (current / total) * 100
                            overall_percent = ((i + (current / total)) / total_files) * 100
                            self.progress_var.set(overall_percent)
                            
                            # Atualizar estatísticas em tempo real
                            self.update_import_stats()
                    
                    # Extrair dados do PDF
                    extracted_data = processor.extract_data_from_pdf(file_path)
                    
                    if extracted_data and len(extracted_data) > 0:
                        # Atualizar status na treeview
                        if i < len(tree_items):
                            self.files_tree.set(tree_items[i], 'status', 'Importando dados...')
                        
                        # Importar dados extraídos
                        importer = DataImporter(self.db_manager)
                        result = importer.import_extracted_data(extracted_data)
                        
                        if result and result.get('success', False):
                            records_imported = result.get('records_imported', len(extracted_data))
                            self.import_stats['success_count'] += 1
                            self.import_stats['total_records'] += records_imported
                            
                            # Atualizar status na treeview
                            if i < len(tree_items):
                                self.files_tree.set(tree_items[i], 'status', f'✓ {records_imported} registros')
                            
                            self.log_message(f"✓ Sucesso: {records_imported} registro(s) extraído(s) e importado(s)", 'success')
                        else:
                            error_msg = result.get('error', 'Falha na importação') if result else 'Falha na importação'
                            self.import_stats['error_count'] += 1
                            
                            # Atualizar status na treeview
                            if i < len(tree_items):
                                self.files_tree.set(tree_items[i], 'status', '✗ Erro na importação')
                            
                            self.log_message(f"✗ Falha na importação: {error_msg}", 'error')
                    else:
                        self.import_stats['error_count'] += 1
                        
                        # Atualizar status na treeview
                        if i < len(tree_items):
                            self.files_tree.set(tree_items[i], 'status', '✗ Sem dados válidos')
                        
                        self.log_message("⚠ Nenhum dado válido encontrado no PDF", 'warning')
                
                except FileNotFoundError:
                    self.import_stats['error_count'] += 1
                    if i < len(tree_items):
                        self.files_tree.set(tree_items[i], 'status', '✗ Não encontrado')
                    self.log_message(f"✗ Arquivo não encontrado: {file_name}", 'error')
                
                except PermissionError:
                    self.import_stats['error_count'] += 1
                    if i < len(tree_items):
                        self.files_tree.set(tree_items[i], 'status', '✗ Sem permissão')
                    self.log_message(f"✗ Sem permissão para acessar: {file_name}", 'error')
                
                except ValueError as e:
                    self.import_stats['error_count'] += 1
                    if i < len(tree_items):
                        self.files_tree.set(tree_items[i], 'status', '✗ Dados inválidos')
                    self.log_message(f"✗ Dados inválidos: {str(e)}", 'error')
                
                except Exception as e:
                    self.import_stats['error_count'] += 1
                    if i < len(tree_items):
                        self.files_tree.set(tree_items[i], 'status', '✗ Erro inesperado')
                    self.log_message(f"✗ Erro inesperado: {str(e)}", 'error')
                    self.logger.error(f"Erro inesperado na importação de PDF {file_path}: {e}")
                
                # Atualizar progresso e estatísticas
                self.import_stats['processed_files'] += 1
                progress = (self.import_stats['processed_files'] / total_files) * 100
                self.progress_var.set(progress)
                self.update_import_stats()
            
            # Finalizar importação
            self.import_stats['end_time'] = time.time()
            
            # Relatório final
            if self.import_thread is not None:
                duration = self.import_stats['end_time'] - self.import_stats['start_time']
                self.log_message("\n=== Importação de PDF Concluída ===", 'info')
                self.log_message(f"✓ Sucessos: {self.import_stats['success_count']}", 'success')
                self.log_message(f"✗ Erros: {self.import_stats['error_count']}", 'error')
                self.log_message(f"📊 Total processado: {self.import_stats['processed_files']}/{total_files}", 'info')
                self.log_message(f"📈 Registros importados: {self.import_stats['total_records']}", 'info')
                self.log_message(f"⏱ Tempo total: {duration:.1f}s", 'info')
                
                # Atualizar estatísticas na janela principal
                if self.callback and self.import_stats['success_count'] > 0:
                    self.window.after(100, self.callback)
        
        except Exception as e:
            self.log_message(f"✗ Erro crítico no processo de importação de PDF: {str(e)}", 'error')
            self.logger.error(f"Erro crítico na importação de PDF: {e}")
            self.import_stats['error_count'] = len(self.selected_files)
        
        finally:
            # Restaurar interface
            import_success = (self.import_stats['success_count'] > 0 and 
                            self.import_stats['error_count'] == 0)
            self.window.after(100, lambda: self.import_finished(import_success, "PDFs"))
    
    def import_finished(self, success=True, import_type="arquivos"):
        """Finaliza o processo de importação com feedback detalhado"""
        try:
            # Parar thread de importação
            self.import_thread = None
            
            # Restaurar interface
            self.import_button.config(state='normal')
            self.import_pdf_button.config(state='normal')
            self.cancel_button.config(state='disabled')
            
            # Atualizar status
            if success:
                self.status_var.set("Importação concluída com sucesso")
            else:
                self.status_var.set("Importação concluída com erros")
            
            # Resetar progresso após um breve delay
            self.window.after(2000, lambda: self.progress_var.set(0))
            
            # Preparar estatísticas finais
            total_files = self.import_stats['total_files']
            success_count = self.import_stats['success_count']
            error_count = self.import_stats['error_count']
            total_records = self.import_stats['total_records']
            
            # Calcular tempo total
            duration = 0
            if self.import_stats['end_time'] and self.import_stats['start_time']:
                duration = self.import_stats['end_time'] - self.import_stats['start_time']
            
            # Feedback detalhado no log
            self.log_message("\n" + "="*50, 'info')
            self.log_message("RESUMO DA IMPORTAÇÃO", 'info')
            self.log_message("="*50, 'info')
            self.log_message(f"Tipo: {import_type.capitalize()}", 'info')
            self.log_message(f"Arquivos processados: {success_count + error_count}/{total_files}", 'info')
            self.log_message(f"Sucessos: {success_count}", 'success' if success_count > 0 else 'info')
            self.log_message(f"Erros: {error_count}", 'error' if error_count > 0 else 'info')
            self.log_message(f"Total de registros importados: {total_records}", 'info')
            if duration > 0:
                self.log_message(f"Tempo total: {duration:.1f} segundos", 'info')
                if total_records > 0:
                    rate = total_records / duration
                    self.log_message(f"Taxa de importação: {rate:.1f} registros/segundo", 'info')
            self.log_message("="*50, 'info')
            
            # Feedback visual com messagebox
            if success and error_count == 0:
                message = (f"Importação de {import_type} concluída com sucesso!\n\n"
                          f"📊 Estatísticas:\n"
                          f"• Arquivos processados: {success_count}/{total_files}\n"
                          f"• Registros importados: {total_records}\n"
                          f"• Tempo total: {duration:.1f}s")
                messagebox.showinfo("✅ Sucesso", message)
                self.log_message("🎉 Importação concluída com sucesso!", 'success')
            
            elif success_count > 0 and error_count > 0:
                message = (f"Importação de {import_type} concluída com avisos.\n\n"
                          f"📊 Estatísticas:\n"
                          f"• Sucessos: {success_count}\n"
                          f"• Erros: {error_count}\n"
                          f"• Registros importados: {total_records}\n\n"
                          f"⚠ Verifique o log para detalhes dos erros.")
                messagebox.showwarning("⚠ Concluído com Avisos", message)
                self.log_message("⚠ Importação concluída com alguns erros", 'warning')
            
            else:
                message = (f"Falha na importação de {import_type}.\n\n"
                          f"❌ Nenhum arquivo foi importado com sucesso.\n"
                          f"Total de erros: {error_count}\n\n"
                          f"Verifique o log para detalhes dos erros.")
                messagebox.showerror("❌ Falha na Importação", message)
                self.log_message("❌ Importação falhou completamente", 'error')
            
            # Atualizar estatísticas na janela principal
            if self.callback and success_count > 0:
                try:
                    self.callback()
                    self.log_message("📈 Estatísticas da janela principal atualizadas", 'info')
                except Exception as e:
                    self.logger.error(f"Erro ao executar callback: {e}")
                    self.log_message(f"⚠ Erro ao atualizar estatísticas: {str(e)}", 'warning')
            
            # Limpar seleção se importação foi bem-sucedida
            if success and error_count == 0:
                self.window.after(3000, self.clear_selection)
            
            # Log de finalização
            self.logger.info(f"Importação de {import_type} finalizada. "
                           f"Sucesso: {success}, Arquivos: {success_count}/{total_files}, "
                           f"Registros: {total_records}, Tempo: {duration:.1f}s")
            
        except Exception as e:
            self.logger.error(f"Erro ao finalizar importação: {e}")
            messagebox.showerror("Erro", f"Erro ao finalizar importação: {str(e)}")
            self.log_message(f"✗ Erro crítico na finalização: {str(e)}", 'error')