#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador de Integridade de Dados Expandido
Responsável por validar a qualidade e integridade dos dados no sistema expandido
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import pandas as pd
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
import re

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.utils.logger import get_logger
    from src.database.enhanced_models import get_all_models
except ImportError as e:
    print(f"Erro de importação: {e}")
    sys.exit(1)

class EnhancedDataValidator:
    """
    Validador de integridade e qualidade de dados expandido
    """
    
    def __init__(self, db_path: str = "dac_enhanced.db"):
        self.logger = get_logger(__name__)
        self.db_path = db_path
        self.engine = None
        self.session = None
        
        # Resultados de validação
        self.validation_results = {
            'timestamp': datetime.utcnow(),
            'database_path': db_path,
            'overall_status': 'pending',
            'total_checks': 0,
            'passed_checks': 0,
            'failed_checks': 0,
            'warnings': 0,
            'critical_errors': 0,
            'tables': {},
            'data_quality_metrics': {},
            'recommendations': []
        }
        
        # Regras de validação expandidas
        self.validation_rules = {
            'regions': {
                'required_fields': ['id', 'code', 'name', 'state'],
                'unique_fields': ['id', 'code'],
                'data_types': {
                    'id': int,
                    'code': str,
                    'name': str,
                    'state': str,
                    'population': int,
                    'area_km2': float
                },
                'constraints': {
                    'code': {'min_length': 2, 'max_length': 10},
                    'name': {'min_length': 3, 'max_length': 100},
                    'population': {'min_value': 0},
                    'area_km2': {'min_value': 0.1},
                    'urban_population_percentage': {'min_value': 0, 'max_value': 100},
                    'rural_population_percentage': {'min_value': 0, 'max_value': 100}
                }
            },
            'households': {
                'required_fields': ['id', 'region_id', 'city', 'area_type', 'household_size'],
                'unique_fields': ['id'],
                'foreign_keys': {'region_id': 'regions.id'},
                'data_types': {
                    'id': int,
                    'region_id': int,
                    'household_size': int,
                    'has_internet': bool,
                    'income_value_min': float,
                    'income_value_max': float,
                    'digital_devices_count': int,
                    'monthly_internet_cost': float,
                    'extraction_confidence': float
                },
                'constraints': {
                    'household_size': {'min_value': 1, 'max_value': 20},
                    'income_value_min': {'min_value': 0},
                    'income_value_max': {'min_value': 0},
                    'digital_devices_count': {'min_value': 0, 'max_value': 50},
                    'monthly_internet_cost': {'min_value': 0, 'max_value': 10000},
                    'extraction_confidence': {'min_value': 0.0, 'max_value': 1.0}
                }
            },
            'individuals': {
                'required_fields': ['id', 'household_id', 'age', 'gender'],
                'unique_fields': ['id'],
                'foreign_keys': {'household_id': 'households.id'},
                'data_types': {
                    'id': int,
                    'household_id': int,
                    'age': int,
                    'has_disability': bool,
                    'education_years': int,
                    'monthly_income': float,
                    'extraction_confidence': float
                },
                'constraints': {
                    'age': {'min_value': 0, 'max_value': 120},
                    'education_years': {'min_value': 0, 'max_value': 25},
                    'monthly_income': {'min_value': 0, 'max_value': 100000},
                    'extraction_confidence': {'min_value': 0.0, 'max_value': 1.0}
                }
            },
            'device_usage': {
                'required_fields': ['id', 'individual_id', 'device_type'],
                'unique_fields': ['id'],
                'foreign_keys': {'individual_id': 'individuals.id'},
                'data_types': {
                    'id': int,
                    'individual_id': int,
                    'has_device': bool,
                    'device_age_years': int,
                    'sharing_with_others': bool,
                    'replacement_needs': bool,
                    'cost_barrier': bool,
                    'extraction_confidence': float
                },
                'constraints': {
                    'device_age_years': {'min_value': 0, 'max_value': 30},
                    'extraction_confidence': {'min_value': 0.0, 'max_value': 1.0}
                }
            },
            'internet_usage': {
                'required_fields': ['id', 'individual_id'],
                'unique_fields': ['id'],
                'foreign_keys': {'individual_id': 'individuals.id'},
                'data_types': {
                    'id': int,
                    'individual_id': int,
                    'uses_internet': bool,
                    'daily_usage_hours': float,
                    'first_access_age': int,
                    'years_using_internet': int,
                    'ecommerce_usage': bool,
                    'online_banking': bool,
                    'online_education': bool,
                    'telehealth_usage': bool,
                    'government_services_online': bool,
                    'cost_barrier': bool,
                    'infrastructure_barrier': bool,
                    'skills_barrier': bool,
                    'accessibility_barrier': bool,
                    'content_barrier': bool,
                    'extraction_confidence': float
                },
                'constraints': {
                    'daily_usage_hours': {'min_value': 0, 'max_value': 24},
                    'first_access_age': {'min_value': 3, 'max_value': 80},
                    'years_using_internet': {'min_value': 0, 'max_value': 50},
                    'extraction_confidence': {'min_value': 0.0, 'max_value': 1.0}
                }
            },
            'accessibility_needs': {
                'required_fields': ['id', 'individual_id', 'need_type'],
                'unique_fields': ['id'],
                'foreign_keys': {'individual_id': 'individuals.id'},
                'data_types': {
                    'id': int,
                    'individual_id': int,
                    'severity_level': int,
                    'has_assistive_technology': bool,
                    'technology_effectiveness': int,
                    'barriers_score': int,
                    'support_availability': int,
                    'extraction_confidence': float
                },
                'constraints': {
                    'severity_level': {'min_value': 1, 'max_value': 5},
                    'technology_effectiveness': {'min_value': 1, 'max_value': 5},
                    'barriers_score': {'min_value': 0, 'max_value': 10},
                    'support_availability': {'min_value': 1, 'max_value': 5},
                    'extraction_confidence': {'min_value': 0.0, 'max_value': 1.0}
                }
            },
            'extracted_data': {
                'required_fields': ['id', 'source_file', 'source_year', 'category'],
                'unique_fields': ['id'],
                'data_types': {
                    'id': int,
                    'source_year': int,
                    'extraction_confidence': float,
                    'numeric_value': float
                },
                'constraints': {
                    'source_year': {'min_value': 2020, 'max_value': 2025},
                    'extraction_confidence': {'min_value': 0.0, 'max_value': 1.0},
                    'numeric_value': {'min_value': 0}
                }
            },
            'data_quality_metrics': {
                'required_fields': ['id', 'table_name', 'metric_name', 'metric_value'],
                'unique_fields': ['id'],
                'data_types': {
                    'id': int,
                    'metric_value': float,
                    'threshold_min': float,
                    'threshold_max': float
                },
                'constraints': {
                    'metric_value': {'min_value': 0, 'max_value': 100}
                }
            },
            'processing_logs': {
                'required_fields': ['id', 'process_type', 'status'],
                'unique_fields': ['id'],
                'data_types': {
                    'id': int,
                    'records_processed': int,
                    'records_successful': int,
                    'records_failed': int,
                    'processing_time_seconds': float
                },
                'constraints': {
                    'records_processed': {'min_value': 0},
                    'records_successful': {'min_value': 0},
                    'records_failed': {'min_value': 0},
                    'processing_time_seconds': {'min_value': 0}
                }
            }
        }
    
    def initialize_connection(self) -> bool:
        """
        Inicializa conexão com o banco de dados
        """
        try:
            if not os.path.exists(self.db_path):
                self.logger.error(f"Banco de dados não encontrado: {self.db_path}")
                return False
            
            self.engine = create_engine(f'sqlite:///{self.db_path}')
            SessionMaker = sessionmaker(bind=self.engine)
            self.session = SessionMaker()
            
            self.logger.info(f"Conectado ao banco de dados: {self.db_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao conectar ao banco: {e}")
            return False
    
    def validate_table_structure(self, table_name: str) -> Dict[str, Any]:
        """
        Valida a estrutura de uma tabela
        """
        validation = {
            'table_name': table_name,
            'exists': False,
            'record_count': 0,
            'structure_valid': True,
            'issues': [],
            'warnings': [],
            'statistics': {}
        }
        
        try:
            # Verificar se a tabela existe
            result = self.session.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"))
            if not result.fetchone():
                validation['exists'] = False
                validation['structure_valid'] = False
                validation['issues'].append(f"Tabela {table_name} não existe")
                return validation
            
            validation['exists'] = True
            
            # Contar registros
            result = self.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            validation['record_count'] = result.scalar()
            
            # Obter informações das colunas
            result = self.session.execute(text(f"PRAGMA table_info({table_name})"))
            columns = result.fetchall()
            
            column_names = [col[1] for col in columns]
            validation['statistics']['columns'] = column_names
            validation['statistics']['column_count'] = len(column_names)
            
            # Verificar campos obrigatórios
            if table_name in self.validation_rules:
                rules = self.validation_rules[table_name]
                
                for required_field in rules.get('required_fields', []):
                    if required_field not in column_names:
                        validation['issues'].append(f"Campo obrigatório ausente: {required_field}")
                        validation['structure_valid'] = False
            
            self.logger.debug(f"Estrutura da tabela {table_name} validada: {validation['record_count']} registros")
            
        except Exception as e:
            validation['structure_valid'] = False
            validation['issues'].append(f"Erro na validação da estrutura: {e}")
            self.logger.error(f"Erro na validação da tabela {table_name}: {e}")
        
        return validation
    
    def validate_data_integrity(self, table_name: str) -> Dict[str, Any]:
        """
        Valida a integridade dos dados de uma tabela
        """
        integrity = {
            'table_name': table_name,
            'integrity_valid': True,
            'null_checks': {},
            'uniqueness_checks': {},
            'foreign_key_checks': {},
            'constraint_checks': {},
            'business_rule_checks': {},
            'issues': [],
            'warnings': []
        }
        
        try:
            if table_name not in self.validation_rules:
                integrity['warnings'].append(f"Regras de validação não definidas para {table_name}")
                return integrity
            
            rules = self.validation_rules[table_name]
            
            # Verificar campos nulos
            for field in rules.get('required_fields', []):
                try:
                    result = self.session.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE {field} IS NULL"))
                    null_count = result.scalar()
                    
                    integrity['null_checks'][field] = {
                        'null_count': null_count,
                        'valid': null_count == 0
                    }
                    
                    if null_count > 0:
                        integrity['issues'].append(f"Campo {field} tem {null_count} valores nulos")
                        integrity['integrity_valid'] = False
                        
                except Exception as e:
                    integrity['null_checks'][field] = {'error': str(e)}
            
            # Verificar unicidade
            for field in rules.get('unique_fields', []):
                try:
                    result = self.session.execute(text(f"""
                        SELECT COUNT(*) - COUNT(DISTINCT {field}) as duplicates 
                        FROM {table_name} WHERE {field} IS NOT NULL
                    """))
                    duplicate_count = result.scalar()
                    
                    integrity['uniqueness_checks'][field] = {
                        'duplicate_count': duplicate_count,
                        'valid': duplicate_count == 0
                    }
                    
                    if duplicate_count > 0:
                        integrity['issues'].append(f"Campo {field} tem {duplicate_count} valores duplicados")
                        integrity['integrity_valid'] = False
                        
                except Exception as e:
                    integrity['uniqueness_checks'][field] = {'error': str(e)}
            
            # Verificar chaves estrangeiras
            for fk_field, ref_table_field in rules.get('foreign_keys', {}).items():
                try:
                    ref_table, ref_field = ref_table_field.split('.')
                    
                    result = self.session.execute(text(f"""
                        SELECT COUNT(*) FROM {table_name} t1
                        LEFT JOIN {ref_table} t2 ON t1.{fk_field} = t2.{ref_field}
                        WHERE t1.{fk_field} IS NOT NULL AND t2.{ref_field} IS NULL
                    """))
                    orphan_count = result.scalar()
                    
                    integrity['foreign_key_checks'][fk_field] = {
                        'orphan_count': orphan_count,
                        'valid': orphan_count == 0,
                        'references': ref_table_field
                    }
                    
                    if orphan_count > 0:
                        integrity['issues'].append(f"Campo {fk_field} tem {orphan_count} referências órfãs")
                        integrity['integrity_valid'] = False
                        
                except Exception as e:
                    integrity['foreign_key_checks'][fk_field] = {'error': str(e)}
            
            # Verificar restrições de valores
            for field, constraints in rules.get('constraints', {}).items():
                try:
                    field_checks = {'field': field, 'valid': True, 'violations': []}
                    
                    # Verificar valor mínimo
                    if 'min_value' in constraints:
                        min_val = constraints['min_value']
                        result = self.session.execute(text(f"""
                            SELECT COUNT(*) FROM {table_name} 
                            WHERE {field} IS NOT NULL AND {field} < {min_val}
                        """))
                        violations = result.scalar()
                        
                        if violations > 0:
                            field_checks['violations'].append(f"{violations} valores abaixo do mínimo ({min_val})")
                            field_checks['valid'] = False
                    
                    # Verificar valor máximo
                    if 'max_value' in constraints:
                        max_val = constraints['max_value']
                        result = self.session.execute(text(f"""
                            SELECT COUNT(*) FROM {table_name} 
                            WHERE {field} IS NOT NULL AND {field} > {max_val}
                        """))
                        violations = result.scalar()
                        
                        if violations > 0:
                            field_checks['violations'].append(f"{violations} valores acima do máximo ({max_val})")
                            field_checks['valid'] = False
                    
                    # Verificar comprimento mínimo (para strings)
                    if 'min_length' in constraints:
                        min_len = constraints['min_length']
                        result = self.session.execute(text(f"""
                            SELECT COUNT(*) FROM {table_name} 
                            WHERE {field} IS NOT NULL AND LENGTH({field}) < {min_len}
                        """))
                        violations = result.scalar()
                        
                        if violations > 0:
                            field_checks['violations'].append(f"{violations} valores com comprimento abaixo do mínimo ({min_len})")
                            field_checks['valid'] = False
                    
                    # Verificar comprimento máximo (para strings)
                    if 'max_length' in constraints:
                        max_len = constraints['max_length']
                        result = self.session.execute(text(f"""
                            SELECT COUNT(*) FROM {table_name} 
                            WHERE {field} IS NOT NULL AND LENGTH({field}) > {max_len}
                        """))
                        violations = result.scalar()
                        
                        if violations > 0:
                            field_checks['violations'].append(f"{violations} valores com comprimento acima do máximo ({max_len})")
                            field_checks['valid'] = False
                    
                    integrity['constraint_checks'][field] = field_checks
                    
                    if not field_checks['valid']:
                        integrity['issues'].extend([f"Campo {field}: {v}" for v in field_checks['violations']])
                        integrity['integrity_valid'] = False
                        
                except Exception as e:
                    integrity['constraint_checks'][field] = {'error': str(e)}
            
            # Verificações de regras de negócio específicas
            business_checks = self._validate_business_rules(table_name)
            integrity['business_rule_checks'] = business_checks
            
            if not business_checks.get('valid', True):
                integrity['issues'].extend(business_checks.get('violations', []))
                integrity['integrity_valid'] = False
            
            self.logger.debug(f"Integridade da tabela {table_name} validada: {'válida' if integrity['integrity_valid'] else 'inválida'}")
            
        except Exception as e:
            integrity['integrity_valid'] = False
            integrity['issues'].append(f"Erro na validação de integridade: {e}")
            self.logger.error(f"Erro na validação de integridade da tabela {table_name}: {e}")
        
        return integrity
    
    def _validate_business_rules(self, table_name: str) -> Dict[str, Any]:
        """
        Valida regras de negócio específicas por tabela
        """
        business_validation = {
            'valid': True,
            'violations': [],
            'checks_performed': []
        }
        
        try:
            if table_name == 'households':
                # Verificar se income_min <= income_max
                result = self.session.execute(text("""
                    SELECT COUNT(*) FROM households 
                    WHERE income_value_min IS NOT NULL 
                    AND income_value_max IS NOT NULL 
                    AND income_value_min > income_value_max
                """))
                violations = result.scalar()
                
                business_validation['checks_performed'].append('income_range_consistency')
                if violations > 0:
                    business_validation['violations'].append(f"{violations} domicílios com renda mínima maior que máxima")
                    business_validation['valid'] = False
                
                # Verificar se percentuais urbano + rural = 100% (para regiões)
                if table_name == 'regions':
                    result = self.session.execute(text("""
                        SELECT COUNT(*) FROM regions 
                        WHERE urban_population_percentage IS NOT NULL 
                        AND rural_population_percentage IS NOT NULL 
                        AND ABS((urban_population_percentage + rural_population_percentage) - 100) > 1
                    """))
                    violations = result.scalar()
                    
                    business_validation['checks_performed'].append('population_percentage_sum')
                    if violations > 0:
                        business_validation['violations'].append(f"{violations} regiões com percentuais de população inconsistentes")
                        business_validation['valid'] = False
            
            elif table_name == 'individuals':
                # Verificar se idade é consistente com anos de educação
                result = self.session.execute(text("""
                    SELECT COUNT(*) FROM individuals 
                    WHERE age IS NOT NULL 
                    AND education_years IS NOT NULL 
                    AND education_years > (age - 5)
                """))
                violations = result.scalar()
                
                business_validation['checks_performed'].append('age_education_consistency')
                if violations > 0:
                    business_validation['violations'].append(f"{violations} indivíduos com anos de educação inconsistentes com idade")
                    business_validation['valid'] = False
            
            elif table_name == 'internet_usage':
                # Verificar se first_access_age <= idade atual do indivíduo
                result = self.session.execute(text("""
                    SELECT COUNT(*) FROM internet_usage iu
                    JOIN individuals i ON iu.individual_id = i.id
                    WHERE iu.first_access_age IS NOT NULL 
                    AND i.age IS NOT NULL 
                    AND iu.first_access_age > i.age
                """))
                violations = result.scalar()
                
                business_validation['checks_performed'].append('first_access_age_consistency')
                if violations > 0:
                    business_validation['violations'].append(f"{violations} registros com idade de primeiro acesso maior que idade atual")
                    business_validation['valid'] = False
                
                # Verificar se years_using_internet <= (idade - first_access_age)
                result = self.session.execute(text("""
                    SELECT COUNT(*) FROM internet_usage iu
                    JOIN individuals i ON iu.individual_id = i.id
                    WHERE iu.years_using_internet IS NOT NULL 
                    AND iu.first_access_age IS NOT NULL 
                    AND i.age IS NOT NULL 
                    AND iu.years_using_internet > (i.age - iu.first_access_age)
                """))
                violations = result.scalar()
                
                business_validation['checks_performed'].append('years_using_consistency')
                if violations > 0:
                    business_validation['violations'].append(f"{violations} registros com anos de uso inconsistentes")
                    business_validation['valid'] = False
            
            elif table_name == 'extracted_data':
                # Verificar se dados extraídos têm confiança mínima aceitável
                result = self.session.execute(text("""
                    SELECT COUNT(*) FROM extracted_data 
                    WHERE extraction_confidence < 0.5
                """))
                low_confidence = result.scalar()
                
                business_validation['checks_performed'].append('extraction_confidence_threshold')
                if low_confidence > 0:
                    business_validation['violations'].append(f"{low_confidence} registros com confiança de extração baixa (<50%)")
                    # Não marca como inválido, apenas aviso
                
        except Exception as e:
            business_validation['error'] = str(e)
            self.logger.warning(f"Erro na validação de regras de negócio para {table_name}: {e}")
        
        return business_validation
    
    def calculate_data_quality_metrics(self, table_name: str) -> Dict[str, Any]:
        """
        Calcula métricas de qualidade dos dados expandidas
        """
        metrics = {
            'table_name': table_name,
            'completeness': {},
            'consistency': {},
            'accuracy': {},
            'timeliness': {},
            'validity': {},
            'uniqueness': {},
            'overall_score': 0.0
        }
        
        try:
            # Obter contagem total de registros
            result = self.session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            total_records = result.scalar()
            
            if total_records == 0:
                metrics['overall_score'] = 0.0
                return metrics
            
            # Calcular completude (% de campos não nulos)
            result = self.session.execute(text(f"PRAGMA table_info({table_name})"))
            columns = [col[1] for col in result.fetchall()]
            
            completeness_scores = []
            for column in columns:
                try:
                    result = self.session.execute(text(f"""
                        SELECT COUNT(*) FROM {table_name} WHERE {column} IS NOT NULL
                    """))
                    non_null_count = result.scalar()
                    completeness = (non_null_count / total_records) * 100
                    
                    metrics['completeness'][column] = {
                        'non_null_count': non_null_count,
                        'total_count': total_records,
                        'completeness_percentage': completeness
                    }
                    
                    completeness_scores.append(completeness)
                    
                except Exception as e:
                    metrics['completeness'][column] = {'error': str(e)}
            
            # Calcular unicidade
            uniqueness_scores = []
            if table_name in self.validation_rules:
                unique_fields = self.validation_rules[table_name].get('unique_fields', [])
                for field in unique_fields:
                    try:
                        result = self.session.execute(text(f"""
                            SELECT COUNT(DISTINCT {field}) as unique_count,
                                   COUNT({field}) as total_count
                            FROM {table_name} WHERE {field} IS NOT NULL
                        """))
                        stats = result.fetchone()
                        
                        if stats and stats[1] > 0:
                            uniqueness = (stats[0] / stats[1]) * 100
                            metrics['uniqueness'][field] = {
                                'unique_count': stats[0],
                                'total_count': stats[1],
                                'uniqueness_percentage': uniqueness
                            }
                            uniqueness_scores.append(uniqueness)
                            
                    except Exception as e:
                        metrics['uniqueness'][field] = {'error': str(e)}
            
            # Calcular validade (conformidade com restrições)
            validity_scores = []
            if table_name in self.validation_rules:
                constraints = self.validation_rules[table_name].get('constraints', {})
                for field, field_constraints in constraints.items():
                    try:
                        valid_count = total_records
                        
                        # Verificar restrições de valor
                        if 'min_value' in field_constraints:
                            result = self.session.execute(text(f"""
                                SELECT COUNT(*) FROM {table_name} 
                                WHERE {field} IS NOT NULL AND {field} < {field_constraints['min_value']}
                            """))
                            valid_count -= result.scalar()
                        
                        if 'max_value' in field_constraints:
                            result = self.session.execute(text(f"""
                                SELECT COUNT(*) FROM {table_name} 
                                WHERE {field} IS NOT NULL AND {field} > {field_constraints['max_value']}
                            """))
                            valid_count -= result.scalar()
                        
                        validity = (valid_count / total_records) * 100
                        metrics['validity'][field] = {
                            'valid_count': valid_count,
                            'total_count': total_records,
                            'validity_percentage': validity
                        }
                        validity_scores.append(validity)
                        
                    except Exception as e:
                        metrics['validity'][field] = {'error': str(e)}
            
            # Calcular consistência (para dados extraídos)
            if table_name == 'extracted_data':
                try:
                    # Verificar consistência de confiança
                    result = self.session.execute(text("""
                        SELECT AVG(extraction_confidence) as avg_confidence,
                               STDDEV(extraction_confidence) as std_confidence
                        FROM extracted_data 
                        WHERE extraction_confidence IS NOT NULL
                    """))
                    stats = result.fetchone()
                    
                    if stats and stats[0] is not None:
                        avg_confidence = stats[0]
                        std_confidence = stats[1] or 0
                        
                        # Consistência baseada na variabilidade da confiança
                        consistency_score = max(0, 100 - (std_confidence * 100))
                        
                        metrics['consistency']['confidence_consistency'] = {
                            'average_confidence': avg_confidence,
                            'std_confidence': std_confidence,
                            'consistency_score': consistency_score
                        }
                    
                    # Verificar distribuição por ano
                    result = self.session.execute(text("""
                        SELECT source_year, COUNT(*) as count 
                        FROM extracted_data 
                        GROUP BY source_year 
                        ORDER BY source_year
                    """))
                    year_distribution = dict(result.fetchall())
                    
                    metrics['consistency']['year_distribution'] = year_distribution
                    
                except Exception as e:
                    metrics['consistency']['error'] = str(e)
            
            # Calcular precisão (para campos numéricos)
            numeric_fields = ['age', 'household_size', 'income_value_min', 'income_value_max', 
                            'extraction_confidence', 'numeric_value', 'daily_usage_hours']
            
            accuracy_scores = []
            for field in numeric_fields:
                if field in columns:
                    try:
                        result = self.session.execute(text(f"""
                            SELECT 
                                COUNT(*) as total,
                                COUNT(CASE WHEN {field} >= 0 THEN 1 END) as valid_range,
                                AVG({field}) as average,
                                MIN({field}) as minimum,
                                MAX({field}) as maximum,
                                STDDEV({field}) as std_dev
                            FROM {table_name} 
                            WHERE {field} IS NOT NULL
                        """))
                        
                        stats = result.fetchone()
                        if stats and stats[0] > 0:
                            accuracy_score = (stats[1] / stats[0]) * 100
                            
                            metrics['accuracy'][field] = {
                                'total_values': stats[0],
                                'valid_values': stats[1],
                                'accuracy_percentage': accuracy_score,
                                'average': stats[2],
                                'minimum': stats[3],
                                'maximum': stats[4],
                                'std_deviation': stats[5]
                            }
                            
                            accuracy_scores.append(accuracy_score)
                            
                    except Exception as e:
                        metrics['accuracy'][field] = {'error': str(e)}
            
            # Calcular atualidade (para campos de timestamp)
            timestamp_fields = ['created_at', 'last_updated', 'processing_timestamp']
            
            timeliness_scores = []
            for field in timestamp_fields:
                if field in columns:
                    try:
                        result = self.session.execute(text(f"""
                            SELECT 
                                COUNT(*) as total,
                                MAX({field}) as latest,
                                MIN({field}) as earliest
                            FROM {table_name} 
                            WHERE {field} IS NOT NULL
                        """))
                        
                        stats = result.fetchone()
                        if stats and stats[0] > 0:
                            # Calcular idade dos dados em dias
                            if stats[1]:  # latest timestamp
                                try:
                                    latest_date = datetime.fromisoformat(stats[1].replace('Z', '+00:00'))
                                    days_old = (datetime.utcnow() - latest_date).days
                                    
                                    timeliness_score = max(0, 100 - (days_old * 2))  # 2% por dia
                                    
                                    metrics['timeliness'][field] = {
                                        'total_records': stats[0],
                                        'latest_timestamp': stats[1],
                                        'earliest_timestamp': stats[2],
                                        'days_since_latest': days_old,
                                        'timeliness_score': timeliness_score
                                    }
                                    
                                    timeliness_scores.append(timeliness_score)
                                    
                                except Exception:
                                    metrics['timeliness'][field] = {'parsing_error': 'Invalid timestamp format'}
                            
                    except Exception as e:
                        metrics['timeliness'][field] = {'error': str(e)}
            
            # Calcular score geral ponderado
            scores = []
            weights = []
            
            # Score de completude (peso 25%)
            if completeness_scores:
                avg_completeness = sum(completeness_scores) / len(completeness_scores)
                scores.append(avg_completeness)
                weights.append(0.25)
            
            # Score de unicidade (peso 20%)
            if uniqueness_scores:
                avg_uniqueness = sum(uniqueness_scores) / len(uniqueness_scores)
                scores.append(avg_uniqueness)
                weights.append(0.20)
            
            # Score de validade (peso 20%)
            if validity_scores:
                avg_validity = sum(validity_scores) / len(validity_scores)
                scores.append(avg_validity)
                weights.append(0.20)
            
            # Score de precisão (peso 20%)
            if accuracy_scores:
                avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)
                scores.append(avg_accuracy)
                weights.append(0.20)
            
            # Score de atualidade (peso 15%)
            if timeliness_scores:
                avg_timeliness = sum(timeliness_scores) / len(timeliness_scores)
                scores.append(avg_timeliness)
                weights.append(0.15)
            
            # Score geral ponderado
            if scores and weights:
                # Normalizar pesos
                total_weight = sum(weights)
                normalized_weights = [w / total_weight for w in weights]
                
                metrics['overall_score'] = sum(score * weight for score, weight in zip(scores, normalized_weights))
            
            self.logger.debug(f"Métricas de qualidade calculadas para {table_name}: score {metrics['overall_score']:.2f}")
            
        except Exception as e:
            metrics['error'] = str(e)
            self.logger.error(f"Erro no cálculo de métricas para {table_name}: {e}")
        
        return metrics
    
    def generate_recommendations(self) -> List[str]:
        """
        Gera recomendações baseadas nos resultados da validação
        """
        recommendations = []
        
        try:
            # Analisar resultados por tabela
            for table_name, table_results in self.validation_results['tables'].items():
                structure = table_results.get('structure', {})
                integrity = table_results.get('integrity', {})
                quality = table_results.get('quality_metrics', {})
                
                # Recomendações de estrutura
                if not structure.get('structure_valid', True):
                    recommendations.append(f"🔧 Corrigir problemas de estrutura na tabela {table_name}")
                
                # Recomendações de integridade
                if not integrity.get('integrity_valid', True):
                    recommendations.append(f"🔗 Resolver problemas de integridade na tabela {table_name}")
                
                # Recomendações de qualidade
                overall_score = quality.get('overall_score', 0)
                if overall_score < 70:
                    recommendations.append(f"📊 Melhorar qualidade dos dados na tabela {table_name} (score: {overall_score:.1f}%)")
                elif overall_score < 85:
                    recommendations.append(f"📈 Otimizar qualidade dos dados na tabela {table_name} (score: {overall_score:.1f}%)")
                
                # Recomendações específicas de completude
                completeness = quality.get('completeness', {})
                for field, field_metrics in completeness.items():
                    if isinstance(field_metrics, dict):
                        completeness_pct = field_metrics.get('completeness_percentage', 100)
                        if completeness_pct < 50:
                            recommendations.append(f"⚠️ Campo {field} na tabela {table_name} tem completude crítica ({completeness_pct:.1f}%)")
                        elif completeness_pct < 80:
                            recommendations.append(f"📝 Melhorar completude do campo {field} na tabela {table_name} ({completeness_pct:.1f}%)")
                
                # Recomendações específicas de unicidade
                uniqueness = quality.get('uniqueness', {})
                for field, field_metrics in uniqueness.items():
                    if isinstance(field_metrics, dict):
                        uniqueness_pct = field_metrics.get('uniqueness_percentage', 100)
                        if uniqueness_pct < 100:
                            recommendations.append(f"🔑 Resolver duplicatas no campo {field} da tabela {table_name} ({uniqueness_pct:.1f}% único)")
                
                # Recomendações de regras de negócio
                business_rules = integrity.get('business_rule_checks', {})
                if not business_rules.get('valid', True):
                    recommendations.append(f"📋 Corrigir violações de regras de negócio na tabela {table_name}")
            
            # Recomendações gerais baseadas em estatísticas
            if self.validation_results['failed_checks'] > 0:
                recommendations.append("🧹 Implementar processo automatizado de limpeza de dados")
            
            if self.validation_results['critical_errors'] > 0:
                recommendations.append("🚨 Corrigir erros críticos antes de usar os dados em produção")
            
            if self.validation_results['warnings'] > 10:
                recommendations.append("⚡ Revisar e resolver avisos de qualidade de dados")
            
            # Recomendações de monitoramento
            recommendations.append("📊 Implementar dashboard de monitoramento contínuo de qualidade")
            recommendations.append("🔔 Criar alertas automáticos para detecção de anomalias")
            recommendations.append("📅 Estabelecer rotina de validação periódica dos dados")
            
            # Recomendações específicas para dados extraídos
            extracted_data_results = self.validation_results['tables'].get('extracted_data', {})
            if extracted_data_results:
                quality = extracted_data_results.get('quality_metrics', {})
                consistency = quality.get('consistency', {})
                
                if 'confidence_consistency' in consistency:
                    avg_confidence = consistency['confidence_consistency'].get('average_confidence', 0)
                    if avg_confidence < 0.8:
                        recommendations.append(f"🎯 Melhorar confiança da extração OCR (atual: {avg_confidence:.1f})")
                
                # Verificar distribuição por ano
                year_dist = consistency.get('year_distribution', {})
                if year_dist:
                    years = list(year_dist.keys())
                    if len(years) < 4:  # Esperamos dados de 2021-2024
                        missing_years = set(range(2021, 2025)) - set(years)
                        if missing_years:
                            recommendations.append(f"📅 Processar dados ausentes dos anos: {', '.join(map(str, sorted(missing_years)))}")
            
        except Exception as e:
            self.logger.error(f"Erro na geração de recomendações: {e}")
            recommendations.append("🔍 Revisar processo de validação de dados")
        
        return recommendations
    
    def run_complete_validation(self) -> Dict[str, Any]:
        """
        Executa validação completa do banco de dados expandido
        """
        try:
            self.logger.info("Iniciando validação completa do banco de dados expandido...")
            
            # Inicializar conexão
            if not self.initialize_connection():
                raise Exception("Falha na inicialização da conexão")
            
            # Tabelas para validar (incluindo novas tabelas)
            tables_to_validate = [
                'regions', 'households', 'individuals', 'device_usage', 
                'internet_usage', 'accessibility_needs', 'extracted_data', 
                'data_quality_metrics', 'processing_logs'
            ]
            
            # Validar cada tabela
            for table_name in tables_to_validate:
                self.logger.info(f"Validando tabela: {table_name}")
                
                table_results = {
                    'structure': self.validate_table_structure(table_name),
                    'integrity': self.validate_data_integrity(table_name),
                    'quality_metrics': self.calculate_data_quality_metrics(table_name)
                }
                
                self.validation_results['tables'][table_name] = table_results
                self.validation_results['total_checks'] += 3
                
                # Contar sucessos e falhas
                if table_results['structure']['structure_valid']:
                    self.validation_results['passed_checks'] += 1
                else:
                    self.validation_results['failed_checks'] += 1
                    if len(table_results['structure']['issues']) > 0:
                        self.validation_results['critical_errors'] += len(table_results['structure']['issues'])
                
                if table_results['integrity']['integrity_valid']:
                    self.validation_results['passed_checks'] += 1
                else:
                    self.validation_results['failed_checks'] += 1
                    if len(table_results['integrity']['issues']) > 0:
                        self.validation_results['critical_errors'] += len(table_results['integrity']['issues'])
                
                # Qualidade sempre conta como verificação
                quality_score = table_results['quality_metrics'].get('overall_score', 0)
                if quality_score >= 70:
                    self.validation_results['passed_checks'] += 1
                else:
                    self.validation_results['failed_checks'] += 1
                
                # Contar avisos
                self.validation_results['warnings'] += len(table_results['structure'].get('warnings', []))
                self.validation_results['warnings'] += len(table_results['integrity'].get('warnings', []))
            
            # Gerar recomendações
            self.validation_results['recommendations'] = self.generate_recommendations()
            
            # Determinar status geral
            if self.validation_results['critical_errors'] == 0 and self.validation_results['failed_checks'] == 0:
                self.validation_results['overall_status'] = 'passed'
            elif self.validation_results['critical_errors'] == 0:
                self.validation_results['overall_status'] = 'passed_with_warnings'
            else:
                self.validation_results['overall_status'] = 'failed'
            
            # Calcular métricas gerais
            total_records = 0
            total_quality_score = 0
            quality_count = 0
            
            for table_results in self.validation_results['tables'].values():
                structure = table_results.get('structure', {})
                quality = table_results.get('quality_metrics', {})
                
                total_records += structure.get('record_count', 0)
                
                if 'overall_score' in quality:
                    total_quality_score += quality['overall_score']
                    quality_count += 1
            
            self.validation_results['data_quality_metrics'] = {
                'total_records': total_records,
                'average_quality_score': total_quality_score / quality_count if quality_count > 0 else 0,
                'tables_validated': len(tables_to_validate),
                'validation_timestamp': datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Validação completa concluída: {self.validation_results['overall_status']}")
            self.logger.info(f"Checks: {self.validation_results['passed_checks']}/{self.validation_results['total_checks']} passaram")
            self.logger.info(f"Erros críticos: {self.validation_results['critical_errors']}, Avisos: {self.validation_results['warnings']}")
            self.logger.info(f"Score médio de qualidade: {self.validation_results['data_quality_metrics']['average_quality_score']:.2f}%")
            
            return self.validation_results
            
        except Exception as e:
            error_msg = f"Erro na validação completa: {e}"
            self.logger.error(error_msg)
            
            self.validation_results['overall_status'] = 'error'
            self.validation_results['error'] = error_msg
            
            return self.validation_results
        
        finally:
            # Fechar conexão
            if self.session:
                self.session.close()
    
    def export_validation_report(self, output_path: str = "enhanced_validation_report.json") -> bool:
        """
        Exporta relatório de validação expandido para arquivo JSON
        """
        try:
            # Converter datetime para string para serialização JSON
            report = self.validation_results.copy()
            report['timestamp'] = report['timestamp'].isoformat()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Relatório de validação expandido exportado: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar relatório: {e}")
            return False
    
    def generate_summary_report(self) -> str:
        """
        Gera relatório resumido em formato texto
        """
        try:
            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append("RELATÓRIO DE VALIDAÇÃO DE DADOS - SISTEMA DAC EXPANDIDO")
            report_lines.append("=" * 60)
            report_lines.append(f"Data/Hora: {self.validation_results['timestamp'].strftime('%d/%m/%Y %H:%M:%S')}")
            report_lines.append(f"Banco de Dados: {self.validation_results['database_path']}")
            report_lines.append(f"Status Geral: {self.validation_results['overall_status'].upper()}")
            report_lines.append("")
            
            # Estatísticas gerais
            report_lines.append("ESTATÍSTICAS GERAIS:")
            report_lines.append("-" * 30)
            report_lines.append(f"Total de Verificações: {self.validation_results['total_checks']}")
            report_lines.append(f"Verificações Aprovadas: {self.validation_results['passed_checks']}")
            report_lines.append(f"Verificações Falharam: {self.validation_results['failed_checks']}")
            report_lines.append(f"Erros Críticos: {self.validation_results['critical_errors']}")
            report_lines.append(f"Avisos: {self.validation_results['warnings']}")
            
            # Métricas de qualidade
            dq_metrics = self.validation_results.get('data_quality_metrics', {})
            if dq_metrics:
                report_lines.append(f"Total de Registros: {dq_metrics.get('total_records', 0):,}")
                report_lines.append(f"Score Médio de Qualidade: {dq_metrics.get('average_quality_score', 0):.2f}%")
                report_lines.append(f"Tabelas Validadas: {dq_metrics.get('tables_validated', 0)}")
            
            report_lines.append("")
            
            # Resultados por tabela
            report_lines.append("RESULTADOS POR TABELA:")
            report_lines.append("-" * 30)
            
            for table_name, table_results in self.validation_results['tables'].items():
                structure = table_results.get('structure', {})
                integrity = table_results.get('integrity', {})
                quality = table_results.get('quality_metrics', {})
                
                report_lines.append(f"\n📊 {table_name.upper()}:")
                report_lines.append(f"   Registros: {structure.get('record_count', 0):,}")
                report_lines.append(f"   Estrutura: {'✅ Válida' if structure.get('structure_valid', False) else '❌ Inválida'}")
                report_lines.append(f"   Integridade: {'✅ Válida' if integrity.get('integrity_valid', False) else '❌ Inválida'}")
                report_lines.append(f"   Qualidade: {quality.get('overall_score', 0):.1f}%")
                
                # Mostrar problemas principais
                issues = structure.get('issues', []) + integrity.get('issues', [])
                if issues:
                    report_lines.append(f"   Problemas: {len(issues)}")
                    for issue in issues[:3]:  # Mostrar apenas os 3 primeiros
                        report_lines.append(f"     • {issue}")
                    if len(issues) > 3:
                        report_lines.append(f"     ... e mais {len(issues) - 3} problemas")
            
            # Recomendações
            recommendations = self.validation_results.get('recommendations', [])
            if recommendations:
                report_lines.append("\n")
                report_lines.append("RECOMENDAÇÕES:")
                report_lines.append("-" * 30)
                for i, rec in enumerate(recommendations[:10], 1):  # Mostrar apenas as 10 primeiras
                    report_lines.append(f"{i:2d}. {rec}")
                
                if len(recommendations) > 10:
                    report_lines.append(f"    ... e mais {len(recommendations) - 10} recomendações")
            
            report_lines.append("\n" + "=" * 60)
            
            return "\n".join(report_lines)
            
        except Exception as e:
            self.logger.error(f"Erro na geração do relatório resumido: {e}")
            return f"Erro na geração do relatório: {e}"

if __name__ == "__main__":
    # Teste da validação expandida
    validator = EnhancedDataValidator("dac_enhanced.db")
    results = validator.run_complete_validation()
    
    print(validator.generate_summary_report())
    
    # Exportar relatório completo
    validator.export_validation_report("enhanced_validation_report.json")