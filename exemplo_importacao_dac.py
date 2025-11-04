#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de uso do sistema de importação de dados DAC 2024
Demonstra como importar e organizar os dados estatísticos em memória
"""

import os
import sys
from datetime import datetime
from typing import List, Dict

# Adiciona o diretório src ao path para importações
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.modules.importador_dados_dac import ImportadorDadosDAC, importar_dados_dac
from src.database.estatisticas_models import (
    EstatisticasDAC,
    AcessoInternetDomicilios,
    PerfilUsuarios,
    PerfilNaoUsuarios,
    AcessoExclusivoCelular,
    HabilidadesDigitais,
    ComercioEletronico
)


def demonstrar_importacao():
    """
    Demonstra o processo completo de importação e organização dos dados
    """
    print("=" * 60)
    print("SISTEMA DE IMPORTAÇÃO DE DADOS DAC 2024")
    print("Representação Orientada a Objetos")
    print("=" * 60)
    
    # Caminho para o arquivo de dados
    caminho_csv = os.path.join(os.path.dirname(__file__), 'Dados', 'DADOS DAC 2024 -.csv')
    
    if not os.path.exists(caminho_csv):
        print(f"❌ Arquivo não encontrado: {caminho_csv}")
        return
    
    print(f"📁 Processando arquivo: {caminho_csv}")
    print()
    
    try:
        # Método 1: Usando a classe ImportadorDadosDAC
        print("🔄 Iniciando importação usando ImportadorDadosDAC...")
        importador = ImportadorDadosDAC(caminho_csv)
        dados = importador.importar_dados()
        
        # Exibe relatório da importação
        relatorio = importador.obter_relatorio_importacao()
        exibir_relatorio_importacao(relatorio)
        
        # Demonstra o acesso aos dados organizados
        demonstrar_acesso_dados(dados)
        
        # Demonstra consultas e análises
        demonstrar_consultas(dados)
        
        print("\n✅ Importação e demonstração concluídas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a importação: {str(e)}")
        return


def exibir_relatorio_importacao(relatorio: Dict):
    """
    Exibe o relatório detalhado da importação
    """
    print("\n📊 RELATÓRIO DE IMPORTAÇÃO")
    print("-" * 40)
    print(f"Arquivo processado: {os.path.basename(relatorio['arquivo_processado'])}")
    print(f"Linhas processadas: {relatorio['linhas_processadas']}")
    print(f"Total de registros: {relatorio['total_registros']}")
    print(f"Erros de processamento: {relatorio['erros_processamento']}")
    print(f"Data da importação: {relatorio['data_importacao'].strftime('%d/%m/%Y %H:%M:%S')}")
    
    print("\n📈 DADOS IMPORTADOS POR CATEGORIA:")
    for categoria, quantidade in relatorio['dados_importados'].items():
        nome_categoria = categoria.replace('_', ' ').title()
        print(f"  • {nome_categoria}: {quantidade} registros")
    
    if relatorio['detalhes_erros']:
        print("\n⚠️  DETALHES DOS ERROS:")
        for erro in relatorio['detalhes_erros'][:5]:  # Mostra apenas os primeiros 5
            print(f"  • {erro}")
        if len(relatorio['detalhes_erros']) > 5:
            print(f"  ... e mais {len(relatorio['detalhes_erros']) - 5} erros")


def demonstrar_acesso_dados(dados: EstatisticasDAC):
    """
    Demonstra como acessar os dados organizados em memória
    """
    print("\n🗂️  DEMONSTRAÇÃO DE ACESSO AOS DADOS")
    print("-" * 40)
    
    # 1. Acesso à Internet nos Domicílios
    print("\n1️⃣ ACESSO À INTERNET NOS DOMICÍLIOS:")
    for acesso in dados.acesso_internet_domicilios[:3]:  # Primeiros 3
        evolucao = acesso.obter_evolucao()
        print(f"  📍 {acesso.categoria}:")
        for ano, valor in evolucao.items():
            if valor is not None:
                print(f"    {ano}: {valor}%")
        
        # Calcula crescimento se possível
        crescimento = acesso.calcular_crescimento('2015', '2024')
        if crescimento is not None:
            print(f"    📈 Crescimento 2015-2024: {crescimento:.1f}%")
        print()
    
    # 2. Perfil dos Usuários
    print("2️⃣ PERFIL DOS USUÁRIOS (Amostra):")
    usuarios_por_categoria = {}
    for usuario in dados.perfil_usuarios:
        if usuario.categoria not in usuarios_por_categoria:
            usuarios_por_categoria[usuario.categoria] = []
        usuarios_por_categoria[usuario.categoria].append(usuario)
    
    for categoria, usuarios in list(usuarios_por_categoria.items())[:2]:
        print(f"  📊 {categoria}:")
        for usuario in usuarios[:3]:  # Primeiros 3 de cada categoria
            print(f"    • {usuario.segmento}: {usuario.percentual_usuarios}%")
        print()
    
    # 3. Não Usuários
    print("3️⃣ PERFIL DOS NÃO USUÁRIOS (Amostra):")
    for nao_usuario in dados.perfil_nao_usuarios[:3]:
        print(f"  🚫 {nao_usuario.categoria} - {nao_usuario.segmento}: {nao_usuario.numero_nao_usuarios} milhões")
    
    # 4. Habilidades Digitais
    print("\n4️⃣ HABILIDADES DIGITAIS (Amostra):")
    for habilidade in dados.habilidades_digitais[:3]:
        print(f"  💻 {habilidade.categoria} - {habilidade.habilidade_servico}: {habilidade.percentual_usuarios}%")


def demonstrar_consultas(dados: EstatisticasDAC):
    """
    Demonstra consultas e análises dos dados
    """
    print("\n🔍 DEMONSTRAÇÃO DE CONSULTAS E ANÁLISES")
    print("-" * 40)
    
    # 1. Busca por categoria
    print("\n1️⃣ BUSCA POR CATEGORIA - 'Área':")
    resultados_area = dados.buscar_por_categoria('Área')
    for resultado in resultados_area[:3]:
        if hasattr(resultado, 'segmento'):
            print(f"  📍 {resultado.categoria} - {resultado.segmento}")
    
    # 2. Busca por segmento
    print("\n2️⃣ BUSCA POR SEGMENTO - 'Rural':")
    resultados_rural = dados.buscar_por_segmento('Rural')
    for resultado in resultados_rural:
        if hasattr(resultado, 'percentual_usuarios'):
            print(f"  🌾 {resultado.categoria}: {resultado.percentual_usuarios}%")
        elif hasattr(resultado, 'numero_nao_usuarios'):
            print(f"  🌾 {resultado.categoria}: {resultado.numero_nao_usuarios} milhões")
    
    # 3. Análise de acesso exclusivo por celular
    print("\n3️⃣ ANÁLISE - ACESSO EXCLUSIVO POR CELULAR:")
    celular_dados = dados.acesso_exclusivo_celular
    if celular_dados:
        # Encontra maior e menor percentual
        maior = max(celular_dados, key=lambda x: x.percentual_acesso_exclusivo)
        menor = min(celular_dados, key=lambda x: x.percentual_acesso_exclusivo)
        
        print(f"  📱 Maior acesso exclusivo: {maior.segmento} ({maior.percentual_acesso_exclusivo}%)")
        print(f"  📱 Menor acesso exclusivo: {menor.segmento} ({menor.percentual_acesso_exclusivo}%)")
    
    # 4. Resumo geral
    print("\n4️⃣ RESUMO GERAL DOS DADOS EM MEMÓRIA:")
    resumo = dados.obter_resumo()
    total_registros = sum(resumo.values())
    print(f"  📊 Total de registros em memória: {total_registros}")
    print(f"  🗂️  Distribuição por tipo:")
    for tipo, quantidade in resumo.items():
        percentual = (quantidade / total_registros * 100) if total_registros > 0 else 0
        nome_tipo = tipo.replace('_', ' ').title()
        print(f"    • {nome_tipo}: {quantidade} ({percentual:.1f}%)")


def exemplo_uso_direto():
    """
    Demonstra o uso da função utilitária para importação direta
    """
    print("\n🚀 EXEMPLO DE USO DIRETO (Função Utilitária)")
    print("-" * 40)
    
    caminho_csv = os.path.join(os.path.dirname(__file__), 'Dados', 'DADOS DAC 2024 -.csv')
    
    try:
        # Importação direta usando a função utilitária
        dados = importar_dados_dac(caminho_csv)
        
        print(f"✅ Dados importados com sucesso!")
        print(f"📊 Total de registros: {sum(dados.obter_resumo().values())}")
        
        # Exemplo de acesso direto aos dados
        if dados.acesso_internet_domicilios:
            primeiro_acesso = dados.acesso_internet_domicilios[0]
            print(f"📈 Primeiro registro de acesso: {primeiro_acesso.categoria}")
            evolucao = primeiro_acesso.obter_evolucao()
            print(f"📊 Evolução: {evolucao}")
        
    except Exception as e:
        print(f"❌ Erro na importação direta: {str(e)}")


def main():
    """
    Função principal que executa todas as demonstrações
    """
    try:
        # Demonstração completa
        demonstrar_importacao()
        
        # Exemplo de uso direto
        exemplo_uso_direto()
        
        print("\n" + "=" * 60)
        print("🎉 DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("")
        print("📝 RESUMO DO QUE FOI IMPLEMENTADO:")
        print("  ✅ Classes orientadas a objetos para cada tipo de dado")
        print("  ✅ Sistema de importação automática do CSV")
        print("  ✅ Organização estruturada dos dados em memória")
        print("  ✅ Métodos de consulta e análise")
        print("  ✅ Relatórios detalhados de importação")
        print("  ✅ Funções utilitárias para uso simplificado")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⏹️  Demonstração interrompida pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()