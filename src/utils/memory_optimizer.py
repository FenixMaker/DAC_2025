
# -*- coding: utf-8 -*-
"""
Otimizador de memória para o sistema DAC
"""

import gc
import psutil
import sys
from typing import Dict, Any, Optional, Callable
from functools import wraps
import logging
from contextlib import contextmanager

class MemoryOptimizer:
    """Otimizador de uso de memória"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.memory_threshold = 500 * 1024 * 1024  # 500MB
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Retorna informações de uso de memória"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024
        }
    
    def force_garbage_collection(self) -> Dict[str, int]:
        """Força coleta de lixo"""
        before = len(gc.get_objects())
        collected = gc.collect()
        after = len(gc.get_objects())
        
        self.logger.debug(f"Garbage collection: {collected} objects collected")
        
        return {
            'objects_before': before,
            'objects_after': after,
            'collected': collected
        }
    
    def check_memory_pressure(self) -> bool:
        """Verifica se há pressão de memória"""
        memory_info = self.get_memory_usage()
        return memory_info['rss_mb'] * 1024 * 1024 > self.memory_threshold
    
    @contextmanager
    def memory_monitor(self, operation_name: str = "operation"):
        """Context manager para monitorar uso de memória"""
        start_memory = self.get_memory_usage()
        start_time = time.time()
        
        try:
            yield
        finally:
            end_memory = self.get_memory_usage()
            end_time = time.time()
            
            memory_diff = end_memory['rss_mb'] - start_memory['rss_mb']
            duration = end_time - start_time
            
            self.logger.info(
                f"{operation_name}: {duration:.2f}s, "
                f"Memory change: {memory_diff:+.2f}MB"
            )
            
            # Força GC se uso de memória aumentou muito
            if memory_diff > 50:  # 50MB
                self.force_garbage_collection()

def memory_efficient(func: Callable) -> Callable:
    """Decorator para operações eficientes em memória"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        optimizer = MemoryOptimizer()
        
        with optimizer.memory_monitor(func.__name__):
            # Verificar pressão de memória antes
            if optimizer.check_memory_pressure():
                optimizer.force_garbage_collection()
            
            result = func(*args, **kwargs)
            
            # Verificar pressão de memória depois
            if optimizer.check_memory_pressure():
                optimizer.force_garbage_collection()
            
            return result
    
    return wrapper

# Instância global
_memory_optimizer = None

def get_memory_optimizer() -> MemoryOptimizer:
    """Retorna instância do otimizador de memória"""
    global _memory_optimizer
    if _memory_optimizer is None:
        _memory_optimizer = MemoryOptimizer()
    return _memory_optimizer
