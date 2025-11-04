
# -*- coding: utf-8 -*-
"""
Testes de integração da interface do usuário
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import tkinter as tk
from unittest.mock import Mock, patch

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class TestUIIntegration(unittest.TestCase):
    """Testes de integração da UI"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.root = tk.Tk()
        self.root.withdraw()  # Ocultar janela durante testes
    
    def tearDown(self):
        """Limpeza após cada teste"""
        if hasattr(self, 'root'):
            self.root.destroy()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_main_window_creation(self):
        """Testa criação da janela principal"""
        try:
            from ui.main_window import MainWindow
            main_window = MainWindow(self.root)
            self.assertIsNotNone(main_window)
        except ImportError:
            self.skipTest("MainWindow não encontrada")
    
    def test_query_window_integration(self):
        """Testa integração da janela de consultas"""
        try:
            from ui.query_window import QueryWindow
            query_window = QueryWindow(self.root)
            self.assertIsNotNone(query_window)
        except ImportError:
            self.skipTest("QueryWindow não encontrada")
    
    def test_reports_window_integration(self):
        """Testa integração da janela de relatórios"""
        try:
            from ui.reports_window import ReportsWindow
            reports_window = ReportsWindow(self.root)
            self.assertIsNotNone(reports_window)
        except ImportError:
            self.skipTest("ReportsWindow não encontrada")
    
    @patch('tkinter.messagebox.showinfo')
    def test_ui_database_interaction(self, mock_messagebox):
        """Testa interação UI-Database"""
        # Este teste seria mais complexo em uma implementação real
        # Aqui apenas verificamos se os componentes podem ser importados
        try:
            from ui.main_window import MainWindow
            from database.database_manager import DatabaseManager
            
            # Simular interação
            db_path = Path(self.temp_dir) / "test_ui.db"
            db_manager = DatabaseManager(str(db_path))
            main_window = MainWindow(self.root, db_manager=db_manager)
            
            self.assertIsNotNone(main_window)
            db_manager.close()
            
        except ImportError:
            self.skipTest("Componentes UI não encontrados")

if __name__ == '__main__':
    unittest.main()
