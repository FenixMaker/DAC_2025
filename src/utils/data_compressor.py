
# -*- coding: utf-8 -*-
"""
Sistema de compressão de dados para o DAC
"""

import gzip
import json
import pickle
import zlib
from typing import Any, Dict, List, Union
from pathlib import Path
import logging

class DataCompressor:
    """Compressor de dados para otimização de armazenamento"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def compress_json(self, data: Union[Dict, List], compression_level: int = 6) -> bytes:
        """Comprime dados JSON"""
        json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        return gzip.compress(json_str.encode('utf-8'), compresslevel=compression_level)
    
    def decompress_json(self, compressed_data: bytes) -> Union[Dict, List]:
        """Descomprime dados JSON"""
        json_str = gzip.decompress(compressed_data).decode('utf-8')
        return json.loads(json_str)
    
    def compress_pickle(self, data: Any, compression_level: int = 6) -> bytes:
        """Comprime dados usando pickle"""
        pickled_data = pickle.dumps(data)
        return gzip.compress(pickled_data, compresslevel=compression_level)
    
    def decompress_pickle(self, compressed_data: bytes) -> Any:
        """Descomprime dados pickle"""
        pickled_data = gzip.decompress(compressed_data)
        return pickle.loads(pickled_data)
    
    def compress_text(self, text: str, compression_level: int = 6) -> bytes:
        """Comprime texto"""
        return gzip.compress(text.encode('utf-8'), compresslevel=compression_level)
    
    def decompress_text(self, compressed_data: bytes) -> str:
        """Descomprime texto"""
        return gzip.decompress(compressed_data).decode('utf-8')
    
    def get_compression_ratio(self, original_size: int, compressed_size: int) -> float:
        """Calcula taxa de compressão"""
        if original_size == 0:
            return 0.0
        return (1 - compressed_size / original_size) * 100
    
    def compress_file(self, input_path: Path, output_path: Path = None) -> Dict[str, Any]:
        """Comprime arquivo"""
        if output_path is None:
            output_path = input_path.with_suffix(input_path.suffix + '.gz')
        
        original_size = input_path.stat().st_size
        
        with open(input_path, 'rb') as f_in:
            with gzip.open(output_path, 'wb') as f_out:
                f_out.writelines(f_in)
        
        compressed_size = output_path.stat().st_size
        compression_ratio = self.get_compression_ratio(original_size, compressed_size)
        
        return {
            'original_file': str(input_path),
            'compressed_file': str(output_path),
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio,
            'space_saved': original_size - compressed_size
        }

# Instância global
_data_compressor = None

def get_data_compressor() -> DataCompressor:
    """Retorna instância do compressor"""
    global _data_compressor
    if _data_compressor is None:
        _data_compressor = DataCompressor()
    return _data_compressor
