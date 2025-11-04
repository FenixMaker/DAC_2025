# -*- coding: utf-8 -*-
"""
Sistema de Ícones Google Material Symbols para DAC System
Integração com Google Fonts Icons (Material Symbols) para UI moderna e consistente
https://fonts.google.com/icons
"""

import tkinter as tk
from tkinter import ttk, font as tkfont
import sys
import os

class MaterialIconManager:
    """
    Gerenciador de ícones usando Google Material Symbols
    
    Os ícones são renderizados usando a fonte Material Symbols disponível no Google Fonts.
    Para melhor resultado, instale a fonte Material Symbols no sistema:
    https://fonts.google.com/icons
    """
    
    def __init__(self):
        self.icons = {}
        self.font_family = 'Segoe Fluent Icons'  # Fallback para Windows 11
        self.emoji_fallback = 'Segoe UI Emoji'
        self.load_material_icons()
        self._check_font_availability()
    
    def _check_font_availability(self):
        """Verifica se as fontes de ícones estão disponíveis"""
        try:
            available_fonts = tkfont.families()
            
            # Tentar usar Material Symbols se disponível
            material_fonts = ['Material Symbols Outlined', 'Material Symbols Rounded', 'Material Icons']
            for font_name in material_fonts:
                if font_name in available_fonts:
                    self.font_family = font_name
                    print(f"✓ Usando fonte de ícones: {font_name}")
                    return
            
            # Fallback para fontes do sistema
            if 'Segoe Fluent Icons' in available_fonts:
                self.font_family = 'Segoe Fluent Icons'
            elif 'Segoe MDL2 Assets' in available_fonts:
                self.font_family = 'Segoe MDL2 Assets'
            else:
                self.font_family = self.emoji_fallback
                
        except Exception as e:
            print(f"⚠ Aviso: Erro ao verificar fontes: {e}")
            self.font_family = self.emoji_fallback
    
    def load_material_icons(self):
        """
        Carrega mapeamento de ícones do Google Material Symbols
        Formato: nome_interno -> (código_material_icon, emoji_fallback, cor)
        """
        # Mapeamento: nome -> (material_icon_name, emoji_fallback, color)
        self.icons = {
            # Navegação e ações principais
            'home': ('home', '🏠', '#8B5CF6'),
            'dashboard': ('dashboard', '📊', '#8B5CF6'),
            'import': ('file_upload', '📥', '#2563EB'),
            'export': ('file_download', '📤', '#2563EB'),
            'upload': ('cloud_upload', '☁️', '#2563EB'),
            'download': ('cloud_download', '💾', '#2563EB'),
            
            # Busca e filtros
            'search': ('search', '🔍', '#059669'),
            'filter': ('filter_list', '🔽', '#059669'),
            'sort': ('sort', '↕️', '#64748B'),
            'tune': ('tune', '🎛️', '#64748B'),
            
            # Dados e análises
            'reports': ('assessment', '📊', '#D97706'),
            'stats': ('analytics', '📈', '#3B82F6'),
            'chart': ('bar_chart', '📊', '#10B981'),
            'pie_chart': ('pie_chart', '🥧', '#F59E0B'),
            'database': ('database', '💾', '#059669'),
            'table': ('table_chart', '📋', '#64748B'),
            
            # Sistema e configurações
            'settings': ('settings', '⚙️', '#64748B'),
            'tune_settings': ('tune', '🎛️', '#64748B'),
            'build': ('build', '🔧', '#64748B'),
            'admin': ('admin_panel_settings', '👤', '#6366F1'),
            
            # Informações e ajuda
            'help': ('help', '❓', '#7C3AED'),
            'info': ('info', 'ℹ️', '#6366F1'),
            'description': ('description', '📄', '#64748B'),
            'article': ('article', '📰', '#64748B'),
            
            # Status e notificações
            'success': ('check_circle', '✅', '#10B981'),
            'error': ('error', '❌', '#EF4444'),
            'warning': ('warning', '⚠️', '#F59E0B'),
            'notification': ('notifications', '🔔', '#F59E0B'),
            'check': ('check', '✓', '#10B981'),
            'close': ('close', '✕', '#EF4444'),
            
            # Usuário e perfil
            'user': ('person', '👤', '#6366F1'),
            'group': ('group', '👥', '#6366F1'),
            'account': ('account_circle', '👤', '#6366F1'),
            
            # Tempo e calendário
            'time': ('schedule', '🕒', '#F59E0B'),
            'calendar': ('calendar_today', '📅', '#F59E0B'),
            'history': ('history', '⏰', '#64748B'),
            'update': ('update', '🔄', '#3B82F6'),
            
            # Edição e ações
            'edit': ('edit', '✏️', '#3B82F6'),
            'delete': ('delete', '🗑️', '#EF4444'),
            'add': ('add', '➕', '#10B981'),
            'remove': ('remove', '➖', '#EF4444'),
            'save': ('save', '💾', '#10B981'),
            'cancel': ('cancel', '✕', '#EF4444'),
            'refresh': ('refresh', '🔄', '#3B82F6'),
            
            # Visualização
            'visibility': ('visibility', '👁️', '#64748B'),
            'visibility_off': ('visibility_off', '🙈', '#64748B'),
            'preview': ('preview', '👁️', '#64748B'),
            'view_list': ('view_list', '📋', '#64748B'),
            'view_module': ('view_module', '▦', '#64748B'),
            
            # Pastas e arquivos
            'folder': ('folder', '📁', '#F59E0B'),
            'folder_open': ('folder_open', '📂', '#F59E0B'),
            'file': ('description', '📄', '#64748B'),
            'attach': ('attach_file', '📎', '#64748B'),
            
            # Comunicação
            'email': ('email', '📧', '#3B82F6'),
            'message': ('message', '💬', '#3B82F6'),
            'chat': ('chat', '💬', '#3B82F6'),
            'send': ('send', '📤', '#3B82F6'),
            
            # Segurança
            'lock': ('lock', '🔒', '#EF4444'),
            'unlock': ('lock_open', '🔓', '#10B981'),
            'security': ('security', '🛡️', '#6366F1'),
            'vpn_key': ('vpn_key', '🔑', '#F59E0B'),
            
            # Navegação direcional
            'arrow_back': ('arrow_back', '←', '#64748B'),
            'arrow_forward': ('arrow_forward', '→', '#64748B'),
            'arrow_up': ('arrow_upward', '↑', '#64748B'),
            'arrow_down': ('arrow_downward', '↓', '#64748B'),
            'expand_more': ('expand_more', '▼', '#64748B'),
            'expand_less': ('expand_less', '▲', '#64748B'),
            
            # Mídia
            'play': ('play_arrow', '▶️', '#10B981'),
            'pause': ('pause', '⏸️', '#F59E0B'),
            'stop': ('stop', '⏹️', '#EF4444'),
            'print': ('print', '🖨️', '#64748B'),
            
            # Conexão e rede
            'wifi': ('wifi', '📶', '#10B981'),
            'cloud': ('cloud', '☁️', '#3B82F6'),
            'sync': ('sync', '🔄', '#3B82F6'),
            'backup': ('backup', '🔙', '#10B981'),
        }
    
    def get_material_icon_code(self, name):
        """Retorna o código do Material Icon"""
        if name in self.icons:
            return self.icons[name][0]
        return 'help_outline'  # Ícone padrão
    
    def get_icon_unicode(self, name):
        """Retorna o emoji Unicode correspondente ao ícone (fallback)"""
        if name in self.icons:
            return self.icons[name][1]
        return '📋'  # Emoji padrão
    
    def get_icon_color(self, name):
        """Retorna a cor associada ao ícone"""
        if name in self.icons:
            return self.icons[name][2]
        return '#64748B'  # Cor padrão (cinza)
    
    def create_icon_label(self, parent, icon_name, size=24, **kwargs):
        """
        Cria um label com ícone usando Material Symbols ou emoji fallback
        
        Args:
            parent: Widget pai
            icon_name: Nome do ícone
            size: Tamanho do ícone em pixels
            **kwargs: Argumentos adicionais para o Label
        """
        icon_text = self.get_icon_unicode(icon_name)
        color = self.get_icon_color(icon_name)
        
        # Calcular tamanho da fonte baseado no tamanho desejado
        font_size = max(10, int(size * 0.8))
        
        # Configurar cor se não foi especificada
        if 'foreground' not in kwargs and 'fg' not in kwargs:
            kwargs['foreground'] = color
        
        label = ttk.Label(
            parent, 
            text=icon_text,
            font=(self.font_family, font_size),
            **kwargs
        )
        return label
    
    def create_icon_button(self, parent, icon_name, text="", command=None, style=None, **kwargs):
        """
        Cria um botão com ícone Material Symbol
        
        Args:
            parent: Widget pai
            icon_name: Nome do ícone
            text: Texto do botão (opcional)
            command: Função a ser executada ao clicar
            style: Estilo ttk do botão
            **kwargs: Argumentos adicionais
        """
        icon_text = self.get_icon_unicode(icon_name)
        
        if text:
            button_text = f"{icon_text}  {text}"
        else:
            button_text = icon_text
            
        button = ttk.Button(
            parent, 
            text=button_text, 
            command=command,
            style=style, 
            **kwargs
        )
        return button
    
    def create_labeled_icon(self, parent, icon_name, label_text, size=32, **kwargs):
        """
        Cria um frame com ícone e label abaixo
        
        Args:
            parent: Widget pai
            icon_name: Nome do ícone
            label_text: Texto do label
            size: Tamanho do ícone
            **kwargs: Argumentos adicionais para o frame
        """
        frame = ttk.Frame(parent, **kwargs)
        
        # Criar ícone
        icon_label = self.create_icon_label(frame, icon_name, size=size)
        icon_label.pack(pady=(0, 5))
        
        # Criar label de texto
        text_label = ttk.Label(frame, text=label_text)
        text_label.pack()
        
        return frame
    
    def get_icon_for_widget(self, icon_name, size=16):
        """
        Retorna caractere de ícone formatado para usar em widgets
        
        Args:
            icon_name: Nome do ícone
            size: Tamanho desejado
        
        Returns:
            str: Caractere do ícone
        """
        return self.get_icon_unicode(icon_name)

# Instância global do gerenciador de ícones
icon_manager = MaterialIconManager()

# Funções de conveniência para compatibilidade
def get_icon(name):
    """
    Obtém o caractere Unicode de um ícone Material Symbol
    
    Args:
        name: Nome do ícone
    
    Returns:
        str: Caractere do ícone
    """
    return icon_manager.get_icon_unicode(name)

def get_icon_color(name):
    """
    Obtém a cor associada a um ícone
    
    Args:
        name: Nome do ícone
    
    Returns:
        str: Código hexadecimal da cor
    """
    return icon_manager.get_icon_color(name)

def create_icon_label(parent, icon_name, size=24, **kwargs):
    """
    Cria um label com ícone
    
    Args:
        parent: Widget pai
        icon_name: Nome do ícone
        size: Tamanho do ícone
        **kwargs: Argumentos adicionais
    
    Returns:
        ttk.Label: Widget de label com ícone
    """
    return icon_manager.create_icon_label(parent, icon_name, size, **kwargs)

def create_icon_button(parent, icon_name, text="", command=None, style=None, **kwargs):
    """
    Cria um botão com ícone
    
    Args:
        parent: Widget pai
        icon_name: Nome do ícone
        text: Texto do botão
        command: Função callback
        style: Estilo ttk
        **kwargs: Argumentos adicionais
    
    Returns:
        ttk.Button: Widget de botão com ícone
    """
    return icon_manager.create_icon_button(parent, icon_name, text, command, style, **kwargs)

def create_labeled_icon(parent, icon_name, label_text, size=32, **kwargs):
    """
    Cria um frame com ícone e label
    
    Args:
        parent: Widget pai
        icon_name: Nome do ícone
        label_text: Texto do label
        size: Tamanho do ícone
        **kwargs: Argumentos adicionais
    
    Returns:
        ttk.Frame: Frame contendo ícone e label
    """
    return icon_manager.create_labeled_icon(parent, icon_name, label_text, size, **kwargs)

# Paleta de cores para ícones (mantida para compatibilidade)
ICON_COLORS = {
    'primary': '#2563EB',
    'success': '#10B981',
    'warning': '#F59E0B',
    'error': '#EF4444',
    'info': '#6366F1',
    'secondary': '#64748B',
    'purple': '#8B5CF6',
    'green': '#059669',
    'orange': '#D97706',
    'indigo': '#7C3AED'
}

# Mapeamento de categorias para cores (mantido para compatibilidade)
CATEGORY_COLORS = {
    'data': ICON_COLORS['primary'],
    'action': ICON_COLORS['success'],
    'system': ICON_COLORS['secondary'],
    'alert': ICON_COLORS['warning'],
    'error': ICON_COLORS['error'],
    'navigation': ICON_COLORS['purple'],
    'analysis': ICON_COLORS['orange']
}

# Lista de ícones disponíveis para referência
AVAILABLE_ICONS = sorted(icon_manager.icons.keys())

def list_available_icons():
    """
    Lista todos os ícones disponíveis
    
    Returns:
        list: Lista de nomes de ícones disponíveis
    """
    return AVAILABLE_ICONS

def print_icon_catalog():
    """Imprime catálogo de ícones disponíveis para referência"""
    print("\n" + "="*60)
    print("📋 CATÁLOGO DE ÍCONES - DAC SYSTEM")
    print("="*60 + "\n")
    
    categories = {
        'Navegação': ['home', 'dashboard', 'arrow_back', 'arrow_forward'],
        'Dados': ['import', 'export', 'database', 'table', 'upload', 'download'],
        'Análise': ['reports', 'stats', 'chart', 'pie_chart', 'analytics'],
        'Busca': ['search', 'filter', 'sort', 'tune'],
        'Sistema': ['settings', 'build', 'admin', 'tune_settings'],
        'Informação': ['help', 'info', 'description', 'article'],
        'Status': ['success', 'error', 'warning', 'notification', 'check', 'close'],
        'Usuário': ['user', 'group', 'account'],
        'Tempo': ['time', 'calendar', 'history', 'update'],
        'Edição': ['edit', 'delete', 'add', 'remove', 'save', 'cancel', 'refresh'],
        'Visualização': ['visibility', 'visibility_off', 'preview', 'view_list', 'view_module'],
        'Arquivos': ['folder', 'folder_open', 'file', 'attach'],
        'Comunicação': ['email', 'message', 'chat', 'send'],
        'Segurança': ['lock', 'unlock', 'security', 'vpn_key'],
        'Mídia': ['play', 'pause', 'stop', 'print'],
        'Rede': ['wifi', 'cloud', 'sync', 'backup']
    }
    
    for category, icon_list in categories.items():
        print(f"\n{category}:")
        print("-" * 40)
        for icon_name in icon_list:
            if icon_name in icon_manager.icons:
                icon = icon_manager.get_icon_unicode(icon_name)
                material_name = icon_manager.get_material_icon_code(icon_name)
                color = icon_manager.get_icon_color(icon_name)
                print(f"  {icon}  {icon_name:20} → {material_name:25} ({color})")
    
    print("\n" + "="*60)
    print(f"Total de ícones: {len(icon_manager.icons)}")
    print("="*60 + "\n")

# Executar demonstração se rodado diretamente
if __name__ == "__main__":
    print_icon_catalog()
    print("\n💡 Dica: Para usar Material Symbols de forma otimizada:")
    print("   Instale a fonte: https://fonts.google.com/icons")
    print("   Baixe: Material Symbols Outlined ou Material Symbols Rounded\n")