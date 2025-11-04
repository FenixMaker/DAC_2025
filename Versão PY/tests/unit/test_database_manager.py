
# -*- coding: utf-8 -*-
"""
Testes unitários para DatabaseManager
"""

import unittest
import tempfile
import sqlite3
from pathlib import Path
import sys
from sqlalchemy import text

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.database.database_manager import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    """Testes para DatabaseManager"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = Path(self.temp_dir) / "test_dac.db"
        self.db_manager = DatabaseManager(str(self.test_db_path))
        # Inicializar o banco de dados
        self.db_manager.initialize_database()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_database_creation(self):
        """Testa criação do banco de dados"""
        self.assertTrue(self.test_db_path.exists())
        # Testar se consegue obter uma conexão
        with self.db_manager.connection as conn:
            self.assertIsNotNone(conn)
    
    def test_table_creation(self):
        """Testa criação de tabelas"""
        # Verificar se pelo menos uma tabela foi criada usando SQLAlchemy
        session = self.db_manager.get_session()
        try:
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = result.fetchall()
            table_names = [table[0] for table in tables]
            
            # Verificar se pelo menos algumas tabelas foram criadas
            self.assertGreater(len(table_names), 0, "Nenhuma tabela foi criada")
            
            # Verificar se existe pelo menos a tabela regions (que usamos nos métodos financeiros)
            expected_tables = ['regions']
            for table in expected_tables:
                self.assertIn(table, table_names, f"Tabela {table} não encontrada")
        finally:
            session.close()
    
    def test_insert_data(self):
        """Testa inserção de dados"""
        test_data = {
            'data': '2025-01-01',
            'valor': 1000.50,
            'descricao': 'Teste unitário',
            'categoria': 'Receita'
        }
        
        result = self.db_manager.insert_financial_data(test_data)
        self.assertTrue(result)
        
        results = self.db_manager.query_financial_data()
        self.assertGreater(len(results), 0)
    
    def test_query_data(self):
        """Testa consulta de dados"""
        test_data = {
            'data': '2025-01-01',
            'valor': 1000.50,
            'descricao': 'Teste consulta',
            'categoria': 'Receita'
        }
        self.db_manager.insert_financial_data(test_data)
        
        results = self.db_manager.query_financial_data()
        self.assertGreater(len(results), 0)
        found_test_record = any(r['descricao'] == 'Teste consulta' for r in results)
        self.assertTrue(found_test_record, "Registro de teste não encontrado")
    
    def test_update_data(self):
        """Testa atualização de dados"""
        test_data = {
            'data': '2025-01-01',
            'valor': 1000.50,
            'descricao': 'Teste original',
            'categoria': 'Receita'
        }
        insert_id = self.db_manager.insert_financial_data(test_data)
        
        update_data = {'descricao': 'Teste atualizado'}
        result = self.db_manager.update_financial_data(insert_id, update_data)
        self.assertTrue(result)
        
        updated_record = self.db_manager.get_financial_data_by_id(insert_id)
        self.assertEqual(updated_record['descricao'], 'Teste atualizado')
    
    def test_delete_data(self):
        """Testa exclusão de dados"""
        test_data = {
            'data': '2025-01-01',
            'valor': 1000.50,
            'descricao': 'Teste exclusão',
            'categoria': 'Receita'
        }
        insert_id = self.db_manager.insert_financial_data(test_data)
        
        result = self.db_manager.delete_financial_data(insert_id)
        self.assertTrue(result)
        
        deleted_record = self.db_manager.get_financial_data_by_id(insert_id)
        self.assertIsNone(deleted_record)
    
    def test_transaction_rollback(self):
        """Testa rollback de transação"""
        # Contar registros antes do teste
        initial_results = self.db_manager.query_financial_data()
        initial_count = len(initial_results)
        
        # Tentar inserir dados em uma transação que falhará
        session = self.db_manager.get_session()
        try:
            from src.database.models import Region
            
            # Inserir dados válidos
            test_region = Region(
                code='ROLLBACK',
                name='Teste transação',
                state='Teste',
                macro_region='Teste',
                description='Teste de rollback'
            )
            session.add(test_region)
            
            # Forçar erro para testar rollback
            raise Exception("Erro forçado para teste")
            
        except Exception:
            session.rollback()  # Rollback explícito
        finally:
            session.close()
        
        # Verificar que os dados não foram commitados
        final_results = self.db_manager.query_financial_data()
        final_count = len(final_results)
        
        # O número de registros deve ser o mesmo
        self.assertEqual(initial_count, final_count, "Rollback não funcionou corretamente")
        
        # Verificar que não há registros com a descrição de teste
        test_records = [r for r in final_results if 'Teste transação' in r.get('descricao', '')]
        self.assertEqual(len(test_records), 0, "Registro de teste encontrado após rollback")

if __name__ == '__main__':
    unittest.main()
