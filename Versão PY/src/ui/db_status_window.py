# -*- coding: utf-8 -*-
"""
Janela de Status do Banco de Dados (SQLite) com monitoramento e manutenção básica.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from ..database.database_manager import DatabaseManager
from .modern_theme import theme
from .modern_components import ModernButton, KPICard, ModernCard, StatusBadge, ModernTooltip
from .icons import get_icon


class DbStatusWindow:
    """Janela para exibir status e métricas do banco de dados."""

    def __init__(self, parent, db_manager: DatabaseManager):
        self.parent = parent
        self.db_manager = db_manager
        self.window = tk.Toplevel(parent)
        self.window.title("Status do Banco de Dados")
        self.window.geometry("900x650")
        self.window.minsize(800, 600)
        self.window.configure(bg=theme.bg_root)
        self.window.transient(parent)

        self.refresh_interval_ms = 5000

        self._build_ui()
        self._schedule_refresh()

    def _build_ui(self):
        container = ttk.Frame(self.window)
        container.pack(fill='both', expand=True, padx=theme.spacing_lg, pady=theme.spacing_lg)
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        # Header
        header = ttk.Frame(container, style='Header.TFrame')
        header.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, theme.spacing_md))
        title = ttk.Label(header, text="Status do Banco de Dados", style='Title.TLabel')
        title.pack(side='left')
        
        self.status_badge = StatusBadge(header, text="Conectando...", status_type="info")
        self.status_badge.pack(side='right')

        # Metrics panel
        metrics_frame = ModernCard(container, title="Métricas")
        metrics_frame.grid(row=1, column=0, sticky='nsew', padx=(0, theme.spacing_md))
        metrics_frame.columnconfigure(0, weight=1)
        metrics_frame.columnconfigure(1, weight=1)

        self.metrics_vars = {
            'sqlite_version': tk.StringVar(value='-'),
            'database_path': tk.StringVar(value='-'),
            'file_size_human': tk.StringVar(value='-'),
            'last_modified': tk.StringVar(value='-'),
            'server_time': tk.StringVar(value='-'),
            'uptime_human': tk.StringVar(value='-'),
            'tables_count': tk.StringVar(value='0'),
            'indexes_count': tk.StringVar(value='0')
        }

        labels = [
            ("SQLite", 'sqlite_version'),
            ("Arquivo", 'database_path'),
            ("Tamanho", 'file_size_human'),
            ("Modificado", 'last_modified'),
            ("Hora do Servidor", 'server_time'),
            ("Uptime", 'uptime_human'),
            ("Tabelas", 'tables_count'),
            ("Índices", 'indexes_count'),
        ]
        for i, (label, key) in enumerate(labels):
            r = i // 2
            c = (i % 2) * 1
            frame = ttk.Frame(metrics_frame, style='Card.TFrame')
            frame.grid(row=r, column=c, sticky='ew', padx=theme.spacing_sm, pady=theme.spacing_sm)
            # KPI estilizado
            kpi = KPICard(frame, label_text=label, value=self.metrics_vars[key].get(), icon='info')
            # Vincular atualização: guardamos referência por chave
            setattr(self, f"kpi_{key}", kpi)
            kpi.pack(fill='x')

        # Performance panel
        perf_frame = ModernCard(container, title="Desempenho")
        perf_frame.grid(row=1, column=1, sticky='nsew')
        perf_frame.columnconfigure(0, weight=1)
        perf_frame.columnconfigure(1, weight=1)

        self.perf_vars = {
            'page_count': tk.StringVar(value='0'),
            'page_size': tk.StringVar(value='0'),
            'freelist_count': tk.StringVar(value='0'),
            'database_size_bytes': tk.StringVar(value='0'),
            'journal_mode': tk.StringVar(value='-'),
            'synchronous': tk.StringVar(value='-'),
            'cache_size': tk.StringVar(value='0'),
            'temp_store': tk.StringVar(value='-'),
        }

        perf_labels = [
            ("Páginas", 'page_count'),
            ("Tamanho da Página", 'page_size'),
            ("Freelist", 'freelist_count'),
            ("Tamanho (bytes)", 'database_size_bytes'),
            ("Journal", 'journal_mode'),
            ("Síncrono", 'synchronous'),
            ("Cache", 'cache_size'),
            ("Temp Store", 'temp_store'),
        ]
        for i, (label, key) in enumerate(perf_labels):
            r = i // 2
            c = (i % 2) * 1
            frame = ttk.Frame(perf_frame, style='Card.TFrame')
            frame.grid(row=r, column=c, sticky='ew', padx=theme.spacing_sm, pady=theme.spacing_sm)
            kpi = KPICard(frame, label_text=label, value=self.perf_vars[key].get(), icon='trending')
            setattr(self, f"kpi_perf_{key}", kpi)
            kpi.pack(fill='x')

        # Top tables panel
        tables_frame = ModernCard(container, title="Top Tabelas (por linhas)")
        tables_frame.grid(row=2, column=0, columnspan=2, sticky='nsew', pady=(theme.spacing_md, 0))
        tables_frame.columnconfigure(0, weight=1)

        self.tables_tree = ttk.Treeview(tables_frame, columns=("tabela", "linhas"), show='headings', height=6)
        self.tables_tree.heading("tabela", text="Tabela")
        self.tables_tree.heading("linhas", text="Linhas")
        self.tables_tree.column("tabela", width=300)
        self.tables_tree.column("linhas", width=120, anchor='e')
        self.tables_tree.pack(fill='both', expand=True, padx=theme.spacing_md, pady=theme.spacing_md)

        # Controls panel
        controls = ttk.Frame(container, style='Header.TFrame')
        controls.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(theme.spacing_md, 0))

        ModernButton(controls, text="Testar Conexão", style_type="primary", icon=get_icon("check"),
                     command=self._test_connection).pack(side='left', padx=(0, theme.spacing_sm))
        ModernButton(controls, text="Vacuum", style_type="secondary", icon=get_icon("database"),
                     command=lambda: self._run_maintenance('VACUUM')).pack(side='left', padx=(0, theme.spacing_sm))
        ModernButton(controls, text="Analyze", style_type="secondary", icon=get_icon("database"),
                     command=lambda: self._run_maintenance('ANALYZE')).pack(side='left', padx=(0, theme.spacing_sm))
        ModernButton(controls, text="Reindex", style_type="secondary", icon=get_icon("database"),
                     command=lambda: self._run_maintenance('REINDEX')).pack(side='left', padx=(0, theme.spacing_sm))
        ModernButton(controls, text="Limpar Cache", style_type="warning", icon=get_icon("refresh"),
                     command=self._clear_cache).pack(side='left', padx=(0, theme.spacing_sm))
        
        # Tooltips informativos
        ModernTooltip(controls, "Operações de manutenção do SQLite para otimização e estatísticas.")

    def _schedule_refresh(self):
        self._refresh()
        self.window.after(self.refresh_interval_ms, self._schedule_refresh)

    def _refresh(self):
        try:
            status = self.db_manager.get_server_status()
            metrics = self.db_manager.get_performance_metrics()
            top_tables = self.db_manager.get_top_tables_by_rows()

            # Atualiza badge de status
            connected = bool(status.get('connected'))
            self.status_badge.configure(text=(" Conectado " if connected else " Desconectado "))
            self.status_badge.configure(background=(theme.success_bg if connected else theme.error_bg),
                                        foreground=(theme.success_light if connected else theme.error_light))

            for k, var in self.metrics_vars.items():
                val = status.get(k)
                val_str = str(val) if val is not None else '-'
                var.set(val_str)
                # Atualiza KPIs visuais
                kpi = getattr(self, f"kpi_{k}", None)
                if kpi:
                    kpi.update_value(val_str)

            for k, var in self.perf_vars.items():
                val = metrics.get(k)
                val_str = str(val) if val is not None else '-'
                var.set(val_str)
                kpi = getattr(self, f"kpi_perf_{k}", None)
                if kpi:
                    kpi.update_value(val_str)

            # Atualizar tabela
            for item in self.tables_tree.get_children():
                self.tables_tree.delete(item)
            for row in top_tables:
                self.tables_tree.insert('', 'end', values=(row.get('name'), row.get('rows')))
        except Exception as e:
            # Não interromper o loop; exibir estado de erro leve
            self.status_label.configure(text=f"Erro: {e}")

    def _test_connection(self):
        try:
            ok = bool(self.db_manager.get_server_status().get('connected'))
            if ok:
                messagebox.showinfo("Conexão", "Conexão com o banco verificada com sucesso.")
            else:
                messagebox.showwarning("Conexão", "Banco desconectado ou indisponível.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao testar conexão: {e}")

    def _run_maintenance(self, action: str):
        try:
            ok = self.db_manager.run_maintenance(action)
            if ok:
                messagebox.showinfo("Manutenção", f"Operação {action} executada com sucesso.")
                self._refresh()
            else:
                messagebox.showwarning("Manutenção", f"Operação {action} não executada.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na manutenção: {e}")

    def _clear_cache(self):
        try:
            self.db_manager.clear_cache()
            messagebox.showinfo("Cache", "Cache de estatísticas limpo.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao limpar cache: {e}")