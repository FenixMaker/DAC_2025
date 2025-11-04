
# -*- coding: utf-8 -*-
"""
Testes unitários para sistema de logging
"""

import unittest
import tempfile
import logging
from pathlib import Path
import sys

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.utils.logger import setup_logger, get_logger

class TestLogger(unittest.TestCase):
    """Testes para sistema de logging"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
    
    def tearDown(self):
        """Limpeza após cada teste"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logger_setup(self):
        """Testa configuração do logger"""
        logger = setup_logger("test_logger", str(self.log_dir))
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger")
    
    def test_log_file_creation(self):
        """Testa criação de arquivo de log"""
        logger = setup_logger("test_logger", str(self.log_dir))
        logger.info("Teste de log")
        
        # Verificar se arquivo foi criado
        log_files = list(self.log_dir.glob("*.log"))
        self.assertGreater(len(log_files), 0)
    
    def test_log_levels(self):
        """Testa diferentes níveis de log"""
        logger = setup_logger("test_logger", str(self.log_dir))
        
        # Testar diferentes níveis
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Verificar se logs foram escritos
        log_files = list(self.log_dir.glob("*.log"))
        self.assertGreater(len(log_files), 0)
        
        # Ler conteúdo do log
        with open(log_files[0], 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        self.assertIn("Info message", log_content)
        self.assertIn("Warning message", log_content)
        self.assertIn("Error message", log_content)
    
    def test_get_logger(self):
        """Testa função get_logger"""
        logger1 = get_logger("test_logger_1")
        logger2 = get_logger("test_logger_1")  # Mesmo nome
        logger3 = get_logger("test_logger_2")  # Nome diferente
        
        # Verificar que loggers com mesmo nome são o mesmo objeto
        self.assertIs(logger1, logger2)
        self.assertIsNot(logger1, logger3)

if __name__ == '__main__':
    unittest.main()
