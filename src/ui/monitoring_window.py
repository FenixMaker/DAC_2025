
# -*- coding: utf-8 -*-
"""
Janela de monitoramento do sistema DAC
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

from ..utils.logger import get_logger
from ..utils.memory_optimizer import get_memory_optimizer
from ..utils.intelligent_cache import get_cache_stats

class MonitoringWindow:
    """Janela de monitoramento do sistema"""
    
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager
        self.logger = get_logger(__name__)
        self.memory_optimizer = get_memory_optimizer()
        
        # Dados de monitoramento
        self.monitoring_data = {
            'timestamps': [],
            'memory_usage': [],
            'cache_hit_rate': [],
            'query_times': []
        }
        
        # Criar janela
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Monitoramento do Sistema - DAC")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        
        # Configurar protocolo de fechamento
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Criar widgets
        self.create_widgets()
        
        # Iniciar monitoramento
        self.monitoring_active = True
        self.start_monitoring()
    
    def create_widgets(self):
        """Cria widgets da interface de monitoramento"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="15")
        main_frame.pack(fill='both', expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="📊 Monitoramento do Sistema",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Notebook para diferentes tipos de monitoramento
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Aba de performance
        self.create_performance_tab()
        
        # Aba de cache
        self.create_cache_tab()
        
        # Aba de banco de dados
        self.create_database_tab()
    
    def create_performance_tab(self):
        """Cria aba de monitoramento de performance"""
        perf_frame = ttk.Frame(self.notebook)
        self.notebook.add(perf_frame, text="⚡ Performance")
        
        # Gráfico de uso de memória
        self.memory_fig = Figure(figsize=(10, 4), dpi=100)
        self.memory_ax = self.memory_fig.add_subplot(111)
        self.memory_canvas = FigureCanvasTkAgg(self.memory_fig, perf_frame)
        self.memory_canvas.get_tk_widget().pack(fill='both', expand=True, pady=10)
        
        # Informações em tempo real
        info_frame = ttk.LabelFrame(perf_frame, text="Informações em Tempo Real", padding=10)
        info_frame.pack(fill='x', pady=10)
        
        self.memory_label = ttk.Label(info_frame, text="Memória: --")
        self.memory_label.pack(anchor='w')
        
        self.cpu_label = ttk.Label(info_frame, text="CPU: --")
        self.cpu_label.pack(anchor='w')
    
    def create_cache_tab(self):
        """Cria aba de monitoramento de cache"""
        cache_frame = ttk.Frame(self.notebook)
        self.notebook.add(cache_frame, text="🗄️ Cache")
        
        # Gráfico de hit rate do cache
        self.cache_fig = Figure(figsize=(10, 4), dpi=100)
        self.cache_ax = self.cache_fig.add_subplot(111)
        self.cache_canvas = FigureCanvasTkAgg(self.cache_fig, cache_frame)
        self.cache_canvas.get_tk_widget().pack(fill='both', expand=True, pady=10)
        
        # Estatísticas do cache
        stats_frame = ttk.LabelFrame(cache_frame, text="Estatísticas do Cache", padding=10)
        stats_frame.pack(fill='x', pady=10)
        
        self.cache_stats_text = tk.Text(stats_frame, height=6, font=('Consolas', 10))
        self.cache_stats_text.pack(fill='both', expand=True)
    
    def create_database_tab(self):
        """Cria aba de monitoramento do banco de dados"""
        db_frame = ttk.Frame(self.notebook)
        self.notebook.add(db_frame, text="🗃️ Banco de Dados")
        
        # Informações do banco
        db_info_frame = ttk.LabelFrame(db_frame, text="Informações do Banco", padding=10)
        db_info_frame.pack(fill='both', expand=True, pady=10)
        
        self.db_info_text = tk.Text(db_info_frame, font=('Consolas', 10))
        self.db_info_text.pack(fill='both', expand=True)
    
    def start_monitoring(self):
        """Inicia thread de monitoramento"""
        def monitor():
            while self.monitoring_active:
                try:
                    self.collect_metrics()
                    self.update_charts()
                    time.sleep(2)  # Atualizar a cada 2 segundos
                except Exception as e:
                    self.logger.error(f"Erro no monitoramento: {e}")
                    time.sleep(5)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def collect_metrics(self):
        """Coleta métricas do sistema"""
        try:
            # Timestamp atual
            now = datetime.now()
            
            # Informações de memória
            memory_info = self.memory_optimizer.get_memory_usage()
            
            # Estatísticas do cache
            cache_stats = get_cache_stats()
            
            # Adicionar aos dados de monitoramento
            self.monitoring_data['timestamps'].append(now)
            self.monitoring_data['memory_usage'].append(memory_info['rss_mb'])
            self.monitoring_data['cache_hit_rate'].append(cache_stats['hit_rate'])
            
            # Manter apenas os últimos 100 pontos
            for key in self.monitoring_data:
                if len(self.monitoring_data[key]) > 100:
                    self.monitoring_data[key] = self.monitoring_data[key][-100:]
            
            # Atualizar labels em tempo real
            self.window.after(0, self.update_real_time_info, memory_info, cache_stats)
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas: {e}")
    
    def update_real_time_info(self, memory_info, cache_stats):
        """Atualiza informações em tempo real na UI"""
        try:
            self.memory_label.config(text=f"Memória: {memory_info['rss_mb']:.1f}MB ({memory_info['percent']:.1f}%)")
            self.cpu_label.config(text=f"Cache Hit Rate: {cache_stats['hit_rate']:.1f}%")
            
            # Atualizar estatísticas do cache
            cache_text = f"""
Estatísticas do Cache:
  Tamanho: {cache_stats['size']}
  Hits: {cache_stats['hits']}
  Misses: {cache_stats['misses']}
  Taxa de Acerto: {cache_stats['hit_rate']:.2f}%
  Total de Requisições: {cache_stats['total_requests']}
"""
            
            self.cache_stats_text.delete(1.0, tk.END)
            self.cache_stats_text.insert(1.0, cache_text)
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar informações: {e}")
    
    def update_charts(self):
        """Atualiza gráficos de monitoramento"""
        try:
            if len(self.monitoring_data['timestamps']) < 2:
                return
            
            # Atualizar gráfico de memória
            self.memory_ax.clear()
            self.memory_ax.plot(self.monitoring_data['timestamps'], 
                              self.monitoring_data['memory_usage'], 
                              'b-', linewidth=2)
            self.memory_ax.set_title('Uso de Memória (MB)')
            self.memory_ax.set_ylabel('MB')
            self.memory_ax.grid(True, alpha=0.3)
            
            # Atualizar gráfico de cache
            self.cache_ax.clear()
            self.cache_ax.plot(self.monitoring_data['timestamps'], 
                             self.monitoring_data['cache_hit_rate'], 
                             'g-', linewidth=2)
            self.cache_ax.set_title('Taxa de Acerto do Cache (%)')
            self.cache_ax.set_ylabel('%')
            self.cache_ax.grid(True, alpha=0.3)
            
            # Redesenhar canvas
            self.window.after(0, lambda: (
                self.memory_canvas.draw(),
                self.cache_canvas.draw()
            ))
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar gráficos: {e}")
    
    def on_closing(self):
        """Manipula fechamento da janela"""
        self.monitoring_active = False
        self.window.destroy()
