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

        # Janela redimensionável para melhor visibilidade
        screen_w = self.parent.winfo_screenwidth()
        screen_h = self.parent.winfo_screenheight()
        # Tamanho inicial adaptado à tela
        init_w = min(max(int(screen_w * 0.7), 900), 1400)
        init_h = min(max(int(screen_h * 0.7), 580), 900)
        self.window.geometry(f"{init_w}x{init_h}")
        try:
            self.window.minsize(900, 580)
        except Exception:
            pass
        self.window.resizable(True, True)

        self.window.configure(bg=theme.bg_root)
        self.window.transient(parent)

        self.refresh_interval_ms = 5000

        # Estado de layout atual (wide/stacked)
        self._layout_mode = None

        self._build_ui()
        self._schedule_refresh()

    def _build_ui(self):
        # Frame principal
        self.container = ttk.Frame(self.window, style='Card.TFrame')
        self.container.pack(fill='both', expand=True, padx=15, pady=15)

        # Largura mínima das colunas para evitar cortes
        self.container.columnconfigure(0, weight=1, minsize=420)
        self.container.columnconfigure(1, weight=1, minsize=420)

        # Header
        header = ttk.Frame(self.container, style='Header.TFrame')
        header.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 12))
        title = ttk.Label(header, text="⚡ Status do Banco de Dados", style='Title.TLabel',
                         font=('Segoe UI', 14, 'bold'))
        title.pack(side='left')
        
        self.status_badge = StatusBadge(header, text="Conectando...", status_type="info")
        self.status_badge.pack(side='right', padx=10)

        # Metrics panel
        self.metrics_frame = ModernCard(self.container, title="📊 Métricas")
        self.metrics_frame.content.columnconfigure(0, weight=1, minsize=380)
        self.metrics_frame.content.columnconfigure(1, weight=1, minsize=380)

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
            frame = ttk.Frame(self.metrics_frame.content, style='Card.TFrame')
            frame.grid(row=r, column=c, sticky='ew', padx=theme.spacing_sm, pady=theme.spacing_sm)
            # KPI estilizado
            kpi = KPICard(frame, label_text=label, value=self.metrics_vars[key].get(), icon='info')
            # Vincular atualização: guardamos referência por chave
            setattr(self, f"kpi_{key}", kpi)
            kpi.pack(fill='x')

            # Ajustes específicos
            if key == 'database_path':
                # Caminho longo: wrap + fonte
                try:
                    kpi.value_label.configure(wraplength=440, anchor='w', font=('Segoe UI', 10))
                except Exception:
                    pass
                # Tooltip com caminho completo
                ModernTooltip(kpi.value_label, "Caminho completo do arquivo do banco")
                # Botão copiar
                copy_btn = ModernButton(frame, text="📋 Copiar", style_type="secondary", icon=get_icon("copy"),
                                        command=self._copy_db_path)
                copy_btn.pack(anchor='w', pady=(5, 0))
            elif key == 'last_modified':
                # Datas: fonte monoespaçada para legibilidade
                try:
                    kpi.value_label.configure(wraplength=300, anchor='w', font=(theme.font_family_mono[0], 11))
                except Exception:
                    pass
            else:
                # Garantir expansão sem cortes
                try:
                    kpi.value_label.configure(wraplength=300, anchor='w')
                except Exception:
                    pass

        # Performance panel
        self.perf_frame = ModernCard(self.container, title="⚡ Desempenho")
        self.perf_frame.content.columnconfigure(0, weight=1, minsize=380)
        self.perf_frame.content.columnconfigure(1, weight=1, minsize=380)

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
            frame = ttk.Frame(self.perf_frame.content, style='Card.TFrame')
            frame.grid(row=r, column=c, sticky='ew', padx=theme.spacing_sm, pady=theme.spacing_sm)
            kpi = KPICard(frame, label_text=label, value=self.perf_vars[key].get(), icon='trending')
            setattr(self, f"kpi_perf_{key}", kpi)
            kpi.pack(fill='x')

        # Top tables panel
        self.tables_frame = ModernCard(self.container, title="📋 Top Tabelas")
        self.tables_frame.content.columnconfigure(0, weight=1)

        self.tables_tree = ttk.Treeview(self.tables_frame.content, columns=("tabela", "linhas"), show='headings', height=5)
        self.tables_tree.heading("tabela", text="📊 Tabela")
        self.tables_tree.heading("linhas", text="🔢 Registros")
        self.tables_tree.column("tabela", width=520, stretch=True)
        self.tables_tree.column("linhas", width=160, anchor='e', stretch=True)
        self.tables_tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Controls panel
        self.controls = ttk.Frame(self.container, style='Header.TFrame')

        ModernButton(self.controls, text="🔍 Testar", style_type="primary", icon=get_icon("check"),
                     command=self._test_connection).pack(side='left', padx=(0, 8))
        ModernButton(self.controls, text="🗜️ Vacuum", style_type="secondary", icon=get_icon("database"),
                     command=lambda: self._run_maintenance('VACUUM')).pack(side='left', padx=(0, 8))
        ModernButton(self.controls, text="📈 Analyze", style_type="secondary", icon=get_icon("database"),
                     command=lambda: self._run_maintenance('ANALYZE')).pack(side='left', padx=(0, 8))
        ModernButton(self.controls, text="🔄 Reindex", style_type="secondary", icon=get_icon("database"),
                     command=lambda: self._run_maintenance('REINDEX')).pack(side='left', padx=(0, theme.spacing_sm))
        ModernButton(self.controls, text="Limpar Cache", style_type="warning", icon=get_icon("refresh"),
                     command=self._clear_cache).pack(side='left', padx=(0, theme.spacing_sm))
        
        # Tooltips
        ModernTooltip(self.controls, "Operações de manutenção do SQLite para otimização e estatísticas.")

        # Layout inicial (usando largura da janela)
        self._apply_layout(stacked=False)

        # Ajuste responsivo no resize da janela
        try:
            self.window.bind('<Configure>', self._on_resize)
        except Exception:
            pass

    def _apply_layout(self, stacked: bool):
        """Aplica layout lado-a-lado (wide) ou empilhado (stacked)."""
        if self._layout_mode == ('stacked' if stacked else 'wide'):
            return
        self._layout_mode = 'stacked' if stacked else 'wide'

        # Limpa grids atuais
        for w in [self.metrics_frame, self.perf_frame, self.tables_frame, self.controls]:
            try:
                w.grid_forget()
            except Exception:
                pass

        if stacked:
            # Painéis empilhados para telas estreitas
            self.metrics_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=(0, 0), pady=(0, 10))
            self.perf_frame.grid(row=2, column=0, columnspan=2, sticky='nsew', padx=(0, 0), pady=(0, 10))
            self.tables_frame.grid(row=3, column=0, columnspan=2, sticky='nsew', pady=(10, 10))
            self.controls.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        else:
            # Lado a lado para telas largas
            self.metrics_frame.grid(row=1, column=0, sticky='nsew', padx=(0, 10), pady=(0, 10))
            self.perf_frame.grid(row=1, column=1, sticky='nsew', pady=(0, 10))
            self.tables_frame.grid(row=2, column=0, columnspan=2, sticky='nsew', pady=(10, 10))
            self.controls.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(10, 0))

        # Reconfigura colunas do container (mínimos já definidos)
        self.container.columnconfigure(0, weight=1)
        self.container.columnconfigure(1, weight=1)

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
                    if k == 'last_modified':
                        try:
                            kpi.value_label.configure(text=val_str)
                        except Exception:
                            pass

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
            # Não interromper o loop; exibir estado de erro leve no badge
            try:
                self.status_badge.configure(text=f" Erro: {e}")
                self.status_badge.configure(background=theme.error_bg, foreground=theme.error_light)
            except Exception:
                pass

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

    def _copy_db_path(self):
        """Copia o caminho do banco para a área de transferência."""
        try:
            path_val = self.metrics_vars.get('database_path').get()
            if path_val and path_val != '-':
                self.window.clipboard_clear()
                self.window.clipboard_append(path_val)
                messagebox.showinfo("Copiado", "Caminho do banco copiado para a área de transferência.")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível copiar o caminho: {e}")

    def _on_resize(self, event):
        """Ajusta layout e wraplength conforme largura disponível."""
        try:
            width = event.width
            height = event.height
            # Muda layout quando a janela fica estreita
            stacked = width < 1100
            self._apply_layout(stacked=stacked)

            # Largura útil por coluna
            if stacked:
                col_width = max(width - 160, 360)
            else:
                col_width = max(int(width / 2) - 140, 320)

            # Campo longo: caminho
            if hasattr(self, 'kpi_database_path'):
                try:
                    self.kpi_database_path.value_label.configure(wraplength=col_width)
                except Exception:
                    pass
            # Campos gerais
            keys = ['sqlite_version','file_size_human','last_modified','server_time','uptime_human','tables_count','indexes_count']
            for k in keys:
                kpi = getattr(self, f"kpi_{k}", None)
                if kpi:
                    try:
                        kpi.value_label.configure(wraplength=max(col_width - 80, 260))
                    except Exception:
                        pass

            # Ajustar largura das colunas da tabela conforme layout
            try:
                total = max(width - 80, 600)
                self.tables_tree.column("tabela", width=int(total * 0.75))
                self.tables_tree.column("linhas", width=int(total * 0.20))
            except Exception:
                pass
        except Exception:
            pass