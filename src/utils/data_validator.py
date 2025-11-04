# -*- coding: utf-8 -*-
"""
Módulo de validação de dados para o sistema DAC
"""

import re
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import sys
import os

# Adicionar o diretório raiz ao path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Tentar importação absoluta primeiro, depois relativa como fallback
try:
    from src.utils.logger import get_logger
except ImportError:
    try:
        from ..utils.logger import get_logger
    except ImportError:
        # Fallback simples se não conseguir importar
        import logging
        def get_logger(name):
             return logging.getLogger(name)

class ValidationError(Exception):
    """Exceção customizada para erros de validação"""
    pass

class DataValidator:
    """Classe responsável pela validação de dados de entrada"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.errors = []
        self.warnings = []
        
        # Definir valores válidos para campos categóricos
        self.valid_values = {
            'gender': ['masculino', 'feminino', 'outro', 'm', 'f', 'o'],
            'area_type': ['urbana', 'rural'],
            'education_levels': [
                'sem_instrucao', 'fundamental_incompleto', 'fundamental_completo',
                'medio_incompleto', 'medio_completo', 'superior_incompleto', 
                'superior_completo', 'pos_graduacao'
            ],
            'income_ranges': [
                'ate_1_sm', '1_a_2_sm', '2_a_3_sm', '3_a_5_sm', 
                '5_a_10_sm', 'mais_10_sm', 'nao_informado'
            ],
            'device_types': [
                'computador', 'notebook', 'tablet', 'smartphone', 
                'celular', 'smart_tv', 'console'
            ],
            'connection_types': [
                'banda_larga', 'discada', 'movel_3g', 'movel_4g', 
                'movel_5g', 'satelite', 'cabo', 'fibra'
            ],
            'region_codes': ['N', 'NE', 'SE', 'S', 'CO']
        }
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
        """Valida um DataFrame completo
        
        Args:
            df: DataFrame a ser validado
            
        Returns:
            Tuple[bool, List[str], List[str]]: (é_válido, erros, avisos)
        """
        self.errors = []
        self.warnings = []
        
        try:
            # Validações básicas
            self._validate_dataframe_structure(df)
            self._validate_required_columns(df)
            
            # Validar cada linha
            for index, row in df.iterrows():
                self._validate_row(row, index)
            
            # Validações de integridade
            self._validate_data_integrity(df)
            
            is_valid = len(self.errors) == 0
            return is_valid, self.errors, self.warnings
            
        except Exception as e:
            self.logger.error(f"Erro na validação do DataFrame: {str(e)}")
            self.errors.append(f"Erro crítico na validação: {str(e)}")
            return False, self.errors, self.warnings
    
    def _validate_dataframe_structure(self, df: pd.DataFrame):
        """Valida a estrutura básica do DataFrame"""
        if df is None:
            self.errors.append("DataFrame é None")
            return
        
        if df.empty:
            self.errors.append("DataFrame está vazio")
            return
        
        if len(df.columns) == 0:
            self.errors.append("DataFrame não possui colunas")
            return
        
        # Verificar duplicatas
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            self.warnings.append(f"Encontradas {duplicates} linhas duplicadas")
    
    def _validate_required_columns(self, df: pd.DataFrame):
        """Valida se as colunas obrigatórias estão presentes"""
        required_columns = {
            'region_related': ['REGIAO', 'UF', 'MUNICIPIO'],
            'household_related': ['RENDA_FAMILIAR', 'CLASSE_SOCIAL', 'AREA'],
            'individual_related': ['IDADE', 'SEXO', 'ESCOLARIDADE']
        }
        
        available_columns = df.columns.tolist()
        
        for category, columns in required_columns.items():
            found_columns = [col for col in columns if col in available_columns]
            if not found_columns:
                self.warnings.append(f"Nenhuma coluna de {category} encontrada: {columns}")
    
    def _validate_row(self, row: pd.Series, index: int):
        """Valida uma linha específica do DataFrame"""
        try:
            # Validar idade
            self._validate_age(row, index)
            
            # Validar gênero
            self._validate_gender(row, index)
            
            # Validar educação
            self._validate_education(row, index)
            
            # Validar renda
            self._validate_income(row, index)
            
            # Validar região
            self._validate_region(row, index)
            
            # Validar dispositivos
            self._validate_devices(row, index)
            
            # Validar internet
            self._validate_internet(row, index)
            
        except Exception as e:
            self.errors.append(f"Erro na validação da linha {index}: {str(e)}")
    
    def _validate_age(self, row: pd.Series, index: int):
        """Valida campo de idade"""
        age_columns = ['IDADE', 'AGE', 'FAIXA_ETARIA']
        
        for col in age_columns:
            if col in row.index and pd.notna(row[col]):
                age_value = row[col]
                
                # Tentar converter para número
                try:
                    age_num = float(age_value)
                    if age_num < 0 or age_num > 120:
                        self.errors.append(f"Linha {index}: Idade inválida ({age_num})")
                except (ValueError, TypeError):
                    # Pode ser faixa etária em texto
                    if not self._is_valid_age_range(str(age_value)):
                        self.warnings.append(f"Linha {index}: Formato de idade não reconhecido ({age_value})")
    
    def _validate_gender(self, row: pd.Series, index: int):
        """Valida campo de gênero"""
        gender_columns = ['SEXO', 'GENDER', 'GENERO']
        
        for col in gender_columns:
            if col in row.index and pd.notna(row[col]):
                gender_value = str(row[col]).lower().strip()
                
                if gender_value not in self.valid_values['gender']:
                    self.warnings.append(f"Linha {index}: Gênero não reconhecido ({row[col]})")
    
    def _validate_education(self, row: pd.Series, index: int):
        """Valida campo de educação"""
        education_columns = ['ESCOLARIDADE', 'EDUCATION', 'GRAU_INSTRUCAO']
        
        for col in education_columns:
            if col in row.index and pd.notna(row[col]):
                education_value = str(row[col]).lower().strip()
                
                # Verificar se é um nível válido (flexível)
                if not self._is_valid_education_level(education_value):
                    self.warnings.append(f"Linha {index}: Nível de educação não reconhecido ({row[col]})")
    
    def _validate_income(self, row: pd.Series, index: int):
        """Valida campo de renda"""
        income_columns = ['RENDA_FAMILIAR', 'INCOME', 'CLASSE_SOCIAL']
        
        for col in income_columns:
            if col in row.index and pd.notna(row[col]):
                income_value = row[col]
                
                # Tentar converter para número
                try:
                    income_num = float(income_value)
                    if income_num < 0:
                        self.errors.append(f"Linha {index}: Renda negativa ({income_num})")
                except (ValueError, TypeError):
                    # Pode ser classe social em texto
                    if not self._is_valid_income_class(str(income_value)):
                        self.warnings.append(f"Linha {index}: Classe de renda não reconhecida ({income_value})")
    
    def _validate_region(self, row: pd.Series, index: int):
        """Valida campos de região"""
        region_columns = ['REGIAO', 'REGION', 'UF', 'STATE']
        
        for col in region_columns:
            if col in row.index and pd.notna(row[col]):
                region_value = str(row[col]).strip()
                
                if col in ['REGIAO', 'REGION']:
                    if not self._is_valid_region(region_value):
                        self.warnings.append(f"Linha {index}: Região não reconhecida ({region_value})")
                elif col in ['UF', 'STATE']:
                    if not self._is_valid_state(region_value):
                        self.warnings.append(f"Linha {index}: Estado não reconhecido ({region_value})")
    
    def _validate_devices(self, row: pd.Series, index: int):
        """Valida campos de dispositivos"""
        device_columns = [
            'COMPUTADOR', 'TABLET', 'CELULAR', 'SMARTPHONE',
            'TEM_COMPUTADOR', 'TEM_TABLET', 'TEM_CELULAR'
        ]
        
        for col in device_columns:
            if col in row.index and pd.notna(row[col]):
                device_value = row[col]
                
                if not self._is_valid_boolean(device_value):
                    self.warnings.append(f"Linha {index}: Valor de dispositivo inválido em {col} ({device_value})")
    
    def _validate_internet(self, row: pd.Series, index: int):
        """Valida campos de internet"""
        internet_columns = [
            'INTERNET', 'USA_INTERNET', 'ACESSO_INTERNET',
            'FREQUENCIA_INTERNET', 'ATIVIDADES_INTERNET'
        ]
        
        for col in internet_columns:
            if col in row.index and pd.notna(row[col]):
                internet_value = row[col]
                
                if col in ['INTERNET', 'USA_INTERNET', 'ACESSO_INTERNET']:
                    if not self._is_valid_boolean(internet_value):
                        self.warnings.append(f"Linha {index}: Valor de internet inválido em {col} ({internet_value})")
    
    def _validate_data_integrity(self, df: pd.DataFrame):
        """Valida integridade dos dados"""
        # Verificar consistência entre campos relacionados
        for index, row in df.iterrows():
            # Se tem smartphone, deveria ter celular
            if 'SMARTPHONE' in row.index and 'CELULAR' in row.index:
                if pd.notna(row['SMARTPHONE']) and pd.notna(row['CELULAR']):
                    if self._is_true_value(row['SMARTPHONE']) and not self._is_true_value(row['CELULAR']):
                        self.warnings.append(f"Linha {index}: Inconsistência - tem smartphone mas não tem celular")
    
    def _is_valid_age_range(self, age_str: str) -> bool:
        """Verifica se é uma faixa etária válida"""
        patterns = [r'\d+\s*[a-]\s*\d+', r'mais\s*de\s*\d+', r'ate\s*\d+', r'\d+\s*anos?']
        return any(re.search(pattern, age_str.lower()) for pattern in patterns)
    
    def _is_valid_education_level(self, education_str: str) -> bool:
        """Verifica se é um nível de educação válido"""
        keywords = ['fundamental', 'medio', 'superior', 'pos', 'graduacao', 'ensino', 'completo', 'incompleto']
        return any(keyword in education_str.lower() for keyword in keywords)
    
    def _is_valid_income_class(self, income_str: str) -> bool:
        """Verifica se é uma classe de renda válida"""
        keywords = ['baixa', 'media', 'alta', 'classe', 'salario', 'sm', 'renda']
        return any(keyword in income_str.lower() for keyword in keywords)
    
    def _is_valid_region(self, region_str: str) -> bool:
        """Verifica se é uma região válida"""
        valid_regions = ['norte', 'nordeste', 'sudeste', 'sul', 'centro-oeste', 'n', 'ne', 'se', 's', 'co']
        return region_str.lower() in valid_regions
    
    def _is_valid_state(self, state_str: str) -> bool:
        """Verifica se é um estado válido"""
        valid_states = ['ac', 'al', 'ap', 'am', 'ba', 'ce', 'df', 'es', 'go', 'ma', 'mt', 'ms', 'mg', 
                       'pa', 'pb', 'pr', 'pe', 'pi', 'rj', 'rn', 'rs', 'ro', 'rr', 'sc', 'sp', 'se', 'to']
        return state_str.lower() in valid_states
    
    def _is_valid_boolean(self, value: Any) -> bool:
        """Verifica se é um valor booleano válido"""
        if isinstance(value, bool):
            return True
        if isinstance(value, (int, float)):
            return value in [0, 1]
        if isinstance(value, str):
            return value.lower().strip() in ['sim', 'nao', 'não', 'yes', 'no', 'true', 'false', '1', '0']
        return False
    
    def _is_true_value(self, value: Any) -> bool:
        """Verifica se o valor representa verdadeiro"""
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value == 1
        if isinstance(value, str):
            return value.lower().strip() in ['sim', 'yes', 'true', '1']
        return False
    
    def validate_single_record(self, record: Dict) -> Tuple[bool, List[str], List[str]]:
        """Valida um único registro
        
        Args:
            record: Dicionário com os dados do registro
            
        Returns:
            Tuple[bool, List[str], List[str]]: (é_válido, erros, avisos)
        """
        self.errors = []
        self.warnings = []
        
        try:
            # Converter para Series para reutilizar métodos existentes
            row = pd.Series(record)
            self._validate_row(row, 0)
            
            is_valid = len(self.errors) == 0
            return is_valid, self.errors, self.warnings
            
        except Exception as e:
            self.logger.error(f"Erro na validação do registro: {str(e)}")
            self.errors.append(f"Erro crítico na validação: {str(e)}")
            return False, self.errors, self.warnings
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Retorna um resumo da validação"""
        return {
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings),
            'errors': self.errors,
            'warnings': self.warnings,
            'is_valid': len(self.errors) == 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def validate_financial_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """Valida dados financeiros
        
        Args:
            data (Dict[str, Any]): Dados financeiros a serem validados
            
        Returns:
            Tuple[bool, List[str], List[str]]: (é_válido, erros, avisos)
        """
        self.errors = []
        self.warnings = []
        
        try:
            # Validar campos obrigatórios
            required_fields = ['valor', 'data', 'categoria']
            for field in required_fields:
                if field not in data or data[field] is None:
                    self.errors.append(f"Campo obrigatório ausente: {field}")
            
            # Validar valor
            if 'valor' in data:
                try:
                    valor = float(data['valor'])
                    if valor < 0:
                        self.warnings.append("Valor negativo detectado")
                    if valor > 1000000:
                        self.warnings.append("Valor muito alto detectado")
                except (ValueError, TypeError):
                    self.errors.append("Valor deve ser um número válido")
            
            # Validar data
            if 'data' in data and data['data']:
                try:
                    if isinstance(data['data'], str):
                        datetime.strptime(data['data'], '%Y-%m-%d')
                    elif not isinstance(data['data'], datetime):
                        self.errors.append("Data deve estar no formato YYYY-MM-DD ou ser um objeto datetime")
                except ValueError:
                    self.errors.append("Formato de data inválido. Use YYYY-MM-DD")
            
            # Validar categoria
            if 'categoria' in data and data['categoria']:
                categoria = str(data['categoria']).strip()
                if len(categoria) < 2:
                    self.errors.append("Categoria deve ter pelo menos 2 caracteres")
                if len(categoria) > 50:
                    self.errors.append("Categoria não pode ter mais de 50 caracteres")
            
            # Validar descrição (opcional, mas se fornecida não pode estar vazia)
            if 'descricao' in data:
                if data['descricao'] is None or str(data['descricao']).strip() == '':
                    self.errors.append("Descrição não pode estar vazia")
                else:
                    descricao = str(data['descricao']).strip()
                    if len(descricao) > 255:
                        self.warnings.append("Descrição muito longa, será truncada")
            
            is_valid = len(self.errors) == 0
            return is_valid, self.errors, self.warnings
            
        except Exception as e:
            self.logger.error(f"Erro na validação de dados financeiros: {str(e)}")
            self.errors.append(f"Erro crítico na validação: {str(e)}")
            return False, self.errors, self.warnings