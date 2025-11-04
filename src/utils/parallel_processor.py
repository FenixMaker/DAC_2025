
# -*- coding: utf-8 -*-
"""
Processamento paralelo para operações do DAC
"""

import concurrent.futures
import multiprocessing
from typing import List, Callable, Any, Dict, Optional
from functools import partial
import time
import logging

class ParallelProcessor:
    """Processador paralelo para operações pesadas"""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(32, (multiprocessing.cpu_count() or 1) + 4)
        self.logger = logging.getLogger(__name__)
    
    def process_in_parallel(self, 
                          func: Callable,
                          data_list: List[Any],
                          chunk_size: Optional[int] = None,
                          timeout: Optional[float] = None) -> List[Any]:
        """Processa lista de dados em paralelo"""
        if not data_list:
            return []
        
        if chunk_size is None:
            chunk_size = max(1, len(data_list) // self.max_workers)
        
        # Dividir dados em chunks
        chunks = [data_list[i:i + chunk_size] for i in range(0, len(data_list), chunk_size)]
        
        results = []
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submeter tarefas
            future_to_chunk = {executor.submit(self._process_chunk, func, chunk): chunk 
                             for chunk in chunks}
            
            # Coletar resultados
            for future in concurrent.futures.as_completed(future_to_chunk, timeout=timeout):
                try:
                    chunk_results = future.result()
                    results.extend(chunk_results)
                except Exception as e:
                    self.logger.error(f"Erro no processamento paralelo: {e}")
        
        processing_time = time.time() - start_time
        self.logger.info(f"Processamento paralelo concluído em {processing_time:.2f}s")
        
        return results
    
    def _process_chunk(self, func: Callable, chunk: List[Any]) -> List[Any]:
        """Processa um chunk de dados"""
        return [func(item) for item in chunk]
    
    def parallel_map(self, func: Callable, data_list: List[Any]) -> List[Any]:
        """Map paralelo simples"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(func, data_list))
    
    def parallel_filter(self, predicate: Callable, data_list: List[Any]) -> List[Any]:
        """Filter paralelo"""
        def filter_chunk(chunk):
            return [item for item in chunk if predicate(item)]
        
        return self.process_in_parallel(filter_chunk, data_list)

# Instância global
_parallel_processor = None

def get_parallel_processor() -> ParallelProcessor:
    """Retorna instância do processador paralelo"""
    global _parallel_processor
    if _parallel_processor is None:
        _parallel_processor = ParallelProcessor()
    return _parallel_processor

def parallel_process(func: Callable, data_list: List[Any], **kwargs) -> List[Any]:
    """Função de conveniência para processamento paralelo"""
    processor = get_parallel_processor()
    return processor.process_in_parallel(func, data_list, **kwargs)
