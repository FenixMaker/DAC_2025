
# -*- coding: utf-8 -*-
"""
Sistema de logging aprimorado para o DAC
"""

import logging
import logging.handlers
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class LogLevel(Enum):
    """Níveis de log personalizados"""
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    TRACE = 5

class StructuredFormatter(logging.Formatter):
    """Formatter para logs estruturados em JSON"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Adicionar contexto extra se disponível
        if hasattr(record, "context"):
            log_entry["context"] = record.context
        
        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id
        
        if hasattr(record, "session_id"):
            log_entry["session_id"] = record.session_id
        
        # Adicionar stack trace para erros
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

class EnhancedLogger:
    """Logger aprimorado com funcionalidades avançadas"""
    
    def __init__(self, name="DAC_Enhanced", level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Evitar duplicação de handlers
        if self.logger.handlers:
            return
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura handlers de logging"""
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Handler para arquivo principal (texto)
        main_log = log_dir / f"dac_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Handler para logs estruturados (JSON)
        json_log = log_dir / f"dac_structured_{datetime.now().strftime('%Y%m%d')}.json"
        json_handler = logging.handlers.RotatingFileHandler(
            json_log, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(StructuredFormatter())
        
        # Handler para erros críticos
        error_log = log_dir / f"dac_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log, maxBytes=5*1024*1024, backupCount=10, encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(file_formatter)
        
        # Adicionar handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(json_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)
    
    def log_with_context(self, level, message, context=None, user_id=None, session_id=None):
        """Log com contexto adicional"""
        extra = {}
        if context:
            extra["context"] = context
        if user_id:
            extra["user_id"] = user_id
        if session_id:
            extra["session_id"] = session_id
        
        self.logger.log(level, message, extra=extra)
    
    def error_with_context(self, message, exception=None, context=None, user_action=None):
        """Log de erro com contexto detalhado"""
        extra = {"context": context or {}, "user_action": user_action}
        
        if exception:
            self.logger.error(message, exc_info=exception, extra=extra)
        else:
            self.logger.error(message, extra=extra)

# Instância global
_enhanced_logger = None

def get_enhanced_logger(name=None):
    """Retorna instância do logger aprimorado"""
    global _enhanced_logger
    if _enhanced_logger is None:
        _enhanced_logger = EnhancedLogger(name or "DAC_Enhanced")
    return _enhanced_logger
