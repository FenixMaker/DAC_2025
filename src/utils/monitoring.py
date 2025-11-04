# -*- coding: utf-8 -*-
"""
Sistema de monitoramento e métricas
"""

import os
import psutil
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from collections import deque, defaultdict
from .logger import get_logger
from .settings import get_setting

class PerformanceMonitor:
    """Monitor de performance do sistema"""
    
    def __init__(self, max_samples=1000):
        """
        Inicializa o monitor de performance
        
        Args:
            max_samples (int): Número máximo de amostras a manter
        """
        self.logger = get_logger(__name__)
        self.max_samples = max_samples
        
        # Métricas de sistema
        self.cpu_usage = deque(maxlen=max_samples)
        self.memory_usage = deque(maxlen=max_samples)
        self.disk_usage = deque(maxlen=max_samples)
        
        # Métricas de aplicação
        self.query_times = deque(maxlen=max_samples)
        self.import_times = deque(maxlen=max_samples)
        self.export_times = deque(maxlen=max_samples)
        
        # Contadores de eventos
        self.event_counters = defaultdict(int)
        self.error_counters = defaultdict(int)
        
        # Timestamps
        self.timestamps = deque(maxlen=max_samples)
        
        # Thread de monitoramento
        self._monitoring = False
        self._monitor_thread = None
        self._monitor_interval = get_setting('monitoring.interval', 5)  # segundos
    
    def start_monitoring(self) -> None:
        """
        Inicia o monitoramento automático
        """
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        self.logger.info("Monitoramento de performance iniciado")
    
    def stop_monitoring(self) -> None:
        """
        Para o monitoramento automático
        """
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)
        self.logger.info("Monitoramento de performance parado")
    
    def _monitor_loop(self) -> None:
        """
        Loop principal de monitoramento
        """
        while self._monitoring:
            try:
                self._collect_system_metrics()
                time.sleep(self._monitor_interval)
            except Exception as e:
                self.logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(self._monitor_interval)
    
    def _collect_system_metrics(self) -> None:
        """
        Coleta métricas do sistema
        """
        try:
            timestamp = datetime.now()
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=None)
            self.cpu_usage.append(cpu_percent)
            
            # Memória
            memory = psutil.virtual_memory()
            self.memory_usage.append(memory.percent)
            
            # Disco
            disk = psutil.disk_usage('/')
            self.disk_usage.append(disk.percent)
            
            # Timestamp
            self.timestamps.append(timestamp)
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas do sistema: {e}")
    
    def record_query_time(self, duration: float) -> None:
        """
        Registra tempo de execução de query
        
        Args:
            duration (float): Duração em segundos
        """
        self.query_times.append(duration)
        self.event_counters['queries'] += 1
    
    def record_import_time(self, duration: float) -> None:
        """
        Registra tempo de importação
        
        Args:
            duration (float): Duração em segundos
        """
        self.import_times.append(duration)
        self.event_counters['imports'] += 1
    
    def record_export_time(self, duration: float) -> None:
        """
        Registra tempo de exportação
        
        Args:
            duration (float): Duração em segundos
        """
        self.export_times.append(duration)
        self.event_counters['exports'] += 1
    
    def record_error(self, error_type: str) -> None:
        """
        Registra um erro
        
        Args:
            error_type (str): Tipo do erro
        """
        self.error_counters[error_type] += 1
        self.event_counters['errors'] += 1
    
    def get_system_metrics(self) -> Dict:
        """
        Retorna métricas atuais do sistema
        
        Returns:
            dict: Métricas do sistema
        """
        try:
            return {
                'cpu': {
                    'current': self.cpu_usage[-1] if self.cpu_usage else 0,
                    'average': sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0,
                    'max': max(self.cpu_usage) if self.cpu_usage else 0
                },
                'memory': {
                    'current': self.memory_usage[-1] if self.memory_usage else 0,
                    'average': sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0,
                    'max': max(self.memory_usage) if self.memory_usage else 0
                },
                'disk': {
                    'current': self.disk_usage[-1] if self.disk_usage else 0,
                    'average': sum(self.disk_usage) / len(self.disk_usage) if self.disk_usage else 0,
                    'max': max(self.disk_usage) if self.disk_usage else 0
                }
            }
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas do sistema: {e}")
            return {}
    
    def get_performance_metrics(self) -> Dict:
        """
        Retorna métricas de performance da aplicação
        
        Returns:
            dict: Métricas de performance
        """
        try:
            def calc_stats(data):
                if not data:
                    return {'count': 0, 'average': 0, 'min': 0, 'max': 0}
                return {
                    'count': len(data),
                    'average': sum(data) / len(data),
                    'min': min(data),
                    'max': max(data)
                }
            
            return {
                'queries': calc_stats(self.query_times),
                'imports': calc_stats(self.import_times),
                'exports': calc_stats(self.export_times),
                'events': dict(self.event_counters),
                'errors': dict(self.error_counters)
            }
        except Exception as e:
            self.logger.error(f"Erro ao obter métricas de performance: {e}")
            return {}
    
    def get_health_status(self) -> Dict:
        """
        Retorna status de saúde do sistema
        
        Returns:
            dict: Status de saúde
        """
        try:
            system_metrics = self.get_system_metrics()
            performance_metrics = self.get_performance_metrics()
            
            # Determinar status baseado em thresholds
            cpu_threshold = get_setting('monitoring.cpu_threshold', 80)
            memory_threshold = get_setting('monitoring.memory_threshold', 85)
            disk_threshold = get_setting('monitoring.disk_threshold', 90)
            
            warnings = []
            errors = []
            
            # Verificar CPU
            if system_metrics.get('cpu', {}).get('current', 0) > cpu_threshold:
                warnings.append(f"Alto uso de CPU: {system_metrics['cpu']['current']:.1f}%")
            
            # Verificar memória
            if system_metrics.get('memory', {}).get('current', 0) > memory_threshold:
                warnings.append(f"Alto uso de memória: {system_metrics['memory']['current']:.1f}%")
            
            # Verificar disco
            if system_metrics.get('disk', {}).get('current', 0) > disk_threshold:
                errors.append(f"Disco quase cheio: {system_metrics['disk']['current']:.1f}%")
            
            # Verificar erros recentes
            total_errors = sum(self.error_counters.values())
            if total_errors > 10:
                warnings.append(f"Muitos erros recentes: {total_errors}")
            
            # Determinar status geral
            if errors:
                status = 'critical'
            elif warnings:
                status = 'warning'
            else:
                status = 'healthy'
            
            return {
                'status': status,
                'warnings': warnings,
                'errors': errors,
                'uptime': self._get_uptime(),
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status de saúde: {e}")
            return {'status': 'unknown', 'errors': [str(e)]}
    
    def _get_uptime(self) -> str:
        """
        Retorna tempo de atividade do sistema
        
        Returns:
            str: Tempo de atividade formatado
        """
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            return f"{days}d {hours}h {minutes}m"
            
        except Exception:
            return "unknown"
    
    def export_metrics(self, file_path: str) -> bool:
        """
        Exporta métricas para arquivo
        
        Args:
            file_path (str): Caminho do arquivo
            
        Returns:
            bool: True se exportou com sucesso
        """
        try:
            import json
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'system_metrics': self.get_system_metrics(),
                'performance_metrics': self.get_performance_metrics(),
                'health_status': self.get_health_status(),
                'raw_data': {
                    'cpu_usage': list(self.cpu_usage),
                    'memory_usage': list(self.memory_usage),
                    'disk_usage': list(self.disk_usage),
                    'query_times': list(self.query_times),
                    'import_times': list(self.import_times),
                    'export_times': list(self.export_times),
                    'timestamps': [ts.isoformat() for ts in self.timestamps]
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"Métricas exportadas para: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar métricas: {e}")
            return False

class AlertManager:
    """Gerenciador de alertas"""
    
    def __init__(self):
        """
        Inicializa o gerenciador de alertas
        """
        self.logger = get_logger(__name__)
        self.alert_handlers = []
        self.alert_history = deque(maxlen=1000)
        
        # Configurações de alertas
        self.enabled = get_setting('monitoring.alerts_enabled', True)
        self.email_alerts = get_setting('monitoring.email_alerts', False)
        self.log_alerts = get_setting('monitoring.log_alerts', True)
    
    def add_handler(self, handler: Callable[[Dict], None]) -> None:
        """
        Adiciona um handler de alerta
        
        Args:
            handler: Função que recebe um dicionário com dados do alerta
        """
        self.alert_handlers.append(handler)
    
    def send_alert(self, level: str, message: str, details: Dict = None) -> None:
        """
        Envia um alerta
        
        Args:
            level (str): Nível do alerta (info, warning, error, critical)
            message (str): Mensagem do alerta
            details (dict, optional): Detalhes adicionais
        """
        if not self.enabled:
            return
        
        try:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'level': level,
                'message': message,
                'details': details or {}
            }
            
            # Adicionar ao histórico
            self.alert_history.append(alert)
            
            # Log do alerta
            if self.log_alerts:
                log_method = getattr(self.logger, level.lower(), self.logger.info)
                log_method(f"ALERT: {message}")
            
            # Executar handlers
            for handler in self.alert_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    self.logger.error(f"Erro no handler de alerta: {e}")
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar alerta: {e}")
    
    def get_alert_history(self, level: str = None, limit: int = 100) -> List[Dict]:
        """
        Retorna histórico de alertas
        
        Args:
            level (str, optional): Filtrar por nível
            limit (int): Limite de alertas
            
        Returns:
            list: Lista de alertas
        """
        try:
            alerts = list(self.alert_history)
            
            if level:
                alerts = [a for a in alerts if a['level'] == level]
            
            # Ordenar por timestamp (mais recente primeiro)
            alerts.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return alerts[:limit]
            
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico de alertas: {e}")
            return []

class MonitoringService:
    """Serviço principal de monitoramento"""
    
    def __init__(self):
        """
        Inicializa o serviço de monitoramento
        """
        self.logger = get_logger(__name__)
        self.performance_monitor = PerformanceMonitor()
        self.alert_manager = AlertManager()
        
        # Configurar handlers de alerta padrão
        self._setup_default_alert_handlers()
        
        # Thread de verificação de saúde
        self._health_check_thread = None
        self._health_check_interval = get_setting('monitoring.health_check_interval', 60)  # segundos
        self._running = False
    
    def _setup_default_alert_handlers(self) -> None:
        """
        Configura handlers de alerta padrão
        """
        # Handler para alertas críticos
        def critical_alert_handler(alert):
            if alert['level'] == 'critical':
                self.logger.critical(f"ALERTA CRÍTICO: {alert['message']}")
        
        self.alert_manager.add_handler(critical_alert_handler)
    
    def start(self) -> None:
        """
        Inicia o serviço de monitoramento
        """
        try:
            self._running = True
            
            # Iniciar monitor de performance
            self.performance_monitor.start_monitoring()
            
            # Iniciar verificação de saúde
            self._health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
            self._health_check_thread.start()
            
            self.logger.info("Serviço de monitoramento iniciado")
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar serviço de monitoramento: {e}")
    
    def stop(self) -> None:
        """
        Para o serviço de monitoramento
        """
        try:
            self._running = False
            
            # Parar monitor de performance
            self.performance_monitor.stop_monitoring()
            
            # Parar verificação de saúde
            if self._health_check_thread:
                self._health_check_thread.join(timeout=1)
            
            self.logger.info("Serviço de monitoramento parado")
            
        except Exception as e:
            self.logger.error(f"Erro ao parar serviço de monitoramento: {e}")
    
    def _health_check_loop(self) -> None:
        """
        Loop de verificação de saúde
        """
        while self._running:
            try:
                health_status = self.performance_monitor.get_health_status()
                
                # Enviar alertas baseado no status
                if health_status['status'] == 'critical':
                    for error in health_status.get('errors', []):
                        self.alert_manager.send_alert('critical', error)
                elif health_status['status'] == 'warning':
                    for warning in health_status.get('warnings', []):
                        self.alert_manager.send_alert('warning', warning)
                
                time.sleep(self._health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Erro na verificação de saúde: {e}")
                time.sleep(self._health_check_interval)
    
    def get_dashboard_data(self) -> Dict:
        """
        Retorna dados para dashboard de monitoramento
        
        Returns:
            dict: Dados do dashboard
        """
        try:
            return {
                'system_metrics': self.performance_monitor.get_system_metrics(),
                'performance_metrics': self.performance_monitor.get_performance_metrics(),
                'health_status': self.performance_monitor.get_health_status(),
                'recent_alerts': self.alert_manager.get_alert_history(limit=10)
            }
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do dashboard: {e}")
            return {}

# Instância global do serviço de monitoramento
_monitoring_service = None

def get_monitoring_service() -> MonitoringService:
    """
    Retorna a instância global do serviço de monitoramento
    
    Returns:
        MonitoringService: Instância do serviço
    """
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = MonitoringService()
    return _monitoring_service

def monitor_performance(func_name: str = None):
    """
    Decorator para monitorar performance de funções
    
    Args:
        func_name (str, optional): Nome da função para logging
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Registrar tempo baseado no tipo de função
                name = func_name or func.__name__
                monitor = get_monitoring_service().performance_monitor
                
                if 'query' in name.lower():
                    monitor.record_query_time(duration)
                elif 'import' in name.lower():
                    monitor.record_import_time(duration)
                elif 'export' in name.lower():
                    monitor.record_export_time(duration)
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                monitor = get_monitoring_service().performance_monitor
                monitor.record_error(type(e).__name__)
                raise
        
        return wrapper
    return decorator