
# -*- coding: utf-8 -*-
"""
Testes de integração do sistema completo
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import sqlite3
from datetime import datetime, timedelta

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.database.database_manager import DatabaseManager
from src.utils.logger import setup_logger
from src.utils.data_validator import DataValidator

class TestSystemIntegration(unittest.TestCase):
    """Testes de integração do sistema"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = Path(self.temp_dir) / "test_integration.db"
        self.log_dir = Path(self.temp_dir) / "logs"
        
        # Configurar componentes
        self.db_manager = DatabaseManager(str(self.test_db_path))
        self.db_manager.initialize_database()  # Inicializar o banco de dados
        self.logger = setup_logger("integration_test", str(self.log_dir))
        self.validator = DataValidator()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_data_flow(self):
        """Testa fluxo completo de dados"""
        # 1. Validar dados
        test_data = {
            'data': '2025-01-01',
            'valor': 1500.75,
            'descricao': 'Teste integração completa',
            'categoria': 'Receita'
        }
        
        is_valid, errors, warnings = self.validator.validate_financial_data(test_data)
        self.assertTrue(is_valid)
        
        # 2. Inserir no banco
        insert_id = self.db_manager.insert_financial_data(test_data)
        self.assertIsNotNone(insert_id)
        
        # 3. Consultar dados
        retrieved_data = self.db_manager.get_financial_data_by_id(insert_id)
        self.assertIsNotNone(retrieved_data)
        self.assertEqual(retrieved_data['descricao'], test_data['descricao'])
        
        # 4. Atualizar dados
        update_data = {'descricao': 'Descrição atualizada'}
        update_result = self.db_manager.update_financial_data(insert_id, update_data)
        self.assertTrue(update_result)
        
        # 5. Verificar atualização
        updated_data = self.db_manager.get_financial_data_by_id(insert_id)
        self.assertEqual(updated_data['descricao'], 'Descrição atualizada')
        
        # 6. Log da operação
        self.logger.info(f"Teste de integração concluído para ID {insert_id}")
        
        # 7. Verificar log
        log_files = list(self.log_dir.glob("*.log"))
        self.assertGreater(len(log_files), 0)
    
    def test_batch_operations(self):
        """Testa operações em lote"""
        # Preparar dados em lote
        batch_data = []
        for i in range(10):
            data = {
                'data': f'2025-01-{i+1:02d}',
                'valor': 100.0 * (i + 1),
                'descricao': f'Lote item {i+1}',
                'categoria': f'Cat{i+1}'
            }
            batch_data.append(data)
        
        # Inserir em lote
        inserted_ids = []
        for data in batch_data:
            # Validar cada item
            is_valid, errors, warnings = self.validator.validate_financial_data(data)
            self.assertTrue(is_valid)
            
            # Inserir
            insert_id = self.db_manager.insert_financial_data(data)
            self.assertIsNotNone(insert_id)
            inserted_ids.append(insert_id)
        
        # Verificar inserções
        self.assertEqual(len(inserted_ids), 10)
        
        # Consultar todos os dados
        all_data = self.db_manager.query_financial_data()
        self.assertGreaterEqual(len(all_data), 10)
        
        # Log da operação
        self.logger.info(f"Operação em lote concluída: {len(inserted_ids)} registros")
    
    def test_error_handling_integration(self):
        """Testa tratamento de erros integrado"""
        # Dados inválidos
        invalid_data = {
            'data': 'data-inválida',
            'valor': 'não-é-número',
            'descricao': '',
            'categoria': 'Categoria-Inexistente'
        }
        
        # Validação deve falhar
        is_valid, errors, warnings = self.validator.validate_financial_data(invalid_data)
        self.assertFalse(is_valid)
        
        # Log do erro
        self.logger.error(f"Dados inválidos detectados: {errors}")
        
        # Não deve inserir no banco
        try:
            insert_id = self.db_manager.insert_financial_data(invalid_data)
            self.fail("Inserção deveria ter falhado")
        except Exception as e:
            self.logger.error(f"Erro esperado na inserção: {e}")
    
    def test_database_constraints(self):
        """Testa restrições do banco de dados"""
        # Dados válidos
        valid_data = {
            'data': '2025-01-01',
            'valor': 1000.0,
            'descricao': 'Teste constraints',
            'categoria': 'Receita'
        }
        
        # Primeira inserção deve funcionar
        insert_id = self.db_manager.insert_financial_data(valid_data)
        self.assertIsNotNone(insert_id)
        
        # Testar constraints específicas (se existirem)
        # Por exemplo, não permitir valores nulos em campos obrigatórios
        invalid_data = valid_data.copy()
        invalid_data['descricao'] = None
        
        try:
            self.db_manager.insert_financial_data(invalid_data)
            self.fail("Inserção com descrição nula deveria falhar")
        except Exception:
            pass  # Esperado

if __name__ == '__main__':
    unittest.main()
