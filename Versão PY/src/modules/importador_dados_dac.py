# -*- coding: utf-8 -*-
"""
Importador de dados DAC 2024
Classe responsável por processar o arquivo CSV e organizar os dados em estruturas orientadas a objetos
"""

import csv
import os
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Importa as classes de modelo
from ..database.estatisticas_models import (
    EstatisticasDAC,
    AcessoInternetDomicilios,
    PerfilUsuarios,
    PerfilNaoUsuarios,
    AcessoExclusivoCelular,
    HabilidadesDigitais,
    ComercioEletronico
)


class ImportadorDadosDAC:
    """Classe para importar e processar dados do arquivo CSV DAC 2024"""
    
    def __init__(self, caminho_arquivo: str):
        """
        Inicializa o importador com o caminho do arquivo CSV
        
        Args:
            caminho_arquivo: Caminho para o arquivo CSV dos dados DAC
        """
        self.caminho_arquivo = caminho_arquivo
        self.dados_processados = EstatisticasDAC()
        self.secao_atual = None
        self.linhas_processadas = 0
        self.erros_processamento = []
    
    def importar_dados(self) -> EstatisticasDAC:
        """
        Importa e processa todos os dados do arquivo CSV
        
        Returns:
            EstatisticasDAC: Objeto contendo todos os dados organizados
        """
        if not os.path.exists(self.caminho_arquivo):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.caminho_arquivo}")
        
        try:
            with open(self.caminho_arquivo, 'r', encoding='utf-8') as arquivo:
                leitor_csv = csv.reader(arquivo)
                
                for numero_linha, linha in enumerate(leitor_csv, 1):
                    try:
                        self._processar_linha(linha, numero_linha)
                        self.linhas_processadas += 1
                    except Exception as e:
                        erro = f"Erro na linha {numero_linha}: {str(e)}"
                        self.erros_processamento.append(erro)
                        print(f"Aviso: {erro}")
            
            print(f"Importação concluída: {self.linhas_processadas} linhas processadas")
            if self.erros_processamento:
                print(f"Avisos: {len(self.erros_processamento)} erros de processamento")
            
            return self.dados_processados
            
        except Exception as e:
            raise Exception(f"Erro ao processar arquivo: {str(e)}")
    
    def _processar_linha(self, linha: List[str], numero_linha: int):
        """
        Processa uma linha individual do CSV
        
        Args:
            linha: Lista de valores da linha
            numero_linha: Número da linha no arquivo
        """
        if not linha or all(not celula.strip() for celula in linha):
            return  # Linha vazia
        
        primeira_coluna = linha[0].strip()
        
        # Identifica seções pelos títulos
        if self._eh_titulo_secao(primeira_coluna):
            self.secao_atual = self._identificar_secao(primeira_coluna)
            return
        
        # Pula cabeçalhos de colunas
        if self._eh_cabecalho(primeira_coluna):
            return
        
        # Processa dados baseado na seção atual
        if self.secao_atual:
            self._processar_dados_secao(linha)
    
    def _eh_titulo_secao(self, texto: str) -> bool:
        """
        Verifica se o texto é um título de seção
        """
        titulos_secao = [
            "Acesso à Internet nos Domicílios",
            "Perfil dos Usuários de Internet",
            "Perfil dos NÃO Usuários de Internet",
            "Acesso Exclusivo pelo Celular",
            "Habilidades Digitais e Uso de Serviços",
            "Comércio Eletrônico",
            "Formas Pagamento"
        ]
        
        return any(titulo in texto for titulo in titulos_secao)
    
    def _eh_cabecalho(self, texto: str) -> bool:
        """
        Verifica se o texto é um cabeçalho de coluna
        """
        cabecalhos = ["Categoria", "Segmento", "Percentual", "Número", "Habilidade"]
        return any(cabecalho in texto for cabecalho in cabecalhos)
    
    def _identificar_secao(self, titulo: str) -> str:
        """
        Identifica o tipo de seção baseado no título
        """
        if "Acesso à Internet nos Domicílios" in titulo:
            return "acesso_domicilios"
        elif "Perfil dos Usuários de Internet" in titulo:
            return "perfil_usuarios"
        elif "Perfil dos NÃO Usuários" in titulo:
            return "perfil_nao_usuarios"
        elif "Acesso Exclusivo pelo Celular" in titulo:
            return "acesso_celular"
        elif "Habilidades Digitais" in titulo:
            return "habilidades_digitais"
        elif "Comércio Eletrônico" in titulo or "Formas Pagamento" in titulo:
            return "comercio_eletronico"
        
        return "desconhecido"
    
    def _processar_dados_secao(self, linha: List[str]):
        """
        Processa dados específicos de cada seção
        """
        if not linha[0].strip():  # Primeira coluna vazia
            return
        
        try:
            if self.secao_atual == "acesso_domicilios":
                self._processar_acesso_domicilios(linha)
            elif self.secao_atual == "perfil_usuarios":
                self._processar_perfil_usuarios(linha)
            elif self.secao_atual == "perfil_nao_usuarios":
                self._processar_perfil_nao_usuarios(linha)
            elif self.secao_atual == "acesso_celular":
                self._processar_acesso_celular(linha)
            elif self.secao_atual == "habilidades_digitais":
                self._processar_habilidades_digitais(linha)
            elif self.secao_atual == "comercio_eletronico":
                self._processar_comercio_eletronico(linha)
        except Exception as e:
            raise Exception(f"Erro ao processar seção {self.secao_atual}: {str(e)}")
    
    def _processar_acesso_domicilios(self, linha: List[str]):
        """Processa dados de acesso à internet nos domicílios"""
        if len(linha) >= 4:
            categoria = linha[0].strip()
            
            # Converte valores, tratando "N/A" como None
            valor_2015 = self._converter_percentual(linha[1]) if linha[1].strip() != "N/A" else None
            valor_2022 = self._converter_percentual(linha[2]) if linha[2].strip() != "N/A" else None
            valor_2024 = self._converter_percentual(linha[3]) if linha[3].strip() != "N/A" else None
            
            acesso = AcessoInternetDomicilios(
                categoria=categoria,
                dados_2015=valor_2015,
                dados_2022=valor_2022,
                dados_2024=valor_2024
            )
            
            self.dados_processados.acesso_internet_domicilios.append(acesso)
    
    def _processar_perfil_usuarios(self, linha: List[str]):
        """Processa dados do perfil dos usuários"""
        if len(linha) >= 3:
            categoria = linha[0].strip()
            segmento = linha[1].strip()
            percentual = self._converter_percentual(linha[2])
            
            if categoria and segmento:  # Ambos preenchidos
                perfil = PerfilUsuarios(
                    categoria=categoria,
                    segmento=segmento,
                    percentual_usuarios=percentual
                )
                self.dados_processados.perfil_usuarios.append(perfil)
            elif segmento:  # Apenas segmento (categoria vazia, usa a anterior)
                if self.dados_processados.perfil_usuarios:
                    ultima_categoria = self.dados_processados.perfil_usuarios[-1].categoria
                    perfil = PerfilUsuarios(
                        categoria=ultima_categoria,
                        segmento=segmento,
                        percentual_usuarios=percentual
                    )
                    self.dados_processados.perfil_usuarios.append(perfil)
    
    def _processar_perfil_nao_usuarios(self, linha: List[str]):
        """Processa dados do perfil dos não usuários"""
        if len(linha) >= 3:
            categoria = linha[0].strip()
            segmento = linha[1].strip()
            numero = self._converter_milhoes(linha[2])
            
            if categoria and segmento:
                perfil = PerfilNaoUsuarios(
                    categoria=categoria,
                    segmento=segmento,
                    numero_nao_usuarios=numero
                )
                self.dados_processados.perfil_nao_usuarios.append(perfil)
            elif segmento:
                if self.dados_processados.perfil_nao_usuarios:
                    ultima_categoria = self.dados_processados.perfil_nao_usuarios[-1].categoria
                    perfil = PerfilNaoUsuarios(
                        categoria=ultima_categoria,
                        segmento=segmento,
                        numero_nao_usuarios=numero
                    )
                    self.dados_processados.perfil_nao_usuarios.append(perfil)
    
    def _processar_acesso_celular(self, linha: List[str]):
        """Processa dados de acesso exclusivo pelo celular"""
        if len(linha) >= 3:
            categoria = linha[0].strip()
            segmento = linha[1].strip()
            percentual = self._converter_percentual(linha[2])
            
            if categoria and segmento:
                acesso = AcessoExclusivoCelular(
                    categoria=categoria,
                    segmento=segmento,
                    percentual_acesso_exclusivo=percentual
                )
                self.dados_processados.acesso_exclusivo_celular.append(acesso)
            elif segmento:
                if self.dados_processados.acesso_exclusivo_celular:
                    ultima_categoria = self.dados_processados.acesso_exclusivo_celular[-1].categoria
                    acesso = AcessoExclusivoCelular(
                        categoria=ultima_categoria,
                        segmento=segmento,
                        percentual_acesso_exclusivo=percentual
                    )
                    self.dados_processados.acesso_exclusivo_celular.append(acesso)
    
    def _processar_habilidades_digitais(self, linha: List[str]):
        """Processa dados de habilidades digitais"""
        if len(linha) >= 3:
            categoria = linha[0].strip()
            habilidade = linha[1].strip()
            percentual = self._converter_percentual(linha[2])
            
            if categoria and habilidade:
                habilidade_obj = HabilidadesDigitais(
                    categoria=categoria,
                    habilidade_servico=habilidade,
                    percentual_usuarios=percentual
                )
                self.dados_processados.habilidades_digitais.append(habilidade_obj)
    
    def _processar_comercio_eletronico(self, linha: List[str]):
        """Processa dados de comércio eletrônico"""
        if len(linha) >= 2:
            item = linha[0].strip()
            valor = linha[1].strip() if len(linha) > 1 else "0%"
            
            # Determina o tipo baseado no contexto
            if "Pix" in item or "Cartão" in item or "Boleto" in item:
                tipo = "Pagamento"
            else:
                tipo = "Compras"
            
            comercio = ComercioEletronico(
                tipo=tipo,
                item=item,
                percentual=valor
            )
            self.dados_processados.comercio_eletronico.append(comercio)
    
    def _converter_percentual(self, valor: str) -> float:
        """Converte string de percentual para float"""
        if not valor or valor.strip() == "N/A":
            return 0.0
        
        valor_limpo = re.sub(r'[^\d,.-]', '', valor.strip())
        valor_limpo = valor_limpo.replace(',', '.')
        
        try:
            return float(valor_limpo)
        except ValueError:
            return 0.0
    
    def _converter_milhoes(self, valor: str) -> float:
        """Converte string de milhões para float"""
        if not valor:
            return 0.0
        
        valor_limpo = valor.replace('mi', '').strip()
        valor_limpo = re.sub(r'[^\d,.-]', '', valor_limpo)
        valor_limpo = valor_limpo.replace(',', '.')
        
        try:
            return float(valor_limpo)
        except ValueError:
            return 0.0
    
    def obter_relatorio_importacao(self) -> Dict[str, any]:
        """Retorna relatório detalhado da importação"""
        resumo = self.dados_processados.obter_resumo()
        
        return {
            'arquivo_processado': self.caminho_arquivo,
            'linhas_processadas': self.linhas_processadas,
            'erros_processamento': len(self.erros_processamento),
            'detalhes_erros': self.erros_processamento,
            'dados_importados': resumo,
            'data_importacao': self.dados_processados.data_importacao,
            'total_registros': sum(resumo.values())
        }


# Função utilitária para uso direto
def importar_dados_dac(caminho_arquivo: str) -> EstatisticasDAC:
    """
    Função utilitária para importar dados DAC de forma simples
    
    Args:
        caminho_arquivo: Caminho para o arquivo CSV
    
    Returns:
        EstatisticasDAC: Dados organizados em memória
    """
    importador = ImportadorDadosDAC(caminho_arquivo)
    return importador.importar_dados()