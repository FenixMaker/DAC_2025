
# -*- coding: utf-8 -*-
"""
Consultas SQL otimizadas para o sistema DAC
"""

from typing import Dict, List, Any, Optional
import sqlite3
from ..utils.intelligent_cache import cached

class OptimizedQueries:
    """Classe com consultas SQL otimizadas"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @cached(ttl=1800)  # Cache por 30 minutos
    def get_regional_statistics(self, region_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Estatísticas regionais otimizadas"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        query = """
        SELECT 
            r.id,
            r.name,
            r.state,
            COUNT(DISTINCT h.id) as total_households,
            COUNT(DISTINCT i.id) as total_individuals,
            AVG(CASE WHEN i.age IS NOT NULL THEN i.age END) as avg_age,
            COUNT(CASE WHEN h.has_internet = 1 THEN 1 END) * 100.0 / COUNT(h.id) as internet_penetration,
            COUNT(CASE WHEN i.gender = 'F' THEN 1 END) * 100.0 / COUNT(i.id) as female_percentage
        FROM regions r
        LEFT JOIN households h ON r.id = h.region_id
        LEFT JOIN individuals i ON h.id = i.household_id
        """
        
        params = []
        if region_id:
            query += " WHERE r.id = ?"
            params.append(region_id)
        
        query += " GROUP BY r.id, r.name, r.state ORDER BY r.name"
        
        cursor = conn.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    @cached(ttl=3600)  # Cache por 1 hora
    def get_device_usage_summary(self) -> List[Dict[str, Any]]:
        """Resumo de uso de dispositivos otimizado"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        query = """
        SELECT 
            d.device_type,
            COUNT(*) as total_records,
            COUNT(CASE WHEN d.has_device = 1 THEN 1 END) as has_device_count,
            COUNT(CASE WHEN d.has_device = 1 THEN 1 END) * 100.0 / COUNT(*) as adoption_rate,
            COUNT(DISTINCT d.individual_id) as unique_individuals
        FROM device_usage d
        WHERE d.device_type IS NOT NULL
        GROUP BY d.device_type
        ORDER BY adoption_rate DESC
        """
        
        cursor = conn.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    @cached(ttl=1800)
    def get_demographic_analysis(self, age_groups: bool = True) -> List[Dict[str, Any]]:
        """Análise demográfica otimizada"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        if age_groups:
            query = """
            SELECT 
                CASE 
                    WHEN i.age < 18 THEN 'Menor de 18'
                    WHEN i.age BETWEEN 18 AND 24 THEN '18-24'
                    WHEN i.age BETWEEN 25 AND 34 THEN '25-34'
                    WHEN i.age BETWEEN 35 AND 44 THEN '35-44'
                    WHEN i.age BETWEEN 45 AND 54 THEN '45-54'
                    WHEN i.age BETWEEN 55 AND 64 THEN '55-64'
                    WHEN i.age >= 65 THEN '65+'
                    ELSE 'Não informado'
                END as age_group,
                i.gender,
                COUNT(*) as count,
                AVG(CASE WHEN iu.has_access = 1 THEN 1.0 ELSE 0.0 END) as internet_access_rate
            FROM individuals i
            LEFT JOIN internet_usage iu ON i.id = iu.individual_id
            GROUP BY age_group, i.gender
            ORDER BY 
                CASE age_group
                    WHEN 'Menor de 18' THEN 1
                    WHEN '18-24' THEN 2
                    WHEN '25-34' THEN 3
                    WHEN '35-44' THEN 4
                    WHEN '45-54' THEN 5
                    WHEN '55-64' THEN 6
                    WHEN '65+' THEN 7
                    ELSE 8
                END, i.gender
            """
        else:
            query = """
            SELECT 
                i.gender,
                i.education_level,
                COUNT(*) as count,
                AVG(CASE WHEN iu.has_access = 1 THEN 1.0 ELSE 0.0 END) as internet_access_rate,
                AVG(i.age) as avg_age
            FROM individuals i
            LEFT JOIN internet_usage iu ON i.id = iu.individual_id
            WHERE i.gender IS NOT NULL AND i.education_level IS NOT NULL
            GROUP BY i.gender, i.education_level
            ORDER BY i.gender, i.education_level
            """
        
        cursor = conn.execute(query)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    @cached(ttl=600)  # Cache por 10 minutos
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Métricas de performance do banco"""
        conn = sqlite3.connect(self.db_path)
        
        # Estatísticas das tabelas
        tables_stats = {}
        tables = ['regions', 'households', 'individuals', 'device_usage', 'internet_usage']
        
        for table in tables:
            try:
                cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                tables_stats[table] = count
            except:
                tables_stats[table] = 0
        
        # Tamanho do banco
        cursor = conn.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()[0]
        
        # Informações de índices
        cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
        index_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'table_counts': tables_stats,
            'database_size_bytes': db_size,
            'database_size_mb': round(db_size / (1024 * 1024), 2),
            'index_count': index_count,
            'total_records': sum(tables_stats.values())
        }
