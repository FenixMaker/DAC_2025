# -*- coding: utf-8 -*-
"""
Ícones SVG para a interface do DAC System
Elementos visuais em formato vetorial para melhor qualidade e acessibilidade
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import io
import base64

class IconManager:
    """Gerenciador de ícones SVG para a interface"""
    
    def __init__(self):
        self.icons = {}
        self.load_icons()
    
    def load_icons(self):
        """Carrega todos os ícones disponíveis"""
        # Ícone de importação de dados
        self.icons['import'] = '''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.89 22 5.99 22H18C19.1 22 20 21.1 20 20V8L14 2Z" stroke="#2563EB" stroke-width="2" fill="#E3F2FD"/>
            <path d="M14 2V8H20" stroke="#2563EB" stroke-width="2" fill="none"/>
            <path d="M12 18L8 14H11V10H13V14H16L12 18Z" fill="#2563EB"/>
        </svg>
        '''
        
        # Ícone de consulta/busca
        self.icons['search'] = '''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="11" cy="11" r="8" stroke="#059669" stroke-width="2" fill="#ECFDF5"/>
            <path d="21 21L16.65 16.65" stroke="#059669" stroke-width="2" stroke-linecap="round"/>
            <circle cx="11" cy="11" r="3" fill="#059669"/>
        </svg>
        '''
        
        # Ícone de relatórios
        self.icons['reports'] = '''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 3V21H21" stroke="#D97706" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9 9L12 6L16 10L20 6" stroke="#D97706" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            <rect x="7" y="12" width="2" height="8" fill="#FED7AA"/>
            <rect x="11" y="8" width="2" height="12" fill="#FDBA74"/>
            <rect x="15" y="14" width="2" height="6" fill="#FB923C"/>
            <rect x="19" y="10" width="2" height="10" fill="#D97706"/>
        </svg>
        '''
        
        # Ícone de configurações
        self.icons['settings'] = '''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="3" stroke="#64748B" stroke-width="2" fill="#F1F5F9"/>
            <path d="M19.4 15C19.2 15.3 19.1 15.7 19.1 16.1C19.1 16.5 19.2 16.9 19.4 17.2L20.4 18.9C20.6 19.3 20.5 19.7 20.2 20L18.8 22C18.5 22.3 18.1 22.4 17.7 22.2L15.8 21.3C15.2 21.7 14.6 22 14 22.2L13.6 24.2C13.5 24.6 13.1 25 12.7 25H10.3C9.9 25 9.5 24.6 9.4 24.2L9 22.2C8.4 22 7.8 21.7 7.2 21.3L5.3 22.2C4.9 22.4 4.5 22.3 4.2 22L2.8 20C2.5 19.7 2.4 19.3 2.6 18.9L3.6 17.2C3.4 16.9 3.3 16.5 3.3 16.1C3.3 15.7 3.4 15.3 3.6 15L2.6 13.3C2.4 12.9 2.5 12.5 2.8 12.2L4.2 10.2C4.5 9.9 4.9 9.8 5.3 10L7.2 10.9C7.8 10.5 8.4 10.2 9 10L9.4 8C9.5 7.6 9.9 7.2 10.3 7.2H12.7C13.1 7.2 13.5 7.6 13.6 8L14 10C14.6 10.2 15.2 10.5 15.8 10.9L17.7 10C18.1 9.8 18.5 9.9 18.8 10.2L20.2 12.2C20.5 12.5 20.6 12.9 20.4 13.3L19.4 15Z" stroke="#64748B" stroke-width="1.5" fill="#F8FAFC"/>
        </svg>
        '''
        
        # Ícone de ajuda
        self.icons['help'] = '''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="#7C3AED" stroke-width="2" fill="#F3E8FF"/>
            <path d="M9.09 9C9.32 8.4 9.77 7.9 10.37 7.6C10.97 7.3 11.64 7.3 12.24 7.6C12.84 7.9 13.29 8.4 13.52 9C13.75 9.6 13.75 10.3 13.52 10.9C13.29 11.5 12.84 12 12.24 12.3C11.64 12.6 10.97 12.6 10.37 12.3" stroke="#7C3AED" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="16" r="1" fill="#7C3AED"/>
        </svg>
        '''
        
        # Ícone de estatísticas
        self.icons['stats'] = '''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="3" y="16" width="4" height="6" rx="1" fill="#3B82F6"/>
            <rect x="10" y="12" width="4" height="10" rx="1" fill="#10B981"/>
            <rect x="17" y="8" width="4" height="14" rx="1" fill="#F59E0B"/>
            <path d="M3 3L7 7L12 2L21 11" stroke="#EF4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        '''
        
        # Ícone de banco de dados
        self.icons['database'] = '''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <ellipse cx="12" cy="5" rx="9" ry="3" stroke="#059669" stroke-width="2" fill="#ECFDF5"/>
            <path d="M21 12C21 13.66 16.97 15 12 15S3 13.66 3 12" stroke="#059669" stroke-width="2"/>
            <path d="M3 5V19C3 20.66 7.03 22 12 22S21 20.66 21 19V5" stroke="#059669" stroke-width="2"/>
            <path d="M21 12C21 13.66 16.97 15 12 15S3 13.66 3 12" stroke="#059669" stroke-width="2"/>
        </svg>
        '''
        
        # Ícone de tempo/relógio
        self.icons['time'] = '''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="#F59E0B" stroke-width="2" fill="#FEF3C7"/>
            <path d="M12 6V12L16 14" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        '''
        
        # Ícone de sucesso/check
        self.icons['success'] = '''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" fill="#10B981"/>
            <path d="M9 12L11 14L15 10" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        '''
        
        # Ícone de erro
        self.icons['error'] = '''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" fill="#EF4444"/>
            <path d="M15 9L9 15" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9 9L15 15" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        '''
        
        # Ícone de aviso
        self.icons['warning'] = '''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10.29 3.86L1.82 18C1.64 18.37 1.64 18.8 1.82 19.17C2 19.54 2.37 19.78 2.82 19.78H21.18C21.63 19.78 22 19.54 22.18 19.17C22.36 18.8 22.36 18.37 22.18 18L13.71 3.86C13.53 3.49 13.16 3.25 12.71 3.25C12.26 3.25 11.89 3.49 11.71 3.86H10.29Z" fill="#F59E0B"/>
            <path d="M12 9V13" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="17" r="1" fill="white"/>
        </svg>
        '''
        
        # Ícone de usuário
        self.icons['user'] = '''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 21V19C20 17.9 19.1 17 18 17H6C4.9 17 4 17.9 4 19V21" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="7" r="4" stroke="#6366F1" stroke-width="2" fill="#E0E7FF"/>
        </svg>
        '''
        
        # Ícone de casa/home
        self.icons['home'] = '''
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 9L12 2L21 9V20C21 20.5 20.5 21 20 21H4C3.5 21 3 20.5 3 20V9Z" stroke="#8B5CF6" stroke-width="2" fill="#F3E8FF"/>
            <path d="M9 22V12H15V22" stroke="#8B5CF6" stroke-width="2" fill="none"/>
        </svg>
        '''
    
    def get_icon_unicode(self, name):
        """Retorna o emoji Unicode correspondente ao ícone"""
        unicode_map = {
            'import': '📥',
            'search': '🔍', 
            'reports': '📊',
            'settings': '⚙️',
            'help': '❓',
            'stats': '📈',
            'database': '💾',
            'time': '🕒',
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'user': '👤',
            'home': '🏠'
        }
        return unicode_map.get(name, '📋')
    
    def create_icon_label(self, parent, icon_name, size=24, **kwargs):
        """Cria um label com ícone Unicode"""
        icon_text = self.get_icon_unicode(icon_name)
        
        # Calcular tamanho da fonte baseado no tamanho desejado
        font_size = max(8, size // 2)
        
        label = ttk.Label(parent, text=icon_text, 
                         font=('Segoe UI Emoji', font_size),
                         **kwargs)
        return label
    
    def create_icon_button(self, parent, icon_name, text="", command=None, style=None, **kwargs):
        """Cria um botão com ícone"""
        icon_text = self.get_icon_unicode(icon_name)
        
        if text:
            button_text = f"{icon_text} {text}"
        else:
            button_text = icon_text
            
        button = ttk.Button(parent, text=button_text, command=command, 
                           style=style, **kwargs)
        return button

# Instância global do gerenciador de ícones
icon_manager = IconManager()

# Funções de conveniência
def get_icon(name):
    """Obtém o emoji Unicode de um ícone"""
    return icon_manager.get_icon_unicode(name)

def create_icon_label(parent, icon_name, size=24, **kwargs):
    """Cria um label com ícone"""
    return icon_manager.create_icon_label(parent, icon_name, size, **kwargs)

def create_icon_button(parent, icon_name, text="", command=None, style=None, **kwargs):
    """Cria um botão com ícone"""
    return icon_manager.create_icon_button(parent, icon_name, text, command, style, **kwargs)

# Paleta de cores para ícones
ICON_COLORS = {
    'primary': '#2563EB',
    'success': '#10B981', 
    'warning': '#F59E0B',
    'error': '#EF4444',
    'info': '#6366F1',
    'secondary': '#64748B'
}

# Mapeamento de categorias para cores
CATEGORY_COLORS = {
    'data': ICON_COLORS['primary'],
    'action': ICON_COLORS['success'],
    'system': ICON_COLORS['secondary'],
    'alert': ICON_COLORS['warning'],
    'error': ICON_COLORS['error']
}