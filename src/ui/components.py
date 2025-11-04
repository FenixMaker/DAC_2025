
# -*- coding: utf-8 -*-
"""
Componentes reutilizáveis para a interface DAC
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Callable, Any

class ModernCard(ttk.Frame):
    """Card moderno para exibir informações"""
    
    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        self.title = title
        self.create_widgets()
    
    def create_widgets(self):
        """Cria widgets do card"""
        # Header do card
        if self.title:
            header = ttk.Label(self, text=self.title, 
                              font=('Segoe UI', 12, 'bold'))
            header.pack(anchor='w', padx=10, pady=(10, 5))
        
        # Separador
        ttk.Separator(self, orient='horizontal').pack(fill='x', padx=10)
        
        # Área de conteúdo
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    def add_metric(self, label: str, value: str, color: str = "black"):
        """Adiciona métrica ao card"""
        metric_frame = ttk.Frame(self.content_frame)
        metric_frame.pack(fill='x', pady=2)
        
        ttk.Label(metric_frame, text=f"{label}:").pack(side='left')
        ttk.Label(metric_frame, text=value, 
                 foreground=color, font=('Segoe UI', 10, 'bold')).pack(side='right')

class ProgressDialog:
    """Diálogo de progresso moderno"""
    
    def __init__(self, parent, title: str = "Processando..."):
        self.parent = parent
        self.title = title
        self.window = None
        self.progress_var = None
        self.status_var = None
        self.create_dialog()
    
    def create_dialog(self):
        """Cria diálogo de progresso"""
        self.window = tk.Toplevel(self.parent)
        self.window.title(self.title)
        self.window.geometry("400x150")
        self.window.resizable(False, False)
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Centralizar
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (150 // 2)
        self.window.geometry(f"400x150+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # Status
        self.status_var = tk.StringVar(value="Iniciando...")
        status_label = ttk.Label(main_frame, textvariable=self.status_var,
                                font=('Segoe UI', 10))
        status_label.pack(pady=(0, 10))
        
        # Barra de progresso
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(main_frame, 
                                     variable=self.progress_var,
                                     mode='determinate',
                                     length=350)
        progress_bar.pack(pady=10)
        
        # Botão cancelar (opcional)
        cancel_btn = ttk.Button(main_frame, text="Cancelar", 
                               command=self.cancel)
        cancel_btn.pack(pady=(10, 0))
    
    def update_progress(self, value: float, status: str = ""):
        """Atualiza progresso"""
        self.progress_var.set(value)
        if status:
            self.status_var.set(status)
        self.window.update()
    
    def cancel(self):
        """Cancela operação"""
        self.window.destroy()
    
    def close(self):
        """Fecha diálogo"""
        self.window.destroy()

class DataTable(ttk.Frame):
    """Tabela de dados com funcionalidades avançadas"""
    
    def __init__(self, parent, columns: List[str], **kwargs):
        super().__init__(parent, **kwargs)
        self.columns = columns
        self.data = []
        self.create_widgets()
    
    def create_widgets(self):
        """Cria widgets da tabela"""
        # Frame para treeview e scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill='both', expand=True)
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show='headings')
        
        # Configurar colunas
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
    
    def insert_data(self, data: List[List[Any]]):
        """Insere dados na tabela"""
        # Limpar dados existentes
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Inserir novos dados
        self.data = data
        for row in data:
            self.tree.insert('', 'end', values=row)
    
    def get_selected_data(self):
        """Retorna dados selecionados"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            return self.tree.item(item)['values']
        return None

class SearchBox(ttk.Frame):
    """Caixa de pesquisa avançada"""
    
    def __init__(self, parent, on_search: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_search = on_search
        self.create_widgets()
    
    def create_widgets(self):
        """Cria widgets da caixa de pesquisa"""
        # Entry de pesquisa
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self, textvariable=self.search_var,
                                     font=('Segoe UI', 10))
        self.search_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        # Botão de pesquisa
        search_btn = ttk.Button(self, text="🔍", command=self.perform_search,
                               width=3)
        search_btn.pack(side='right')
        
        # Bind Enter key
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
    
    def perform_search(self):
        """Executa pesquisa"""
        if self.on_search:
            self.on_search(self.search_var.get())
    
    def get_search_text(self):
        """Retorna texto de pesquisa"""
        return self.search_var.get()
    
    def clear_search(self):
        """Limpa pesquisa"""
        self.search_var.set("")
