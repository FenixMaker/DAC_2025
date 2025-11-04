#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Migração de Dados
Responsável por migrar dados do esquema antigo para o novo esquema expandido
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.utils.logger import get_logger
    from src.database.models import Base as OldBase
    from src.database.enhanced_models import Base as NewBase, get_all_models
    from src.modules.image_processor import ImageProcessor
except ImportError as e:
    print(f"Erro de importação: {e}")
    sys.exit(1)

class MigrationManager:
    """
    Gerenciador de migração de dados do sistema antigo para o novo
    """
    
    def __init__(self, old_db_path: str = "dac_database.db", new_db_path: str = "dac_enhanced.db"):
        self.logger = get_logger(__name__)
        self.old_db_path = old_db_path
        self.new_db_path = new_db_path
        
        # Engines de banco de dados
        self.old_engine = None
        self.new_engine = None
        self.old_session = None
        self.new_session = None
        
        # Processador de imagens
        self.image_processor = ImageProcessor()
        
        # Estatísticas de migração
        self.migration_stats = {
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'tables_migrated': 0,
            'records_migrated': 0,
            'records_enhanced': 0,
            'errors': [],
            'warnings': []
        }
        
        # Mapeamentos de migração
        self.field_mappings = {
            'regions': {
                'direct_copy': ['id', 'code', 'name', 'state', 'macro_region', 'description'],
                'new_fields': {
                    'population': None,
                    'area_km2': None,
                    'urban_population_percentage': None,
                    'rural_population_percentage': None,
                    'economic_indicators': None
                }
            },
            'households': {
                'direct_copy': ['id', 'region_id', 'city', 'area_type', 'income_range', 'household_size', 'has_internet'],
                'enhanced_fields': {
                    'income_value_min': 'derive_from_income_range',
                    'income_value_max': 'derive_from_income_range',
                    'housing_type': None,
                    'housing_ownership': None,
                    'basic_services': None,
                    'internet_type': None,
                    'internet_speed': None,
                    'digital_devices_count': 'count_from_device_usage',
                    'monthly_internet_cost': None,
                    'internet_barriers': None,
                    'data_source': 'pdf_legacy',
                    'extraction_confidence': 0.8,
                    'last_updated': 'current_timestamp'
                }
            },
            'individuals': {
                'direct_copy': ['id', 'household_id', 'age', 'gender', 'education_level', 'has_disability', 'employment_status', 'created_at'],
                'enhanced_fields': {
                    'age_range': 'derive_from_age',
                    'education_years': 'derive_from_education_level',
                    'occupation': None,
                    'monthly_income': None,
                    'disability_type': None,
                    'disability_severity': None,
                    'digital_literacy_level': None,
                    'internet_usage_frequency': None,
                    'main_internet_activities': None,
                    'digital_skills': None,
                    'barriers_to_internet': None,
                    'data_source': 'pdf_legacy',
                    'extraction_confidence': 0.8,
                    'last_updated': 'current_timestamp'
                }
            }
        }
    
    def initialize_connections(self) -> bool:
        """
        Inicializa conexões com os bancos de dados antigo e novo
        """
        try:
            # Conexão com banco antigo
            if os.path.exists(self.old_db_path):
                self.old_engine = create_engine(f'sqlite:///{self.old_db_path}')
                OldSessionMaker = sessionmaker(bind=self.old_engine)
                self.old_session = OldSessionMaker()
                self.logger.info(f"Conectado ao banco antigo: {self.old_db_path}")
            else:
                self.logger.warning(f"Banco antigo não encontrado: {self.old_db_path}")
                return False
            
            # Conexão com banco novo
            self.new_engine = create_engine(f'sqlite:///{self.new_db_path}')
            
            # Criar tabelas no novo banco
            NewBase.metadata.create_all(self.new_engine)
            
            NewSessionMaker = sessionmaker(bind=self.new_engine)
            self.new_session = NewSessionMaker()
            self.logger.info(f"Banco novo inicializado: {self.new_db_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar conexões: {e}")
            return False
    
    def analyze_old_database(self) -> Dict[str, Any]:
        """
        Analisa a estrutura e conteúdo do banco antigo
        """
        analysis = {
            'tables': {},
            'total_records': 0,
            'data_quality': {},
            'migration_complexity': 'low'
        }
        
        try:
            if not self.old_session:
                return analysis
            
            # Inspecionar estrutura
            inspector = inspect(self.old_engine)
            tables = inspector.get_table_names()
            
            for table_name in tables:
                columns = inspector.get_columns(table_name)
                
                # Contar registros
                result = self.old_session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                record_count = result.scalar()
                
                analysis['tables'][table_name] = {
                    'columns': [col['name'] for col in columns],
                    'record_count': record_count,
                    'column_details': columns
                }
                
                analysis['total_records'] += record_count
            
            self.logger.info(f"Análise do banco antigo concluída: {len(tables)} tabelas, {analysis['total_records']} registros")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erro na análise do banco antigo: {e}")
            return analysis
    
    def migrate_regions(self) -> bool:
        """
        Migra dados da tabela regions
        """
        try:
            self.logger.info("Iniciando migração de regiões...")
            
            # Buscar dados antigos
            old_regions = self.old_session.execute(text("SELECT * FROM regions")).fetchall()
            
            models = get_all_models()
            Region = models['Region']
            
            migrated_count = 0
            
            for old_region in old_regions:
                # Criar nova região com campos expandidos
                new_region = Region(
                    id=old_region.id,
                    code=old_region.code,
                    name=old_region.name,
                    state=old_region.state,
                    macro_region=old_region.macro_region,
                    description=old_region.description,
                    # Novos campos ficam como None por enquanto
                    population=None,
                    area_km2=None,
                    urban_population_percentage=None,
                    rural_population_percentage=None,
                    economic_indicators=None
                )
                
                self.new_session.add(new_region)
                migrated_count += 1
            
            self.new_session.commit()
            self.logger.info(f"Migração de regiões concluída: {migrated_count} registros")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na migração de regiões: {e}")
            self.new_session.rollback()
            return False
    
    def migrate_households(self) -> bool:
        """
        Migra dados da tabela households com campos expandidos
        """
        try:
            self.logger.info("Iniciando migração de domicílios...")
            
            # Buscar dados antigos
            old_households = self.old_session.execute(text("SELECT * FROM households")).fetchall()
            
            models = get_all_models()
            Household = models['Household']
            
            migrated_count = 0
            
            for old_household in old_households:
                # Derivar valores de faixa de renda
                income_min, income_max = self._derive_income_range(old_household.income_range)
                
                # Contar dispositivos (se existir relação)
                device_count = self._count_household_devices(old_household.id)
                
                # Criar novo domicílio
                new_household = Household(
                    id=old_household.id,
                    region_id=old_household.region_id,
                    city=old_household.city,
                    area_type=old_household.area_type,
                    income_range=old_household.income_range,
                    household_size=old_household.household_size,
                    has_internet=old_household.has_internet,
                    # Campos expandidos
                    income_value_min=income_min,
                    income_value_max=income_max,
                    housing_type=None,
                    housing_ownership=None,
                    basic_services=None,
                    internet_type=None,
                    internet_speed=None,
                    digital_devices_count=device_count,
                    monthly_internet_cost=None,
                    internet_barriers=None,
                    data_source='pdf_legacy',
                    extraction_confidence=0.8,
                    last_updated=datetime.utcnow()
                )
                
                self.new_session.add(new_household)
                migrated_count += 1
            
            self.new_session.commit()
            self.logger.info(f"Migração de domicílios concluída: {migrated_count} registros")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na migração de domicílios: {e}")
            self.new_session.rollback()
            return False
    
    def migrate_individuals(self) -> bool:
        """
        Migra dados da tabela individuals com campos expandidos
        """
        try:
            self.logger.info("Iniciando migração de indivíduos...")
            
            # Buscar dados antigos
            old_individuals = self.old_session.execute(text("SELECT * FROM individuals")).fetchall()
            
            models = get_all_models()
            Individual = models['Individual']
            
            migrated_count = 0
            
            for old_individual in old_individuals:
                # Acessar dados por índice (id, household_id, age, gender, education_level, has_disability, employment_status, created_at)
                individual_id = old_individual[0]
                household_id = old_individual[1]
                age = old_individual[2]
                gender = old_individual[3]
                education_level = old_individual[4]
                has_disability = old_individual[5]
                employment_status = old_individual[6]
                created_at_str = old_individual[7]
                
                # Converter string de data para datetime se necessário
                if isinstance(created_at_str, str):
                    try:
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    except:
                        created_at = datetime.utcnow()
                else:
                    created_at = created_at_str or datetime.utcnow()
                
                # Derivar faixa etária
                age_range = self._derive_age_range(age)
                
                # Derivar anos de educação
                education_years = self._derive_education_years(education_level)
                
                # Criar novo indivíduo
                new_individual = Individual(
                    id=individual_id,
                    household_id=household_id,
                    age=age,
                    gender=gender,
                    education_level=education_level,
                    has_disability=has_disability,
                    employment_status=employment_status,
                    created_at=created_at,
                    # Campos expandidos
                    age_range=age_range,
                    education_years=education_years,
                    occupation=None,
                    monthly_income=None,
                    disability_type=None,
                    disability_severity=None,
                    digital_literacy_level=None,
                    internet_usage_frequency=None,
                    main_internet_activities=None,
                    digital_skills=None,
                    barriers_to_internet=None,
                    data_source='pdf_legacy',
                    extraction_confidence=0.8,
                    last_updated=datetime.utcnow()
                )
                
                self.new_session.add(new_individual)
                migrated_count += 1
            
            self.new_session.commit()
            self.logger.info(f"Migração de indivíduos concluída: {migrated_count} registros")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na migração de indivíduos: {e}")
            self.new_session.rollback()
            return False
    
    def migrate_device_usage(self) -> bool:
        """
        Migra dados da tabela device_usage com campos expandidos
        """
        try:
            self.logger.info("Iniciando migração de uso de dispositivos...")
            
            # Buscar dados antigos
            old_device_usage = self.old_session.execute(text("SELECT * FROM device_usage")).fetchall()
            
            models = get_all_models()
            DeviceUsage = models['DeviceUsage']
            
            migrated_count = 0
            
            for old_usage in old_device_usage:
                # Acessar dados por índice
                usage_id = old_usage[0]
                individual_id = old_usage[1]
                device_type = old_usage[2]
                has_device = old_usage[3]
                usage_frequency = old_usage[4]
                access_location = old_usage[5]
                created_at_str = old_usage[6]
                
                # Converter string de data para datetime se necessário
                if isinstance(created_at_str, str):
                    try:
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    except:
                        created_at = datetime.utcnow()
                else:
                    created_at = created_at_str or datetime.utcnow()
                
                # Criar novo registro de uso de dispositivo
                new_usage = DeviceUsage(
                    id=usage_id,
                    individual_id=individual_id,
                    device_type=device_type,
                    has_device=has_device,
                    usage_frequency=usage_frequency,
                    access_location=access_location,
                    created_at=created_at,
                    # Campos expandidos
                    device_brand=None,
                    device_model=None,
                    device_age_years=None,
                    device_condition=None,
                    acquisition_method=None,
                    sharing_with_others=False,
                    main_usage_purposes=None,
                    technical_issues=None,
                    replacement_needs=False,
                    cost_barrier=False,
                    data_source='pdf_legacy',
                    extraction_confidence=0.8,
                    last_updated=datetime.utcnow()
                )
                
                self.new_session.add(new_usage)
                migrated_count += 1
            
            self.new_session.commit()
            self.logger.info(f"Migração de uso de dispositivos concluída: {migrated_count} registros")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na migração de uso de dispositivos: {e}")
            self.new_session.rollback()
            return False
    
    def migrate_internet_usage(self) -> bool:
        """
        Migra dados da tabela internet_usage com campos expandidos
        """
        try:
            self.logger.info("Iniciando migração de uso de internet...")
            
            # Buscar dados antigos
            old_internet_usage = self.old_session.execute(text("SELECT * FROM internet_usage")).fetchall()
            
            models = get_all_models()
            InternetUsage = models['InternetUsage']
            
            migrated_count = 0
            
            for old_usage in old_internet_usage:
                # Acessar dados por índice
                usage_id = old_usage[0]
                individual_id = old_usage[1]
                uses_internet = old_usage[2]
                access_frequency = old_usage[3]
                main_activities = old_usage[4]
                barriers_to_access = old_usage[5]
                created_at_str = old_usage[6]
                
                # Converter string de data para datetime se necessário
                if isinstance(created_at_str, str):
                    try:
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    except:
                        created_at = datetime.utcnow()
                else:
                    created_at = created_at_str or datetime.utcnow()
                
                # Criar novo registro de uso de internet
                new_usage = InternetUsage(
                    id=usage_id,
                    individual_id=individual_id,
                    uses_internet=uses_internet,
                    access_frequency=access_frequency,
                    main_activities=main_activities,
                    barriers_to_access=barriers_to_access,
                    created_at=created_at,
                    # Campos expandidos
                    first_access_age=None,
                    years_using_internet=None,
                    daily_usage_hours=None,
                    preferred_access_device=None,
                    internet_skills_level=None,
                    online_services_used=None,
                    social_media_usage=None,
                    ecommerce_usage=False,
                    online_banking=False,
                    online_education=False,
                    telehealth_usage=False,
                    government_services_online=False,
                    privacy_concerns=None,
                    security_knowledge=None,
                    cost_barrier=False,
                    infrastructure_barrier=False,
                    skills_barrier=False,
                    accessibility_barrier=False,
                    content_barrier=False,
                    data_source='pdf_legacy',
                    extraction_confidence=0.8,
                    last_updated=datetime.utcnow()
                )
                
                self.new_session.add(new_usage)
                migrated_count += 1
            
            self.new_session.commit()
            self.logger.info(f"Migração de uso de internet concluída: {migrated_count} registros")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na migração de uso de internet: {e}")
            self.new_session.rollback()
            return False
    
    def process_and_integrate_images(self, images_directory: str = "Dados") -> bool:
        """
        Processa imagens e integra dados extraídos ao banco expandido
        """
        try:
            self.logger.info("Iniciando processamento e integração de imagens...")
            
            # Processar imagens
            results = self.image_processor.process_all_images(images_directory)
            
            if not results.get('success', False):
                self.logger.error(f"Falha no processamento de imagens: {results.get('error', 'Erro desconhecido')}")
                return False
            
            # Obter dados processados
            processed_data = self.image_processor.get_processed_data()
            
            # Integrar dados extraídos
            models = get_all_models()
            ExtractedData = models['ExtractedData']
            
            total_integrated = 0
            
            for category, data_list in processed_data.items():
                for data_item in data_list:
                    try:
                        # Criar registro de dados extraídos
                        extracted_record = ExtractedData(
                            source_file=data_item.get('source_line', 'unknown'),
                            source_year=data_item.get('year', datetime.now().year),
                            category=category,
                            subcategory=data_item.get('category', 'general'),
                            extracted_text=data_item.get('source_line', ''),
                            structured_data=json.dumps(data_item),
                            numeric_value=data_item.get('value'),
                            unit=data_item.get('unit', 'count'),
                            context_text=data_item.get('context', ''),
                            extraction_confidence=0.9,  # Alta confiança para OCR
                            validation_status='pending',
                            extraction_method='ocr',
                            processing_timestamp=datetime.utcnow()
                        )
                        
                        self.new_session.add(extracted_record)
                        total_integrated += 1
                        
                    except Exception as e:
                        self.logger.warning(f"Erro ao integrar item de dados: {e}")
                        continue
            
            self.new_session.commit()
            self.logger.info(f"Integração de dados de imagens concluída: {total_integrated} registros")
            
            # Atualizar estatísticas
            self.migration_stats['records_enhanced'] = total_integrated
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro no processamento e integração de imagens: {e}")
            self.new_session.rollback()
            return False
    
    def validate_migration(self) -> Dict[str, Any]:
        """
        Valida a integridade da migração
        """
        validation_results = {
            'success': True,
            'errors': [],
            'warnings': [],
            'statistics': {},
            'data_integrity': {}
        }
        
        try:
            # Comparar contagens de registros
            old_counts = {}
            new_counts = {}
            
            # Contar registros no banco antigo
            if self.old_session:
                for table in ['regions', 'households', 'individuals', 'device_usage', 'internet_usage']:
                    try:
                        result = self.old_session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        old_counts[table] = result.scalar()
                    except:
                        old_counts[table] = 0
            
            # Contar registros no banco novo
            for table in ['regions', 'households', 'individuals', 'device_usage', 'internet_usage']:
                try:
                    result = self.new_session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    new_counts[table] = result.scalar()
                except:
                    new_counts[table] = 0
            
            # Verificar integridade
            for table in old_counts:
                if old_counts[table] != new_counts[table]:
                    validation_results['warnings'].append(
                        f"Contagem diferente em {table}: antigo={old_counts[table]}, novo={new_counts[table]}"
                    )
            
            validation_results['statistics'] = {
                'old_database': old_counts,
                'new_database': new_counts,
                'migration_stats': self.migration_stats
            }
            
            # Verificar dados extraídos
            extracted_count = self.new_session.execute(text("SELECT COUNT(*) FROM extracted_data")).scalar()
            validation_results['statistics']['extracted_data_records'] = extracted_count
            
            self.logger.info(f"Validação concluída: {len(validation_results['errors'])} erros, {len(validation_results['warnings'])} avisos")
            
        except Exception as e:
            validation_results['success'] = False
            validation_results['errors'].append(f"Erro na validação: {e}")
            self.logger.error(f"Erro na validação da migração: {e}")
        
        return validation_results
    
    def run_complete_migration(self, images_directory: str = "Dados") -> Dict[str, Any]:
        """
        Executa migração completa do sistema
        """
        self.migration_stats['start_time'] = datetime.utcnow()
        
        try:
            self.logger.info("Iniciando migração completa do sistema...")
            
            # 1. Inicializar conexões
            if not self.initialize_connections():
                raise Exception("Falha na inicialização das conexões")
            
            # 2. Analisar banco antigo
            analysis = self.analyze_old_database()
            self.logger.info(f"Banco antigo analisado: {analysis['total_records']} registros")
            
            # 2.5. Limpar tabelas existentes para evitar conflitos
            self.logger.info("Limpando tabelas existentes...")
            for table_name in ['internet_usage', 'device_usage', 'individuals', 'households', 'regions']:
                try:
                    self.new_session.execute(text(f"DELETE FROM {table_name}"))
                except Exception as e:
                    self.logger.warning(f"Erro ao limpar tabela {table_name}: {e}")
            self.new_session.commit()
            
            # 3. Migrar tabelas principais
            migration_steps = [
                ('regions', self.migrate_regions),
                ('households', self.migrate_households),
                ('individuals', self.migrate_individuals),
                ('device_usage', self.migrate_device_usage),
                ('internet_usage', self.migrate_internet_usage)
            ]
            
            for table_name, migration_func in migration_steps:
                self.logger.info(f"Migrando tabela: {table_name}")
                if migration_func():
                    self.migration_stats['tables_migrated'] += 1
                    self.logger.info(f"Tabela {table_name} migrada com sucesso")
                else:
                    raise Exception(f"Falha na migração da tabela {table_name}")
            
            # 4. Processar e integrar imagens
            if self.process_and_integrate_images(images_directory):
                self.logger.info("Dados de imagens integrados com sucesso")
            else:
                self.migration_stats['warnings'].append("Falha na integração de dados de imagens")
            
            # 5. Validar migração
            validation = self.validate_migration()
            
            # 6. Finalizar
            self.migration_stats['end_time'] = datetime.utcnow()
            self.migration_stats['duration_seconds'] = (
                self.migration_stats['end_time'] - self.migration_stats['start_time']
            ).total_seconds()
            
            # Contar registros migrados
            total_records = sum(analysis['tables'].get(table, {}).get('record_count', 0) 
                              for table in ['regions', 'households', 'individuals', 'device_usage', 'internet_usage'])
            self.migration_stats['records_migrated'] = total_records
            
            self.logger.info(f"Migração completa concluída em {self.migration_stats['duration_seconds']:.2f} segundos")
            
            return {
                'success': True,
                'migration_stats': self.migration_stats,
                'validation_results': validation,
                'database_analysis': analysis
            }
            
        except Exception as e:
            self.migration_stats['end_time'] = datetime.utcnow()
            self.migration_stats['errors'].append(str(e))
            
            error_msg = f"Erro na migração completa: {e}"
            self.logger.error(error_msg)
            
            return {
                'success': False,
                'error': error_msg,
                'migration_stats': self.migration_stats
            }
        
        finally:
            # Fechar conexões
            if self.old_session:
                self.old_session.close()
            if self.new_session:
                self.new_session.close()
    
    # Métodos auxiliares para derivação de dados
    
    def _derive_income_range(self, income_range: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Deriva valores numéricos da faixa de renda
        """
        if not income_range:
            return None, None
        
        income_mappings = {
            'Até 1 SM': (0, 1320),
            '1 a 2 SM': (1320, 2640),
            '2 a 3 SM': (2640, 3960),
            '3 a 5 SM': (3960, 6600),
            'Mais de 5 SM': (6600, None)
        }
        
        return income_mappings.get(income_range, (None, None))
    
    def _derive_age_range(self, age: Optional[int]) -> Optional[str]:
        """
        Deriva faixa etária padronizada da idade
        """
        if age is None:
            return None
        
        if age < 16:
            return '10-15 anos'
        elif age < 25:
            return '16-24 anos'
        elif age < 35:
            return '25-34 anos'
        elif age < 45:
            return '35-44 anos'
        elif age < 60:
            return '45-59 anos'
        else:
            return '60+ anos'
    
    def _derive_education_years(self, education_level: Optional[str]) -> Optional[int]:
        """
        Deriva anos de estudo do nível educacional
        """
        if not education_level:
            return None
        
        education_mappings = {
            'Analfabeto': 0,
            'Fundamental incompleto': 4,
            'Fundamental completo': 9,
            'Médio incompleto': 10,
            'Médio completo': 12,
            'Superior incompleto': 14,
            'Superior completo': 16,
            'Pós-graduação': 18
        }
        
        return education_mappings.get(education_level, None)
    
    def _count_household_devices(self, household_id: int) -> int:
        """
        Conta dispositivos de um domicílio
        """
        try:
            if not self.old_session:
                return 0
            
            # Contar dispositivos através dos indivíduos do domicílio
            result = self.old_session.execute(text("""
                SELECT COUNT(DISTINCT du.device_type)
                FROM device_usage du
                JOIN individuals i ON du.individual_id = i.id
                WHERE i.household_id = :household_id AND du.has_device = 1
            """), {'household_id': household_id})
            
            return result.scalar() or 0
            
        except Exception:
            return 0

if __name__ == "__main__":
    # Teste da migração
    migration_manager = MigrationManager()
    results = migration_manager.run_complete_migration("f:\\Sites\\DAC\\Dados")
    print(f"Migração concluída: {results}")