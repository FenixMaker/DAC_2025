# -*- coding: utf-8 -*-
"""
Janela de consulta e filtragem de dados
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from typing import Dict, List, Optional

from ..utils.logger import get_logger
from ..database.models import Region, Household, Individual, DeviceUsage, InternetUsage
from .icons import get_icon, get_icon_color
from .modern_components import ModernScrollableFrame

class QueryWindow:
    """Janela para consulta e filtragem de dados"""
    
    def __init__(self, master, db_manager):
        """Inicializa a janela de consulta com recursos avançados"""
        self.master = master
        self.db_manager = db_manager
        self.current_results = []
        self.total_records = 0
        self.current_page = 1
        self.records_per_page = 100
        self.total_pages = 1
        
        # Configurar logging
        self.logger = get_logger(__name__)
        
        # Criar janela com Material Symbol
        self.window = tk.Toplevel(master)
        search_icon = get_icon('search')
        self.window.title(f"{search_icon} Consulta e Filtragem de Dados - DAC")
        # Tamanho compacto e adequado
        self.window.geometry("1050x680")
        self.window.resizable(False, False)
        
        # Aplicar tema escuro
        self.window.configure(bg='#0D1117')
        self.setup_dark_theme()
        
        # Configurar protocolo de fechamento
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Centralizar janela
        # Centralizar janela após ajustar geometry
        self.center_window()
        
        # Criar widgets
        self.create_widgets()
        
        # Carregar opções de filtro
        self.load_filter_options()
        
        # Configurar atalhos de teclado
        self.setup_keyboard_shortcuts()
    
    def setup_dark_theme(self):
        """Configurar tema escuro para a janela de consulta"""
        style = ttk.Style()
        
        # Cores do tema escuro
        colors = {
            'bg_primary': '#0D1117',
            'bg_secondary': '#161B22', 
            'bg_card': '#21262D',
            'bg_hover': '#30363D',
            'text_primary': '#F0F6FC',
            'text_secondary': '#8B949E',
            'accent_blue': '#238CF5',
            'accent_green': '#34D399',
            'border': '#30363D'
        }
        
        # Configurar estilos TTK para consulta
        style.configure('Query.TFrame',
                       background=colors['bg_primary'])
        
        style.configure('Query.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['text_primary'],
                       font=('Segoe UI', 10))
        
        style.configure('Query.Title.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['text_primary'],
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Query.TButton',
                       background=colors['accent_blue'],
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'),
                       padding=(15, 8),
                       relief='flat',
                       borderwidth=0)
        
        style.map('Query.TButton',
                 background=[('active', colors['bg_hover']),
                           ('pressed', colors['accent_green'])])
        
        style.configure('Query.TCombobox',
                       background=colors['bg_card'],
                       foreground=colors['text_primary'],
                       fieldbackground=colors['bg_card'],
                       borderwidth=1,
                       lightcolor=colors['border'],
                       darkcolor=colors['border'])
        
        style.configure('Query.TEntry',
                       background=colors['bg_card'],
                       foreground=colors['text_primary'],
                       fieldbackground=colors['bg_card'],
                       borderwidth=1,
                       lightcolor=colors['border'],
                       darkcolor=colors['border'])
        
        style.configure('Query.Treeview',
                       background=colors['bg_card'],
                       foreground=colors['text_primary'],
                       fieldbackground=colors['bg_card'],
                       borderwidth=0,
                       font=('Segoe UI', 10))
        
        style.configure('Query.Treeview.Heading',
                       background=colors['bg_secondary'],
                       foreground=colors['text_primary'],
                       font=('Segoe UI', 11, 'bold'))
        
        style.configure('Query.TLabelFrame',
                       background=colors['bg_primary'],
                       relief='solid',
                       borderwidth=1,
                       lightcolor=colors['border'],
                       darkcolor=colors['border'])
        
        style.configure('Query.TLabelFrame.Label',
                       background=colors['bg_primary'],
                       foreground=colors['text_primary'],
                       font=('Segoe UI', 12, 'bold'))
        
        # Estilos para scrollbars
        style.configure('Query.Vertical.TScrollbar',
                       background=colors['bg_card'],  # Cor mais clara para melhor visibilidade
                       troughcolor=colors['bg_primary'],
                       bordercolor=colors['border'],
                       arrowcolor=colors['text_primary'],  # Cor mais clara para as setas
                       darkcolor=colors['bg_card'],
                       lightcolor=colors['bg_card'],
                       width=20)  # Aumentar largura da scrollbar vertical para 20px (mais espessa)
        
        style.configure('Query.Horizontal.TScrollbar',
                       background=colors['bg_card'],  # Cor mais clara para melhor visibilidade
                       troughcolor=colors['bg_primary'],
                       bordercolor=colors['border'],
                       arrowcolor=colors['text_primary'],  # Cor mais clara para as setas
                       darkcolor=colors['bg_card'],
                       lightcolor=colors['bg_card'],
                       width=16)  # Aumentar altura da scrollbar horizontal
        
        # Adicionar estilos de hover para melhor interatividade
        style.map('Query.Vertical.TScrollbar',
                 background=[('active', colors['bg_hover']),
                           ('pressed', colors['accent_blue'])],
                 arrowcolor=[('active', colors['text_primary']),
                           ('pressed', colors['accent_green'])],
                 darkcolor=[('active', colors['bg_hover'])],
                 lightcolor=[('active', colors['bg_hover'])])
        
        style.map('Query.Horizontal.TScrollbar',
                 background=[('active', colors['bg_hover']),
                           ('pressed', colors['accent_blue'])],
                 arrowcolor=[('active', colors['text_primary']),
                           ('pressed', colors['accent_green'])],
                 darkcolor=[('active', colors['bg_hover'])],
                 lightcolor=[('active', colors['bg_hover'])])
    
    def load_filter_options(self):
        """Carrega as opções disponíveis para os filtros com tratamento robusto de erros"""
        try:
            # Verificar se o database manager está disponível
            if not self.db_manager:
                raise ValueError("Gerenciador de banco de dados não disponível")
            
            # Carregar regiões únicas do banco de dados
            with self.db_manager.get_session() as session:
                try:
                    regions = session.query(Region.name).distinct().filter(Region.name.isnot(None)).all()
                    region_values = ['Todas'] + [r[0] for r in regions if r[0] and r[0].strip()]
                    
                    if not region_values or len(region_values) == 1:  # Apenas 'Todas'
                        self.logger.warning("Nenhuma região encontrada no banco de dados")
                        region_values = ['Todas', 'Sem dados']
                    
                    self.region_combo['values'] = region_values
                    self.region_combo.set('Todas')
                    
                except Exception as e:
                    self.logger.error(f"Erro ao carregar regiões: {e}")
                    self.region_combo['values'] = ['Todas', 'Erro ao carregar']
                    self.region_combo.set('Todas')
                
                try:
                    # Carregar faixas de renda únicas
                    incomes = session.query(Household.income_range).distinct().filter(Household.income_range.isnot(None)).all()
                    income_values = ['Todas'] + [i[0] for i in incomes if i[0] and i[0].strip()]
                    
                    if not income_values or len(income_values) == 1:  # Apenas 'Todas'
                        self.logger.warning("Nenhuma faixa de renda encontrada no banco de dados")
                        income_values = ['Todas', 'Sem dados']
                    
                    self.income_combo['values'] = income_values
                    self.income_combo.set('Todas')
                    
                except Exception as e:
                    self.logger.error(f"Erro ao carregar faixas de renda: {e}")
                    self.income_combo['values'] = ['Todas', 'Erro ao carregar']
                    self.income_combo.set('Todas')
                
        except ValueError as e:
            self.logger.error(f"Erro de validação: {e}")
            messagebox.showerror("Erro de Validação", str(e))
            # Definir valores padrão
            self.region_combo['values'] = ['Todas']
            self.region_combo.set('Todas')
            self.income_combo['values'] = ['Todas']
            self.income_combo.set('Todas')
            
        except Exception as e:
            self.logger.error(f"Erro crítico ao carregar opções de filtro: {e}")
            messagebox.showerror("Erro Crítico", f"Erro ao carregar opções de filtro: {e}\n\nVerifique a conexão com o banco de dados.")
            # Definir valores padrão para evitar crash
            self.region_combo['values'] = ['Todas']
            self.region_combo.set('Todas')
            self.income_combo['values'] = ['Todas']
            self.income_combo.set('Todas')
    
    def apply_filters(self, page=1):
        """Aplica os filtros selecionados e exibe os resultados com paginação"""
        try:
            # Verificar se o database manager está disponível
            if not self.db_manager:
                raise ValueError("Gerenciador de banco de dados não disponível")
            
            # Validar filtros de idade antes de aplicar
            min_age = None
            max_age = None
            
            if self.age_min_var.get().strip():
                try:
                    min_age = int(self.age_min_var.get().strip())
                    if min_age < 0 or min_age > 150:
                        raise ValueError("Idade mínima deve estar entre 0 e 150 anos")
                except ValueError as e:
                    if "invalid literal" in str(e):
                        messagebox.showwarning("Aviso", "Idade mínima deve ser um número válido")
                    else:
                        messagebox.showwarning("Aviso", str(e))
                    return
            
            if self.age_max_var.get().strip():
                try:
                    max_age = int(self.age_max_var.get().strip())
                    if max_age < 0 or max_age > 150:
                        raise ValueError("Idade máxima deve estar entre 0 e 150 anos")
                except ValueError as e:
                    if "invalid literal" in str(e):
                        messagebox.showwarning("Aviso", "Idade máxima deve ser um número válido")
                    else:
                        messagebox.showwarning("Aviso", str(e))
                    return
            
            # Validar se idade mínima não é maior que máxima
            if min_age is not None and max_age is not None and min_age > max_age:
                messagebox.showwarning("Aviso", "Idade mínima não pode ser maior que a idade máxima")
                return
            
            # Atualizar página atual
            self.current_page = page
            
            with self.db_manager.get_session() as session:
                try:
                    # Construir consulta base com joins seguros
                    query = session.query(Individual).join(Household, Individual.household_id == Household.id).join(Region, Household.region_id == Region.id)
                    
                    # Aplicar filtro de região
                    region_filter = self.region_var.get()
                    if region_filter and region_filter not in ['Todas', 'Sem dados', 'Erro ao carregar']:
                        query = query.filter(Region.name == region_filter)
                    
                    # Aplicar filtros de idade
                    if min_age is not None:
                        query = query.filter(Individual.age >= min_age)
                    
                    if max_age is not None:
                        query = query.filter(Individual.age <= max_age)
                    
                    # Aplicar filtro de gênero
                    gender_filter = self.gender_var.get()
                    if gender_filter and gender_filter != 'Todos':
                        query = query.filter(Individual.gender == gender_filter)
                    
                    # Aplicar filtro de renda
                    income_filter = self.income_var.get()
                    if income_filter and income_filter not in ['Todas', 'Sem dados', 'Erro ao carregar']:
                        query = query.filter(Household.income_range == income_filter)
                    
                    # Aplicar filtro de deficiência
                    disability_filter = self.disability_var.get()
                    if disability_filter and disability_filter != 'Todos':
                        has_disability = disability_filter == 'Sim'
                        query = query.filter(Individual.has_disability == has_disability)
                    
                    # Aplicar filtro de internet
                    internet_filter = self.internet_var.get()
                    if internet_filter and internet_filter != 'Todos':
                        has_internet = internet_filter == 'Sim'
                        query = query.filter(Household.has_internet == has_internet)
                    
                    # Contar total de registros
                    self.total_records = query.count()
                    self.total_pages = max(1, (self.total_records + self.records_per_page - 1) // self.records_per_page)
                    
                    # Aplicar paginação
                    offset = (self.current_page - 1) * self.records_per_page
                    results = query.offset(offset).limit(self.records_per_page).all()
                    
                    self.current_results = results
                    
                    # Limpar resultados anteriores
                    for item in self.results_tree.get_children():
                        self.results_tree.delete(item)
                    
                    # Inserir novos resultados com tratamento de erros
                    success_count = 0
                    error_count = 0
                    
                    for individual in results:
                        try:
                            # Acessar dados com segurança
                            region_name = 'N/A'
                            if individual.household and individual.household.region:
                                region_name = individual.household.region.name or 'N/A'
                            
                            devices = 'Nenhum'
                            if individual.device_usage:
                                device_list = [d.device_type for d in individual.device_usage if d.device_type]
                                devices = ', '.join(device_list) if device_list else 'Nenhum'
                            
                            income_range = 'N/A'
                            if individual.household:
                                income_range = individual.household.income_range or 'N/A'
                            
                            has_internet = 'N/A'
                            if individual.household:
                                has_internet = 'Sim' if individual.household.has_internet else 'Não'
                            
                            self.results_tree.insert('', 'end', values=(
                                individual.id or 'N/A',
                                region_name,
                                individual.age or 'N/A',
                                individual.gender or 'N/A',
                                income_range,
                                'Sim' if individual.has_disability else 'Não',
                                has_internet,
                                devices
                            ))
                            success_count += 1
                            
                        except Exception as e:
                            self.logger.error(f"Erro ao processar registro individual {individual.id}: {e}")
                            error_count += 1
                    
                    # Atualizar informações dos resultados
                    result_text = f"Página {self.current_page} de {self.total_pages} - "
                    result_text += f"Exibindo {len(results)} de {self.total_records} registros"
                    if error_count > 0:
                        result_text += f" ({error_count} com problemas)"
                    self.results_info_label.config(text=result_text)
                    
                    # Atualizar botões de paginação
                    self.update_pagination_buttons()
                    
                    self.logger.info(f"Consulta executada: página {self.current_page}, {success_count} registros exibidos, {error_count} com problemas")
                    
                except Exception as e:
                    self.logger.error(f"Erro na execução da consulta: {e}")
                    messagebox.showerror("Erro na Consulta", f"Erro ao executar consulta no banco de dados: {e}")
                    
        except ValueError as e:
            self.logger.error(f"Erro de validação: {e}")
            messagebox.showerror("Erro de Validação", str(e))
            
        except Exception as e:
            self.logger.error(f"Erro crítico ao aplicar filtros: {e}")
            messagebox.showerror("Erro Crítico", f"Erro crítico ao aplicar filtros: {e}\n\nVerifique a conexão com o banco de dados.")
    
    def clear_filters(self):
        """Limpa todos os filtros"""
        self.region_var.set('Todas')
        self.age_min_var.set('')
        self.age_max_var.set('')
        self.gender_var.set('Todos')
        self.income_var.set('Todas')
        self.disability_var.set('Todos')
        self.internet_var.set('Todos')
        
        # Limpar resultados
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.results_info_label.config(text="Nenhuma consulta realizada")
        self.current_results = []
    
    def export_results(self):
        """Exporta os resultados filtrados para CSV com validação robusta"""
        try:
            # Verificar se há resultados para exportar
            if not hasattr(self, 'current_results') or not self.current_results:
                messagebox.showwarning("Aviso", "Nenhum resultado para exportar. Execute uma consulta primeiro.")
                return
            
            # Verificar se a lista de resultados não está vazia
            if len(self.current_results) == 0:
                messagebox.showwarning("Aviso", "A consulta não retornou resultados para exportar.")
                return
            
            # Solicitar local para salvar o arquivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Salvar resultados como..."
            )
            
            if not filename:
                return  # Usuário cancelou
            
            # Validar se o diretório de destino existe e é acessível
            import os
            directory = os.path.dirname(filename)
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("Erro", f"Não foi possível criar o diretório: {e}")
                    return
            
            if not os.access(directory, os.W_OK):
                messagebox.showerror("Erro", "Sem permissão de escrita no diretório selecionado.")
                return
            
            try:
                # Converter resultados para DataFrame com tratamento de erros
                data = []
                success_count = 0
                error_count = 0
                
                for individual in self.current_results:
                    try:
                        # Acessar dados com segurança
                        region_name = 'N/A'
                        if individual.household and individual.household.region:
                            region_name = individual.household.region.name or 'N/A'
                        
                        devices = 'Nenhum'
                        if individual.device_usage:
                            device_list = [d.device_type for d in individual.device_usage if d.device_type]
                            devices = ', '.join(device_list) if device_list else 'Nenhum'
                        
                        income_range = 'N/A'
                        if individual.household:
                            income_range = individual.household.income_range or 'N/A'
                        
                        has_internet = 'N/A'
                        if individual.household:
                            has_internet = 'Sim' if individual.household.has_internet else 'Não'
                        
                        data.append({
                            'ID': individual.id or 'N/A',
                            'Região': region_name,
                            'Idade': individual.age or 'N/A',
                            'Gênero': individual.gender or 'N/A',
                            'Faixa de Renda': income_range,
                            'Tem Deficiência': 'Sim' if individual.has_disability else 'Não',
                            'Tem Internet': has_internet,
                            'Dispositivos': devices
                        })
                        success_count += 1
                        
                    except Exception as e:
                        self.logger.error(f"Erro ao processar registro {individual.id} para exportação: {e}")
                        error_count += 1
                
                if not data:
                    messagebox.showerror("Erro", "Nenhum registro válido encontrado para exportação.")
                    return
                
                # Criar DataFrame e exportar
                df = pd.DataFrame(data)
                
                # Tentar salvar o arquivo
                try:
                    df.to_csv(filename, index=False, encoding='utf-8-sig')
                    
                    # Verificar se o arquivo foi criado com sucesso
                    if os.path.exists(filename) and os.path.getsize(filename) > 0:
                        success_msg = f"Resultados exportados com sucesso para {filename}\n\n"
                        success_msg += f"Registros exportados: {success_count}"
                        if error_count > 0:
                            success_msg += f"\nRegistros com problemas: {error_count}"
                        
                        messagebox.showinfo("Sucesso", success_msg)
                        self.logger.info(f"Exportação concluída: {success_count} registros, {error_count} erros")
                    else:
                        raise Exception("Arquivo não foi criado ou está vazio")
                        
                except PermissionError:
                    messagebox.showerror("Erro", "Arquivo está sendo usado por outro programa. Feche o arquivo e tente novamente.")
                except Exception as e:
                    messagebox.showerror("Erro", f"Erro ao salvar arquivo: {e}")
                
            except ImportError:
                messagebox.showerror("Erro", "Biblioteca pandas não está disponível para exportação.")
            except Exception as e:
                self.logger.error(f"Erro durante a exportação: {e}")
                messagebox.showerror("Erro", f"Erro durante a exportação: {e}")
                
        except Exception as e:
            self.logger.error(f"Erro crítico na exportação: {e}")
            messagebox.showerror("Erro Crítico", f"Erro crítico na exportação: {e}")
    
    def generate_report(self):
        """Gera relatório com os dados filtrados"""
        if not self.current_results:
            messagebox.showwarning("Aviso", "Nenhum dado disponível para gerar relatório.")
            return
        
        try:
            # Importar a janela de relatórios
            from .reports_window import ReportsWindow
            
            # Abrir janela de relatórios com dados filtrados
            reports_window = ReportsWindow(self.master, self.db_manager, filtered_data=self.current_results)
            
            self.logger.info(f"Relatório gerado com {len(self.current_results)} registros filtrados")
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatório: {e}")
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
        
    def center_window(self):
        """Centraliza a janela na tela"""
        self.window.update_idletasks()
        w = 1050
        h = 680
        x = (self.window.winfo_screenwidth() // 2) - (w // 2)
        y = (self.window.winfo_screenheight() // 2) - (h // 2)
        self.window.geometry(f"{w}x{h}+{x}+{y}")
    
    def setup_keyboard_shortcuts(self):
        """Configura atalhos de teclado"""
        self.window.bind('<Control-f>', lambda e: self.apply_filters())
        self.window.bind('<Control-r>', lambda e: self.clear_filters())
        self.window.bind('<Control-e>', lambda e: self.export_results())
        self.window.bind('<F5>', lambda e: self.refresh_data())
        self.window.bind('<Escape>', lambda e: self.window.destroy())
    
    def on_closing(self):
        """Trata o fechamento da janela"""
        try:
            self.logger.info("Fechando janela de consulta")
            self.window.destroy()
        except Exception as e:
            self.logger.error(f"Erro ao fechar janela de consulta: {e}")
    
    def refresh_data(self):
        """Atualiza os dados da consulta atual"""
        try:
            if hasattr(self, 'current_results') and self.current_results:
                self.apply_filters()
                self.logger.info("Dados da consulta atualizados")
            else:
                self.load_filter_options()
                self.logger.info("Opções de filtro atualizadas")
        except Exception as e:
            self.logger.error(f"Erro ao atualizar dados: {e}")
            messagebox.showerror("Erro", f"Erro ao atualizar dados: {e}")
    
    def create_widgets(self):
        """Cria os widgets da interface com tema escuro"""
        # Frame principal com tema escuro (tamanho fixo, sem scroll)
        main_frame = tk.Frame(self.window, bg='#0D1117')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Configurar grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título com tema escuro
        title_label = tk.Label(main_frame, 
                              text="🔍 Consulta e Filtragem de Dados",
                              font=('Segoe UI', 16, 'bold'),
                              bg='#0D1117',
                              fg='#F0F6FC')
        title_label.grid(row=0, column=0, pady=(0, 20), sticky='w')
        
        # Área de conteúdo lado a lado (filtros e resultados)
        content_frame = tk.Frame(main_frame, bg='#0D1117')
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=2)
        content_frame.rowconfigure(0, weight=1)

        # Frame de filtros (lado esquerdo)
        self.filters_root = content_frame
        self.create_filters_frame(content_frame)
        
        # Frame de resultados (lado direito)
        self.results_root = content_frame
        self.create_results_frame(content_frame)
        
        # Frame de botões (parte inferior)
        self.create_buttons_frame(main_frame)

        # Guardar referências para regrid dinâmico
        self._content_frame = content_frame
    
    def create_filters_frame(self, parent):
        """Cria o frame de filtros com tema escuro"""
        # Container principal dos filtros
        filters_container = tk.Frame(parent, bg='#0D1117')
        # Posição padrão: col=0 (lado esquerdo)
        filters_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 15))
        filters_container.columnconfigure(0, weight=1)
        filters_container.rowconfigure(1, weight=1)  # Permitir expansão do frame de filtros
        self.filters_container = filters_container
        
        # Título da seção de filtros
        filters_title = tk.Label(filters_container,
                                text="📋 Filtros de Consulta",
                                font=('Segoe UI', 12, 'bold'),
                                bg='#0D1117',
                                fg='#F0F6FC')
        filters_title.grid(row=0, column=0, sticky=tk.W, pady=(0, 15))
        
        # Criar frame com scroll para os filtros
        # Frame container para o canvas e scrollbar
        scroll_container = tk.Frame(filters_container, bg='#21262D', relief='flat', bd=1)
        scroll_container.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=0, pady=0)
        scroll_container.columnconfigure(0, weight=1)
        scroll_container.rowconfigure(0, weight=1)
        
        # Canvas para os filtros
        filters_canvas = tk.Canvas(scroll_container, bg='#21262D', highlightthickness=0, relief='flat')
        filters_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar vertical
        v_scrollbar = ttk.Scrollbar(scroll_container, orient=tk.VERTICAL, command=filters_canvas.yview, style='Query.Vertical.TScrollbar')
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=(4, 4), pady=4)  # Aumentar padding para melhor usabilidade (4px de cada lado)
        
        # Configurar canvas para usar a scrollbar
        filters_canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Frame interno dos filtros que será colocado no canvas
        filters_frame = tk.Frame(filters_canvas, bg='#21262D')
        filters_frame.columnconfigure(0, weight=1)
        
        # Adicionar o frame ao canvas (largura ajustada para acomodar scrollbar mais espessa)
        canvas_window = filters_canvas.create_window((0, 0), window=filters_frame, anchor='nw', width=280)
        
        # Padding interno
        filters_content = tk.Frame(filters_frame, bg='#21262D')
        filters_content.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=15, pady=15)
        filters_content.columnconfigure(0, weight=1)
        
        # Filtro por região
        region_label = tk.Label(filters_content, text="🌍 Região:", 
                               font=('Segoe UI', 10, 'bold'),
                               bg='#21262D', fg='#F0F6FC')
        region_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 3))
        
        self.region_var = tk.StringVar()
        self.region_combo = ttk.Combobox(filters_content, textvariable=self.region_var, 
                                        state="readonly", style='Query.TCombobox')
        self.region_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Filtro por faixa etária
        age_label = tk.Label(filters_content, text="📅 Faixa Etária:", 
                            font=('Segoe UI', 10, 'bold'),
                            bg='#21262D', fg='#F0F6FC')
        age_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 3))
        
        age_frame = tk.Frame(filters_content, bg='#21262D')
        age_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        age_frame.columnconfigure(1, weight=1)
        
        de_label = tk.Label(age_frame, text="De:", bg='#21262D', fg='#8B949E', font=('Segoe UI', 9))
        de_label.grid(row=0, column=0, padx=(0, 5))
        
        self.age_min_var = tk.StringVar()
        age_min_entry = ttk.Entry(age_frame, textvariable=self.age_min_var, 
                                 width=8, style='Query.TEntry')
        age_min_entry.grid(row=0, column=1, padx=(0, 8))
        
        ate_label = tk.Label(age_frame, text="Até:", bg='#21262D', fg='#8B949E', font=('Segoe UI', 9))
        ate_label.grid(row=0, column=2, padx=(0, 5))
        
        self.age_max_var = tk.StringVar()
        age_max_entry = ttk.Entry(age_frame, textvariable=self.age_max_var, 
                                 width=8, style='Query.TEntry')
        age_max_entry.grid(row=0, column=3)
        
        # Filtro por gênero
        gender_label = tk.Label(filters_content, text="👤 Gênero:", 
                               font=('Segoe UI', 10, 'bold'),
                               bg='#21262D', fg='#F0F6FC')
        gender_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 3))
        self.gender_var = tk.StringVar()
        self.gender_combo = ttk.Combobox(filters_content, textvariable=self.gender_var, 
                                        state="readonly", style='Query.TCombobox')
        self.gender_combo['values'] = ('Todos', 'Masculino', 'Feminino')
        self.gender_combo.set('Todos')
        self.gender_combo.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Filtro por renda
        income_label = tk.Label(filters_content, text="💰 Faixa de Renda:", 
                               font=('Segoe UI', 10, 'bold'),
                               bg='#21262D', fg='#F0F6FC')
        income_label.grid(row=6, column=0, sticky=tk.W, pady=(0, 3))
        self.income_var = tk.StringVar()
        self.income_combo = ttk.Combobox(filters_content, textvariable=self.income_var, 
                                        state="readonly", style='Query.TCombobox')
        self.income_combo.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Filtro por deficiência
        disability_label = tk.Label(filters_content, text="♿ Pessoa com Deficiência:", 
                                   font=('Segoe UI', 10, 'bold'),
                                   bg='#21262D', fg='#F0F6FC')
        disability_label.grid(row=8, column=0, sticky=tk.W, pady=(0, 3))
        self.disability_var = tk.StringVar()
        self.disability_combo = ttk.Combobox(filters_content, textvariable=self.disability_var, 
                                           state="readonly", style='Query.TCombobox')
        self.disability_combo['values'] = ('Todos', 'Sim', 'Não')
        self.disability_combo.set('Todos')
        self.disability_combo.grid(row=9, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Filtro por acesso à internet
        internet_label = tk.Label(filters_content, text="🌐 Acesso à Internet:", 
                                 font=('Segoe UI', 10, 'bold'),
                                 bg='#21262D', fg='#F0F6FC')
        internet_label.grid(row=10, column=0, sticky=tk.W, pady=(0, 3))
        self.internet_var = tk.StringVar()
        self.internet_combo = ttk.Combobox(filters_content, textvariable=self.internet_var, 
                                         state="readonly", style='Query.TCombobox')
        self.internet_combo['values'] = ('Todos', 'Sim', 'Não')
        self.internet_combo.set('Todos')
        self.internet_combo.grid(row=11, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botões de filtro
        filter_buttons_frame = tk.Frame(filters_content, bg='#21262D')
        filter_buttons_frame.grid(row=12, column=0, sticky=(tk.W, tk.E), pady=(0, 0))
        filter_buttons_frame.columnconfigure(0, weight=1)
        filter_buttons_frame.columnconfigure(1, weight=1)
        
        apply_btn = tk.Button(filter_buttons_frame, text="Aplicar Filtros", 
                             command=self.apply_filters,
                             bg='#238CF5', fg='white', font=('Segoe UI', 9, 'bold'),
                             relief='flat', padx=12, pady=6)
        apply_btn.grid(row=0, column=0, padx=(0, 5), sticky=(tk.W, tk.E))
        
        clear_btn = tk.Button(filter_buttons_frame, text="Limpar Filtros", 
                             command=self.clear_filters,
                             bg='#8B949E', fg='white', font=('Segoe UI', 9, 'bold'),
                             relief='flat', padx=12, pady=6)
        clear_btn.grid(row=0, column=1, padx=(5, 0), sticky=(tk.W, tk.E))
        
        # Configurar scroll do canvas
        def configure_scroll(event):
            filters_canvas.configure(scrollregion=filters_canvas.bbox('all'))
        
        filters_frame.bind('<Configure>', configure_scroll)
        
        # Configurar altura máxima do canvas (para não expandir demais)
        filters_canvas.configure(height=450)  # Altura máxima para o painel de filtros
        
        # Salvar referências para uso posterior
        self.filters_canvas = filters_canvas
        self.filters_frame = filters_frame
        self.scroll_container = scroll_container
    
    def create_results_frame(self, parent):
        """Cria o frame de resultados"""
        # Frame principal dos resultados
        results_frame = tk.Frame(parent, bg='#0D1117')
        # Posição padrão: col=1 (lado direito)
        results_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        self.results_frame = results_frame
        
        # Título dos resultados
        title_frame = tk.Frame(results_frame, bg='#21262D', height=40)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        title_frame.grid_propagate(False)
        
        title_label = tk.Label(title_frame, text="📊 Resultados da Consulta", 
                              font=('Segoe UI', 12, 'bold'),
                              bg='#21262D', fg='#F0F6FC')
        title_label.pack(side='left', padx=10, pady=10)
        
        # Informações dos resultados
        self.results_info_label = tk.Label(results_frame, 
                                          text="Nenhuma consulta realizada", 
                                          font=('Segoe UI', 10),
                                          bg='#0D1117', fg='#8B949E')
        self.results_info_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # Treeview para exibir resultados
        tree_frame = tk.Frame(results_frame, bg='#0D1117')
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Definir colunas
        columns = ('ID', 'Região', 'Idade', 'Gênero', 'Renda', 'Deficiência', 'Internet', 'Dispositivos')
        self.results_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', 
                                        height=15, style='Query.Treeview')
        
        # Configurar cabeçalhos
        for col in columns:
            self.results_tree.heading(col, text=col)
            if col == 'ID':
                self.results_tree.column(col, width=50, minwidth=50, stretch=True)
            elif col in ['Idade', 'Gênero']:
                self.results_tree.column(col, width=80, minwidth=80, stretch=True)
            else:
                self.results_tree.column(col, width=120, minwidth=100, stretch=True)
        
        # Scrollbars com tema escuro
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                   command=self.results_tree.yview, style='Query.Vertical.TScrollbar')
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, 
                                   command=self.results_tree.xview, style='Query.Horizontal.TScrollbar')
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid dos componentes
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def create_buttons_frame(self, parent):
        """Cria o frame de botões com controles de paginação"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=2, column=0, columnspan=2, pady=(15, 0))
        self.buttons_frame = buttons_frame
        
        # Frame de paginação
        pagination_frame = ttk.Frame(buttons_frame)
        pagination_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Botões de paginação
        self.first_page_btn = ttk.Button(pagination_frame, text="<<", 
                                        command=self.first_page, width=5)
        self.first_page_btn.grid(row=0, column=0, padx=2)
        
        self.prev_page_btn = ttk.Button(pagination_frame, text="<", 
                                       command=self.prev_page, width=5)
        self.prev_page_btn.grid(row=0, column=1, padx=2)
        
        self.page_info_label = ttk.Label(pagination_frame, text="Página 0 de 0")
        self.page_info_label.grid(row=0, column=2, padx=10)
        
        self.next_page_btn = ttk.Button(pagination_frame, text=">", 
                                       command=self.next_page, width=5)
        self.next_page_btn.grid(row=0, column=3, padx=2)
        
        self.last_page_btn = ttk.Button(pagination_frame, text=">>", 
                                       command=self.last_page, width=5)
        self.last_page_btn.grid(row=0, column=4, padx=2)
        
        # Controle de registros por página
        ttk.Label(pagination_frame, text="Registros por página:").grid(row=0, column=5, padx=(20, 5))
        self.records_per_page_var = tk.StringVar(value=str(self.records_per_page))
        records_combo = ttk.Combobox(pagination_frame, textvariable=self.records_per_page_var,
                                   values=['50', '100', '200', '500'], width=8, state="readonly")
        records_combo.grid(row=0, column=6, padx=5)
        records_combo.bind('<<ComboboxSelected>>', self.on_records_per_page_changed)
        
        # Botões de ação
        action_frame = ttk.Frame(buttons_frame)
        action_frame.grid(row=1, column=0, columnspan=3)
        
        ttk.Button(action_frame, text="Exportar Resultados", 
                  command=self.export_results).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(action_frame, text="Gerar Relatório", 
                  command=self.generate_report).grid(row=0, column=1, padx=10)
        ttk.Button(action_frame, text="Atualizar (F5)", 
                  command=self.refresh_data).grid(row=0, column=2, padx=10)
        ttk.Button(action_frame, text="Fechar", 
                  command=self.window.destroy).grid(row=0, column=3, padx=(10, 0))
        
        # Inicializar estado dos botões
        self.update_pagination_buttons()
    
    def update_pagination_buttons(self):
        """Atualiza o estado dos botões de paginação"""
        try:
            # Atualizar label de informação da página
            self.page_info_label.config(text=f"Página {self.current_page} de {self.total_pages}")
            
            # Habilitar/desabilitar botões baseado na página atual
            if self.current_page <= 1:
                self.first_page_btn.config(state='disabled')
                self.prev_page_btn.config(state='disabled')
            else:
                self.first_page_btn.config(state='normal')
                self.prev_page_btn.config(state='normal')
            
            if self.current_page >= self.total_pages:
                self.next_page_btn.config(state='disabled')
                self.last_page_btn.config(state='disabled')
            else:
                self.next_page_btn.config(state='normal')
                self.last_page_btn.config(state='normal')
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar botões de paginação: {e}")
    
    def first_page(self):
        """Vai para a primeira página"""
        if self.current_page > 1:
            self.apply_filters(1)
    
    def prev_page(self):
        """Vai para a página anterior"""
        if self.current_page > 1:
            self.apply_filters(self.current_page - 1)
    
    def next_page(self):
        """Vai para a próxima página"""
        if self.current_page < self.total_pages:
            self.apply_filters(self.current_page + 1)
    
    def last_page(self):
        """Vai para a última página"""
        if self.current_page < self.total_pages:
            self.apply_filters(self.total_pages)
    
    def on_records_per_page_changed(self, event=None):
        """Trata mudança no número de registros por página"""
        try:
            new_value = int(self.records_per_page_var.get())
            if new_value != self.records_per_page:
                self.records_per_page = new_value
                # Recalcular página atual para manter posição aproximada
                current_record = (self.current_page - 1) * self.records_per_page + 1
                new_page = max(1, (current_record - 1) // self.records_per_page + 1)
                self.apply_filters(new_page)
        except ValueError:
            self.records_per_page_var.set(str(self.records_per_page))

    def _on_resize(self, event=None):
        """Reorganiza layout quando largura fica estreita para evitar corte."""
        try:
            width = self.window.winfo_width()
            threshold = 1100
            if width < threshold and not self._stacked:
                # Empilhar verticalmente
                if self.results_frame and self.filters_container:
                    self.results_frame.grid_forget()
                    self.filters_container.grid_forget()
                    # Filtros primeiro
                    self.filters_container.grid(row=0, column=0, sticky='nwe', padx=(0, 0), pady=(0, 10))
                    # Resultados abaixo
                    self.results_frame.grid(row=1, column=0, sticky='nsew', padx=0, pady=(0, 10))
                    # Botões
                    self.buttons_frame.grid_forget()
                    self.buttons_frame.grid(row=2, column=0, pady=(5, 0))
                    # Ajustar expansão
                    self._content_frame.columnconfigure(0, weight=1)
                    self._content_frame.columnconfigure(1, weight=0)
                    self._content_frame.rowconfigure(0, weight=0)
                    self._content_frame.rowconfigure(1, weight=1)
                    self._stacked = True
                    # Ajustar altura do canvas quando empilhado
                    if hasattr(self, 'filters_canvas'):
                        self.filters_canvas.configure(height=300)
            elif width >= threshold and self._stacked:
                # Restaurar layout lado a lado
                self.filters_container.grid_forget()
                self.results_frame.grid_forget()
                self.buttons_frame.grid_forget()
                self.filters_container.grid(row=0, column=0, sticky='nsew', padx=(0, 15))
                self.results_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)
                self.buttons_frame.grid(row=2, column=0, columnspan=2, pady=(15, 0))
                self._content_frame.columnconfigure(0, weight=1)
                self._content_frame.columnconfigure(1, weight=2)
                self._stacked = False
                # Restaurar altura normal do canvas
                if hasattr(self, 'filters_canvas'):
                    self.filters_canvas.configure(height=450)
            # Ajuste dinâmico do wrap de títulos/labels se desejado (futuro)
        except Exception as e:
            self.logger.error(f"Erro ao ajustar layout responsivo: {e}")