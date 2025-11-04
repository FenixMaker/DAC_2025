# -*- coding: utf-8 -*-
"""
Sistema de Tooltips e Instruções Contextuais

Este módulo fornece um sistema abrangente de tooltips e instruções
para melhorar a usabilidade e acessibilidade da interface.
"""

import tkinter as tk
from tkinter import ttk

class ToolTip:
    """
    Classe para criar tooltips informativos e acessíveis
    """
    
    def __init__(self, widget, text='Widget info', delay=500, wraplength=250):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.wraplength = wraplength
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        
        # Bind eventos
        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.leave)
        self.widget.bind('<ButtonPress>', self.leave)
    
    def enter(self, event=None):
        """Inicia o timer para mostrar o tooltip"""
        self.schedule()
    
    def leave(self, event=None):
        """Esconde o tooltip e cancela o timer"""
        self.unschedule()
        self.hidetip()
    
    def schedule(self):
        """Agenda a exibição do tooltip"""
        self.unschedule()
        self.id = self.widget.after(self.delay, self.showtip)
    
    def unschedule(self):
        """Cancela a exibição agendada do tooltip"""
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)
    
    def showtip(self, event=None):
        """Exibe o tooltip"""
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        # Cria a janela do tooltip
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        
        # Estilo do tooltip
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("Segoe UI", "9", "normal"),
                        wraplength=self.wraplength,
                        padx=8, pady=6)
        label.pack(ipadx=1)
    
    def hidetip(self):
        """Esconde o tooltip"""
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

class InstructionPanel:
    """
    Painel de instruções contextuais que aparece em diferentes seções
    """
    
    def __init__(self, parent, instructions):
        self.parent = parent
        self.instructions = instructions
        self.panel = None
        self.is_visible = False
    
    def create_panel(self):
        """Cria o painel de instruções"""
        self.panel = ttk.Frame(self.parent, style='Instruction.TFrame')
        
        # Título
        title_frame = ttk.Frame(self.panel)
        title_frame.pack(fill='x', pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="💡 Instruções",
                               font=('Segoe UI', 12, 'bold'),
                               foreground='#2c3e50')
        title_label.pack(side='left')
        
        # Botão para fechar
        close_btn = ttk.Button(title_frame, text="✕", width=3,
                              command=self.hide_panel)
        close_btn.pack(side='right')
        
        # Lista de instruções
        for i, instruction in enumerate(self.instructions, 1):
            inst_frame = ttk.Frame(self.panel)
            inst_frame.pack(fill='x', pady=2)
            
            # Número da instrução
            num_label = ttk.Label(inst_frame, text=f"{i}.",
                                 font=('Segoe UI', 10, 'bold'),
                                 foreground='#3498db')
            num_label.pack(side='left', padx=(0, 8))
            
            # Texto da instrução
            text_label = ttk.Label(inst_frame, text=instruction,
                                  font=('Segoe UI', 10),
                                  foreground='#34495e',
                                  wraplength=300)
            text_label.pack(side='left', fill='x', expand=True)
    
    def show_panel(self):
        """Mostra o painel de instruções"""
        if not self.panel:
            self.create_panel()
        
        if not self.is_visible:
            self.panel.pack(fill='x', pady=10, padx=10)
            self.is_visible = True
    
    def hide_panel(self):
        """Esconde o painel de instruções"""
        if self.panel and self.is_visible:
            self.panel.pack_forget()
            self.is_visible = False
    
    def toggle_panel(self):
        """Alterna a visibilidade do painel"""
        if self.is_visible:
            self.hide_panel()
        else:
            self.show_panel()

class HelpSystem:
    """
    Sistema centralizado de ajuda e instruções
    """
    
    # Dicionário com instruções para cada seção
    INSTRUCTIONS = {
        'main': [
            "Bem-vindo ao Sistema de Análise de Dados!",
            "Use a barra lateral para navegar entre as funcionalidades",
            "Comece importando seus dados CSV na seção 'Importar Dados'",
            "Explore os dados usando filtros na seção 'Consultar Dados'",
            "Gere relatórios personalizados na seção 'Relatórios'"
        ],
        'import': [
            "Selecione um ou mais arquivos CSV para importar",
            "Verifique se os arquivos seguem o formato esperado",
            "Configure as opções de importação conforme necessário",
            "Clique em 'Iniciar Importação' para processar os dados",
            "Acompanhe o progresso na barra de status"
        ],
        'query': [
            "Use os filtros para refinar sua busca",
            "Combine múltiplos critérios para resultados precisos",
            "Visualize os resultados na tabela abaixo",
            "Exporte os dados filtrados se necessário",
            "Salve consultas frequentes para uso futuro"
        ],
        'reports': [
            "Escolha o tipo de relatório desejado",
            "Configure os parâmetros e filtros",
            "Selecione o formato de saída (PDF, Excel, etc.)",
            "Visualize uma prévia antes de gerar",
            "Salve ou compartilhe o relatório gerado"
        ]
    }
    
    # Tooltips para componentes comuns
    TOOLTIPS = {
        'import_btn': "Importar novos dados CSV para o sistema",
        'query_btn': "Consultar e filtrar dados existentes",
        'reports_btn': "Gerar relatórios e análises personalizadas",
        'settings_btn': "Configurar preferências do sistema",
        'help_btn': "Acessar ajuda e documentação",
        'refresh_btn': "Atualizar dados e estatísticas",
        'export_btn': "Exportar dados para arquivo",
        'clear_btn': "Limpar filtros e formulários",
        'save_btn': "Salvar configurações ou dados",
        'cancel_btn': "Cancelar operação atual"
    }
    
    @classmethod
    def create_tooltip(cls, widget, tooltip_key=None, custom_text=None):
        """Cria um tooltip para um widget"""
        if custom_text:
            text = custom_text
        elif tooltip_key and tooltip_key in cls.TOOLTIPS:
            text = cls.TOOLTIPS[tooltip_key]
        else:
            text = "Informação não disponível"
        
        return ToolTip(widget, text)
    
    @classmethod
    def create_instruction_panel(cls, parent, section_key):
        """Cria um painel de instruções para uma seção"""
        instructions = cls.INSTRUCTIONS.get(section_key, [])
        return InstructionPanel(parent, instructions)
    
    @classmethod
    def add_help_button(cls, parent, section_key, **button_kwargs):
        """Adiciona um botão de ajuda que mostra instruções"""
        instruction_panel = cls.create_instruction_panel(parent, section_key)
        
        help_btn = ttk.Button(parent, text="❓ Ajuda",
                             command=instruction_panel.toggle_panel,
                             **button_kwargs)
        
        cls.create_tooltip(help_btn, custom_text="Clique para ver instruções detalhadas")
        
        return help_btn, instruction_panel

def create_enhanced_tooltip(widget, text, delay=500):
    """Função auxiliar para criar tooltips aprimorados"""
    return ToolTip(widget, text, delay)

def add_contextual_help(parent, section):
    """Adiciona sistema de ajuda contextual a uma seção"""
    return HelpSystem.add_help_button(parent, section)