
# -*- coding: utf-8 -*-
"""
Gerenciador de temas modernos para o Sistema DAC
Tema moderno inspirado em Power BI, Stripe Dashboard e VS Code
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
from .modern_theme import theme

class ThemeManager:
    """Gerenciador de temas modernos da aplicação"""
    
    def __init__(self):
        self.current_theme = 'modern_dark'
        self.style = None
    
    def apply_theme(self, root):
        """Aplica tema moderno à aplicação"""
        # Configurar estilo ttk
        self.style = ttk.Style()
        
        # Usar tema base clam (mais customizável)
        self.style.theme_use('clam')
        
        # ===== CONFIGURAR ROOT =====
        root.configure(bg=theme.bg_root)
        
        # ===== FRAMES =====
        self.style.configure('TFrame', 
                           background=theme.bg_primary,
                           borderwidth=0)
        
        self.style.configure('Card.TFrame',
                           background=theme.bg_secondary,
                           relief='flat',
                           borderwidth=1)
        
        self.style.configure('Sidebar.TFrame',
                           background=theme.bg_primary)
        
        # ===== LABELS =====
        # Label padrão
        self.style.configure('TLabel',
                           background=theme.bg_primary,
                           foreground=theme.text_primary,
                           font=(theme.font_family[0], theme.font_size_normal))
        
        # Título principal
        self.style.configure('Title.TLabel',
                           background=theme.bg_primary,
                           foreground=theme.text_primary,
                           font=(theme.font_family[0], theme.font_size_xlarge, 'bold'))
        
        # Subtítulo/Heading
        self.style.configure('Heading.TLabel',
                           background=theme.bg_primary,
                           foreground=theme.text_primary,
                           font=(theme.font_family[0], theme.font_size_large, 'bold'))
        
        # Label secundário
        self.style.configure('Secondary.TLabel',
                           background=theme.bg_primary,
                           foreground=theme.text_secondary,
                           font=(theme.font_family[0], theme.font_size_small))
        
        # KPI (número grande)
        self.style.configure('KPI.TLabel',
                           background=theme.bg_secondary,
                           foreground=theme.text_primary,
                           font=(theme.font_family[0], theme.font_size_kpi, 'bold'))
        
        # Label do KPI (texto pequeno acima do número)
        self.style.configure('KPILabel.TLabel',
                           background=theme.bg_secondary,
                           foreground=theme.text_secondary,
                           font=(theme.font_family[0], theme.font_size_small))
        
        # ===== BOTÕES =====
        # Botão primário
        self.style.configure('Primary.TButton',
                           background=theme.accent_primary,
                           foreground=theme.text_on_accent,
                           borderwidth=0,
                           relief='flat',
                           padding=(theme.button_padding_x, theme.button_padding_y),
                           font=(theme.font_family[0], theme.font_size_medium, 'bold'))
        
        self.style.map('Primary.TButton',
                      background=[('active', theme.accent_hover),
                                ('pressed', theme.accent_dark)])
        
        # Botão secundário
        self.style.configure('Secondary.TButton',
                           background=theme.bg_secondary,
                           foreground=theme.text_primary,
                           borderwidth=1,
                           bordercolor=theme.border,
                           relief='flat',
                           padding=(theme.button_padding_x, theme.button_padding_y),
                           font=(theme.font_family[0], theme.font_size_medium))
        
        self.style.map('Secondary.TButton',
                      background=[('active', theme.bg_hover),
                                ('pressed', theme.bg_hover_light)])
        
        # Botão da sidebar
        self.style.configure('Sidebar.TButton',
                           background=theme.bg_primary,
                           foreground=theme.text_secondary,
                           borderwidth=0,
                           relief='flat',
                           anchor='w',
                           padding=(theme.spacing_lg, theme.spacing_md),
                           font=(theme.font_family[0], theme.font_size_medium))
        
        self.style.map('Sidebar.TButton',
                      background=[('active', theme.bg_hover)],
                      foreground=[('active', theme.text_primary)])
        
        # Botão de sucesso
        self.style.configure('Success.TButton',
                           background=theme.success,
                           foreground=theme.text_on_accent,
                           borderwidth=0,
                           relief='flat',
                           padding=(theme.button_padding_x, theme.button_padding_y),
                           font=(theme.font_family[0], theme.font_size_medium, 'bold'))
        
        self.style.map('Success.TButton',
                      background=[('active', theme.success_light)])
        
        # Botão de perigo
        self.style.configure('Danger.TButton',
                           background=theme.error,
                           foreground=theme.text_on_accent,
                           borderwidth=0,
                           relief='flat',
                           padding=(theme.button_padding_x, theme.button_padding_y),
                           font=(theme.font_family[0], theme.font_size_medium, 'bold'))
        
        self.style.map('Danger.TButton',
                      background=[('active', theme.error_light)])
        
        # ===== ENTRIES (CAMPOS DE TEXTO) =====
        self.style.configure('TEntry',
                           fieldbackground=theme.bg_primary,
                           background=theme.bg_primary,
                           foreground=theme.text_primary,
                           borderwidth=1,
                           relief='flat',
                           insertcolor=theme.text_primary,
                           selectbackground=theme.accent_primary,
                           selectforeground=theme.text_on_accent,
                           padding=theme.spacing_md)
        
        self.style.map('TEntry',
                      bordercolor=[('focus', theme.accent_primary),
                                 ('!focus', theme.border)])
        
        # ===== COMBOBOX =====
        self.style.configure('TCombobox',
                           fieldbackground=theme.bg_primary,
                           background=theme.bg_primary,
                           foreground=theme.text_primary,
                           borderwidth=1,
                           arrowcolor=theme.text_secondary,
                           padding=theme.spacing_md)
        
        self.style.map('TCombobox',
                      fieldbackground=[('readonly', theme.bg_primary)],
                      selectbackground=[('readonly', theme.bg_primary)],
                      bordercolor=[('focus', theme.accent_primary),
                                 ('!focus', theme.border)])
        
        # Dropdown do combobox
        root.option_add('*TCombobox*Listbox.background', theme.bg_secondary)
        root.option_add('*TCombobox*Listbox.foreground', theme.text_primary)
        root.option_add('*TCombobox*Listbox.selectBackground', theme.accent_primary)
        root.option_add('*TCombobox*Listbox.selectForeground', theme.text_on_accent)
        
        # ===== NOTEBOOK (ABAS) =====
        self.style.configure('TNotebook',
                           background=theme.bg_primary,
                           borderwidth=0,
                           tabmargins=[0, 0, 0, 0])
        
        self.style.configure('TNotebook.Tab',
                           background=theme.bg_secondary,
                           foreground=theme.text_secondary,
                           padding=(theme.spacing_xl, theme.spacing_md),
                           borderwidth=0,
                           font=(theme.font_family[0], theme.font_size_medium))
        
        self.style.map('TNotebook.Tab',
                      background=[('selected', theme.bg_primary)],
                      foreground=[('selected', theme.text_primary),
                                ('active', theme.text_primary)],
                      expand=[('selected', [1, 1, 1, 0])])
        
        # ===== TREEVIEW (TABELAS) =====
        self.style.configure('Treeview',
                           background=theme.bg_primary,
                           foreground=theme.text_primary,
                           fieldbackground=theme.bg_primary,
                           borderwidth=0,
                           relief='flat',
                           rowheight=32,
                           font=(theme.font_family[0], theme.font_size_normal))
        
        self.style.configure('Treeview.Heading',
                           background=theme.bg_secondary,
                           foreground=theme.text_secondary,
                           borderwidth=0,
                           relief='flat',
                           padding=(theme.spacing_md, theme.spacing_md),
                           font=(theme.font_family[0], theme.font_size_small, 'bold'))
        
        self.style.map('Treeview',
                      background=[('selected', theme.accent_primary)],
                      foreground=[('selected', theme.text_on_accent)])
        
        self.style.map('Treeview.Heading',
                      background=[('active', theme.bg_hover)])
        
        # ===== SCROLLBAR =====
        self.style.configure('Vertical.TScrollbar',
                           background=theme.bg_primary,
                           troughcolor=theme.bg_primary,
                           borderwidth=0,
                           relief='flat',
                           arrowsize=0,
                           width=10)
        
        self.style.map('Vertical.TScrollbar',
                      background=[('active', theme.bg_hover_light)])
        
        self.style.configure('Horizontal.TScrollbar',
                           background=theme.bg_primary,
                           troughcolor=theme.bg_primary,
                           borderwidth=0,
                           relief='flat',
                           arrowsize=0,
                           width=10)
        
        self.style.map('Horizontal.TScrollbar',
                      background=[('active', theme.bg_hover_light)])
        
        # ===== PROGRESSBAR =====
        self.style.configure('TProgressbar',
                           background=theme.accent_primary,
                           troughcolor=theme.bg_secondary,
                           borderwidth=0,
                           thickness=8)
        
        # ===== SEPARATOR =====
        self.style.configure('TSeparator',
                           background=theme.border)
        
        # ===== CHECKBUTTON =====
        self.style.configure('TCheckbutton',
                           background=theme.bg_primary,
                           foreground=theme.text_primary,
                           borderwidth=0,
                           font=(theme.font_family[0], theme.font_size_normal))
        
        self.style.map('TCheckbutton',
                      background=[('active', theme.bg_hover)])
        
        # ===== RADIOBUTTON =====
        self.style.configure('TRadiobutton',
                           background=theme.bg_primary,
                           foreground=theme.text_primary,
                           borderwidth=0,
                           font=(theme.font_family[0], theme.font_size_normal))
        
        self.style.map('TRadiobutton',
                      background=[('active', theme.bg_hover)])
    
    def get_theme_colors(self):
        """Retorna cores do tema atual"""
        return {
            'bg_root': theme.bg_root,
            'bg_primary': theme.bg_primary,
            'bg_secondary': theme.bg_secondary,
            'bg_hover': theme.bg_hover,
            'border': theme.border,
            'accent': theme.accent_primary,
            'text_primary': theme.text_primary,
            'text_secondary': theme.text_secondary,
            'text_on_accent': theme.text_on_accent,
            'success': theme.success,
            'warning': theme.warning,
            'error': theme.error,
            'info': theme.info
        }
    
    def get_current_theme(self):
        """Retorna nome do tema atual"""
        return self.current_theme
