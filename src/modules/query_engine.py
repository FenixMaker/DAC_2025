#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de motor de consultas para o sistema DAC
"""

from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, or_
from datetime import datetime
import logging

from ..database.models import Individual, Household, Region, DeviceUsage, InternetUsage
from ..database.database_manager import DatabaseManager
from ..utils.logger import get_logger

class QueryEngine:
    """Motor de consultas para filtrar e buscar dados no sistema DAC"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        """Inicializa o motor de consultas"""
        self.db_manager = db_manager or DatabaseManager()
        self.logger = get_logger(__name__)
        
    def execute_query(self, filters: Dict[str, Any], page: int = 1, per_page: int = 100) -> Optional[List[Dict]]:
        """
        Executa consulta com filtros especificados
        
        Args:
            filters: Dicionário com filtros a aplicar
            page: Página atual (para paginação)
            per_page: Registros por página
            
        Returns:
            Lista de dicionários com os resultados ou None em caso de erro
        """
        try:
            with self.db_manager.get_session() as session:
                # Query base com joins necessários
                query = session.query(Individual)\
                    .join(Household, Individual.household_id == Household.id)\
                    .join(Region, Household.region_id == Region.id)\
                    .options(
                        joinedload(Individual.household),
                        joinedload(Individual.device_usage),
                        joinedload(Individual.internet_usage)
                    )
                
                # Aplicar filtros
                query = self._apply_filters(query, filters)
                
                # Aplicar paginação
                offset = (page - 1) * per_page
                results = query.offset(offset).limit(per_page).all()
                
                # Converter para dicionários
                return self._convert_to_dict(results)
                
        except Exception as e:
            self.logger.error(f"Erro ao executar consulta: {e}")
            return None
    
    def count_results(self, filters: Dict[str, Any]) -> int:
        """
        Conta o número total de resultados para os filtros especificados
        
        Args:
            filters: Dicionário com filtros a aplicar
            
        Returns:
            Número total de registros que atendem aos filtros
        """
        try:
            with self.db_manager.get_session() as session:
                query = session.query(Individual)\
                    .join(Household, Individual.household_id == Household.id)\
                    .join(Region, Household.region_id == Region.id)
                
                query = self._apply_filters(query, filters)
                return query.count()
                
        except Exception as e:
            self.logger.error(f"Erro ao contar resultados: {e}")
            return 0
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """
        Aplica filtros à consulta
        
        Args:
            query: Query SQLAlchemy
            filters: Dicionário com filtros
            
        Returns:
            Query com filtros aplicados
        """
        try:
            # Filtro por região
            if filters.get('region') and filters['region'] not in ['Todas', 'Todos']:
                query = query.filter(Region.name == filters['region'])
            
            # Filtro por idade
            if filters.get('age_min') is not None:
                query = query.filter(Individual.age >= filters['age_min'])
            if filters.get('age_max') is not None:
                query = query.filter(Individual.age <= filters['age_max'])
            
            # Filtro por gênero
            if filters.get('gender') and filters['gender'] not in ['Todos', 'Todas']:
                query = query.filter(Individual.gender == filters['gender'])
            
            # Filtro por renda
            if filters.get('income') and filters['income'] not in ['Todas', 'Todos', 'Sem dados']:
                query = query.filter(Household.income_range == filters['income'])
            
            # Filtro por deficiência
            if filters.get('disability') and filters['disability'] not in ['Todos', 'Todas']:
                has_disability = filters['disability'] == 'Sim'
                query = query.filter(Individual.has_disability == has_disability)
            
            # Filtro por acesso à internet
            if filters.get('internet') and filters['internet'] not in ['Todos', 'Todas']:
                has_internet = filters['internet'] == 'Sim'
                query = query.filter(Household.has_internet == has_internet)
            
            # Filtro por educação
            if filters.get('education') and filters['education'] not in ['Todas', 'Todos', 'Sem dados']:
                query = query.filter(Individual.education_level == filters['education'])
            
            # Filtro por tamanho do domicílio
            if filters.get('household_size_min') is not None:
                query = query.filter(Household.household_size >= filters['household_size_min'])
            if filters.get('household_size_max') is not None:
                query = query.filter(Household.household_size <= filters['household_size_max'])
            
            return query
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar filtros: {e}")
            return query
    
    def _convert_to_dict(self, results: List) -> List[Dict]:
        """
        Converte resultados SQLAlchemy para dicionários
        
        Args:
            results: Lista de objetos SQLAlchemy
            
        Returns:
            Lista de dicionários
        """
        converted_results = []
        
        for individual in results:
            try:
                result_dict = {
                    'id': individual.id,
                    'age': individual.age,
                    'gender': individual.gender,
                    'education_level': individual.education_level,
                    'has_disability': individual.has_disability,
                    'household': {
                        'id': individual.household.id if individual.household else None,
                        'household_size': individual.household.household_size if individual.household else None,
                        'income_range': individual.household.income_range if individual.household else None,
                        'has_internet': individual.household.has_internet if individual.household else None,
                        'region': {
                            'name': individual.household.region.name if individual.household and individual.household.region else None,
                            'state': individual.household.region.state if individual.household and individual.household.region else None
                        } if individual.household else None
                    },
                    'devices': [],
                    'internet_usage': []
                }
                
                # Adicionar dispositivos
                if individual.device_usage:
                    for device in individual.device_usage:
                        result_dict['devices'].append({
                            'device_type': device.device_type,
                            'has_device': device.has_device
                        })
                
                # Adicionar uso de internet
                if individual.internet_usage:
                    for usage in individual.internet_usage:
                        result_dict['internet_usage'].append({
                            'usage_type': usage.usage_type,
                            'frequency': usage.frequency
                        })
                
                converted_results.append(result_dict)
                
            except Exception as e:
                self.logger.warning(f"Erro ao converter registro {individual.id}: {e}")
                continue
        
        return converted_results
    
    def get_filter_options(self) -> Dict[str, List[str]]:
        """
        Retorna opções disponíveis para filtros
        
        Returns:
            Dicionário com listas de opções para cada filtro
        """
        options = {
            'regions': ['Todas'],
            'genders': ['Todos', 'Masculino', 'Feminino'],
            'incomes': ['Todas'],
            'educations': ['Todas'],
            'disabilities': ['Todos', 'Sim', 'Não'],
            'internet': ['Todos', 'Sim', 'Não']
        }
        
        try:
            with self.db_manager.get_session() as session:
                # Carregar regiões
                regions = session.query(Region.name).distinct().filter(Region.name.isnot(None)).all()
                options['regions'].extend([r[0] for r in regions if r[0] and r[0].strip()])
                
                # Carregar faixas de renda
                incomes = session.query(Household.income_range).distinct().filter(Household.income_range.isnot(None)).all()
                options['incomes'].extend([i[0] for i in incomes if i[0] and i[0].strip()])
                
                # Carregar níveis de educação
                educations = session.query(Individual.education_level).distinct().filter(Individual.education_level.isnot(None)).all()
                options['educations'].extend([e[0] for e in educations if e[0] and e[0].strip()])
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar opções de filtro: {e}")
        
        return options
    
    def execute_advanced_query(self, query_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Executa consulta avançada com agregações e estatísticas
        
        Args:
            query_params: Parâmetros da consulta avançada
            
        Returns:
            Dicionário com resultados e estatísticas
        """
        try:
            results = self.execute_query(query_params.get('filters', {}), 
                                       query_params.get('page', 1),
                                       query_params.get('per_page', 1000))
            
            if results is None:
                return None
            
            # Calcular estatísticas
            stats = self._calculate_statistics(results)
            
            return {
                'results': results,
                'statistics': stats,
                'total_count': len(results),
                'query_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao executar consulta avançada: {e}")
            return None
    
    def _calculate_statistics(self, results: List[Dict]) -> Dict[str, Any]:
        """
        Calcula estatísticas dos resultados
        
        Args:
            results: Lista de resultados
            
        Returns:
            Dicionário com estatísticas
        """
        if not results:
            return {}
        
        try:
            stats = {
                'total_individuals': len(results),
                'age_distribution': {},
                'gender_distribution': {},
                'education_distribution': {},
                'region_distribution': {},
                'disability_count': 0,
                'internet_access_count': 0
            }
            
            for result in results:
                # Distribuição por idade
                age = result.get('age')
                if age is not None:
                    age_group = f"{(age // 10) * 10}-{(age // 10) * 10 + 9}"
                    stats['age_distribution'][age_group] = stats['age_distribution'].get(age_group, 0) + 1
                
                # Distribuição por gênero
                gender = result.get('gender')
                if gender:
                    stats['gender_distribution'][gender] = stats['gender_distribution'].get(gender, 0) + 1
                
                # Distribuição por educação
                education = result.get('education_level')
                if education:
                    stats['education_distribution'][education] = stats['education_distribution'].get(education, 0) + 1
                
                # Distribuição por região
                if result.get('household') and result['household'].get('region'):
                    region = result['household']['region'].get('name')
                    if region:
                        stats['region_distribution'][region] = stats['region_distribution'].get(region, 0) + 1
                
                # Contagem de deficiências
                if result.get('has_disability'):
                    stats['disability_count'] += 1
                
                # Contagem de acesso à internet
                if result.get('household') and result['household'].get('has_internet'):
                    stats['internet_access_count'] += 1
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular estatísticas: {e}")
            return {}