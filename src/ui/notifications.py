
# -*- coding: utf-8 -*-
"""
Sistema de notificações para o DAC
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class NotificationType(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"

class NotificationManager:
    """Gerenciador de notificações do sistema"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.notifications = []
        self.notification_widgets = []
        
    def show_info(self, message: str, duration: int = 3000):
        """Mostra notificação de informação"""
        self._show_notification(message, NotificationType.INFO, duration)
    
    def show_success(self, message: str, duration: int = 3000):
        """Mostra notificação de sucesso"""
        self._show_notification(message, NotificationType.SUCCESS, duration)
    
    def show_warning(self, message: str, duration: int = 5000):
        """Mostra notificação de aviso"""
        self._show_notification(message, NotificationType.WARNING, duration)
    
    def show_error(self, message: str, duration: int = 7000):
        """Mostra notificação de erro"""
        self._show_notification(message, NotificationType.ERROR, duration)
    
    def _show_notification(self, message: str, notification_type: NotificationType, duration: int):
        """Mostra notificação na tela"""
        if not self.parent:
            return
        
        # Criar janela de notificação
        notification_window = tk.Toplevel(self.parent)
        notification_window.withdraw()  # Ocultar inicialmente
        
        # Configurar janela
        notification_window.overrideredirect(True)  # Sem bordas
        notification_window.attributes('-topmost', True)  # Sempre no topo
        
        # Cores por tipo
        colors = {
            NotificationType.INFO: {'bg': '#3498db', 'fg': 'white'},
            NotificationType.SUCCESS: {'bg': '#2ecc71', 'fg': 'white'},
            NotificationType.WARNING: {'bg': '#f39c12', 'fg': 'white'},
            NotificationType.ERROR: {'bg': '#e74c3c', 'fg': 'white'}
        }
        
        color_config = colors[notification_type]
        
        # Frame da notificação
        frame = tk.Frame(notification_window, 
                        bg=color_config['bg'], 
                        relief='raised', 
                        borderwidth=2)
        frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Ícones por tipo
        icons = {
            NotificationType.INFO: 'ℹ️',
            NotificationType.SUCCESS: '✅',
            NotificationType.WARNING: '⚠️',
            NotificationType.ERROR: '❌'
        }
        
        # Label com ícone e mensagem
        label = tk.Label(frame, 
                        text=f"{icons[notification_type]} {message}",
                        bg=color_config['bg'],
                        fg=color_config['fg'],
                        font=('Segoe UI', 10, 'bold'),
                        padx=15,
                        pady=10)
        label.pack()
        
        # Posicionar no canto superior direito
        notification_window.update_idletasks()
        width = notification_window.winfo_reqwidth()
        height = notification_window.winfo_reqheight()
        
        screen_width = notification_window.winfo_screenwidth()
        x = screen_width - width - 20
        y = 20 + len(self.notification_widgets) * (height + 10)
        
        notification_window.geometry(f"{width}x{height}+{x}+{y}")
        notification_window.deiconify()  # Mostrar janela
        
        # Adicionar à lista
        self.notification_widgets.append(notification_window)
        
        # Agendar remoção
        def remove_notification():
            try:
                if notification_window in self.notification_widgets:
                    self.notification_widgets.remove(notification_window)
                notification_window.destroy()
                self._reposition_notifications()
            except:
                pass
        
        notification_window.after(duration, remove_notification)
        
        # Permitir fechar clicando
        label.bind('<Button-1>', lambda e: remove_notification())
    
    def _reposition_notifications(self):
        """Reposiciona notificações após remoção"""
        for i, notification in enumerate(self.notification_widgets):
            try:
                notification.update_idletasks()
                width = notification.winfo_reqwidth()
                height = notification.winfo_reqheight()
                
                screen_width = notification.winfo_screenwidth()
                x = screen_width - width - 20
                y = 20 + i * (height + 10)
                
                notification.geometry(f"{width}x{height}+{x}+{y}")
            except:
                pass
