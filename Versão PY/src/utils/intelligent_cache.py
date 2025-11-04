
# -*- coding: utf-8 -*-
"""
Sistema de cache inteligente para o DAC
"""

import time
import json
import hashlib
from typing import Any, Dict, Optional, Callable
from collections import OrderedDict
from threading import RLock
from functools import wraps
from pathlib import Path

class IntelligentCache:
    """Cache inteligente com TTL e LRU"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache = OrderedDict()
        self.timestamps = {}
        self.ttls = {}
        self.lock = RLock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera item do cache"""
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None
            
            # Verificar TTL
            if self._is_expired(key):
                self._remove(key)
                self.misses += 1
                return None
            
            # Mover para o final (LRU)
            value = self.cache.pop(key)
            self.cache[key] = value
            self.hits += 1
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Armazena item no cache"""
        with self.lock:
            if key in self.cache:
                self.cache.pop(key)
            
            # Remover itens antigos se necessário
            while len(self.cache) >= self.max_size:
                oldest_key = next(iter(self.cache))
                self._remove(oldest_key)
            
            self.cache[key] = value
            self.timestamps[key] = time.time()
            self.ttls[key] = ttl or self.default_ttl
    
    def _is_expired(self, key: str) -> bool:
        """Verifica se item expirou"""
        if key not in self.timestamps:
            return True
        
        age = time.time() - self.timestamps[key]
        return age > self.ttls.get(key, self.default_ttl)
    
    def _remove(self, key: str) -> None:
        """Remove item do cache"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
        self.ttls.pop(key, None)
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
            self.ttls.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }

# Cache global
_global_cache = IntelligentCache()

def cached(ttl: int = 3600, key_func: Optional[Callable] = None):
    """Decorator para cache automático"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Gerar chave do cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Tentar recuperar do cache
            result = _global_cache.get(cache_key)
            if result is not None:
                return result
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            _global_cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

def get_cache_stats():
    """Retorna estatísticas do cache global"""
    return _global_cache.get_stats()

def clear_cache():
    """Limpa cache global"""
    _global_cache.clear()
