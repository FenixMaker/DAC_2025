# -*- coding: utf-8 -*-
"""
Módulo para importação de dados TIC Domicílios
"""

import pandas as pd
import os
from typing import Optional, Callable, Dict, List, Any
from sqlalchemy.orm import Session
from pathlib import Path
import sys

# Adicionar o diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.database.models import Region, Household, Individual, DeviceUsage, InternetUsage
    from src.utils.logger import get_logger
except ImportError:
    # Fallback para importações diretas
    import logging
    def get_logger(name):
        return logging.getLogger(name)
    
    # Tentar importar modelos diretamente
    try:
        from database.models import Region, Household, Individual, DeviceUsage, InternetUsage
    except ImportError:
        print("ERRO: Não foi possível importar os modelos do banco de dados")
        sys.exit(1)

class DataImporter:
    """Classe para importação de dados do TIC Domicílios"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = get_logger(__name__)
        
    def import_file(self, file_path: str, progress_callback: Optional[Callable] = None) -> bool:
        """Importa dados de um arquivo CSV ou Excel
        
        Args:
            file_path: Caminho para o arquivo
            progress_callback: Função de callback para progresso
            
        Returns:
            bool: True se importação foi bem-sucedida
        """
        try:
            self.logger.info(f"Iniciando importação do arquivo: {file_path}")
            
            # Verificar se arquivo existe
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
            # Determinar tipo de arquivo e carregar dados
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8')
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Formato de arquivo não suportado: {file_ext}")
            
            self.logger.info(f"Arquivo carregado com {len(df)} registros")
            
            # Processar dados
            return self._process_data(df, progress_callback)
            
        except Exception as e:
            self.logger.error(f"Erro na importação: {str(e)}")
            return False
    
    def _process_data(self, df: pd.DataFrame, progress_callback: Optional[Callable] = None) -> bool:
        """Processa os dados do DataFrame e insere no banco
        
        Args:
            df: DataFrame com os dados
            progress_callback: Função de callback para progresso
            
        Returns:
            bool: True se processamento foi bem-sucedido
        """
        try:
            session = self.db_manager.get_session()
            total_rows = len(df)
            processed = 0
            
            # Mapear colunas esperadas (exemplo baseado na estrutura TIC)
            column_mapping = {
                'REGIAO': 'region_code',
                'UF': 'state',
                'MUNICIPIO': 'city',
                'AREA': 'area_type',
                'RENDA_FAMILIAR': 'household_income',
                'IDADE': 'age',
                'SEXO': 'gender',
                'ESCOLARIDADE': 'education_level',
                'DEFICIENCIA': 'has_disability',
                'TEM_COMPUTADOR': 'has_computer',
                'TEM_TABLET': 'has_tablet',
                'TEM_CELULAR': 'has_mobile',
                'USA_INTERNET': 'uses_internet',
                'FREQ_INTERNET': 'internet_frequency'
            }
            
            # Processar cada linha
            for index, row in df.iterrows():
                try:
                    # Criar/obter região
                    region = self._get_or_create_region(session, row, column_mapping)
                    
                    # Criar domicílio
                    household = self._create_household(session, row, column_mapping, region)
                    
                    # Criar indivíduo
                    individual = self._create_individual(session, row, column_mapping, household)
                    
                    # Criar registros de uso de dispositivos
                    self._create_device_usage(session, row, column_mapping, individual)
                    
                    # Criar registros de uso da internet
                    self._create_internet_usage(session, row, column_mapping, individual)
                    
                    processed += 1
                    
                    # Callback de progresso
                    if progress_callback and processed % 100 == 0:
                        progress = (processed / total_rows) * 100
                        progress_callback(progress)
                    
                except Exception as e:
                    self.logger.warning(f"Erro ao processar linha {index}: {str(e)}")
                    continue
            
            # Commit das alterações
            session.commit()
            self.logger.info(f"Importação concluída: {processed}/{total_rows} registros processados")
            
            # Callback final
            if progress_callback:
                progress_callback(100)
            
            return True
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Erro no processamento: {str(e)}")
            return False
        finally:
            session.close()
    
    def _get_or_create_region(self, session: Session, row: pd.Series, mapping: dict) -> Region:
        """Obtém ou cria uma região"""
        region_code = str(row.get(mapping.get('region_code', 'REGIAO'), 'N/A'))
        state = str(row.get(mapping.get('state', 'UF'), 'N/A'))
        
        region = session.query(Region).filter_by(code=region_code).first()
        if not region:
            region = Region(
                code=region_code,
                name=f"Região {region_code}",
                state=state
            )
            session.add(region)
            session.flush()
        
        return region
    
    def _create_household(self, session: Session, row: pd.Series, mapping: dict, region: Region) -> Household:
        """Cria um registro de domicílio"""
        household = Household(
            region_id=region.id,
            city=str(row.get(mapping.get('city', 'MUNICIPIO'), 'N/A')),
            area_type=str(row.get(mapping.get('area_type', 'AREA'), 'N/A')),
            income_range=str(row.get(mapping.get('household_income', 'RENDA_FAMILIAR'), 'N/A'))
        )
        session.add(household)
        session.flush()
        return household
    
    def _create_individual(self, session: Session, row: pd.Series, mapping: dict, household: Household) -> Individual:
        """Cria um registro de indivíduo"""
        # Converter idade para inteiro
        try:
            age = int(row.get(mapping.get('age', 'IDADE'), 0))
        except (ValueError, TypeError):
            age = 0
        
        # Converter deficiência para boolean
        has_disability_val = row.get(mapping.get('has_disability', 'DEFICIENCIA'), 'N')
        has_disability = str(has_disability_val).upper() in ['S', 'SIM', '1', 'TRUE']
        
        individual = Individual(
            household_id=household.id,
            age=age,
            gender=str(row.get(mapping.get('gender', 'SEXO'), 'N/A')),
            education_level=str(row.get(mapping.get('education_level', 'ESCOLARIDADE'), 'N/A')),
            has_disability=has_disability
        )
        session.add(individual)
        session.flush()
        return individual
    
    def _create_device_usage(self, session: Session, row: pd.Series, mapping: dict, individual: Individual):
        """Cria registros de uso de dispositivos"""
        devices = {
            'computer': row.get(mapping.get('has_computer', 'TEM_COMPUTADOR'), 'N'),
            'tablet': row.get(mapping.get('has_tablet', 'TEM_TABLET'), 'N'),
            'mobile': row.get(mapping.get('has_mobile', 'TEM_CELULAR'), 'N')
        }
        
        for device_type, has_device_val in devices.items():
            has_device = str(has_device_val).upper() in ['S', 'SIM', '1', 'TRUE']
            
            device_usage = DeviceUsage(
                individual_id=individual.id,
                device_type=device_type,
                has_device=has_device,
                usage_frequency='daily' if has_device else 'never'
            )
            session.add(device_usage)
    
    def _create_internet_usage(self, session: Session, row: pd.Series, mapping: dict, individual: Individual):
        """Cria registros de uso da internet"""
        uses_internet_val = row.get(mapping.get('uses_internet', 'USA_INTERNET'), 'N')
        uses_internet = str(uses_internet_val).upper() in ['S', 'SIM', '1', 'TRUE']
        
        frequency = str(row.get(mapping.get('internet_frequency', 'FREQ_INTERNET'), 'never'))
        if not uses_internet:
            frequency = 'never'
        
        internet_usage = InternetUsage(
            individual_id=individual.id,
            uses_internet=uses_internet,
            access_frequency=frequency,
            main_activities='N/A' if not uses_internet else 'general'
        )
        session.add(internet_usage)
    
    def import_processed_data(self, processed_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Importa dados processados pelo ImageProcessor para o banco de dados"""
        imported_counts = {
            'regions': 0,
            'households': 0,
            'individuals': 0,
            'device_usage': 0,
            'internet_usage': 0
        }
        
        try:
            self.logger.info("Iniciando importação de dados processados")
            
            # Inicializar banco de dados se necessário
            self.db_manager.initialize_database()
            
            session = self.db_manager.get_session()
            
            try:
                # Importar regiões
                for region_data in processed_data.get('region', []):
                    region = self._get_or_create_region_simple(session, region_data.get('name', 'Desconhecida'))
                    imported_counts['regions'] += 1
                
                # Importar domicílios
                for household_data in processed_data.get('household', []):
                    household = self._create_household_from_processed(session, household_data)
                    imported_counts['households'] += 1
                
                # Importar indivíduos
                for individual_data in processed_data.get('individual', []):
                    individual = self._create_individual_from_processed(session, individual_data)
                    imported_counts['individuals'] += 1
                
                # Importar uso de dispositivos
                for device_data in processed_data.get('device', []):
                    device_usage = self._create_device_usage_from_processed(session, device_data)
                    imported_counts['device_usage'] += 1
                
                # Importar uso de internet
                for internet_data in processed_data.get('internet', []):
                    internet_usage = self._create_internet_usage_from_processed(session, internet_data)
                    imported_counts['internet_usage'] += 1
                
                session.commit()
                self.logger.info(f"Importação concluída: {imported_counts}")
                
                return {
                    'success': True,
                    'imported_counts': imported_counts,
                    'total_imported': sum(imported_counts.values())
                }
                
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
                
        except Exception as e:
            error_msg = f"Erro na importação de dados processados: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'imported_counts': imported_counts
            }
    
    def _create_household_from_processed(self, session: Session, household_data: Dict) -> Household:
        """Cria domicílio a partir de dados processados"""
        # Buscar ou criar região
        region = self._get_or_create_region_simple(session, household_data.get('region', 'Desconhecida'))
        
        household = Household(
            region_id=region.id,
            city=household_data.get('city', 'N/A'),
            area_type=household_data.get('area_type', 'urbana'),
            income_range=household_data.get('income_range', 'N/A'),
            household_size=household_data.get('household_size', 1),
            has_internet=household_data.get('has_internet', False)
        )
        session.add(household)
        session.flush()
        return household
    
    def _create_individual_from_processed(self, session: Session, individual_data: Dict) -> Individual:
        """Cria indivíduo a partir de dados processados"""
        # Criar domicílio padrão se não existir
        region = self._get_or_create_region_simple(session, individual_data.get('region', 'Desconhecida'))
        household = Household(
            region_id=region.id,
            city='N/A',
            area_type='urbana',
            income_range='N/A',
            household_size=1,
            has_internet=False
        )
        session.add(household)
        session.flush()
        
        individual = Individual(
            household_id=household.id,
            age=individual_data.get('age', None),
            gender=individual_data.get('gender', 'N/A'),
            education_level=individual_data.get('education_level', 'N/A'),
            has_disability=individual_data.get('has_disability', False),
            employment_status=individual_data.get('employment_status', 'N/A')
        )
        session.add(individual)
        session.flush()
        return individual
    
    def _create_device_usage_from_processed(self, session: Session, device_data: Dict) -> DeviceUsage:
        """Cria uso de dispositivo a partir de dados processados"""
        # Criar indivíduo padrão se não existir
        individual = self._create_individual_from_processed(session, device_data)
        
        device_usage = DeviceUsage(
            individual_id=individual.id,
            device_type=device_data.get('device_type', 'computer'),
            has_device=device_data.get('has_device', False),
            usage_frequency=device_data.get('usage_frequency', 'N/A'),
            access_location=device_data.get('access_location', 'N/A')
        )
        session.add(device_usage)
        return device_usage
    
    def _create_internet_usage_from_processed(self, session: Session, internet_data: Dict) -> InternetUsage:
        """Cria uso de internet a partir de dados processados"""
        # Criar indivíduo padrão se não existir
        individual = self._create_individual_from_processed(session, internet_data)
        
        internet_usage = InternetUsage(
            individual_id=individual.id,
            uses_internet=internet_data.get('uses_internet', False),
            access_frequency=internet_data.get('access_frequency', 'N/A'),
            main_activities=internet_data.get('main_activities', 'N/A'),
            barriers_to_access=internet_data.get('barriers_to_access', 'N/A')
        )
        session.add(internet_usage)
        return internet_usage
    
    def _get_or_create_region_simple(self, session: Session, region_name: str) -> Region:
        """Versão simplificada para buscar ou criar região"""
        # Buscar região existente
        region = session.query(Region).filter_by(name=region_name).first()
        
        if not region:
            # Criar nova região
            region = Region(
                code=f'REG_{len(session.query(Region).all()) + 1:03d}',
                name=region_name,
                state='N/A',
                macro_region='N/A',
                description=f'Região extraída de dados: {region_name}'
            )
            session.add(region)
            session.flush()
        
        return region