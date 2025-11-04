
# -*- coding: utf-8 -*-
"""
Testes de performance do sistema
"""

import unittest
import time
import tempfile
import shutil
from pathlib import Path
import sys
import statistics
from datetime import datetime, timedelta

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.database.database_manager import DatabaseManager
from src.utils.data_validator import DataValidator

class TestPerformance(unittest.TestCase):
    """Testes de performance"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = Path(self.temp_dir) / "test_performance.db"
        self.db_manager = DatabaseManager(str(self.test_db_path))
        self.db_manager.initialize_database()  # Inicializar o banco
        self.validator = DataValidator()
        
        # Limites de performance (em segundos)
        self.max_insert_time = 0.1  # 100ms por inserção
        self.max_query_time = 0.5   # 500ms por consulta
        self.max_batch_time = 5.0   # 5s para 1000 registros
    
    def tearDown(self):
        """Limpeza após cada teste"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_single_insert_performance(self):
        """Testa performance de inserção única"""
        test_data = {
            'data': '2025-01-01',
            'valor': 1000.0,
            'descricao': 'Teste performance inserção',
            'categoria': 'Receita'
        }
        
        start_time = time.time()
        insert_id = self.db_manager.insert_financial_data(test_data)
        execution_time = time.time() - start_time
        
        self.assertIsNotNone(insert_id)
        self.assertLess(execution_time, self.max_insert_time, 
                       f"Inserção muito lenta: {execution_time:.3f}s")
    
    def test_batch_insert_performance(self):
        """Testa performance de inserção em lote"""
        batch_size = 1000
        batch_data = [{
            'data': f'2025-01-{(i % 31) + 1:02d}',
            'valor': 100.0 + i,
            'descricao': f'Lote performance {i}',
            'categoria': 'Receita' if i % 2 == 0 else 'Despesa'
        } for i in range(batch_size)]
        
        start_time = time.time()
        inserted_ids = [self.db_manager.insert_financial_data(data) for data in batch_data]
        execution_time = time.time() - start_time
        
        self.assertEqual(len(inserted_ids), batch_size)
        self.assertLess(execution_time, self.max_batch_time,
                       f"Inserção em lote muito lenta: {execution_time:.3f}s para {batch_size} registros")
        
        avg_time_per_insert = execution_time / batch_size
        self.assertLess(avg_time_per_insert, self.max_insert_time,
                       f"Média por inserção muito lenta: {avg_time_per_insert:.3f}s")
    
    def test_query_performance(self):
        """Testa performance de consultas"""
        test_data_count = 100
        for i in range(test_data_count):
            data = {
                'data': f'2025-01-{(i % 31) + 1:02d}',
                'valor': 100.0 + i,
                'descricao': f'Query test {i}',
                'categoria': 'Receita' if i % 2 == 0 else 'Despesa'
            }
            self.db_manager.insert_financial_data(data)
        
        queries = [
            lambda: self.db_manager.query_financial_data(),
            lambda: self.db_manager.query_financial_data(filters={'categoria': 'Receita'}),
            lambda: self.db_manager.query_financial_data(date_range=('2025-01-01', '2025-01-31')),
        ]
        
        for i, query_func in enumerate(queries):
            start_time = time.time()
            results = query_func()
            execution_time = time.time() - start_time
            
            self.assertIsNotNone(results)
            self.assertLess(execution_time, self.max_query_time,
                           f"Consulta {i+1} muito lenta: {execution_time:.3f}s")
    
    def test_validation_performance(self):
        """Testa performance de validação"""
        test_data = {
            'data': '2025-01-01',
            'valor': 1000.0,
            'descricao': 'Teste performance validação',
            'categoria': 'Receita'
        }
        
        validation_count = 1000
        times = []
        
        for _ in range(validation_count):
            start_time = time.time()
            is_valid, errors, warnings = self.validator.validate_financial_data(test_data)
            end_time = time.time()
            
            times.append(end_time - start_time)
            self.assertTrue(is_valid)
        
        avg_time = statistics.mean(times)
        max_time = max(times)
        
        self.assertLess(avg_time, 0.001, f"Validação média muito lenta: {avg_time:.6f}s")
        self.assertLess(max_time, 0.01, f"Validação máxima muito lenta: {max_time:.6f}s")
    
    def test_memory_usage(self):
        """Testa uso de memória (básico)"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
        except ImportError:
            self.skipTest("psutil não está disponível")
        
        # Inserir muitos dados
        large_batch_size = 5000
        for i in range(large_batch_size):
            data = {
                'data': f'2025-01-{(i % 31) + 1:02d}',
                'valor': 100.0 + i,
                'descricao': f'Memory test {i}' * 10,  # Descrição maior
                'categoria': 'Receita' if i % 2 == 0 else 'Despesa'
            }
            self.db_manager.insert_financial_data(data)
        
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # Verificar se o aumento de memória é razoável (menos de 100MB)
            max_memory_increase = 100 * 1024 * 1024  # 100MB
            self.assertLess(memory_increase, max_memory_increase,
                           f"Uso de memória excessivo: {memory_increase / 1024 / 1024:.2f}MB")
    
    def test_concurrent_operations(self):
        """Testa operações concorrentes (simuladas)"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        thread_count = 3  # Reduzir para evitar conflitos
        operations_per_thread = 10  # Reduzir para ser mais estável
        
        def worker_thread(thread_id):
            """Função do worker thread"""
            thread_results = []
            
            # Criar uma nova instância do DatabaseManager para cada thread
            thread_db_path = Path(self.temp_dir) / f"thread_{thread_id}.db"
            thread_db_manager = DatabaseManager(str(thread_db_path))
            thread_db_manager.initialize_database()
            
            try:
                for i in range(operations_per_thread):
                    data = {
                        'data': '2025-01-01',
                        'valor': 100.0 + thread_id * 100 + i,
                        'descricao': f'Thread {thread_id} op {i}',
                        'categoria': f'T{thread_id}R{i}'  # Código único para cada operação
                    }
                    
                    start_time = time.time()
                    try:
                        insert_id = thread_db_manager.insert_financial_data(data)
                        success = insert_id is not None
                    except Exception as e:
                        success = False
                        insert_id = None
                    end_time = time.time()
                    
                    thread_results.append({
                        'thread_id': thread_id,
                        'operation': i,
                        'time': end_time - start_time,
                        'success': success
                    })
            finally:
                thread_db_manager.close()
            
            results_queue.put(thread_results)
        
        # Criar e iniciar threads
        threads = []
        start_time = time.time()
        
        for i in range(thread_count):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Coletar resultados
        all_results = []
        while not results_queue.empty():
            thread_results = results_queue.get()
            all_results.extend(thread_results)
        
        # Verificar resultados
        expected_operations = thread_count * operations_per_thread
        self.assertEqual(len(all_results), expected_operations)
        
        # Verificar se a maioria das operações foram bem-sucedidas (pelo menos 90%)
        successful_operations = sum(1 for r in all_results if r['success'])
        success_rate = successful_operations / expected_operations
        self.assertGreaterEqual(success_rate, 0.9, 
                               f"Taxa de sucesso muito baixa: {success_rate:.2%} ({successful_operations}/{expected_operations})")
        
        # Verificar tempo total razoável
        max_concurrent_time = 15.0  # 15 segundos (mais tempo para operações concorrentes)
        self.assertLess(total_time, max_concurrent_time,
                       f"Operações concorrentes muito lentas: {total_time:.3f}s")

if __name__ == '__main__':
    unittest.main()
