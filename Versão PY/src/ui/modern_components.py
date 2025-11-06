"""
Componentes UI Modernos para o Sistema DAC
Componentes reutilizáveis com design moderno e profissional
"""

import tkinter as tk
from tkinter import ttk
from .modern_theme import theme
from .icons import get_icon, get_icon_color


class ModernCard(ttk.Frame):
    """Card moderno com bordas e padding"""
    
    def __init__(self, parent, title=None, **kwargs):
        super().__init__(parent, style='Card.TFrame', **kwargs)
        
        self.configure(padding=theme.card_padding)

        # Header sempre usa pack dentro do próprio card
        if title:
            title_label = ttk.Label(self, text=title, style='Heading.TLabel')
            title_label.pack(anchor='w', pady=(0, theme.spacing_lg))

        # Área de conteúdo isolada para permitir grid interno sem conflitar com pack
        self.content = ttk.Frame(self, style='Card.TFrame')
        self.content.pack(fill='both', expand=True)


class KPICard(ttk.Frame):
    """Card de KPI com número grande e label usando Material Symbols"""
    
    def __init__(self, parent, label_text, value="0", icon=None, **kwargs):
        super().__init__(parent, style='Card.TFrame', **kwargs)
        
        self.configure(padding=theme.card_padding)
        
        # Container interno
        container = ttk.Frame(self, style='Card.TFrame')
        container.pack(fill='both', expand=True)
        
        # Ícone com Material Symbols
        if icon:
            icon_char = get_icon(icon)
            icon_color = get_icon_color(icon)
            icon_label = ttk.Label(container, text=icon_char, 
                                 foreground=icon_color,
                                 font=(theme.font_family[0], theme.font_size_large))
            icon_label.pack(anchor='w', pady=(0, theme.spacing_sm))
        
        # Label do KPI (texto pequeno)
        self.label = ttk.Label(container, text=label_text.upper(), 
                              style='KPILabel.TLabel')
        self.label.pack(anchor='w', pady=(0, theme.spacing_sm))
        
        # Valor do KPI (número grande)
        self.value_label = ttk.Label(container, text=value, style='KPI.TLabel')
        self.value_label.pack(anchor='w')
    
    def update_value(self, new_value):
        """Atualiza o valor do KPI"""
        self.value_label.configure(text=str(new_value))


class ModernButton(ttk.Button):
    """Botão moderno com diferentes estilos"""
    
    def __init__(self, parent, text, style_type="primary", icon=None, 
                 command=None, **kwargs):
        
        # Adicionar ícone ao texto se fornecido
        if icon:
            display_text = f"{icon}  {text}"
        else:
            display_text = text
        
        # Determinar o estilo
        style_map = {
            "primary": "Primary.TButton",
            "secondary": "Secondary.TButton",
            "success": "Success.TButton",
            "danger": "Danger.TButton",
            "sidebar": "Sidebar.TButton"
        }
        
        button_style = style_map.get(style_type, "Primary.TButton")
        
        super().__init__(parent, text=display_text, style=button_style, 
                        command=command, **kwargs)


class ModernEntry(ttk.Entry):
    """Campo de entrada moderno com placeholder"""
    
    def __init__(self, parent, placeholder=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.placeholder = placeholder
        self.placeholder_active = False
        
        if placeholder:
            self.insert(0, placeholder)
            self.placeholder_active = True
            self.configure(foreground=theme.text_secondary)
            
            self.bind('<FocusIn>', self._on_focus_in)
            self.bind('<FocusOut>', self._on_focus_out)
    
    def _on_focus_in(self, event):
        """Remove placeholder ao focar"""
        if self.placeholder_active:
            self.delete(0, 'end')
            self.configure(foreground=theme.text_primary)
            self.placeholder_active = False
    
    def _on_focus_out(self, event):
        """Restaura placeholder se vazio"""
        if not self.get() and self.placeholder:
            self.insert(0, self.placeholder)
            self.configure(foreground=theme.text_secondary)
            self.placeholder_active = True
    
    def get_value(self):
        """Retorna o valor, ignorando placeholder"""
        if self.placeholder_active:
            return ""
        return self.get()


class ModernCombobox(ttk.Combobox):
    """Combobox moderno"""
    
    def __init__(self, parent, values=None, **kwargs):
        super().__init__(parent, values=values or [], **kwargs)
        
        # Configurar estado readonly por padrão
        self.configure(state='readonly')


class ModernTreeview(ttk.Treeview):
    """Treeview moderno com zebra striping"""
    
    def __init__(self, parent, columns, **kwargs):
        super().__init__(parent, columns=columns, show='tree headings', **kwargs)
        
        # Configurar tags para zebra striping
        self.tag_configure('oddrow', background=theme.bg_primary)
        self.tag_configure('evenrow', background=theme.bg_secondary)
        
        # Configurar colunas
        for col in columns:
            self.heading(col, text=col.upper())
            self.column(col, anchor='w', width=100)
    
    def insert_row(self, values, tags=None):
        """Insere uma linha com zebra striping automático"""
        # Determinar tag baseado no número de linhas
        children = self.get_children()
        row_num = len(children)
        
        if tags is None:
            tags = []
        
        # Adicionar tag de zebra
        zebra_tag = 'evenrow' if row_num % 2 == 0 else 'oddrow'
        tags.append(zebra_tag)
        
        return self.insert('', 'end', values=values, tags=tuple(tags))


class ModernScrollableFrame(ttk.Frame):
    """Frame com scroll moderno"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Canvas para scroll
        self.canvas = tk.Canvas(self, bg=theme.bg_primary, 
                               highlightthickness=0)
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient='vertical', 
                                       command=self.canvas.yview)
        
        # Frame interno
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configurar scroll
        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        )
        
        self.canvas_frame = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor='nw'
        )
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Bind mouse wheel
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        
        # Pack
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scroll"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')


class ModernSidebar(ttk.Frame):
    """Sidebar moderna com navegação"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, style='Sidebar.TFrame', **kwargs)
        
        self.configure(width=theme.sidebar_width)
        
        # Armazenar botões
        self.buttons = {}
        self.active_button = None
        
        # Header da sidebar
        header_frame = ttk.Frame(self, style='Sidebar.TFrame')
        header_frame.pack(fill='x', padx=theme.spacing_lg, 
                         pady=(theme.spacing_xxl, theme.spacing_xl))
        
        # Logo/Título
        title = ttk.Label(header_frame, text="Sistema DAC", 
                         style='Title.TLabel')
        title.pack(anchor='w')
        
        subtitle = ttk.Label(header_frame, text="Digital Analysis Center", 
                           style='Secondary.TLabel')
        subtitle.pack(anchor='w')
        
        # Separador
        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=theme.spacing_lg)
    
    def add_menu_item(self, name, text, icon=None, command=None):
        """Adiciona item ao menu"""
        # Criar botão
        if icon:
            display_text = f"{icon}  {text}"
        else:
            display_text = f"   {text}"
        
        button = ttk.Button(self, text=display_text, style='Sidebar.TButton',
                           command=lambda: self._on_menu_click(name, command))
        button.pack(fill='x', pady=2)
        
        self.buttons[name] = button
        
        return button
    
    def _on_menu_click(self, name, command):
        """Handle menu item click"""
        # Atualizar botão ativo
        if self.active_button and self.active_button != name:
            # Resetar botão anterior
            pass
        
        self.active_button = name
        
        # Executar comando
        if command:
            command()
    
    def set_active(self, name):
        """Define o item ativo"""
        self.active_button = name


class StatusBadge(ttk.Label):
    """Badge de status colorido"""
    
    def __init__(self, parent, text, status_type="info", **kwargs):
        
        # Determinar cores baseado no tipo
        colors = {
            "success": (theme.success_bg, theme.success_light),
            "warning": (theme.warning_bg, theme.warning_light),
            "error": (theme.error_bg, theme.error_light),
            "info": (theme.info_bg, theme.info_light)
        }
        
        bg, fg = colors.get(status_type, colors["info"])
        
        super().__init__(parent, text=f" {text} ", **kwargs)
        self.configure(background=bg, foreground=fg,
                      font=(theme.font_family[0], theme.font_size_small),
                      padding=(theme.spacing_sm, theme.spacing_xs))


class ModernProgressBar(ttk.Progressbar):
    """Barra de progresso moderna"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, mode='determinate', **kwargs)
        
        self.configure(length=300)


class IconLabel(ttk.Label):
    """Label com ícone"""
    
    def __init__(self, parent, text, icon=None, icon_size="normal", **kwargs):
        
        if icon:
            display_text = f"{icon}  {text}"
        else:
            display_text = text
        
        super().__init__(parent, text=display_text, **kwargs)


class ModernTooltip:
    """Tooltip moderno"""
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        widget.bind('<Enter>', self.show_tooltip)
        widget.bind('<Leave>', self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """Mostra tooltip"""
        if self.tooltip_window or not self.text:
            return
        
        x, y, _, _ = self.widget.bbox('insert')
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25
        
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f'+{x}+{y}')
        
        label = tk.Label(tw, text=self.text, justify='left',
                        background=theme.bg_hover_light, 
                        foreground=theme.text_primary,
                        relief='flat', borderwidth=1,
                        font=(theme.font_family[0], theme.font_size_small),
                        padding=theme.spacing_md)
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Esconde tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
