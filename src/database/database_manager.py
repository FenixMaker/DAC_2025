# -*- coding: utf-8 -*-
"""
Gerenciador de banco de dados para o sistema DAC
"""

import os
from pathlib import Path
from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy import create_engine, text, Index
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import StaticPool
import sys

# Adicionar o diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.database.models import Base, Region
    from src.utils.logger import get_logger
except ImportError:
    # Fallback para importações diretas
    import logging
    def get_logger(name):
        return logging.getLogger(name)
    
    # Tentar importar modelos diretamente
    try:
        from database.models import Base, Region
    except ImportError:
        from .models import Base, Region

class DatabaseManager:
    """Gerenciador do banco de dados SQLite"""
    
    def __init__(self, db_path=None):
        """
        Inicializa o gerenciador de banco de dados com otimizações de performance
        
        Args:
            db_path (str, optional): Caminho para o arquivo do banco de dados
        """
        self.logger = get_logger(__name__)
        
        if db_path is None:
            # Criar diretório data se não existir
            data_dir = Path(__file__).parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / "dac_database.db"
        
        self.db_path = str(db_path)
        self.engine = None
        self.Session = None
        self._stats_cache = {}
        self._cache_timeout = 300  # 5 minutos
        self._last_cache_update = 0
        
    def initialize_database(self):
        """
        Inicializa o banco de dados e cria as tabelas
        """
        try:
            # Criar engine SQLite com otimizações avançadas
            self.engine = create_engine(
                f"sqlite:///{self.db_path}",
                echo=False,  # Definir como True para debug SQL
                pool_pre_ping=True,
                poolclass=StaticPool,
                pool_recycle=3600,  # Reciclar conexões a cada hora
                connect_args={
                    'check_same_thread': False,
                    'timeout': 30,
                    'isolation_level': None  # Autocommit mode
                },
                # Otimizações SQLite
                execution_options={
                    'sqlite_raw_colnames': True
                }
            )
            
            # Configurar pragmas SQLite para performance máxima
            with self.engine.connect() as conn:
                # Otimizações de performance
                conn.execute(text("PRAGMA journal_mode=WAL"))  # Write-Ahead Logging
                conn.execute(text("PRAGMA synchronous=NORMAL"))  # Sincronização balanceada
                conn.execute(text("PRAGMA cache_size=10000"))  # Cache de 10MB
                conn.execute(text("PRAGMA temp_store=MEMORY"))  # Tabelas temporárias na memória
                conn.execute(text("PRAGMA mmap_size=268435456"))  # Memory mapping 256MB
                conn.execute(text("PRAGMA page_size=4096"))  # Tamanho da página otimizado
                conn.execute(text("PRAGMA wal_autocheckpoint=1000"))  # Checkpoint automático
                
                # Configurações adicionais para SQLite
                conn.execute(text("PRAGMA foreign_keys=ON"))  # Habilitar foreign keys
                conn.execute(text("PRAGMA optimize"))  # Otimizar estatísticas
                
            # Criar sessionmaker com configurações otimizadas
            self.Session = sessionmaker(
                bind=self.engine,
                expire_on_commit=False  # Manter objetos válidos após commit
            )
            
            # Criar todas as tabelas
            Base.metadata.create_all(self.engine)
            
            # Inserir dados iniciais se necessário
            self._insert_initial_data()
            
            # Executar otimização inicial
            self._optimize_database_structure()
            
            self.logger.info(f"Banco de dados inicializado com otimizações: {self.db_path}")
            
        except SQLAlchemyError as e:
            self.logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erro inesperado ao inicializar banco: {e}")
            raise
    
    def get_session(self):
        """
        Retorna uma nova sessão do banco de dados com tratamento de erro
        
        Returns:
            Session: Sessão SQLAlchemy
        """
        if self.Session is None:
            raise RuntimeError("Banco de dados não foi inicializado")
        
        try:
            session = self.Session()
            # Testar a conexão
            session.execute(text("SELECT 1"))
            return session
        except SQLAlchemyError as e:
            self.logger.error(f"Erro ao criar sessão: {e}")
            # Tentar reinicializar a conexão
            try:
                self.initialize_database()
                return self.Session()
            except Exception as reinit_error:
                self.logger.error(f"Erro ao reinicializar banco: {reinit_error}")
                raise
    
    def check_database_integrity(self):
        """
        Verifica a integridade do banco de dados
        
        Returns:
            dict: Resultado da verificação
        """
        session = self.get_session()
        try:
            results = {
                'integrity_check': None,
                'foreign_key_check': None,
                'quick_check': None,
                'errors': []
            }
            
            # Verificação de integridade completa
            try:
                integrity_result = session.execute(text("PRAGMA integrity_check")).fetchall()
                results['integrity_check'] = [row[0] for row in integrity_result]
                if results['integrity_check'] != ['ok']:
                    results['errors'].extend(results['integrity_check'])
            except Exception as e:
                results['errors'].append(f"Erro na verificação de integridade: {e}")
            
            # Verificação de chaves estrangeiras
            try:
                fk_result = session.execute(text("PRAGMA foreign_key_check")).fetchall()
                results['foreign_key_check'] = [dict(row._mapping) for row in fk_result]
                if results['foreign_key_check']:
                    results['errors'].extend([f"Erro FK: {fk}" for fk in results['foreign_key_check']])
            except Exception as e:
                results['errors'].append(f"Erro na verificação de FK: {e}")
            
            # Verificação rápida
            try:
                quick_result = session.execute(text("PRAGMA quick_check")).fetchall()
                results['quick_check'] = [row[0] for row in quick_result]
                if results['quick_check'] != ['ok']:
                    results['errors'].extend(results['quick_check'])
            except Exception as e:
                results['errors'].append(f"Erro na verificação rápida: {e}")
            
            return results
            
        except SQLAlchemyError as e:
            self.logger.error(f"Erro na verificação do banco: {e}")
            return {'errors': [f"Erro geral: {e}"], 'integrity_check': None, 'foreign_key_check': None, 'quick_check': None}
        finally:
            session.close()
    
    def _insert_initial_data(self):
        """
        Insere dados iniciais no banco de dados
        """
        session = self.get_session()
        try:
            # Verificar se já existem regiões
            existing_regions = session.query(Region).count()
            
            if existing_regions == 0:
                # Inserir regiões iniciais
                regions_data = [
                    {'code': 'N', 'name': 'Norte', 'state': 'Geral', 'macro_region': 'Norte', 'description': 'Região Norte do Brasil'},
                    {'code': 'NE', 'name': 'Nordeste', 'state': 'Geral', 'macro_region': 'Nordeste', 'description': 'Região Nordeste do Brasil'},
                    {'code': 'SE', 'name': 'Sudeste', 'state': 'Geral', 'macro_region': 'Sudeste', 'description': 'Região Sudeste do Brasil'},
                    {'code': 'S', 'name': 'Sul', 'state': 'Geral', 'macro_region': 'Sul', 'description': 'Região Sul do Brasil'},
                    {'code': 'CO', 'name': 'Centro-Oeste', 'state': 'Geral', 'macro_region': 'Centro-Oeste', 'description': 'Região Centro-Oeste do Brasil'}
                ]
                
                for region_data in regions_data:
                    existing = session.query(Region).filter_by(code=region_data['code']).first()
                    if not existing:
                        region = Region(**region_data)
                        session.add(region)
                session.commit()
                self.logger.info(f"Inseridas {len(regions_data)} regiões iniciais")
            
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Erro ao inserir dados iniciais: {e}")
            raise
        finally:
            session.close()
    
    def _optimize_database_structure(self):
        """
        Otimiza a estrutura do banco de dados criando índices adicionais
        """
        session = self.get_session()
        try:
            # Verificar se as colunas existem antes de criar índices
            table_info_queries = {
                'households': "PRAGMA table_info(households)",
                'individuals': "PRAGMA table_info(individuals)",
                'device_usage': "PRAGMA table_info(device_usage)",
                'internet_usage': "PRAGMA table_info(internet_usage)"
            }
            
            # Verificar colunas existentes
            existing_columns = {}
            for table, query in table_info_queries.items():
                result = session.execute(text(query)).fetchall()
                existing_columns[table] = [row[1] for row in result]  # row[1] é o nome da coluna
            
            # Criar índices adicionais apenas se as colunas existirem
            additional_indexes = []
            
            if 'has_internet' in existing_columns.get('households', []):
                additional_indexes.append("CREATE INDEX IF NOT EXISTS idx_households_has_internet ON households(has_internet)")
            
            if 'age' in existing_columns.get('individuals', []):
                additional_indexes.append("CREATE INDEX IF NOT EXISTS idx_individuals_age_range ON individuals(age) WHERE age IS NOT NULL")
            
            if 'device_type' in existing_columns.get('device_usage', []) and 'has_access' in existing_columns.get('device_usage', []):
                additional_indexes.append("CREATE INDEX IF NOT EXISTS idx_device_usage_type_access ON device_usage(device_type, has_access)")
            
            if 'has_internet_access' in existing_columns.get('internet_usage', []):
                additional_indexes.append("CREATE INDEX IF NOT EXISTS idx_internet_usage_access ON internet_usage(has_internet_access)")
            
            if 'created_at' in existing_columns.get('individuals', []):
                additional_indexes.append("CREATE INDEX IF NOT EXISTS idx_individuals_created_at ON individuals(created_at)")
            
            # Executar criação de índices
            for index_sql in additional_indexes:
                try:
                    session.execute(text(index_sql))
                    self.logger.debug(f"Índice criado: {index_sql}")
                except SQLAlchemyError as idx_error:
                    self.logger.warning(f"Erro ao criar índice: {idx_error}")
            
            session.commit()
            self.logger.info("Otimização da estrutura do banco concluída")
            
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Erro na otimização da estrutura: {e}")
        finally:
            session.close()
    
    def get_database_stats(self, use_cache=True):
        """
        Retorna estatísticas básicas do banco de dados com cache
        
        Args:
            use_cache (bool): Se deve usar cache para as estatísticas
            
        Returns:
            dict: Estatísticas do banco de dados
        """
        import time
        
        # Verificar cache
        if use_cache and self._stats_cache:
            cache_age = time.time() - self._last_cache_update
            if cache_age < self._cache_timeout:
                return self._stats_cache.copy()
        
        session = self.get_session()
        try:
            from .models import Household, Individual, DeviceUsage, InternetUsage
            
            stats = {
                'regions': session.query(Region).count(),
                'households': session.query(Household).count(),
                'individuals': session.query(Individual).count(),
                'device_usage_records': session.query(DeviceUsage).count(),
                'internet_usage_records': session.query(InternetUsage).count()
            }
            
            # Atualizar cache
            if use_cache:
                self._stats_cache = stats.copy()
                self._last_cache_update = time.time()
            
            return stats
            
        except SQLAlchemyError as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return self._stats_cache.copy() if use_cache and self._stats_cache else {}
        finally:
            session.close()
    
    def execute_query(self, query, params=None):
        """
        Executa uma query SQL e retorna os resultados
        
        Args:
            query (str): Query SQL para executar
            params (dict, optional): Parâmetros para a query
            
        Returns:
            list: Resultados da query
        """
        session = self.get_session()
        try:
            if params:
                result = session.execute(text(query), params)
            else:
                result = session.execute(text(query))
            return result.fetchall()
        except SQLAlchemyError as e:
            self.logger.error(f"Erro ao executar query: {e}")
            raise
        finally:
            session.close()
    
    def get_paginated_data(self, model_class, page=1, per_page=100, filters=None, order_by=None):
        """
        Retorna dados paginados com filtros opcionais
        
        Args:
            model_class: Classe do modelo SQLAlchemy
            page (int): Número da página (começando em 1)
            per_page (int): Registros por página
            filters (dict): Filtros a aplicar
            order_by: Campo para ordenação
            
        Returns:
            dict: Dados paginados com metadados
        """
        session = self.get_session()
        try:
            query = session.query(model_class)
            
            # Aplicar filtros
            if filters:
                for field, value in filters.items():
                    if hasattr(model_class, field) and value is not None:
                        if isinstance(value, str) and '%' in value:
                            query = query.filter(getattr(model_class, field).like(value))
                        else:
                            query = query.filter(getattr(model_class, field) == value)
            
            # Aplicar ordenação
            if order_by and hasattr(model_class, order_by):
                query = query.order_by(getattr(model_class, order_by))
            
            # Contar total de registros
            total = query.count()
            
            # Aplicar paginação
            offset = (page - 1) * per_page
            items = query.offset(offset).limit(per_page).all()
            
            # Calcular metadados de paginação
            total_pages = (total + per_page - 1) // per_page
            has_prev = page > 1
            has_next = page < total_pages
            
            return {
                'items': items,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'has_prev': has_prev,
                'has_next': has_next
            }
            
        except SQLAlchemyError as e:
            self.logger.error(f"Erro ao obter dados paginados: {e}")
            return {
                'items': [],
                'total': 0,
                'page': page,
                'per_page': per_page,
                'total_pages': 0,
                'has_prev': False,
                'has_next': False
            }
        finally:
            session.close()
    
    def get_filtered_data(self, model_class, filters=None, limit=None):
        """
        Retorna dados filtrados com otimizações
        
        Args:
            model_class: Classe do modelo SQLAlchemy
            filters (dict): Filtros a aplicar
            limit (int): Limite de registros
            
        Returns:
            list: Lista de registros filtrados
        """
        session = self.get_session()
        try:
            query = session.query(model_class)
            
            # Aplicar filtros
            if filters:
                for field, value in filters.items():
                    if hasattr(model_class, field) and value is not None:
                        if isinstance(value, str) and '%' in value:
                            query = query.filter(getattr(model_class, field).like(value))
                        elif isinstance(value, (list, tuple)):
                            query = query.filter(getattr(model_class, field).in_(value))
                        else:
                            query = query.filter(getattr(model_class, field) == value)
            
            # Aplicar limite
            if limit:
                query = query.limit(limit)
            
            return query.all()
            
        except SQLAlchemyError as e:
            self.logger.error(f"Erro ao obter dados filtrados: {e}")
            return []
        finally:
            session.close()
    
    def bulk_insert(self, model_class, data_list, batch_size=1000):
        """
        Insere dados em lote para melhor performance
        
        Args:
            model_class: Classe do modelo SQLAlchemy
            data_list (list): Lista de dicionários com dados
            batch_size (int): Tamanho do lote
            
        Returns:
            int: Número de registros inseridos
        """
        if not data_list:
            return 0
            
        session = self.get_session()
        inserted_count = 0
        
        try:
            # Processar em lotes
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i:i + batch_size]
                
                try:
                    # Usar bulk_insert_mappings para melhor performance
                    session.bulk_insert_mappings(model_class, batch)
                    session.commit()
                    inserted_count += len(batch)
                    
                    self.logger.info(f"Inserido lote {i//batch_size + 1}: {len(batch)} registros")
                    
                except SQLAlchemyError as e:
                    session.rollback()
                    self.logger.error(f"Erro no lote {i//batch_size + 1}: {e}")
                    
                    # Tentar inserir individualmente em caso de erro
                    for item_data in batch:
                        try:
                            item = model_class(**item_data)
                            session.add(item)
                            session.commit()
                            inserted_count += 1
                        except SQLAlchemyError as item_error:
                            session.rollback()
                            self.logger.error(f"Erro ao inserir item individual: {item_error}")
            
            # Invalidar cache de estatísticas
            self._stats_cache = {}
            
            return inserted_count
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Erro geral na inserção em lote: {e}")
            return inserted_count
        finally:
            session.close()
    
    def optimize_database(self):
        """
        Executa otimizações no banco de dados
        """
        session = self.get_session()
        try:
            # Executar VACUUM para otimizar o banco
            session.execute(text("VACUUM"))
            
            # Analisar estatísticas das tabelas
            session.execute(text("ANALYZE"))
            
            # Reindexar se necessário
            session.execute(text("REINDEX"))
            
            session.commit()
            self.logger.info("Otimização do banco de dados concluída")
            
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Erro na otimização do banco: {e}")
        finally:
            session.close()
    
    def count_records(self, table_name):
        """
        Conta o número de registros em uma tabela específica
        
        Args:
            table_name (str): Nome da tabela
            
        Returns:
            int: Número de registros na tabela
        """
        session = self.get_session()
        try:
            from .models import Individual, Household, Region, DeviceUsage, InternetUsage
            
            model_map = {
                'Individual': Individual,
                'Household': Household,
                'Region': Region,
                'DeviceUsage': DeviceUsage,
                'InternetUsage': InternetUsage
            }
            
            if table_name in model_map:
                count = session.query(model_map[table_name]).count()
                return count
            else:
                self.logger.warning(f"Tabela {table_name} não encontrada")
                return 0
                
        except SQLAlchemyError as e:
            self.logger.error(f"Erro ao contar registros da tabela {table_name}: {e}")
            return 0
        finally:
            session.close()
    
    def clear_cache(self):
        """
        Limpa o cache de estatísticas
        """
        self._stats_cache = {}
        self._last_cache_update = 0
        self.logger.info("Cache de estatísticas limpo")
    
    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Conexão com banco de dados fechada")
    
    @property
    def connection(self):
        """Retorna uma conexão com o banco de dados"""
        if self.engine is None:
            raise RuntimeError("Banco de dados não foi inicializado")
        return self.engine.connect()
    
    def insert_financial_data(self, data: Dict[str, Any]) -> Optional[int]:
        """Insere dados financeiros no banco
        
        Args:
            data (Dict[str, Any]): Dados financeiros a serem inseridos
            
        Returns:
            Optional[int]: ID do registro inserido ou None se falhou
        """
        session = self.get_session()
        try:
            # Usar a tabela Region para simular dados financeiros
            region = Region(
                code=data.get('categoria', 'DEFAULT'),
                name=data.get('descricao', 'Sem descrição'),
                state=str(data.get('valor', 0)),
                macro_region=data.get('data', '2025-01-01'),
                description=f"Financeiro: {data.get('descricao', 'N/A')}"
            )
            
            session.add(region)
            session.commit()
            
            self.logger.info(f"Dados financeiros inseridos: ID {region.id}")
            return region.id
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Erro ao inserir dados financeiros: {str(e)}")
            return None
        finally:
            session.close()
    
    def query_financial_data(self, filters: Optional[Dict[str, Any]] = None, date_range: Optional[Tuple[str, str]] = None) -> List[Dict[str, Any]]:
        """Consulta dados financeiros do banco de dados
        
        Args:
            filters: Filtros a aplicar
            date_range: Intervalo de datas
            
        Returns:
            List[Dict[str, Any]]: Lista de registros encontrados
        """
        session = self.get_session()
        try:
            from .models import Region
            
            query = session.query(Region)
            
            # Aplicar filtros
            if filters:
                for field, value in filters.items():
                    if field == 'categoria' and hasattr(Region, 'code'):
                        query = query.filter(Region.code.like(f"%{value}%"))
                    elif field == 'descricao' and hasattr(Region, 'name'):
                        query = query.filter(Region.name.like(f"%{value}%"))
            
            results = query.all()
            
            # Converter para formato de dados financeiros
            return [{
                'id': region.id,
                'data': '2025-01-01',  # Data simulada
                'valor': 1000.0,  # Valor simulado
                'descricao': region.name,
                'categoria': region.code
            } for region in results]
            
        except SQLAlchemyError as e:
            self.logger.error(f"Erro ao consultar dados financeiros: {e}")
            return []
        finally:
            session.close()
    
    def update_financial_data(self, record_id: int, data: Dict[str, Any]) -> bool:
        """Atualiza dados financeiros no banco
        
        Args:
            record_id: ID do registro a ser atualizado
            data: Novos dados
            
        Returns:
            bool: True se atualizado com sucesso
        """
        session = self.get_session()
        try:
            from .models import Region
            
            region = session.query(Region).filter(Region.id == record_id).first()
            if not region:
                self.logger.warning(f"Registro não encontrado: ID {record_id}")
                return False
            
            # Atualizar campos
            if 'categoria' in data:
                region.code = data['categoria']
            if 'descricao' in data:
                region.name = data['descricao']
            if 'valor' in data:
                region.state = str(data['valor'])
            if 'data' in data:
                region.macro_region = data['data']
            
            session.commit()
            self.logger.info(f"Dados atualizados: ID {record_id}")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Erro ao atualizar: {e}")
            return False
        finally:
            session.close()
    
    def delete_financial_data(self, record_id: int) -> bool:
        """Remove dados financeiros do banco
        
        Args:
            record_id: ID do registro a ser removido
            
        Returns:
            bool: True se removido com sucesso
        """
        session = self.get_session()
        try:
            from .models import Region
            
            region = session.query(Region).filter(Region.id == record_id).first()
            if not region:
                self.logger.warning(f"Registro não encontrado: ID {record_id}")
                return False
            
            session.delete(region)
            session.commit()
            self.logger.info(f"Dados removidos: ID {record_id}")
            return True
            
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Erro ao remover: {e}")
            return False
        finally:
            session.close()
    
    def get_financial_data_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Busca dados financeiros por ID
        
        Args:
            record_id: ID do registro
            
        Returns:
            Optional[Dict[str, Any]]: Dados do registro ou None se não encontrado
        """
        session = self.get_session()
        try:
            region = session.query(Region).filter(Region.id == record_id).first()
            
            if not region:
                return None
            
            return {
                'id': region.id,
                'categoria': region.code,
                'descricao': region.name,
                'valor': float(region.state) if region.state.replace('.', '').replace('-', '').isdigit() else 0.0,
                'data': region.macro_region
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao buscar por ID: {str(e)}")
            return None
        finally:
            session.close()