# -*- coding: utf-8 -*-
"""
Sistema de logging para o DAC
"""

import logging
import os
from pathlib import Path
from datetime import datetime

def setup_logger(name="DAC", log_dir=None, level=logging.INFO):
    """
    Configura o sistema de logging da aplicação
    
    Args:
        name (str): Nome do logger
        log_dir (str, optional): Diretório para os logs. Se None, usa o padrão
        level: Nível de logging
    
    Returns:
        logging.Logger: Logger configurado
    """
    # Criar diretório de logs se não existir
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent / "logs"
    else:
        log_dir = Path(log_dir)
    log_dir.mkdir(exist_ok=True, parents=True)
    
    # Nome do arquivo de log com data
    log_filename = f"dac_{datetime.now().strftime('%Y%m%d')}.log"
    log_path = log_dir / log_filename
    
    # Configurar logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Limpar handlers existentes para permitir reconfiguração
    logger.handlers.clear()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para arquivo
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Adicionar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name=None):
    """
    Retorna um logger existente ou cria um novo
    
    Args:
        name (str): Nome do logger
    
    Returns:
        logging.Logger: Logger
    """
    if name is None:
        name = "DAC"
    
    logger = logging.getLogger(name)
    
    # Se o logger não foi configurado, configurar agora
    if not logger.handlers:
        return setup_logger(name)
    
    return logger