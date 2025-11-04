#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema DAC - Digital Analysis and Control
Sistema Acadêmico para Análise de Exclusão Digital no Brasil

Este é o ponto de entrada principal do Sistema DAC, desenvolvido como trabalho
de conclusão de curso para análise de dados relacionados à exclusão digital no Brasil.

Autor: Alejandro Alexandre
RA: 197890
Curso: Análise e Desenvolvimento de Sistemas
Instituição: [Nome da Instituição]
Data: 2025
Versão: 1.0.0
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ui.main_window import MainWindow
from src.database.database_manager import DatabaseManager
from src.utils.logger import setup_logger

def main():
    """Função principal da aplicação"""
    logger = None
    
    try:
        # Configurar logging primeiro
        logger = setup_logger()
        logger.info("Iniciando aplicação DAC")
        
        # Verificar dependências críticas
        try:
            import tkinter as tk
            import sqlalchemy
            import pandas as pd
        except ImportError as imp_error:
            error_msg = f"Dependência crítica não encontrada: {imp_error}"
            if logger:
                logger.error(error_msg)
            print(f"ERRO: {error_msg}")
            print("Execute: pip install -r requirements.txt")
            sys.exit(1)
        
        # Inicializar banco de dados com verificação
        logger.info("Inicializando banco de dados...")
        db_manager = DatabaseManager()
        
        try:
            db_manager.initialize_database()
            logger.info("Banco de dados inicializado com sucesso")
            
            # Verificar integridade do banco
            integrity_check = db_manager.check_database_integrity()
            if integrity_check['errors']:
                logger.warning(f"Problemas de integridade detectados: {integrity_check['errors']}")
            else:
                logger.info("Verificação de integridade do banco: OK")
                
        except Exception as db_error:
            logger.error(f"Erro crítico no banco de dados: {db_error}")
            # Tentar continuar mesmo com problemas no banco
            print(f"AVISO: Problemas no banco de dados detectados: {db_error}")
            print("A aplicação tentará continuar, mas algumas funcionalidades podem estar limitadas.")
        
        # Criar e executar interface principal
        logger.info("Iniciando interface gráfica...")
        try:
            app = MainWindow(db_manager)
            logger.info("Interface criada com sucesso")
            
            # Executar aplicação
            app.run()
            
        except Exception as ui_error:
            logger.error(f"Erro na interface: {ui_error}")
            print(f"ERRO: Falha na interface gráfica: {ui_error}")
            sys.exit(1)
        
    except KeyboardInterrupt:
        if logger:
            logger.info("Aplicação interrompida pelo usuário")
        print("\nAplicação interrompida pelo usuário.")
        sys.exit(0)
        
    except Exception as e:
        error_msg = f"Erro crítico na aplicação: {e}"
        if logger:
            logger.error(error_msg, exc_info=True)
        print(f"ERRO CRÍTICO: {error_msg}")
        print("Verifique o arquivo de log para mais detalhes.")
        sys.exit(1)
    
    finally:
        if logger:
            logger.info("Finalizando aplicação DAC")
        # Cleanup se necessário
        try:
            if 'db_manager' in locals() and db_manager:
                db_manager.close()
        except:
            pass

if __name__ == "__main__":
    main()