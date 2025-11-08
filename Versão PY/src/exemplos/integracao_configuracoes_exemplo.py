"""
Exemplo de integração da aba de configurações ao menu principal do sistema DAC.
Este arquivo demonstra como adicionar a aba de configurações a uma aplicação existente.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from gui.configuracoes_integracao import ConfiguracoesIntegracao, integrar_configuracoes


class AplicacaoPrincipalExemplo:
    """Classe de exemplo mostrando como integrar as configurações ao sistema principal."""
    
    def __init__(self):
        """Inicializa a aplicação principal de exemplo."""
        # Cria a janela principal
        self.root = tk.Tk()
        self.root.title("Sistema DAC - Exemplo de Integração")
        self.root.geometry("1200x800")
        
        # Configura o ícone da aplicação (se existir)
        self.configurar_icone()
        
        # Cria a barra de menu
        self.criar_menu_principal()
        
        # Cria a interface principal
        self.criar_interface_principal()
        
        # Integra as configurações
        self.integrar_configuracoes()
        
        # Configura o fechamento da aplicação
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def configurar_icone(self):
        """Configura o ícone da aplicação."""
        try:
            # Tenta carregar ícone se existir
            icon_path = Path(__file__).resolve().parents[2] / "recursos" / "icones" / "dac.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass  # Ignora erro se não conseguir carregar ícone
    
    def criar_menu_principal(self):
        """Cria a barra de menu principal."""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Menu Arquivo
        arquivo_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Arquivo", menu=arquivo_menu)
        arquivo_menu.add_command(label="Novo", command=self.novo_arquivo)
        arquivo_menu.add_command(label="Abrir", command=self.abrir_arquivo)
        arquivo_menu.add_separator()
        arquivo_menu.add_command(label="Sair", command=self.on_closing)
        
        # Menu Visualizar
        visualizar_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Visualizar", menu=visualizar_menu)
        visualizar_menu.add_command(label="Dashboard", command=self.mostrar_dashboard)
        visualizar_menu.add_command(label="Relatórios", command=self.mostrar_relatorios)
        visualizar_menu.add_command(label="Consultas", command=self.mostrar_consultas)
        
        # Menu Ferramentas (será populado pela integração de configurações)
        self.ferramentas_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Ferramentas", menu=self.ferramentas_menu)
        
        # Menu Ajuda
        ajuda_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Ajuda", menu=ajuda_menu)
        ajuda_menu.add_command(label="Documentação", command=self.mostrar_documentacao)
        ajuda_menu.add_command(label="Sobre", command=self.mostrar_sobre)
    
    def criar_interface_principal(self):
        """Cria a interface principal com notebook."""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Notebook principal para as abas
        self.notebook_principal = ttk.Notebook(main_frame)
        self.notebook_principal.pack(fill=tk.BOTH, expand=True)
        
        # Cria abas principais
        self.criar_aba_dashboard()
        self.criar_aba_consultas()
        self.criar_aba_relatorios()
        
        # Barra de status
        self.status_bar = ttk.Label(main_frame, text="Pronto", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def criar_aba_dashboard(self):
        """Cria a aba do dashboard."""
        dashboard_frame = ttk.Frame(self.notebook_principal)
        self.notebook_principal.add(dashboard_frame, text="📊 Dashboard")
        
        # Conteúdo do dashboard
        ttk.Label(dashboard_frame, text="Dashboard do Sistema DAC", 
                 font=('Arial', 16, 'bold')).pack(pady=20)
        
        # Frame de estatísticas
        stats_frame = ttk.LabelFrame(dashboard_frame, text="Estatísticas Rápidas", padding=10)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Labels de estatísticas
        self.total_registros_label = ttk.Label(stats_frame, text="Total de Registros: --")
        self.total_registros_label.pack(anchor='w', pady=2)
        
        self.conexao_status_label = ttk.Label(stats_frame, text="Status da Conexão: --")
        self.conexao_status_label.pack(anchor='w', pady=2)
        
        self.ultima_atualizacao_label = ttk.Label(stats_frame, text="Última Atualização: --")
        self.ultima_atualizacao_label.pack(anchor='w', pady=2)
        
        # Botão de atualizar
        ttk.Button(dashboard_frame, text="Atualizar Dados", 
                  command=self.atualizar_dashboard).pack(pady=10)
    
    def criar_aba_consultas(self):
        """Cria a aba de consultas."""
        consultas_frame = ttk.Frame(self.notebook_principal)
        self.notebook_principal.add(consultas_frame, text="🔍 Consultas")
        
        # Conteúdo da aba de consultas
        ttk.Label(consultas_frame, text="Consultas SQL", 
                 font=('Arial', 16, 'bold')).pack(pady=20)
        
        # Área de texto para consultas
        self.consulta_text = tk.Text(consultas_frame, height=10, width=80)
        self.consulta_text.pack(pady=10)
        
        # Frame de botões
        button_frame = ttk.Frame(consultas_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Executar Consulta", 
                  command=self.executar_consulta).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Limpar", 
                  command=self.limpar_consulta).pack(side=tk.LEFT, padx=5)
        
        # Resultados
        resultados_frame = ttk.LabelFrame(consultas_frame, text="Resultados", padding=10)
        resultados_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.resultados_text = tk.Text(resultados_frame, height=8, width=80, state='disabled')
        self.resultados_text.pack(fill=tk.BOTH, expand=True)
    
    def criar_aba_relatorios(self):
        """Cria a aba de relatórios."""
        relatorios_frame = ttk.Frame(self.notebook_principal)
        self.notebook_principal.add(relatorios_frame, text="📈 Relatórios")
        
        # Conteúdo da aba de relatórios
        ttk.Label(relatorios_frame, text="Relatórios do Sistema", 
                 font=('Arial', 16, 'bold')).pack(pady=20)
        
        # Tipos de relatórios
        tipos_frame = ttk.LabelFrame(relatorios_frame, text="Tipos de Relatórios", padding=10)
        tipos_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Checkboxes para tipos de relatórios
        self.relatorios_vars = {}
        tipos_relatorios = [
            "Análise por Período",
            "Comparativo de Dados", 
            "Estatísticas Gerais",
            "Relatório de Auditoria"
        ]
        
        for i, tipo in enumerate(tipos_relatorios):
            var = tk.BooleanVar(value=True)
            self.relatorios_vars[tipo] = var
            ttk.Checkbutton(tipos_frame, text=tipo, variable=var).grid(row=i//2, column=i%2, sticky='w', padx=10, pady=5)
        
        # Botão de gerar relatórios
        ttk.Button(relatorios_frame, text="Gerar Relatórios Selecionados", 
                  command=self.gerar_relatorios).pack(pady=20)
    
    def integrar_configuracoes(self):
        """Integra a aba de configurações ao sistema."""
        try:
            # Usa a função de integração
            self.config_integracao = integrar_configuracoes(
                self.root, 
                self.notebook_principal, 
                self.menubar
            )
            
            # Adiciona comando adicional ao menu ferramentas
            self.ferramentas_menu.add_separator()
            self.ferramentas_menu.add_command(
                label="Preferências",
                command=self.abrir_preferencias,
                accelerator="Ctrl+P"
            )
            
            # Configura atalho
            self.root.bind_all("<Control-p>", lambda e: self.abrir_preferencias())
            
            print("Configurações integradas com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao integrar configurações:\n{str(e)}")
    
    def abrir_preferencias(self):
        """Abre a aba de configurações."""
        self.config_integracao.abrir_configuracoes()
    
    def novo_arquivo(self):
        """Ação para novo arquivo."""
        messagebox.showinfo("Informação", "Funcionalidade 'Novo Arquivo' em desenvolvimento.")
    
    def abrir_arquivo(self):
        """Ação para abrir arquivo."""
        messagebox.showinfo("Informação", "Funcionalidade 'Abrir Arquivo' em desenvolvimento.")
    
    def mostrar_dashboard(self):
        """Mostra a aba do dashboard."""
        for i in range(self.notebook_principal.index('end')):
            if "Dashboard" in self.notebook_principal.tab(i, 'text'):
                self.notebook_principal.select(i)
                break
    
    def mostrar_relatorios(self):
        """Mostra a aba de relatórios."""
        for i in range(self.notebook_principal.index('end')):
            if "Relatórios" in self.notebook_principal.tab(i, 'text'):
                self.notebook_principal.select(i)
                break
    
    def mostrar_consultas(self):
        """Mostra a aba de consultas."""
        for i in range(self.notebook_principal.index('end')):
            if "Consultas" in self.notebook_principal.tab(i, 'text'):
                self.notebook_principal.select(i)
                break
    
    def mostrar_documentacao(self):
        """Mostra a documentação."""
        messagebox.showinfo("Documentação", "Documentação do sistema em desenvolvimento.")
    
    def mostrar_sobre(self):
        """Mostra informações sobre o sistema."""
        sobre_text = """
Sistema DAC - Data Analysis & Control

Versão: 1.0.0
Desenvolvido para análise e gerenciamento de dados

© 2024 - Todos os direitos reservados
        """
        messagebox.showinfo("Sobre", sobre_text.strip())
    
    def atualizar_dashboard(self):
        """Atualiza os dados do dashboard."""
        # Simula atualização dos dados
        self.total_registros_label.config(text="Total de Registros: 1.234")
        self.conexao_status_label.config(text="Status da Conexão: Conectado")
        self.ultima_atualizacao_label.config(text="Última Atualização: Agora")
        
        self.status_bar.config(text="Dashboard atualizado com sucesso!")
        
        # Atualiza após 3 segundos
        self.root.after(3000, lambda: self.status_bar.config(text="Pronto"))
    
    def executar_consulta(self):
        """Executa a consulta SQL."""
        consulta = self.consulta_text.get('1.0', tk.END).strip()
        
        if not consulta:
            messagebox.showwarning("Aviso", "Por favor, insira uma consulta SQL.")
            return
        
        # Simula execução da consulta
        self.resultados_text.config(state='normal')
        self.resultados_text.delete('1.0', tk.END)
        self.resultados_text.insert('1.0', f"Executando consulta: {consulta}\n\n")
        self.resultados_text.insert(tk.END, "Resultados da consulta seriam exibidos aqui...\n")
        self.resultados_text.config(state='disabled')
        
        self.status_bar.config(text="Consulta executada com sucesso!")
    
    def limpar_consulta(self):
        """Limpa a área de consulta."""
        self.consulta_text.delete('1.0', tk.END)
        self.resultados_text.config(state='normal')
        self.resultados_text.delete('1.0', tk.END)
        self.resultados_text.config(state='disabled')
    
    def gerar_relatorios(self):
        """Gera os relatórios selecionados."""
        selecionados = [tipo for tipo, var in self.relatorios_vars.items() if var.get()]
        
        if not selecionados:
            messagebox.showwarning("Aviso", "Por favor, selecione pelo menos um tipo de relatório.")
            return
        
        relatorios_text = "Relatórios gerados:\n" + "\n".join(f"- {tipo}" for tipo in selecionados)
        messagebox.showinfo("Relatórios", relatorios_text)
        
        self.status_bar.config(text=f"{len(selecionados)} relatórios gerados com sucesso!")
    
    def on_closing(self):
        """Trata o fechamento da aplicação."""
        if messagebox.askokcancel("Sair", "Deseja realmente sair do sistema?"):
            self.root.destroy()
    
    def run(self):
        """Inicia a aplicação."""
        # Atualiza dashboard inicial
        self.atualizar_dashboard()
        
        # Inicia o loop principal
        self.root.mainloop()


def main():
    """Função principal."""
    app = AplicacaoPrincipalExemplo()
    app.run()


if __name__ == "__main__":
    main()