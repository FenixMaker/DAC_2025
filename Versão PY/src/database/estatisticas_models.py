# -*- coding: utf-8 -*-
"""
Modelos de dados para estatísticas DAC 2024
Classes orientadas a objetos para representar dados estatísticos sobre acesso à internet
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from datetime import datetime
import csv
import os


@dataclass
class DadoEstatistico:
    """Classe base para dados estatísticos"""
    categoria: str
    segmento: str
    valor: Union[str, float, int]
    unidade: str = "%"  # %, milhões, etc.
    ano: int = 2024
    
    def __post_init__(self):
        """Processa o valor após inicialização"""
        if isinstance(self.valor, str):
            self.valor = self._processar_valor_string(self.valor)
    
    def _processar_valor_string(self, valor: str) -> Union[float, int, str]:
        """Converte strings de valores para tipos numéricos quando possível"""
        valor = valor.strip()
        
        # Remove símbolos comuns
        if valor.endswith('%'):
            self.unidade = "%"
            valor = valor[:-1]
        elif 'mi' in valor:
            self.unidade = "milhões"
            valor = valor.replace('mi', '').strip()
        elif 'p.p.' in valor:
            self.unidade = "pontos percentuais"
            valor = valor.replace('p.p.', '').strip()
        
        # Tenta converter para número
        try:
            if ',' in valor:
                return float(valor.replace(',', '.'))
            return int(valor) if valor.isdigit() else float(valor)
        except (ValueError, TypeError):
            return valor


@dataclass
class AcessoInternetDomicilios:
    """Dados sobre acesso à internet nos domicílios (2015-2024)"""
    categoria: str
    dados_2015: Optional[float] = None
    dados_2022: Optional[float] = None
    dados_2024: Optional[float] = None
    
    def obter_evolucao(self) -> Dict[str, float]:
        """Retorna a evolução dos dados ao longo dos anos"""
        evolucao = {}
        if self.dados_2015 is not None:
            evolucao['2015'] = self.dados_2015
        if self.dados_2022 is not None:
            evolucao['2022'] = self.dados_2022
        if self.dados_2024 is not None:
            evolucao['2024'] = self.dados_2024
        return evolucao
    
    def calcular_crescimento(self, ano_inicial: str, ano_final: str) -> Optional[float]:
        """Calcula o crescimento percentual entre dois anos"""
        dados = self.obter_evolucao()
        if ano_inicial in dados and ano_final in dados:
            inicial = dados[ano_inicial]
            final = dados[ano_final]
            if inicial > 0:
                return ((final - inicial) / inicial) * 100
        return None


@dataclass
class PerfilUsuarios:
    """Perfil dos usuários de internet (2024)"""
    categoria: str
    segmento: str
    percentual_usuarios: float
    
    def __post_init__(self):
        """Processa dados após inicialização"""
        if isinstance(self.percentual_usuarios, str):
            valor_str = self.percentual_usuarios.replace('%', '').strip()
            try:
                self.percentual_usuarios = float(valor_str)
            except ValueError:
                self.percentual_usuarios = 0.0


@dataclass
class PerfilNaoUsuarios:
    """Perfil dos não usuários de internet (2024)"""
    categoria: str
    segmento: str
    numero_nao_usuarios: float  # em milhões
    
    def __post_init__(self):
        """Processa dados após inicialização"""
        if isinstance(self.numero_nao_usuarios, str):
            valor_str = self.numero_nao_usuarios.replace('mi', '').strip()
            try:
                self.numero_nao_usuarios = float(valor_str)
            except ValueError:
                self.numero_nao_usuarios = 0.0


@dataclass
class AcessoExclusivoCelular:
    """Dados sobre acesso exclusivo pelo celular (2024)"""
    categoria: str
    segmento: str
    percentual_acesso_exclusivo: float
    
    def __post_init__(self):
        """Processa dados após inicialização"""
        if isinstance(self.percentual_acesso_exclusivo, str):
            valor_str = self.percentual_acesso_exclusivo.replace('%', '').strip()
            try:
                self.percentual_acesso_exclusivo = float(valor_str)
            except ValueError:
                self.percentual_acesso_exclusivo = 0.0


@dataclass
class HabilidadesDigitais:
    """Habilidades digitais e uso de serviços"""
    categoria: str
    habilidade_servico: str
    percentual_usuarios: float
    
    def __post_init__(self):
        """Processa dados após inicialização"""
        if isinstance(self.percentual_usuarios, str):
            # Remove informações extras como "(73 milhões de pessoas)"
            valor_str = self.percentual_usuarios.split('(')[0].replace('%', '').strip()
            try:
                self.percentual_usuarios = float(valor_str)
            except ValueError:
                self.percentual_usuarios = 0.0


@dataclass
class ComercioEletronico:
    """Dados sobre comércio eletrônico e formas de pagamento"""
    tipo: str  # "Compras" ou "Pagamento"
    item: str
    percentual: float
    informacao_adicional: Optional[str] = None
    
    def __post_init__(self):
        """Processa dados após inicialização"""
        if isinstance(self.percentual, str):
            # Extrai informação adicional se houver
            if '(' in self.percentual:
                partes = self.percentual.split('(')
                valor_str = partes[0].replace('%', '').strip()
                self.informacao_adicional = partes[1].replace(')', '').strip()
            else:
                valor_str = self.percentual.replace('%', '').strip()
            
            try:
                self.percentual = float(valor_str)
            except ValueError:
                self.percentual = 0.0


@dataclass
class EstatisticasDAC:
    """Classe principal que agrupa todas as estatísticas DAC"""
    acesso_internet_domicilios: List[AcessoInternetDomicilios] = field(default_factory=list)
    perfil_usuarios: List[PerfilUsuarios] = field(default_factory=list)
    perfil_nao_usuarios: List[PerfilNaoUsuarios] = field(default_factory=list)
    acesso_exclusivo_celular: List[AcessoExclusivoCelular] = field(default_factory=list)
    habilidades_digitais: List[HabilidadesDigitais] = field(default_factory=list)
    comercio_eletronico: List[ComercioEletronico] = field(default_factory=list)
    data_importacao: datetime = field(default_factory=datetime.now)
    
    def obter_resumo(self) -> Dict[str, int]:
        """Retorna um resumo da quantidade de dados por categoria"""
        return {
            'acesso_internet_domicilios': len(self.acesso_internet_domicilios),
            'perfil_usuarios': len(self.perfil_usuarios),
            'perfil_nao_usuarios': len(self.perfil_nao_usuarios),
            'acesso_exclusivo_celular': len(self.acesso_exclusivo_celular),
            'habilidades_digitais': len(self.habilidades_digitais),
            'comercio_eletronico': len(self.comercio_eletronico)
        }
    
    def buscar_por_categoria(self, categoria: str) -> List:
        """Busca dados por categoria específica"""
        resultados = []
        
        # Busca em todas as listas
        for lista_dados in [self.perfil_usuarios, self.perfil_nao_usuarios, 
                           self.acesso_exclusivo_celular, self.habilidades_digitais]:
            for item in lista_dados:
                if hasattr(item, 'categoria') and categoria.lower() in item.categoria.lower():
                    resultados.append(item)
        
        return resultados
    
    def buscar_por_segmento(self, segmento: str) -> List:
        """Busca dados por segmento específico"""
        resultados = []
        
        for lista_dados in [self.perfil_usuarios, self.perfil_nao_usuarios, 
                           self.acesso_exclusivo_celular]:
            for item in lista_dados:
                if hasattr(item, 'segmento') and segmento.lower() in item.segmento.lower():
                    resultados.append(item)
        
        return resultados
    
    def obter_estatisticas_por_faixa_etaria(self) -> Dict[str, Dict[str, float]]:
        """Retorna estatísticas organizadas por faixa etária"""
        stats = {}
        
        # Processa dados de usuários
        for usuario in self.perfil_usuarios:
            if 'anos' in usuario.segmento.lower():
                faixa = usuario.segmento
                if faixa not in stats:
                    stats[faixa] = {}
                stats[faixa]['percentual_usuarios'] = usuario.percentual_usuarios
        
        # Processa dados de não usuários
        for nao_usuario in self.perfil_nao_usuarios:
            if 'anos' in nao_usuario.segmento.lower():
                faixa = nao_usuario.segmento
                if faixa not in stats:
                    stats[faixa] = {}
                stats[faixa]['nao_usuarios_milhoes'] = nao_usuario.numero_nao_usuarios
        
        return stats
    
    def obter_comparacao_classes_sociais(self) -> Dict[str, Dict[str, float]]:
        """Compara dados entre diferentes classes sociais"""
        classes = {}
        
        # Dados de usuários por classe
        for usuario in self.perfil_usuarios:
            if usuario.categoria == 'Classe Social':
                classe = usuario.segmento
                if classe not in classes:
                    classes[classe] = {}
                classes[classe]['percentual_usuarios'] = usuario.percentual_usuarios
        
        # Dados de acesso exclusivo por celular
        for acesso in self.acesso_exclusivo_celular:
            if acesso.categoria == 'Classe Social':
                classe = acesso.segmento
                if classe not in classes:
                    classes[classe] = {}
                classes[classe]['acesso_exclusivo_celular'] = acesso.percentual_acesso_exclusivo
        
        return classes
    
    def obter_analise_vulnerabilidade_digital(self) -> Dict[str, any]:
        """Identifica grupos em situação de vulnerabilidade digital"""
        vulnerabilidades = {
            'grupos_risco': [],
            'indicadores': {},
            'recomendacoes': []
        }
        
        # Identifica grupos com baixo acesso
        for usuario in self.perfil_usuarios:
            if usuario.percentual_usuarios < 50:  # Menos de 50% de usuários
                vulnerabilidades['grupos_risco'].append({
                    'categoria': usuario.categoria,
                    'segmento': usuario.segmento,
                    'percentual_usuarios': usuario.percentual_usuarios,
                    'tipo': 'baixo_acesso'
                })
        
        # Identifica grupos com alto acesso exclusivo por celular
        for acesso in self.acesso_exclusivo_celular:
            if acesso.percentual_acesso_exclusivo > 70:  # Mais de 70% só celular
                vulnerabilidades['grupos_risco'].append({
                    'categoria': acesso.categoria,
                    'segmento': acesso.segmento,
                    'percentual_exclusivo': acesso.percentual_acesso_exclusivo,
                    'tipo': 'dependencia_celular'
                })
        
        # Calcula indicadores gerais
        if self.perfil_nao_usuarios:
            total_nao_usuarios = sum(nu.numero_nao_usuarios for nu in self.perfil_nao_usuarios)
            vulnerabilidades['indicadores']['total_nao_usuarios_milhoes'] = total_nao_usuarios
        
        # Gera recomendações básicas
        if vulnerabilidades['grupos_risco']:
            vulnerabilidades['recomendacoes'] = [
                "Implementar programas de inclusão digital para grupos identificados",
                "Desenvolver infraestrutura de banda larga em áreas rurais",
                "Criar programas de capacitação digital para idosos",
                "Facilitar acesso a dispositivos além do celular"
            ]
        
        return vulnerabilidades
    
    def exportar_resumo_executivo(self) -> Dict[str, any]:
        """Gera um resumo executivo dos dados para relatórios"""
        resumo = {
            'data_geracao': datetime.now(),
            'fonte_dados': 'DADOS DAC 2024',
            'total_registros': sum(self.obter_resumo().values()),
            'principais_indicadores': {},
            'tendencias': {},
            'grupos_vulneraveis': []
        }
        
        # Principais indicadores
        if self.acesso_internet_domicilios:
            # Busca dados gerais de 2024
            for acesso in self.acesso_internet_domicilios:
                if acesso.categoria == 'Total' and acesso.dados_2024:
                    resumo['principais_indicadores']['acesso_geral_2024'] = acesso.dados_2024
                elif acesso.categoria == 'Área Rural' and acesso.dados_2024:
                    resumo['principais_indicadores']['acesso_rural_2024'] = acesso.dados_2024
                elif acesso.categoria == 'Área Urbana' and acesso.dados_2024:
                    resumo['principais_indicadores']['acesso_urbano_2024'] = acesso.dados_2024
        
        # Identifica tendências de crescimento
        for acesso in self.acesso_internet_domicilios:
            if acesso.dados_2015 and acesso.dados_2024:
                crescimento = acesso.calcular_crescimento('2015', '2024')
                if crescimento:
                    resumo['tendencias'][acesso.categoria] = f"{crescimento:.1f}% de crescimento"
        
        # Grupos vulneráveis (simplificado)
        analise_vuln = self.obter_analise_vulnerabilidade_digital()
        resumo['grupos_vulneraveis'] = analise_vuln['grupos_risco'][:5]  # Top 5
        
        return resumo