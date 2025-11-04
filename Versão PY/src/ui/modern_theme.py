"""
Sistema DAC - Modern Dark Theme
Tema moderno profissional inspirado em Power BI, Stripe e VS Code
"""

class ModernDarkTheme:
    """
    Paleta de cores e configurações do tema moderno escuro
    Inspirado em: Power BI, Stripe Dashboard, Metabase, VS Code
    """
    
    # ===== CORES DE FUNDO =====
    # Plano de fundo principal (root)
    bg_root = "#0D1117"
    
    # Plano de fundo de conteúdo (cards, sidebar, modais)
    bg_primary = "#161B22"
    bg_secondary = "#1E1E1E"
    
    # Hover states
    bg_hover = "#21262D"
    bg_hover_light = "#30363D"
    
    # ===== BORDAS E SEPARADORES =====
    border = "#30363D"
    border_light = "#3D444D"
    
    # ===== CORES DE DESTAQUE =====
    # Cor primária (accent) - Roxo moderno profissional
    accent_primary = "#8B5CF6"
    accent_hover = "#A78BFA"
    accent_light = "#C4B5FD"
    accent_dark = "#7C3AED"
    
    # Alternativa verde (para opção)
    accent_green = "#39D353"
    accent_green_hover = "#4ADE66"
    
    # ===== CORES DE TEXTO =====
    # Texto principal (títulos, dados)
    text_primary = "#F0F6FC"
    
    # Texto secundário (rótulos, descrições)
    text_secondary = "#8D96A0"
    
    # Texto sobre cor de destaque
    text_on_accent = "#FFFFFF"
    
    # Texto desabilitado
    text_disabled = "#6E7681"
    
    # ===== CORES SEMÂNTICAS =====
    success = "#238636"
    success_light = "#2EA043"
    success_bg = "#0D1E15"
    
    warning = "#B69100"
    warning_light = "#E5B800"
    warning_bg = "#1F1A0D"
    
    error = "#DA3633"
    error_light = "#F85149"
    error_bg = "#1E0D0D"
    
    info = "#388BFD"
    info_light = "#58A6FF"
    info_bg = "#0D1A2E"
    
    # ===== TIPOGRAFIA =====
    # Fontes (prioridade de fallback)
    font_family = ("Segoe UI", "Inter", "Roboto", "Arial", "sans-serif")
    font_family_mono = ("Consolas", "Monaco", "Courier New", "monospace")
    
    # Tamanhos de fonte
    font_size_tiny = 10
    font_size_small = 11
    font_size_normal = 13
    font_size_medium = 14
    font_size_large = 16
    font_size_xlarge = 20
    font_size_title = 24
    font_size_kpi = 36
    font_size_kpi_large = 48
    
    # Pesos de fonte
    font_weight_normal = "normal"
    font_weight_medium = "bold"  # Tkinter não tem medium, usamos bold
    font_weight_bold = "bold"
    
    # ===== ESPAÇAMENTO =====
    # Padding e margin padrões
    spacing_xs = 4
    spacing_sm = 8
    spacing_md = 12
    spacing_lg = 16
    spacing_xl = 20
    spacing_xxl = 24
    spacing_xxxl = 32
    
    # ===== DIMENSÕES =====
    # Sidebar
    sidebar_width = 240
    sidebar_button_height = 48
    
    # Botões
    button_height = 36
    button_height_large = 44
    button_padding_x = 20
    button_padding_y = 10
    
    # Cards
    card_padding = 20
    card_margin = 10
    card_border_radius = 8
    
    # Inputs
    input_height = 36
    input_padding = 12
    
    # ===== ÍCONES =====
    # Configurações de ícones (usando caracteres Unicode como fallback)
    icons = {
        # Navegação
        'dashboard': '■',  # Será substituído por ícone real
        'import': '↑',
        'search': '⌕',
        'reports': '▤',
        'settings': '⚙',
        'refresh': '↻',
        
        # Ações
        'add': '+',
        'remove': '−',
        'edit': '✎',
        'delete': '🗑',
        'save': '✓',
        'cancel': '✕',
        'close': '✕',
        
        # Status
        'success': '✓',
        'error': '✕',
        'warning': '⚠',
        'info': 'ℹ',
        
        # Arquivos
        'file': '📄',
        'folder': '📁',
        'upload': '↑',
        'download': '↓',
        
        # Navegação (setas)
        'chevron_right': '›',
        'chevron_left': '‹',
        'chevron_up': '⌃',
        'chevron_down': '⌄',
        
        # Filtros
        'filter': '⊶',
        'clear_filter': '✕',
    }
    
    # ===== SOMBRAS (Para efeito visual) =====
    # Tkinter não suporta sombras nativamente, mas podemos simular com bordas
    shadow_color = "#000000"
    shadow_alpha = 0.2
    
    # ===== ANIMAÇÕES =====
    # Durações de transição (em ms)
    transition_fast = 100
    transition_normal = 200
    transition_slow = 300
    
    # ===== MÉTODOS AUXILIARES =====
    
    @classmethod
    def get_button_style(cls, style_type="primary"):
        """Retorna configurações de estilo para botões"""
        styles = {
            "primary": {
                "background": cls.accent_primary,
                "foreground": cls.text_on_accent,
                "borderwidth": 0,
                "relief": "flat",
                "padding": (cls.button_padding_x, cls.button_padding_y),
                "font": (cls.font_family[0], cls.font_size_medium, cls.font_weight_medium)
            },
            "secondary": {
                "background": "transparent",
                "foreground": cls.text_primary,
                "borderwidth": 1,
                "bordercolor": cls.border,
                "relief": "flat",
                "padding": (cls.button_padding_x, cls.button_padding_y),
                "font": (cls.font_family[0], cls.font_size_medium)
            },
            "sidebar": {
                "background": cls.bg_primary,
                "foreground": cls.text_secondary,
                "borderwidth": 0,
                "relief": "flat",
                "padding": (cls.spacing_lg, cls.spacing_md),
                "font": (cls.font_family[0], cls.font_size_medium),
                "anchor": "w"
            },
            "danger": {
                "background": cls.error,
                "foreground": cls.text_on_accent,
                "borderwidth": 0,
                "relief": "flat",
                "padding": (cls.button_padding_x, cls.button_padding_y),
                "font": (cls.font_family[0], cls.font_size_medium, cls.font_weight_medium)
            },
            "success": {
                "background": cls.success,
                "foreground": cls.text_on_accent,
                "borderwidth": 0,
                "relief": "flat",
                "padding": (cls.button_padding_x, cls.button_padding_y),
                "font": (cls.font_family[0], cls.font_size_medium, cls.font_weight_medium)
            }
        }
        return styles.get(style_type, styles["primary"])
    
    @classmethod
    def get_card_style(cls):
        """Retorna configurações de estilo para cards"""
        return {
            "background": cls.bg_secondary,
            "borderwidth": 1,
            "relief": "flat",
            "bordercolor": cls.border,
            "padding": cls.card_padding
        }
    
    @classmethod
    def get_input_style(cls):
        """Retorna configurações de estilo para inputs"""
        return {
            "background": cls.bg_primary,
            "foreground": cls.text_primary,
            "borderwidth": 1,
            "bordercolor": cls.border,
            "relief": "flat",
            "insertbackground": cls.text_primary,
            "selectbackground": cls.accent_primary,
            "selectforeground": cls.text_on_accent,
            "font": (cls.font_family[0], cls.font_size_normal)
        }
    
    @classmethod
    def get_label_style(cls, style_type="primary"):
        """Retorna configurações de estilo para labels"""
        styles = {
            "primary": {
                "foreground": cls.text_primary,
                "background": cls.bg_primary,
                "font": (cls.font_family[0], cls.font_size_normal)
            },
            "secondary": {
                "foreground": cls.text_secondary,
                "background": cls.bg_primary,
                "font": (cls.font_family[0], cls.font_size_small)
            },
            "title": {
                "foreground": cls.text_primary,
                "background": cls.bg_primary,
                "font": (cls.font_family[0], cls.font_size_xlarge, cls.font_weight_bold)
            },
            "heading": {
                "foreground": cls.text_primary,
                "background": cls.bg_primary,
                "font": (cls.font_family[0], cls.font_size_large, cls.font_weight_medium)
            },
            "kpi": {
                "foreground": cls.text_primary,
                "background": cls.bg_secondary,
                "font": (cls.font_family[0], cls.font_size_kpi, cls.font_weight_medium)
            },
            "kpi_label": {
                "foreground": cls.text_secondary,
                "background": cls.bg_secondary,
                "font": (cls.font_family[0], cls.font_size_small)
            }
        }
        return styles.get(style_type, styles["primary"])


# Instância global do tema
theme = ModernDarkTheme()
