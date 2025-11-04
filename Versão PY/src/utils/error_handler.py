# -*- coding: utf-8 -*-
"""
Módulo de tratamento de erros robusto para o sistema DAC
"""

import time
import functools
import os
import shutil
from typing import Callable, Any, Optional, Type, Tuple
from sqlalchemy.exc import (
    SQLAlchemyError, DisconnectionError, TimeoutError as SQLTimeoutError,
    IntegrityError, OperationalError, DatabaseError
)
from ..utils.logger import get_logger

class DatabaseErrorHandler:
    """Classe para tratamento robusto de erros de banco de dados"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.logger = get_logger(__name__)
    
    def retry_on_db_error(self, 
                         max_retries: Optional[int] = None,
                         base_delay: Optional[float] = None,
                         exponential_backoff: bool = True):
        """Decorator para retry automático em operações de banco de dados
        
        Args:
            max_retries: Número máximo de tentativas
            base_delay: Delay base entre tentativas (segundos)
            exponential_backoff: Se deve usar backoff exponencial
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                retries = max_retries or self.max_retries
                delay = base_delay or self.base_delay
                
                last_exception = None
                
                for attempt in range(retries + 1):
                    try:
                        return func(*args, **kwargs)
                    
                    except (DisconnectionError, SQLTimeoutError, OperationalError) as e:
                        last_exception = e
                        
                        if attempt < retries:
                            wait_time = delay * (2 ** attempt if exponential_backoff else 1)
                            self.logger.warning(
                                f"Tentativa {attempt + 1}/{retries + 1} falhou para {func.__name__}: {str(e)}. "
                                f"Tentando novamente em {wait_time:.1f}s"
                            )
                            time.sleep(wait_time)
                        else:
                            self.logger.error(
                                f"Todas as {retries + 1} tentativas falharam para {func.__name__}: {str(e)}"
                            )
                    
                    except IntegrityError as e:
                        # Erros de integridade não devem ser retentados
                        self.logger.error(f"Erro de integridade em {func.__name__}: {str(e)}")
                        raise
                    
                    except SQLAlchemyError as e:
                        # Outros erros SQLAlchemy podem ser retentados uma vez
                        last_exception = e
                        
                        if attempt == 0:
                            self.logger.warning(
                                f"Erro SQLAlchemy em {func.__name__}: {str(e)}. Tentando novamente..."
                            )
                            time.sleep(delay)
                        else:
                            self.logger.error(
                                f"Erro SQLAlchemy persistente em {func.__name__}: {str(e)}"
                            )
                            raise
                    
                    except Exception as e:
                        # Outros erros não são retentados
                        self.logger.error(f"Erro não relacionado ao banco em {func.__name__}: {str(e)}")
                        raise
                
                # Se chegou aqui, todas as tentativas falharam
                raise last_exception
            
            return wrapper
        return decorator
    
    def safe_execute(self, 
                    func: Callable, 
                    *args, 
                    default_return: Any = None,
                    log_errors: bool = True,
                    **kwargs) -> Tuple[bool, Any]:
        """Executa uma função de forma segura com tratamento de erros
        
        Args:
            func: Função a ser executada
            *args: Argumentos posicionais
            default_return: Valor padrão em caso de erro
            log_errors: Se deve logar erros
            **kwargs: Argumentos nomeados
            
        Returns:
            Tuple[bool, Any]: (sucesso, resultado)
        """
        try:
            result = func(*args, **kwargs)
            return True, result
        
        except Exception as e:
            if log_errors:
                self.logger.error(f"Erro na execução de {func.__name__}: {str(e)}")
            return False, default_return
    
    def handle_transaction(self, session, operations: list, rollback_on_error: bool = True) -> bool:
        """Executa múltiplas operações em uma transação com tratamento de erros
        
        Args:
            session: Sessão do SQLAlchemy
            operations: Lista de operações (funções) a serem executadas
            rollback_on_error: Se deve fazer rollback em caso de erro
            
        Returns:
            bool: True se todas as operações foram bem-sucedidas
        """
        try:
            for i, operation in enumerate(operations):
                try:
                    if callable(operation):
                        operation()
                    else:
                        self.logger.warning(f"Operação {i} não é callable: {operation}")
                
                except Exception as e:
                    self.logger.error(f"Erro na operação {i}: {str(e)}")
                    if rollback_on_error:
                        session.rollback()
                    raise
            
            session.commit()
            return True
        
        except Exception as e:
            self.logger.error(f"Erro na transação: {str(e)}")
            if rollback_on_error:
                try:
                    session.rollback()
                except Exception as rollback_error:
                    self.logger.error(f"Erro no rollback: {str(rollback_error)}")
            return False
    
    def validate_session(self, session) -> bool:
        """Valida se a sessão está ativa e funcional
        
        Args:
            session: Sessão do SQLAlchemy
            
        Returns:
            bool: True se a sessão está válida
        """
        try:
            # Tenta executar uma query simples
            session.execute('SELECT 1')
            return True
        
        except Exception as e:
            self.logger.error(f"Sessão inválida: {str(e)}")
            return False
    
    def get_error_category(self, error: Exception) -> str:
        """Categoriza o tipo de erro para melhor tratamento
        
        Args:
            error: Exceção a ser categorizada
            
        Returns:
            str: Categoria do erro
        """
        if isinstance(error, DisconnectionError):
            return "connection_lost"
        elif isinstance(error, SQLTimeoutError):
            return "timeout"
        elif isinstance(error, IntegrityError):
            return "integrity_violation"
        elif isinstance(error, OperationalError):
            return "operational_error"
        elif isinstance(error, DatabaseError):
            return "database_error"
        elif isinstance(error, SQLAlchemyError):
            return "sqlalchemy_error"
        else:
            return "unknown_error"
    
    def should_retry(self, error: Exception) -> bool:
        """Determina se um erro deve ser retentado
        
        Args:
            error: Exceção a ser analisada
            
        Returns:
            bool: True se deve ser retentado
        """
        category = self.get_error_category(error)
        
        # Erros que devem ser retentados
        retryable_categories = {
            "connection_lost",
            "timeout", 
            "operational_error"
        }
        
        return category in retryable_categories
    
    def log_error_details(self, error: Exception, context: str = ""):
        """Loga detalhes completos do erro
        
        Args:
            error: Exceção a ser logada
            context: Contexto adicional
        """
        category = self.get_error_category(error)
        
        error_details = {
            "type": type(error).__name__,
            "category": category,
            "message": str(error),
            "context": context,
            "retryable": self.should_retry(error)
        }
        
        self.logger.error(f"Detalhes do erro: {error_details}")
        
        # Log adicional para erros específicos
        if isinstance(error, IntegrityError):
            self.logger.error(f"Violação de integridade - verifique constraints e dados duplicados")
        elif isinstance(error, DisconnectionError):
            self.logger.error(f"Conexão perdida - verifique conectividade com o banco")
        elif isinstance(error, SQLTimeoutError):
            self.logger.error(f"Timeout - considere otimizar a query ou aumentar timeout")


class FileErrorHandler:
    """Classe para tratamento de erros relacionados a arquivos"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def safe_file_operation(self, 
                           operation: Callable,
                           file_path: str,
                           *args,
                           create_backup: bool = False,
                           **kwargs) -> Tuple[bool, Any]:
        """Executa operação de arquivo de forma segura
        
        Args:
            operation: Operação a ser executada
            file_path: Caminho do arquivo
            create_backup: Se deve criar backup antes da operação
            
        Returns:
            Tuple[bool, Any]: (sucesso, resultado)
        """
        try:
            # Criar backup se solicitado
            if create_backup and os.path.exists(file_path):
                backup_path = f"{file_path}.backup_{int(time.time())}"
                shutil.copy2(file_path, backup_path)
                self.logger.info(f"Backup criado: {backup_path}")
            
            result = operation(file_path, *args, **kwargs)
            return True, result
        
        except FileNotFoundError:
            self.logger.error(f"Arquivo não encontrado: {file_path}")
            return False, None
        
        except PermissionError:
            self.logger.error(f"Sem permissão para acessar: {file_path}")
            return False, None
        
        except OSError as e:
            self.logger.error(f"Erro do sistema operacional: {str(e)}")
            return False, None
        
        except Exception as e:
            self.logger.error(f"Erro inesperado na operação de arquivo: {str(e)}")
            return False, None


# Instâncias globais para uso em todo o sistema
db_error_handler = DatabaseErrorHandler()
file_error_handler = FileErrorHandler()

# Decorators convenientes
retry_db_operation = db_error_handler.retry_on_db_error()
retry_db_operation_aggressive = db_error_handler.retry_on_db_error(max_retries=5, base_delay=2.0)