"""
Gerenciador PostgreSQL para o Sistema DAC
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from .models import Base
from ..utils.logger import get_logger

class PostgreSQLManager:
    """Gerenciador de banco PostgreSQL"""
    
    def __init__(self, host='localhost', port=5432, database='sistema_dac', 
                 username='postgres', password='142525'):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.engine = None
        self.Session = None
        self.logger = get_logger(__name__)
        
    def get_connection_string(self):
        """Retorna string de conexão PostgreSQL"""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def create_database_if_not_exists(self):
        """Cria o banco de dados se não existir"""
        try:
            # Conectar ao postgres (banco padrão) para criar o banco dac
            admin_conn_string = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/postgres"
            
            # Usar psycopg2 diretamente para operações administrativas
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                database='postgres'
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            cursor = conn.cursor()
            
            # Verificar se o banco já existe
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.database,))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f'CREATE DATABASE "{self.database}"')
                self.logger.info(f"Banco de dados '{self.database}' criado com sucesso")
            else:
                self.logger.info(f"Banco de dados '{self.database}' já existe")
                
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Erro ao criar banco de dados: {e}")
            raise
    
    def initialize_connection(self):
        """Inicializa conexão com PostgreSQL"""
        try:
            # Criar banco se não existir
            self.create_database_if_not_exists()
            
            # Criar engine do SQLAlchemy com configurações em PT-BR
            conn_string = self.get_connection_string()
            self.engine = create_engine(
                conn_string,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False,
                connect_args={
                    "client_encoding": "utf8",
                    "application_name": "Sistema DAC - Análise de Dados"
                }
            )
            
            # Criar sessionmaker
            self.Session = sessionmaker(bind=self.engine)
            
            # Testar conexão
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            self.logger.info("Conexão PostgreSQL inicializada com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao conectar com PostgreSQL: {e}")
            return False
    
    def create_tables(self):
        """Cria todas as tabelas no PostgreSQL"""
        try:
            if not self.engine:
                raise Exception("Engine não inicializada. Chame initialize_connection() primeiro.")
                
            Base.metadata.create_all(self.engine)
            self.logger.info("Tabelas criadas com sucesso no PostgreSQL")
            
        except Exception as e:
            self.logger.error(f"Erro ao criar tabelas: {e}")
            raise
    
    def get_session(self):
        """Retorna uma nova sessão"""
        if not self.Session:
            raise Exception("Sessão não inicializada. Chame initialize_connection() primeiro.")
        return self.Session()
    
    def test_connection(self):
        """Testa a conexão com o banco"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                self.logger.info(f"Conexão teste OK. PostgreSQL: {version}")
                return True, version
        except Exception as e:
            self.logger.error(f"Teste de conexão falhou: {e}")
            return False, str(e)
    
    def close_connection(self):
        """Fecha a conexão"""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Conexão PostgreSQL fechada")
