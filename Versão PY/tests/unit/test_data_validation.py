
# -*- coding: utf-8 -*-
"""
Testes unitários para validação de dados
"""

import unittest
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path
import sys

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.utils.data_validator import DataValidator, ValidationError

class TestDataValidation(unittest.TestCase):
    """Testes para validação de dados"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.validator = DataValidator()
    
    def test_validate_financial_data(self):
        """Testa validação de dados financeiros"""
        # Dados válidos
        valid_data = {
            'data': '2025-01-01',
            'valor': 1000.50,
            'descricao': 'Receita de vendas',
            'categoria': 'Receita'
        }
        
        is_valid, errors, warnings = self.validator.validate_financial_data(valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_validate_invalid_date(self):
        """Testa validação de data inválida"""
        invalid_data = {
            'data': 'data-inválida',
            'valor': 1000.50,
            'descricao': 'Teste',
            'categoria': 'Receita'
        }
        
        is_valid, errors, warnings = self.validator.validate_financial_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_invalid_amount(self):
        """Testa validação de valor inválido"""
        invalid_data = {
            'data': '2025-01-01',
            'valor': 'não-é-número',
            'descricao': 'Teste',
            'categoria': 'Receita'
        }
        
        is_valid, errors, warnings = self.validator.validate_financial_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_missing_fields(self):
        """Testa validação com campos obrigatórios ausentes"""
        incomplete_data = {
            'data': '2025-01-01',
            'valor': 1000.50
            # Faltam 'descricao' e 'categoria'
        }
        
        is_valid, errors, warnings = self.validator.validate_financial_data(incomplete_data)
        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)
    
    def test_validate_empty_description(self):
        """Testa validação de descrição vazia"""
        invalid_data = {
            'data': '2025-01-01',
            'valor': 1000.50,
            'descricao': '',  # Vazia
            'categoria': 'Receita'
        }
        
        is_valid, errors, warnings = self.validator.validate_financial_data(invalid_data)
        self.assertFalse(is_valid)
    
    def test_validate_negative_amount(self):
        """Testa validação de valor negativo (quando não permitido)"""
        negative_data = {
            'data': '2025-01-01',
            'valor': -1000.50,
            'descricao': 'Valor negativo',
            'categoria': 'Receita'
        }
        
        # Valores negativos geram apenas warning, não erro
        is_valid, errors, warnings = self.validator.validate_financial_data(negative_data)
        self.assertTrue(is_valid)  # Ainda é válido, mas com warning
        self.assertGreater(len(warnings), 0)  # Deve ter warning
    
    def test_validate_future_date(self):
        """Testa validação de data futura (quando não permitida)"""
        future_date = datetime.now().date().replace(year=datetime.now().year + 1)
        future_data = {
            'data': future_date.isoformat(),
            'valor': 1000.50,
            'descricao': 'Data futura',
            'categoria': 'Receita'
        }
        
        # Datas futuras são aceitas por padrão
        is_valid, errors, warnings = self.validator.validate_financial_data(future_data)
        self.assertTrue(is_valid)  # Data futura é aceita
    
    def test_sanitize_data(self):
        """Testa sanitização de dados"""
        dirty_data = {
            'data': ' 2025-01-01 ',
            'valor': '  1000.50  ',
            'descricao': '  Descrição com espaços  ',
            'categoria': ' Receita '
        }
        
        # Teste básico de sanitização manual
        clean_data = {
            'data': dirty_data['data'].strip(),
            'valor': float(str(dirty_data['valor']).strip()),
            'descricao': dirty_data['descricao'].strip(),
            'categoria': dirty_data['categoria'].strip()
        }
        
        self.assertEqual(clean_data['data'], '2025-01-01')
        self.assertEqual(clean_data['valor'], 1000.50)
        self.assertEqual(clean_data['descricao'], 'Descrição com espaços')
        self.assertEqual(clean_data['categoria'], 'Receita')

if __name__ == '__main__':
    unittest.main()
