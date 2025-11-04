# -*- coding: utf-8 -*-
"""
Janela de administração do sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..utils.logger import get_logger
from ..utils.backup import get_backup_manager
from ..utils.monitoring import get_monitoring_service
from ..utils.settings import get_settings_manager

class AdminWindow:
    """Janela de administração do sistema"""
    
    def __init__(self, parent=None):
        """
        Inicializa a janela de administração
        
        Args:
            parent: Janela pai
        """
        self.logger = get_logger(__name__)
        self.parent = parent
        
        # Gerenciadores
        self.backup_manager = get_backup_manager()
        self.monitoring_service = get_monitoring_service()
        self.settings_manager = get_settings_manager()
        
        # Janela
        self.window = None
        self.notebook = None
        
        # Variáveis de controle
        self.monitoring_enabled = tk.BooleanVar()
        self.auto_backup_enabled = tk.BooleanVar()
        
        # Widgets de backup
        self.backup_tree = None
        self.backup_progress = None
        
        # Widgets de monitoramento
        self.metrics_text = None
        self.alerts_tree = None
        
        # Thread de atualização
        self._update_thread = None
        self._updating = False
    
    def show(self) -> None:
        """
        Exibe a janela de administração
        """
        try:
            if self.window and self.window.winfo_exists():
                self.window.lift()
                self.window.focus_force()
                return
            
            self._create_window()
            self._setup_ui()
            self._load_initial_data()
            self._start_updates()
            
        except Exception as e:
            self.logger.error(f"Erro ao exibir janela de administração: {e}")
            messagebox.showerror("Erro", f"Erro ao abrir janela de administração: {e}")
    
    def _create_window(self) -> None:
        """
        Cria a janela principal
        """
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Administração do Sistema DAC")
        self.window.geometry("900x700")
        self.window.minsize(800, 600)
        
        # Centralizar janela
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Protocolo de fechamento
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_ui(self) -> None:
        """
        Configura a interface do usuário
        """
        # Notebook principal
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Abas
        self._create_backup_tab()
        self._create_monitoring_tab()
        self._create_settings_tab()
        self._create_logs_tab()
    
    def _create_backup_tab(self) -> None:
        """
        Cria a aba de backup
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Backup")
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(frame, text="Controles de Backup")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Botões de backup
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Criar Backup", 
                  command=self._create_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Restaurar Backup", 
                  command=self._restore_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Excluir Backup", 
                  command=self._delete_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Atualizar Lista", 
                  command=self._refresh_backups).pack(side=tk.LEFT, padx=5)
        
        # Configurações de backup
        config_frame = ttk.Frame(controls_frame)
        config_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.auto_backup_enabled.set(self.backup_manager.auto_backup)
        ttk.Checkbutton(config_frame, text="Backup Automático", 
                       variable=self.auto_backup_enabled,
                       command=self._toggle_auto_backup).pack(side=tk.LEFT, padx=5)
        
        # Lista de backups
        list_frame = ttk.LabelFrame(frame, text="Backups Disponíveis")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview para backups
        columns = ('Nome', 'Data', 'Tamanho', 'Tipo')
        self.backup_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.backup_tree.heading(col, text=col)
            self.backup_tree.column(col, width=150)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.backup_tree.yview)
        h_scroll = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.backup_tree.xview)
        self.backup_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Pack treeview e scrollbars
        self.backup_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Barra de progresso
        self.backup_progress = ttk.Progressbar(frame, mode='indeterminate')
        self.backup_progress.pack(fill=tk.X, padx=5, pady=5)
    
    def _create_monitoring_tab(self) -> None:
        """
        Cria a aba de monitoramento
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Monitoramento")
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(frame, text="Controles de Monitoramento")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Botões de controle
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Iniciar Monitoramento", 
                  command=self._start_monitoring).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Parar Monitoramento", 
                  command=self._stop_monitoring).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Exportar Métricas", 
                  command=self._export_metrics).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Atualizar", 
                  command=self._refresh_monitoring).pack(side=tk.LEFT, padx=5)
        
        # Notebook para métricas
        metrics_notebook = ttk.Notebook(frame)
        metrics_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba de métricas do sistema
        system_frame = ttk.Frame(metrics_notebook)
        metrics_notebook.add(system_frame, text="Sistema")
        
        self.metrics_text = tk.Text(system_frame, wrap=tk.WORD, font=('Consolas', 10))
        metrics_scroll = ttk.Scrollbar(system_frame, orient=tk.VERTICAL, command=self.metrics_text.yview)
        self.metrics_text.configure(yscrollcommand=metrics_scroll.set)
        
        self.metrics_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        metrics_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Aba de alertas
        alerts_frame = ttk.Frame(metrics_notebook)
        metrics_notebook.add(alerts_frame, text="Alertas")
        
        # Treeview para alertas
        alert_columns = ('Timestamp', 'Nível', 'Mensagem')
        self.alerts_tree = ttk.Treeview(alerts_frame, columns=alert_columns, show='headings')
        
        for col in alert_columns:
            self.alerts_tree.heading(col, text=col)
            self.alerts_tree.column(col, width=200)
        
        alerts_scroll = ttk.Scrollbar(alerts_frame, orient=tk.VERTICAL, command=self.alerts_tree.yview)
        self.alerts_tree.configure(yscrollcommand=alerts_scroll.set)
        
        self.alerts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        alerts_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_settings_tab(self) -> None:
        """
        Cria a aba de configurações
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Configurações")
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(frame, text="Gerenciamento de Configurações")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Exportar Configurações", 
                  command=self._export_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Importar Configurações", 
                  command=self._import_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Resetar Padrões", 
                  command=self._reset_settings).pack(side=tk.LEFT, padx=5)
        
        # Configurações principais
        main_frame = ttk.LabelFrame(frame, text="Configurações Principais")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Criar campos de configuração
        self._create_setting_fields(main_frame)
    
    def _create_setting_fields(self, parent) -> None:
        """
        Cria campos de configuração
        
        Args:
            parent: Widget pai
        """
        # Canvas e scrollbar para configurações
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configurações de interface
        ui_frame = ttk.LabelFrame(scrollable_frame, text="Interface")
        ui_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Theme
        ttk.Label(ui_frame, text="Tema:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        theme_var = tk.StringVar(value=self.settings_manager.get('ui.theme', 'default'))
        theme_combo = ttk.Combobox(ui_frame, textvariable=theme_var, 
                                  values=['default', 'dark', 'light'])
        theme_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        
        # Configurações de dados
        data_frame = ttk.LabelFrame(scrollable_frame, text="Dados")
        data_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Max backups
        ttk.Label(data_frame, text="Máximo de Backups:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        max_backups_var = tk.IntVar(value=self.settings_manager.get('data.max_backups', 5))
        max_backups_spin = ttk.Spinbox(data_frame, from_=1, to=20, textvariable=max_backups_var)
        max_backups_spin.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        
        # Configurar grid
        ui_frame.columnconfigure(1, weight=1)
        data_frame.columnconfigure(1, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_logs_tab(self) -> None:
        """
        Cria a aba de logs
        """
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Logs")
        
        # Frame de controles
        controls_frame = ttk.LabelFrame(frame, text="Controles de Log")
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="Atualizar Logs", 
                  command=self._refresh_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Limpar Logs", 
                  command=self._clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Exportar Logs", 
                  command=self._export_logs).pack(side=tk.LEFT, padx=5)
        
        # Área de logs
        self.logs_text = tk.Text(frame, wrap=tk.WORD, font=('Consolas', 9))
        logs_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.logs_text.yview)
        self.logs_text.configure(yscrollcommand=logs_scroll.set)
        
        self.logs_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        logs_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def _load_initial_data(self) -> None:
        """
        Carrega dados iniciais
        """
        try:
            self._refresh_backups()
            self._refresh_monitoring()
            self._refresh_logs()
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados iniciais: {e}")
    
    def _start_updates(self) -> None:
        """
        Inicia atualizações automáticas
        """
        self._updating = True
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()
    
    def _update_loop(self) -> None:
        """
        Loop de atualização automática
        """
        import time
        
        while self._updating:
            try:
                if self.window and self.window.winfo_exists():
                    self.window.after(0, self._refresh_monitoring)
                    time.sleep(10)  # Atualizar a cada 10 segundos
                else:
                    break
            except Exception as e:
                self.logger.error(f"Erro no loop de atualização: {e}")
                time.sleep(10)
    
    def _create_backup(self) -> None:
        """
        Cria um novo backup
        """
        try:
            self.backup_progress.start()
            
            def backup_thread():
                try:
                    backup_path = self.backup_manager.create_backup()
                    if backup_path:
                        self.window.after(0, lambda: messagebox.showinfo(
                            "Sucesso", f"Backup criado com sucesso:\n{backup_path}"))
                        self.window.after(0, self._refresh_backups)
                    else:
                        self.window.after(0, lambda: messagebox.showerror(
                            "Erro", "Falha ao criar backup"))
                except Exception as e:
                    self.window.after(0, lambda: messagebox.showerror(
                        "Erro", f"Erro ao criar backup: {e}"))
                finally:
                    self.window.after(0, self.backup_progress.stop)
            
            threading.Thread(target=backup_thread, daemon=True).start()
            
        except Exception as e:
            self.backup_progress.stop()
            messagebox.showerror("Erro", f"Erro ao iniciar backup: {e}")
    
    def _restore_backup(self) -> None:
        """
        Restaura um backup selecionado
        """
        try:
            selection = self.backup_tree.selection()
            if not selection:
                messagebox.showwarning("Aviso", "Selecione um backup para restaurar")
                return
            
            item = self.backup_tree.item(selection[0])
            backup_name = item['values'][0]
            
            # Confirmar restauração
            if not messagebox.askyesno("Confirmar", 
                                     f"Deseja restaurar o backup '{backup_name}'?\n\n"
                                     "ATENÇÃO: Esta operação substituirá os dados atuais!"):
                return
            
            # Encontrar caminho do backup
            backups = self.backup_manager.list_backups()
            backup_path = None
            for backup in backups:
                if backup['name'] == backup_name:
                    backup_path = backup['path']
                    break
            
            if not backup_path:
                messagebox.showerror("Erro", "Backup não encontrado")
                return
            
            self.backup_progress.start()
            
            def restore_thread():
                try:
                    success = self.backup_manager.restore_backup(backup_path)
                    if success:
                        self.window.after(0, lambda: messagebox.showinfo(
                            "Sucesso", "Backup restaurado com sucesso"))
                    else:
                        self.window.after(0, lambda: messagebox.showerror(
                            "Erro", "Falha ao restaurar backup"))
                except Exception as e:
                    self.window.after(0, lambda: messagebox.showerror(
                        "Erro", f"Erro ao restaurar backup: {e}"))
                finally:
                    self.window.after(0, self.backup_progress.stop)
            
            threading.Thread(target=restore_thread, daemon=True).start()
            
        except Exception as e:
            self.backup_progress.stop()
            messagebox.showerror("Erro", f"Erro ao restaurar backup: {e}")
    
    def _delete_backup(self) -> None:
        """
        Exclui um backup selecionado
        """
        try:
            selection = self.backup_tree.selection()
            if not selection:
                messagebox.showwarning("Aviso", "Selecione um backup para excluir")
                return
            
            item = self.backup_tree.item(selection[0])
            backup_name = item['values'][0]
            
            # Confirmar exclusão
            if not messagebox.askyesno("Confirmar", 
                                     f"Deseja excluir o backup '{backup_name}'?"):
                return
            
            # Encontrar caminho do backup
            backups = self.backup_manager.list_backups()
            backup_path = None
            for backup in backups:
                if backup['name'] == backup_name:
                    backup_path = backup['path']
                    break
            
            if backup_path and self.backup_manager.delete_backup(backup_path):
                messagebox.showinfo("Sucesso", "Backup excluído com sucesso")
                self._refresh_backups()
            else:
                messagebox.showerror("Erro", "Falha ao excluir backup")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir backup: {e}")
    
    def _refresh_backups(self) -> None:
        """
        Atualiza a lista de backups
        """
        try:
            # Limpar lista atual
            for item in self.backup_tree.get_children():
                self.backup_tree.delete(item)
            
            # Carregar backups
            backups = self.backup_manager.list_backups()
            
            for backup in backups:
                # Formatar dados
                name = backup.get('name', 'Unknown')
                timestamp = backup.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_date = dt.strftime('%d/%m/%Y %H:%M')
                    except:
                        formatted_date = timestamp
                else:
                    formatted_date = 'Unknown'
                
                size = backup.get('file_size', 0)
                size_str = self._format_file_size(size)
                
                backup_type = backup.get('type', 'unknown')
                
                # Inserir na lista
                self.backup_tree.insert('', tk.END, values=(name, formatted_date, size_str, backup_type))
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar lista de backups: {e}")
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        Formata tamanho de arquivo
        
        Args:
            size_bytes (int): Tamanho em bytes
            
        Returns:
            str: Tamanho formatado
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def _toggle_auto_backup(self) -> None:
        """
        Alterna backup automático
        """
        try:
            self.backup_manager.auto_backup = self.auto_backup_enabled.get()
            self.settings_manager.set('data.auto_backup', self.backup_manager.auto_backup)
            self.settings_manager.save()
        except Exception as e:
            self.logger.error(f"Erro ao alterar configuração de backup automático: {e}")
    
    def _start_monitoring(self) -> None:
        """
        Inicia o monitoramento
        """
        try:
            self.monitoring_service.start()
            messagebox.showinfo("Sucesso", "Monitoramento iniciado")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar monitoramento: {e}")
    
    def _stop_monitoring(self) -> None:
        """
        Para o monitoramento
        """
        try:
            self.monitoring_service.stop()
            messagebox.showinfo("Sucesso", "Monitoramento parado")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao parar monitoramento: {e}")
    
    def _refresh_monitoring(self) -> None:
        """
        Atualiza dados de monitoramento
        """
        try:
            # Atualizar métricas
            dashboard_data = self.monitoring_service.get_dashboard_data()
            
            # Formatar métricas para exibição
            metrics_text = self._format_metrics(dashboard_data)
            
            if self.metrics_text:
                self.metrics_text.delete(1.0, tk.END)
                self.metrics_text.insert(1.0, metrics_text)
            
            # Atualizar alertas
            if self.alerts_tree:
                # Limpar alertas atuais
                for item in self.alerts_tree.get_children():
                    self.alerts_tree.delete(item)
                
                # Adicionar alertas recentes
                alerts = dashboard_data.get('recent_alerts', [])
                for alert in alerts:
                    timestamp = alert.get('timestamp', '')
                    if timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            formatted_time = dt.strftime('%d/%m/%Y %H:%M:%S')
                        except:
                            formatted_time = timestamp
                    else:
                        formatted_time = 'Unknown'
                    
                    level = alert.get('level', 'info')
                    message = alert.get('message', '')
                    
                    self.alerts_tree.insert('', tk.END, values=(formatted_time, level, message))
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar monitoramento: {e}")
    
    def _format_metrics(self, data: Dict) -> str:
        """
        Formata métricas para exibição
        
        Args:
            data (dict): Dados do dashboard
            
        Returns:
            str: Métricas formatadas
        """
        try:
            lines = []
            lines.append("=== MÉTRICAS DO SISTEMA ===")
            lines.append("")
            
            # Métricas do sistema
            system_metrics = data.get('system_metrics', {})
            if system_metrics:
                lines.append("Sistema:")
                
                cpu = system_metrics.get('cpu', {})
                lines.append(f"  CPU: {cpu.get('current', 0):.1f}% (avg: {cpu.get('average', 0):.1f}%, max: {cpu.get('max', 0):.1f}%)")
                
                memory = system_metrics.get('memory', {})
                lines.append(f"  Memória: {memory.get('current', 0):.1f}% (avg: {memory.get('average', 0):.1f}%, max: {memory.get('max', 0):.1f}%)")
                
                disk = system_metrics.get('disk', {})
                lines.append(f"  Disco: {disk.get('current', 0):.1f}% (avg: {disk.get('average', 0):.1f}%, max: {disk.get('max', 0):.1f}%)")
                
                lines.append("")
            
            # Métricas de performance
            perf_metrics = data.get('performance_metrics', {})
            if perf_metrics:
                lines.append("Performance:")
                
                queries = perf_metrics.get('queries', {})
                lines.append(f"  Consultas: {queries.get('count', 0)} (avg: {queries.get('average', 0):.3f}s, max: {queries.get('max', 0):.3f}s)")
                
                imports = perf_metrics.get('imports', {})
                lines.append(f"  Importações: {imports.get('count', 0)} (avg: {imports.get('average', 0):.3f}s, max: {imports.get('max', 0):.3f}s)")
                
                exports = perf_metrics.get('exports', {})
                lines.append(f"  Exportações: {exports.get('count', 0)} (avg: {exports.get('average', 0):.3f}s, max: {exports.get('max', 0):.3f}s)")
                
                lines.append("")
            
            # Status de saúde
            health = data.get('health_status', {})
            if health:
                lines.append(f"Status: {health.get('status', 'unknown').upper()}")
                
                warnings = health.get('warnings', [])
                if warnings:
                    lines.append("Avisos:")
                    for warning in warnings:
                        lines.append(f"  - {warning}")
                
                errors = health.get('errors', [])
                if errors:
                    lines.append("Erros:")
                    for error in errors:
                        lines.append(f"  - {error}")
                
                uptime = health.get('uptime', 'unknown')
                lines.append(f"Uptime: {uptime}")
            
            return "\n".join(lines)
            
        except Exception as e:
            return f"Erro ao formatar métricas: {e}"
    
    def _export_metrics(self) -> None:
        """
        Exporta métricas para arquivo
        """
        try:
            file_path = filedialog.asksaveasfilename(
                title="Exportar Métricas",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                monitor = self.monitoring_service.performance_monitor
                if monitor.export_metrics(file_path):
                    messagebox.showinfo("Sucesso", f"Métricas exportadas para: {file_path}")
                else:
                    messagebox.showerror("Erro", "Falha ao exportar métricas")
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar métricas: {e}")
    
    def _export_settings(self) -> None:
        """
        Exporta configurações
        """
        try:
            file_path = filedialog.asksaveasfilename(
                title="Exportar Configurações",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                if self.settings_manager.export_settings(file_path):
                    messagebox.showinfo("Sucesso", f"Configurações exportadas para: {file_path}")
                else:
                    messagebox.showerror("Erro", "Falha ao exportar configurações")
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar configurações: {e}")
    
    def _import_settings(self) -> None:
        """
        Importa configurações
        """
        try:
            file_path = filedialog.askopenfilename(
                title="Importar Configurações",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                if self.settings_manager.import_settings(file_path):
                    messagebox.showinfo("Sucesso", "Configurações importadas com sucesso")
                else:
                    messagebox.showerror("Erro", "Falha ao importar configurações")
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar configurações: {e}")
    
    def _reset_settings(self) -> None:
        """
        Reseta configurações para padrão
        """
        try:
            if messagebox.askyesno("Confirmar", "Deseja resetar todas as configurações para os valores padrão?"):
                self.settings_manager.reset_to_defaults()
                messagebox.showinfo("Sucesso", "Configurações resetadas para padrão")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao resetar configurações: {e}")
    
    def _refresh_logs(self) -> None:
        """
        Atualiza logs
        """
        try:
            # Ler logs recentes
            logs_dir = Path(__file__).parent.parent.parent / "logs"
            log_file = logs_dir / "dac.log"
            
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    # Ler últimas 1000 linhas
                    lines = f.readlines()
                    recent_lines = lines[-1000:] if len(lines) > 1000 else lines
                    
                    if hasattr(self, 'logs_text') and self.logs_text:
                        self.logs_text.delete(1.0, tk.END)
                        self.logs_text.insert(1.0, ''.join(recent_lines))
                        self.logs_text.see(tk.END)
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar logs: {e}")
    
    def _clear_logs(self) -> None:
        """
        Limpa logs
        """
        try:
            if messagebox.askyesno("Confirmar", "Deseja limpar todos os logs?"):
                logs_dir = Path(__file__).parent.parent.parent / "logs"
                log_file = logs_dir / "dac.log"
                
                if log_file.exists():
                    log_file.unlink()
                    messagebox.showinfo("Sucesso", "Logs limpos com sucesso")
                    self._refresh_logs()
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao limpar logs: {e}")
    
    def _export_logs(self) -> None:
        """
        Exporta logs
        """
        try:
            file_path = filedialog.asksaveasfilename(
                title="Exportar Logs",
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                logs_dir = Path(__file__).parent.parent.parent / "logs"
                log_file = logs_dir / "dac.log"
                
                if log_file.exists():
                    import shutil
                    shutil.copy2(log_file, file_path)
                    messagebox.showinfo("Sucesso", f"Logs exportados para: {file_path}")
                else:
                    messagebox.showwarning("Aviso", "Nenhum log encontrado")
                    
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar logs: {e}")
    
    def _on_closing(self) -> None:
        """
        Manipula o fechamento da janela
        """
        try:
            self._updating = False
            if self._update_thread:
                self._update_thread.join(timeout=1)
            
            if self.window:
                self.window.destroy()
                
        except Exception as e:
            self.logger.error(f"Erro ao fechar janela de administração: {e}")