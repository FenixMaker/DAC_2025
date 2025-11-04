# -*- coding: utf-8 -*-
"""
Sistema de Navegação Intuitivo

Este módulo implementa um sistema de navegação lógico e intuitivo
que guia o usuário através das funcionalidades do sistema.
"""

import tkinter as tk
from tkinter import ttk
from .icons import create_icon_label, create_icon_button
from .tooltip_system import HelpSystem

class NavigationManager:
    """
    Gerenciador de navegação que controla o fluxo entre janelas
    """
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.current_section = 'main'
        self.navigation_history = ['main']
        self.breadcrumb_frame = None
        
        # Mapeamento de seções e suas dependências
        self.section_flow = {
            'main': {
                'next_suggested': ['import'],
                'description': 'Tela inicial com visão geral do sistema'
            },
            'import': {
                'next_suggested': ['query', 'reports'],
                'previous': ['main'],
                'description': 'Importação de dados CSV'
            },
            'query': {
                'next_suggested': ['reports'],
                'previous': ['main', 'import'],
                'description': 'Consulta e filtragem de dados'
            },
            'reports': {
                'previous': ['main', 'import', 'query'],
                'description': 'Geração de relatórios e análises'
            },
            'settings': {
                'previous': ['main'],
                'description': 'Configurações do sistema'
            }
        }
    
    def create_breadcrumb_navigation(self, parent):
        """
        Cria navegação breadcrumb para mostrar onde o usuário está
        """
        self.breadcrumb_frame = ttk.Frame(parent, style='Breadcrumb.TFrame')
        self.breadcrumb_frame.pack(fill='x', padx=20, pady=(10, 0))
        
        self.update_breadcrumb()
        
        return self.breadcrumb_frame
    
    def update_breadcrumb(self):
        """
        Atualiza a navegação breadcrumb
        """
        if not self.breadcrumb_frame:
            return
        
        # Limpa breadcrumb atual
        for widget in self.breadcrumb_frame.winfo_children():
            widget.destroy()
        
        # Ícone de casa
        home_btn = create_icon_button(self.breadcrumb_frame, 'home', "",
                                     command=lambda: self.navigate_to('main'))
        home_btn.pack(side='left', padx=(0, 5))
        HelpSystem.create_tooltip(home_btn, custom_text="Voltar à tela inicial")
        
        # Separador e seção atual se não for main
        if self.current_section != 'main':
            sep_label = ttk.Label(self.breadcrumb_frame, text=">",
                                 font=('Segoe UI', 10),
                                 foreground='#7f8c8d')
            sep_label.pack(side='left', padx=5)
            
            current_label = ttk.Label(self.breadcrumb_frame, 
                                     text=self.get_section_title(self.current_section),
                                     font=('Segoe UI', 10, 'bold'),
                                     foreground='#2c3e50')
            current_label.pack(side='left', padx=(5, 0))
    
    def create_navigation_suggestions(self, parent):
        """
        Cria sugestões de próximos passos baseadas na seção atual
        """
        suggestions_frame = ttk.Frame(parent, style='Card.TFrame')
        suggestions_frame.pack(fill='x', padx=20, pady=10)
        suggestions_frame.configure(padding=15)
        
        # Título
        title_frame = ttk.Frame(suggestions_frame, style='Card.TFrame')
        title_frame.pack(fill='x', pady=(0, 10))
        
        icon = create_icon_label(title_frame, 'navigation', size=20)
        icon.pack(side='left', padx=(0, 8))
        
        title_label = ttk.Label(title_frame, text="Próximos Passos Sugeridos",
                               font=('Segoe UI', 12, 'bold'),
                               foreground='#2c3e50')
        title_label.pack(side='left')
        
        # Sugestões baseadas na seção atual
        current_flow = self.section_flow.get(self.current_section, {})
        next_sections = current_flow.get('next_suggested', [])
        
        if next_sections:
            for section in next_sections:
                self.create_suggestion_button(suggestions_frame, section)
        else:
            # Se não há sugestões, mostrar opções gerais
            no_suggestions_label = ttk.Label(suggestions_frame, 
                                           text="Você pode navegar para qualquer seção usando o menu lateral.",
                                           font=('Segoe UI', 10),
                                           foreground='#7f8c8d')
            no_suggestions_label.pack(pady=10)
        
        return suggestions_frame
    
    def create_suggestion_button(self, parent, section):
        """
        Cria um botão de sugestão para uma seção
        """
        btn_frame = ttk.Frame(parent, style='Card.TFrame')
        btn_frame.pack(fill='x', pady=5)
        
        # Ícone da seção
        icon_name = self.get_section_icon(section)
        icon = create_icon_label(btn_frame, icon_name, size=16)
        icon.pack(side='left', padx=(0, 10))
        
        # Botão principal
        btn_text = f"Ir para {self.get_section_title(section)}"
        btn = ttk.Button(btn_frame, text=btn_text,
                        style='Secondary.TButton',
                        command=lambda s=section: self.navigate_to(s))
        btn.pack(side='left', fill='x', expand=True)
        
        # Tooltip com descrição
        description = self.section_flow.get(section, {}).get('description', '')
        HelpSystem.create_tooltip(btn, custom_text=description)
    
    def navigate_to(self, section):
        """
        Navega para uma seção específica
        """
        if section == self.current_section:
            return
        
        # Adiciona à história se não for um retorno
        if not self.navigation_history or self.navigation_history[-1] != section:
            self.navigation_history.append(section)
        
        # Atualiza seção atual
        previous_section = self.current_section
        self.current_section = section
        
        # Chama método de navegação da janela principal
        if hasattr(self.main_window, 'handle_navigation'):
            self.main_window.handle_navigation(section, previous_section)
        
        # Atualiza breadcrumb
        self.update_breadcrumb()
    
    def go_back(self):
        """
        Volta para a seção anterior
        """
        if len(self.navigation_history) > 1:
            self.navigation_history.pop()  # Remove atual
            previous_section = self.navigation_history[-1]
            self.navigate_to(previous_section)
    
    def get_section_title(self, section):
        """
        Retorna o título amigável de uma seção
        """
        titles = {
            'main': 'Início',
            'import': 'Importar Dados',
            'query': 'Consultar Dados',
            'reports': 'Relatórios',
            'settings': 'Configurações'
        }
        return titles.get(section, section.title())
    
    def get_section_icon(self, section):
        """
        Retorna o ícone de uma seção
        """
        icons = {
            'main': 'home',
            'import': 'import',
            'query': 'search',
            'reports': 'reports',
            'settings': 'settings'
        }
        return icons.get(section, 'default')
    
    def create_quick_actions(self, parent):
        """
        Cria ações rápidas baseadas no contexto atual
        """
        actions_frame = ttk.Frame(parent, style='Card.TFrame')
        actions_frame.pack(fill='x', padx=20, pady=10)
        actions_frame.configure(padding=15)
        
        # Título
        title_label = ttk.Label(actions_frame, text="⚡ Ações Rápidas",
                               font=('Segoe UI', 12, 'bold'),
                               foreground='#2c3e50')
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Ações baseadas na seção atual
        actions = self.get_contextual_actions()
        
        for action in actions:
            action_btn = ttk.Button(actions_frame, 
                                   text=action['text'],
                                   style='Primary.TButton',
                                   command=action['command'])
            action_btn.pack(fill='x', pady=2)
            
            if 'tooltip' in action:
                HelpSystem.create_tooltip(action_btn, custom_text=action['tooltip'])
        
        return actions_frame
    
    def get_contextual_actions(self):
        """
        Retorna ações contextuais baseadas na seção atual
        """
        actions = {
            'main': [
                {
                    'text': '📥 Importar Novos Dados',
                    'command': lambda: self.navigate_to('import'),
                    'tooltip': 'Começar importando seus dados CSV'
                },
                {
                    'text': '🔍 Consultar Dados Existentes',
                    'command': lambda: self.navigate_to('query'),
                    'tooltip': 'Explorar dados já importados'
                }
            ],
            'import': [
                {
                    'text': '🔍 Consultar Dados Importados',
                    'command': lambda: self.navigate_to('query'),
                    'tooltip': 'Ver os dados que foram importados'
                }
            ],
            'query': [
                {
                    'text': '📊 Gerar Relatório dos Resultados',
                    'command': lambda: self.navigate_to('reports'),
                    'tooltip': 'Criar relatório com os dados filtrados'
                }
            ],
            'reports': [
                {
                    'text': '🔍 Voltar às Consultas',
                    'command': lambda: self.navigate_to('query'),
                    'tooltip': 'Refinar filtros para novo relatório'
                }
            ]
        }
        
        return actions.get(self.current_section, [])

class ProgressIndicator:
    """
    Indicador de progresso do fluxo de trabalho
    """
    
    def __init__(self, parent):
        self.parent = parent
        self.steps = [
            ('import', 'Importar'),
            ('query', 'Consultar'),
            ('reports', 'Relatórios')
        ]
        self.current_step = 0
        self.progress_frame = None
    
    def create_progress_indicator(self):
        """
        Cria indicador visual de progresso
        """
        self.progress_frame = ttk.Frame(self.parent, style='Card.TFrame')
        self.progress_frame.pack(fill='x', padx=20, pady=10)
        self.progress_frame.configure(padding=15)
        
        # Título
        title_label = ttk.Label(self.progress_frame, text="📈 Progresso do Fluxo",
                               font=('Segoe UI', 12, 'bold'),
                               foreground='#2c3e50')
        title_label.pack(anchor='w', pady=(0, 15))
        
        # Container dos passos
        steps_frame = ttk.Frame(self.progress_frame, style='Card.TFrame')
        steps_frame.pack(fill='x')
        
        for i, (step_id, step_name) in enumerate(self.steps):
            # Frame do passo
            step_frame = ttk.Frame(steps_frame, style='Card.TFrame')
            step_frame.pack(side='left', fill='x', expand=True)
            
            # Círculo do passo
            circle_color = '#3498db' if i <= self.current_step else '#bdc3c7'
            circle_text = '✓' if i < self.current_step else str(i + 1)
            
            circle_label = ttk.Label(step_frame, text=circle_text,
                                    font=('Segoe UI', 12, 'bold'),
                                    foreground='white',
                                    background=circle_color,
                                    width=3)
            circle_label.pack(pady=(0, 5))
            
            # Nome do passo
            name_label = ttk.Label(step_frame, text=step_name,
                                  font=('Segoe UI', 9),
                                  foreground='#2c3e50')
            name_label.pack()
            
            # Linha conectora (exceto no último)
            if i < len(self.steps) - 1:
                line_color = '#3498db' if i < self.current_step else '#bdc3c7'
                line_frame = ttk.Frame(steps_frame, style='Card.TFrame')
                line_frame.pack(side='left', fill='x', expand=True)
                
                line_label = ttk.Label(line_frame, text="───",
                                      foreground=line_color)
                line_label.pack(pady=15)
        
        return self.progress_frame
    
    def update_progress(self, current_section):
        """
        Atualiza o indicador de progresso
        """
        step_mapping = {'import': 0, 'query': 1, 'reports': 2}
        if current_section in step_mapping:
            self.current_step = step_mapping[current_section]
            if self.progress_frame:
                # Recria o indicador
                self.progress_frame.destroy()
                self.create_progress_indicator()