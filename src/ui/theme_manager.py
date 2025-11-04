
# -*- coding: utf-8 -*-
"""
Gerenciador de temas para o sistema DAC
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

class ThemeManager:
    """Gerenciador de temas da aplicação"""
    
    def __init__(self):
        self.themes = {
            'dark': {
                'bg': '#2b2b2b',
                'fg': '#ffffff',
                'select_bg': '#404040',
                'select_fg': '#ffffff',
                'button_bg': '#404040',
                'button_fg': '#ffffff',
                'entry_bg': '#404040',
                'entry_fg': '#ffffff',
                'frame_bg': '#2b2b2b',
                'accent': '#0078d4'
            },
            'light': {
                'bg': '#ffffff',
                'fg': '#000000',
                'select_bg': '#e3f2fd',
                'select_fg': '#000000',
                'button_bg': '#f5f5f5',
                'button_fg': '#000000',
                'entry_bg': '#ffffff',
                'entry_fg': '#000000',
                'frame_bg': '#f8f9fa',
                'accent': '#0078d4'
            }
        }
        
        self.current_theme = 'dark'
    
    def apply_theme(self, root, theme_name: str):
        """Aplica tema à aplicação"""
        if theme_name not in self.themes:
            return
        
        self.current_theme = theme_name
        theme = self.themes[theme_name]
        
        # Configurar estilo ttk
        style = ttk.Style()
        
        # Configurar cores do tema
        style.theme_use('clam')  # Base theme
        
        # Configurar estilos personalizados
        style.configure('TFrame', background=theme['frame_bg'])
        style.configure('TLabel', background=theme['frame_bg'], foreground=theme['fg'])
        style.configure('TButton', background=theme['button_bg'], foreground=theme['button_fg'])
        style.configure('TEntry', fieldbackground=theme['entry_bg'], foreground=theme['entry_fg'])
        
        # Estilos específicos
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10))
        style.configure('Menu.TButton', padding=(10, 5))
        style.configure('Info.TLabel', font=('Segoe UI', 9))
        
        # Configurar root
        root.configure(bg=theme['bg'])
    
    def get_current_theme(self):
        """Retorna tema atual"""
        return self.current_theme
    
    def get_theme_colors(self, theme_name: str = None):
        """Retorna cores do tema"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes['dark'])
