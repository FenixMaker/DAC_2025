# -*- coding: utf-8 -*-
"""
Gerenciador de configurações e preferências do usuário
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from .logger import get_logger

class SettingsManager:
    """Gerenciador de configurações e preferências do usuário"""
    
    def __init__(self, config_file=None):
        """
        Inicializa o gerenciador de configurações
        
        Args:
            config_file (str, optional): Caminho para o arquivo de configuração
        """
        self.logger = get_logger(__name__)
        
        if config_file is None:
            # Criar diretório de configuração se não existir
            config_dir = Path(__file__).parent.parent.parent / "config"
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / "user_settings.json"
        
        self.config_file = Path(config_file)
        self.settings = self._load_default_settings()
        self.load_settings()
    
    def _load_default_settings(self) -> Dict[str, Any]:
        """
        Carrega as configurações padrão do sistema
        
        Returns:
            dict: Configurações padrão
        """
        return {
            # Configurações da interface
            'ui': {
                'theme': 'default',
                'font_size': 10,
                'font_family': 'Arial',
                'window_width': 1200,
                'window_height': 800,
                'window_maximized': False,
                'show_tooltips': True,
                'auto_save': True
            },
            
            # Configurações de dados
            'data': {
                'auto_backup': True,
                'backup_interval': 24,  # horas
                'max_backups': 5,
                'cache_enabled': True,
                'cache_timeout': 300,  # segundos
                'batch_size': 1000,
                'max_records_display': 10000
            },
            
            # Configurações de relatórios
            'reports': {
                'default_format': 'pdf',
                'include_charts': True,
                'chart_style': 'default',
                'auto_open_reports': True,
                'save_location': str(Path.home() / 'Downloads'),
                'filename_template': 'relatorio_dac_{timestamp}',
                'page_orientation': 'portrait',
                'chart_colors': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
            },
            
            # Configurações de importação
            'import': {
                'auto_validate': True,
                'skip_duplicates': True,
                'show_progress': True,
                'chunk_size': 100,
                'timeout': 30,
                'retry_attempts': 3
            },
            
            # Configurações de consulta
            'query': {
                'default_page_size': 100,
                'max_results': 10000,
                'auto_refresh': False,
                'refresh_interval': 60,  # segundos
                'remember_filters': True,
                'export_format': 'excel'
            },
            
            # Configurações de logging
            'logging': {
                'level': 'INFO',
                'max_file_size': 10,  # MB
                'backup_count': 5,
                'console_output': True,
                'file_output': True
            },
            
            # Configurações de performance
            'performance': {
                'enable_caching': True,
                'cache_size': 1000,
                'lazy_loading': True,
                'optimize_queries': True,
                'parallel_processing': False,
                'max_workers': 4
            }
        }
    
    def load_settings(self) -> bool:
        """
        Carrega as configurações do arquivo
        
        Returns:
            bool: True se carregou com sucesso, False caso contrário
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                
                # Mesclar com configurações padrão
                self._merge_settings(self.settings, saved_settings)
                
                self.logger.info(f"Configurações carregadas de: {self.config_file}")
                return True
            else:
                self.logger.info("Arquivo de configuração não encontrado, usando padrões")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
            return False
    
    def save_settings(self) -> bool:
        """
        Salva as configurações no arquivo
        
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            # Criar diretório se não existir
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"Configurações salvas em: {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
            return False
    
    def get_setting(self, key_path: str, default=None) -> Any:
        """
        Obtém uma configuração usando notação de ponto
        
        Args:
            key_path (str): Caminho da configuração (ex: 'ui.theme')
            default: Valor padrão se não encontrar
            
        Returns:
            Any: Valor da configuração
        """
        try:
            keys = key_path.split('.')
            value = self.settings
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
            
        except Exception as e:
            self.logger.error(f"Erro ao obter configuração '{key_path}': {e}")
            return default
    
    def set_setting(self, key_path: str, value: Any) -> bool:
        """
        Define uma configuração usando notação de ponto
        
        Args:
            key_path (str): Caminho da configuração (ex: 'ui.theme')
            value: Valor a definir
            
        Returns:
            bool: True se definiu com sucesso, False caso contrário
        """
        try:
            keys = key_path.split('.')
            current = self.settings
            
            # Navegar até o penúltimo nível
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            # Definir o valor
            current[keys[-1]] = value
            
            # Auto-salvar se habilitado
            if self.get_setting('ui.auto_save', True):
                self.save_settings()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao definir configuração '{key_path}': {e}")
            return False
    
    def _merge_settings(self, default: Dict, saved: Dict) -> None:
        """
        Mescla configurações salvas com as padrão
        
        Args:
            default (dict): Configurações padrão
            saved (dict): Configurações salvas
        """
        for key, value in saved.items():
            if key in default:
                if isinstance(default[key], dict) and isinstance(value, dict):
                    self._merge_settings(default[key], value)
                else:
                    default[key] = value
            else:
                default[key] = value
    
    def reset_to_defaults(self, section: Optional[str] = None) -> bool:
        """
        Restaura configurações padrão
        
        Args:
            section (str, optional): Seção específica para restaurar
            
        Returns:
            bool: True se restaurou com sucesso, False caso contrário
        """
        try:
            defaults = self._load_default_settings()
            
            if section:
                if section in defaults:
                    self.settings[section] = defaults[section]
                else:
                    self.logger.warning(f"Seção '{section}' não encontrada")
                    return False
            else:
                self.settings = defaults
            
            self.save_settings()
            self.logger.info(f"Configurações restauradas: {section or 'todas'}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao restaurar configurações: {e}")
            return False
    
    def export_settings(self, file_path: str) -> bool:
        """
        Exporta configurações para um arquivo
        
        Args:
            file_path (str): Caminho do arquivo de destino
            
        Returns:
            bool: True se exportou com sucesso, False caso contrário
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"Configurações exportadas para: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar configurações: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """
        Importa configurações de um arquivo
        
        Args:
            file_path (str): Caminho do arquivo de origem
            
        Returns:
            bool: True se importou com sucesso, False caso contrário
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # Validar estrutura básica
            if not isinstance(imported_settings, dict):
                raise ValueError("Arquivo de configuração inválido")
            
            # Mesclar com configurações atuais
            self._merge_settings(self.settings, imported_settings)
            
            self.save_settings()
            self.logger.info(f"Configurações importadas de: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao importar configurações: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        Retorna todas as configurações
        
        Returns:
            dict: Todas as configurações
        """
        return self.settings.copy()
    
    def validate_settings(self) -> Dict[str, list]:
        """
        Valida as configurações atuais
        
        Returns:
            dict: Dicionário com erros encontrados por seção
        """
        errors = {}
        
        try:
            # Validar configurações de UI
            ui_errors = []
            if not isinstance(self.get_setting('ui.font_size'), (int, float)):
                ui_errors.append("Tamanho da fonte deve ser numérico")
            if self.get_setting('ui.font_size', 0) <= 0:
                ui_errors.append("Tamanho da fonte deve ser positivo")
            
            if ui_errors:
                errors['ui'] = ui_errors
            
            # Validar configurações de dados
            data_errors = []
            if not isinstance(self.get_setting('data.batch_size'), int):
                data_errors.append("Tamanho do lote deve ser inteiro")
            if self.get_setting('data.batch_size', 0) <= 0:
                data_errors.append("Tamanho do lote deve ser positivo")
            
            if data_errors:
                errors['data'] = data_errors
            
            # Validar configurações de relatórios
            reports_errors = []
            save_location = self.get_setting('reports.save_location')
            if save_location and not os.path.exists(save_location):
                reports_errors.append(f"Diretório de salvamento não existe: {save_location}")
            
            if reports_errors:
                errors['reports'] = reports_errors
            
        except Exception as e:
            self.logger.error(f"Erro na validação de configurações: {e}")
            errors['validation'] = [str(e)]
        
        return errors

# Instância global do gerenciador de configurações
_settings_manager = None

def get_settings_manager() -> SettingsManager:
    """
    Retorna a instância global do gerenciador de configurações
    
    Returns:
        SettingsManager: Instância do gerenciador
    """
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager

def get_setting(key_path: str, default=None) -> Any:
    """
    Função de conveniência para obter uma configuração
    
    Args:
        key_path (str): Caminho da configuração
        default: Valor padrão
        
    Returns:
        Any: Valor da configuração
    """
    return get_settings_manager().get_setting(key_path, default)

def set_setting(key_path: str, value: Any) -> bool:
    """
    Função de conveniência para definir uma configuração
    
    Args:
        key_path (str): Caminho da configuração
        value: Valor a definir
        
    Returns:
        bool: True se definiu com sucesso
    """
    return get_settings_manager().set_setting(key_path, value)