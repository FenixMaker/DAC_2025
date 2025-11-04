
# -*- coding: utf-8 -*-
"""
Fixtures e dados de teste
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any

class TestDataFixtures:
    """Fixtures de dados para testes"""
    
    @staticmethod
    def get_valid_financial_data() -> Dict[str, Any]:
        """Retorna dados financeiros válidos para teste"""
        return {
            'data': '2025-01-01',
            'valor': 1000.50,
            'descricao': 'Receita de teste',
            'categoria': 'Receita'
        }
    
    @staticmethod
    def get_invalid_financial_data() -> List[Dict[str, Any]]:
        """Retorna lista de dados financeiros inválidos"""
        return [
            {
                'data': 'data-inválida',
                'valor': 1000.50,
                'descricao': 'Teste',
                'categoria': 'Receita'
            },
            {
                'data': '2025-01-01',
                'valor': 'não-é-número',
                'descricao': 'Teste',
                'categoria': 'Receita'
            },
            {
                'data': '2025-01-01',
                'valor': 1000.50,
                'descricao': '',  # Vazia
                'categoria': 'Receita'
            },
            {
                'data': '2025-01-01',
                'valor': 1000.50,
                'descricao': 'Teste'
                # Falta categoria
            }
        ]
    
    @staticmethod
    def get_batch_financial_data(count: int = 10) -> List[Dict[str, Any]]:
        """Retorna lote de dados financeiros para teste"""
        batch_data = []
        base_date = datetime(2025, 1, 1)
        
        for i in range(count):
            date_obj = base_date + timedelta(days=i)
            data = {
                'data': date_obj.strftime('%Y-%m-%d'),
                'valor': 100.0 * (i + 1),
                'descricao': f'Lote item {i + 1}',
                'categoria': 'Receita' if i % 2 == 0 else 'Despesa'
            }
            batch_data.append(data)
        
        return batch_data
    
    @staticmethod
    def get_performance_test_data(count: int = 1000) -> List[Dict[str, Any]]:
        """Retorna dados para testes de performance"""
        return TestDataFixtures.get_batch_financial_data(count)
    
    @staticmethod
    def get_database_config() -> Dict[str, Any]:
        """Retorna configuração de banco para testes"""
        return {
            'database_type': 'sqlite',
            'test_database_name': 'test_dac.db',
            'memory_database': ':memory:',
            'pragma_settings': {
                'journal_mode': 'WAL',
                'synchronous': 'NORMAL',
                'cache_size': 10000,
                'temp_store': 'MEMORY'
            }
        }
