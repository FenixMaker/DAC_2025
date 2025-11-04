# -*- coding: utf-8 -*-
"""
Sistema de Acessibilidade

Este módulo implementa recursos de acessibilidade para garantir
que a interface seja utilizável por todos os usuários.
"""

import tkinter as tk
from tkinter import ttk
import colorsys

class AccessibilityManager:
    """
    Gerenciador de recursos de acessibilidade
    """
    
    def __init__(self):
        self.current_theme = 'default'
        self.font_size_multiplier = 1.0
        self.high_contrast_mode = False
        
        # Temas de cores acessíveis
        self.themes = {
            'default': {
                'bg_primary': '#f8f9fa',
                'bg_secondary': '#e9ecef',
                'bg_card': '#ffffff',
                'text_primary': '#212529',
                'text_secondary': '#6c757d',
                'text_muted': '#adb5bd',
                'accent': '#007bff',
                'accent_hover': '#0056b3',
                'success': '#28a745',
                'warning': '#ffc107',
                'danger': '#dc3545',
                'border': '#dee2e6'
            },
            'high_contrast': {
                'bg_primary': '#000000',
                'bg_secondary': '#1a1a1a',
                'bg_card': '#2d2d2d',
                'text_primary': '#ffffff',
                'text_secondary': '#e0e0e0',
                'text_muted': '#b0b0b0',
                'accent': '#00ff00',
                'accent_hover': '#00cc00',
                'success': '#00ff00',
                'warning': '#ffff00',
                'danger': '#ff0000',
                'border': '#ffffff'
            },
            'dark': {
                'bg_primary': '#1e1e1e',
                'bg_secondary': '#2d2d30',
                'bg_card': '#3e3e42',
                'text_primary': '#ffffff',
                'text_secondary': '#cccccc',
                'text_muted': '#969696',
                'accent': '#0078d4',
                'accent_hover': '#106ebe',
                'success': '#107c10',
                'warning': '#ffb900',
                'danger': '#d13438',
                'border': '#464647'
            },
            'light': {
                'bg_primary': '#ffffff',
                'bg_secondary': '#f3f2f1',
                'bg_card': '#faf9f8',
                'text_primary': '#323130',
                'text_secondary': '#605e5c',
                'text_muted': '#8a8886',
                'accent': '#0078d4',
                'accent_hover': '#106ebe',
                'success': '#107c10',
                'warning': '#ffb900',
                'danger': '#d13438',
                'border': '#edebe9'
            }
        }
        
        # Tamanhos de fonte base
        self.base_font_sizes = {
            'small': 8,
            'normal': 10,
            'medium': 12,
            'large': 14,
            'xlarge': 16,
            'title': 18,
            'heading': 24
        }
    
    def get_current_colors(self):
        """Retorna as cores do tema atual"""
        return self.themes[self.current_theme]
    
    def set_theme(self, theme_name):
        """Define o tema de cores"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def toggle_high_contrast(self):
        """Alterna modo de alto contraste"""
        if self.current_theme == 'high_contrast':
            self.current_theme = 'default'
            self.high_contrast_mode = False
        else:
            self.current_theme = 'high_contrast'
            self.high_contrast_mode = True
    
    def increase_font_size(self):
        """Aumenta o tamanho da fonte"""
        if self.font_size_multiplier < 2.0:
            self.font_size_multiplier += 0.1
    
    def decrease_font_size(self):
        """Diminui o tamanho da fonte"""
        if self.font_size_multiplier > 0.5:
            self.font_size_multiplier -= 0.1
    
    def reset_font_size(self):
        """Reseta o tamanho da fonte"""
        self.font_size_multiplier = 1.0
    
    def get_font_size(self, size_key):
        """Retorna o tamanho da fonte ajustado"""
        base_size = self.base_font_sizes.get(size_key, 10)
        return int(base_size * self.font_size_multiplier)
    
    def get_font_config(self, size_key='normal', weight='normal'):
        """Retorna configuração completa da fonte"""
        return {
            'family': 'Segoe UI',
            'size': self.get_font_size(size_key),
            'weight': weight
        }
    
    def check_contrast_ratio(self, color1, color2):
        """
        Verifica a razão de contraste entre duas cores
        Retorna True se o contraste for adequado (>= 4.5:1)
        """
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def get_luminance(rgb):
            def normalize(c):
                c = c / 255.0
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            
            r, g, b = [normalize(c) for c in rgb]
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        lum1 = get_luminance(rgb1)
        lum2 = get_luminance(rgb2)
        
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        contrast_ratio = (lighter + 0.05) / (darker + 0.05)
        return contrast_ratio >= 4.5
    
    def create_accessible_style(self, root):
        """Cria estilos acessíveis para ttk"""
        style = ttk.Style(root)
        colors = self.get_current_colors()
        
        # Configurações gerais
        style.theme_use('clam')
        
        # Estilos para frames
        style.configure('Main.TFrame',
                       background=colors['bg_primary'],
                       borderwidth=0)
        
        style.configure('Sidebar.TFrame',
                       background=colors['bg_secondary'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=colors['border'])
        
        style.configure('Card.TFrame',
                       background=colors['bg_card'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=colors['border'],
                       padding=10)
        
        style.configure('Header.TFrame',
                       background=colors['bg_primary'],
                       borderwidth=0)
        
        # Estilos para labels
        style.configure('Main.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['text_primary'],
                       font=self.get_font_config('normal'))
        
        style.configure('Sidebar.TLabel',
                       background=colors['bg_secondary'],
                       foreground=colors['text_primary'],
                       font=self.get_font_config('normal'))
        
        style.configure('Card.TLabel',
                       background=colors['bg_card'],
                       foreground=colors['text_primary'],
                       font=self.get_font_config('normal'))
        
        style.configure('Title.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['text_primary'],
                       font=self.get_font_config('title', 'bold'))
        
        style.configure('Heading.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['text_primary'],
                       font=self.get_font_config('heading', 'bold'))
        
        # Estilos para botões
        style.configure('Primary.TButton',
                       background=colors['accent'],
                       foreground='white',
                       font=self.get_font_config('medium', 'bold'),
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 10))
        
        style.map('Primary.TButton',
                 background=[('active', colors['accent_hover']),
                           ('pressed', colors['accent_hover'])],
                 relief=[('pressed', 'flat'),
                        ('!pressed', 'raised')])
        
        style.configure('Secondary.TButton',
                       background=colors['bg_card'],
                       foreground=colors['text_primary'],
                       font=self.get_font_config('normal'),
                       borderwidth=1,
                       bordercolor=colors['border'],
                       focuscolor='none',
                       padding=(15, 8))
        
        style.map('Secondary.TButton',
                 background=[('active', colors['bg_secondary']),
                           ('pressed', colors['bg_secondary'])],
                 bordercolor=[('active', colors['accent']),
                            ('pressed', colors['accent'])])
        
        # Estilos para entrada de texto
        style.configure('Accessible.TEntry',
                       fieldbackground=colors['bg_card'],
                       foreground=colors['text_primary'],
                       bordercolor=colors['border'],
                       borderwidth=2,
                       font=self.get_font_config('medium'),
                       padding=8)
        
        style.map('Accessible.TEntry',
                 bordercolor=[('focus', colors['accent'])])
        
        # Estilos para combobox
        style.configure('Accessible.TCombobox',
                       fieldbackground=colors['bg_card'],
                       foreground=colors['text_primary'],
                       bordercolor=colors['border'],
                       borderwidth=2,
                       font=self.get_font_config('medium'),
                       padding=8)
        
        style.map('Accessible.TCombobox',
                 bordercolor=[('focus', colors['accent'])])
        
        return style
    
    def create_accessibility_toolbar(self, parent):
        """
        Cria barra de ferramentas de acessibilidade
        """
        toolbar = ttk.Frame(parent, style='Sidebar.TFrame')
        toolbar.pack(fill='x', padx=5, pady=5)
        
        # Título da barra
        title_label = ttk.Label(toolbar, text="♿ Acessibilidade",
                               font=self.get_font_config('medium', 'bold'),
                               style='Sidebar.TLabel')
        title_label.pack(anchor='w', pady=(5, 10))
        
        # Controles de fonte
        font_frame = ttk.Frame(toolbar, style='Sidebar.TFrame')
        font_frame.pack(fill='x', pady=2)
        
        font_label = ttk.Label(font_frame, text="Tamanho da Fonte:",
                              style='Sidebar.TLabel')
        font_label.pack(anchor='w')
        
        font_controls = ttk.Frame(font_frame, style='Sidebar.TFrame')
        font_controls.pack(fill='x', pady=(2, 0))
        
        decrease_btn = ttk.Button(font_controls, text="A-", width=3,
                                 command=self.decrease_font_size,
                                 style='Secondary.TButton')
        decrease_btn.pack(side='left', padx=(0, 2))
        
        reset_btn = ttk.Button(font_controls, text="A", width=3,
                              command=self.reset_font_size,
                              style='Secondary.TButton')
        reset_btn.pack(side='left', padx=2)
        
        increase_btn = ttk.Button(font_controls, text="A+", width=3,
                                 command=self.increase_font_size,
                                 style='Secondary.TButton')
        increase_btn.pack(side='left', padx=(2, 0))
        
        # Controle de tema
        theme_frame = ttk.Frame(toolbar, style='Sidebar.TFrame')
        theme_frame.pack(fill='x', pady=(10, 2))
        
        theme_label = ttk.Label(theme_frame, text="Tema:",
                               style='Sidebar.TLabel')
        theme_label.pack(anchor='w')
        
        theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = ttk.Combobox(theme_frame, textvariable=theme_var,
                                  values=list(self.themes.keys()),
                                  state='readonly',
                                  style='Accessible.TCombobox')
        theme_combo.pack(fill='x', pady=(2, 0))
        theme_combo.bind('<<ComboboxSelected>>', 
                        lambda e: self.change_theme(theme_var.get()))
        
        # Botão de alto contraste
        contrast_btn = ttk.Button(toolbar, text="🔆 Alto Contraste",
                                 command=self.toggle_high_contrast,
                                 style='Secondary.TButton')
        contrast_btn.pack(fill='x', pady=(10, 5))
        
        return toolbar
    
    def change_theme(self, theme_name):
        """Muda o tema e atualiza a interface"""
        if self.set_theme(theme_name):
            # Aqui você pode adicionar lógica para atualizar a interface
            # quando o tema muda
            pass
    
    def add_keyboard_navigation(self, widget):
        """
        Adiciona navegação por teclado a um widget
        """
        def on_key_press(event):
            if event.keysym == 'Return' or event.keysym == 'space':
                if hasattr(widget, 'invoke'):
                    widget.invoke()
                elif hasattr(widget, 'event_generate'):
                    widget.event_generate('<Button-1>')
        
        widget.bind('<KeyPress>', on_key_press)
        widget.focus_set()
    
    def create_focus_indicator(self, widget):
        """
        Cria indicador visual de foco para um widget
        """
        colors = self.get_current_colors()
        
        def on_focus_in(event):
            widget.configure(highlightbackground=colors['accent'],
                           highlightcolor=colors['accent'],
                           highlightthickness=2)
        
        def on_focus_out(event):
            widget.configure(highlightthickness=0)
        
        widget.bind('<FocusIn>', on_focus_in)
        widget.bind('<FocusOut>', on_focus_out)
    
    def add_screen_reader_support(self, widget, description):
        """
        Adiciona suporte para leitores de tela
        """
        # Define atributos de acessibilidade
        widget.configure(takefocus=True)
        
        # Adiciona descrição para leitores de tela
        if hasattr(widget, 'configure'):
            try:
                widget.configure(name=description)
            except:
                pass

class ColorBlindnessSupport:
    """
    Suporte para daltonismo
    """
    
    @staticmethod
    def simulate_colorblindness(color, type_='protanopia'):
        """
        Simula como uma cor aparece para pessoas com daltonismo
        """
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(*[int(c) for c in rgb])
        
        r, g, b = hex_to_rgb(color)
        
        # Matrizes de transformação para diferentes tipos de daltonismo
        matrices = {
            'protanopia': [
                [0.567, 0.433, 0],
                [0.558, 0.442, 0],
                [0, 0.242, 0.758]
            ],
            'deuteranopia': [
                [0.625, 0.375, 0],
                [0.7, 0.3, 0],
                [0, 0.3, 0.7]
            ],
            'tritanopia': [
                [0.95, 0.05, 0],
                [0, 0.433, 0.567],
                [0, 0.475, 0.525]
            ]
        }
        
        matrix = matrices.get(type_, matrices['protanopia'])
        
        new_r = matrix[0][0] * r + matrix[0][1] * g + matrix[0][2] * b
        new_g = matrix[1][0] * r + matrix[1][1] * g + matrix[1][2] * b
        new_b = matrix[2][0] * r + matrix[2][1] * g + matrix[2][2] * b
        
        return rgb_to_hex((new_r, new_g, new_b))
    
    @staticmethod
    def get_colorblind_friendly_palette():
        """
        Retorna uma paleta de cores amigável para daltônicos
        """
        return {
            'blue': '#0173b2',
            'orange': '#de8f05',
            'green': '#029e73',
            'red': '#cc78bc',
            'purple': '#ca9161',
            'brown': '#fbafe4',
            'pink': '#949494',
            'gray': '#ece133'
        }

def create_accessible_interface(root):
    """
    Função auxiliar para criar uma interface acessível
    """
    accessibility_manager = AccessibilityManager()
    style = accessibility_manager.create_accessible_style(root)
    
    return accessibility_manager, style