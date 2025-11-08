"""
Módulo de gerenciamento de configurações do sistema DAC.
Fornece funções para ler, salvar e validar configurações em arquivos JSON.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigManager:
    """Gerenciador de configurações do sistema."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            config_dir: Diretório dos arquivos de configuração. 
                       Se None, usa o diretório padrão.
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Diretório padrão: recursos/configuracoes
            self.config_dir = Path(__file__).resolve().parents[2] / "recursos" / "configuracoes"
        
        # Garante que o diretório existe
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Arquivos de configuração padrão
        self.config_files = {
            'database': 'database_config.json',
            'cache': 'cache_config.json',
            'logging': 'logging_config.json',
            'error_monitoring': 'error_monitoring.json',
            'appearance': 'appearance_config.json',
            'performance': 'performance_config.json',
            'reports': 'reports_config.json'
        }
    
    def load_config(self, config_type: str) -> Dict[str, Any]:
        """
        Carrega configurações de um arquivo JSON.
        
        Args:
            config_type: Tipo de configuração ('database', 'cache', etc.)
            
        Returns:
            Dict com as configurações
        """
        if config_type not in self.config_files:
            raise ValueError(f"Tipo de configuração inválido: {config_type}")
        
        config_file = self.config_dir / self.config_files[config_type]
        
        if not config_file.exists():
            # Retorna configurações padrão se o arquivo não existe
            return self.get_default_config(config_type)
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Erro ao carregar configuração {config_type}: {e}")
            return self.get_default_config(config_type)
    
    def save_config(self, config_type: str, config_data: Dict[str, Any]) -> bool:
        """
        Salva configurações em arquivo JSON.
        
        Args:
            config_type: Tipo de configuração
            config_data: Dados a serem salvos
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        if config_type not in self.config_files:
            raise ValueError(f"Tipo de configuração inválido: {config_type}")
        
        config_file = self.config_dir / self.config_files[config_type]
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            return True
        except (IOError, TypeError) as e:
            print(f"Erro ao salvar configuração {config_type}: {e}")
            return False
    
    def get_default_config(self, config_type: str) -> Dict[str, Any]:
        """
        Retorna configurações padrão para cada tipo.
        
        Args:
            config_type: Tipo de configuração
            
        Returns:
            Dict com configurações padrão
        """
        defaults = {
            'database': {
                'type': 'SQLite',
                'host': 'localhost',
                'port': 5432,
                'database': 'dac_db',
                'user': 'postgres',
                'password': '',
                'sslmode': 'prefer',
                'pool_size': 10,
                'timeout_ms': 30000,
                'retry_count': 3,
                'sqlite_path': str(Path(__file__).resolve().parents[2] / 'data' / 'dac_database.db')
            },
            'cache': {
                'enabled': True,
                'ttl_seconds': 300,
                'max_items': 1000,
                'cleanup_interval': 60
            },
            'logging': {
                'level': 'INFO',
                'file_path': 'logs/dac.log',
                'max_size_mb': 10,
                'backup_count': 5,
                'console_output': True,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
            'error_monitoring': {
                'enabled': True,
                'sample_rate': 1.0,
                'max_errors_per_minute': 100,
                'notification_email': '',
                'webhook_url': ''
            },
            'appearance': {
                'theme': 'system',
                'font_size': 12,
                'ui_scale': 1.0,
                'logo_variant': 'simplified',
                'animations_enabled': True,
                'table_density': 'normal'
            },
            'performance': {
                'max_query_rows': 10000,
                'query_timeout_seconds': 30,
                'chart_quality': 'high',
                'auto_refresh_interval': 60,
                'memory_limit_mb': 512
            },
            'reports': {
                'default_period_days': 30,
                'decimal_places': 2,
                'percentage_format': '0.1%',
                'export_format': 'png',
                'resolution_dpi': 300,
                'include_metadata': True
            }
        }
        
        return defaults.get(config_type, {})
    
    def validate_config(self, config_type: str, config_data: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Valida configurações antes de salvar.
        
        Args:
            config_type: Tipo de configuração
            config_data: Dados a validar
            
        Returns:
            Tuple (válido, lista de erros)
        """
        errors = []
        
        if config_type == 'database':
            db_type = config_data.get('type', 'PostgreSQL')
            if db_type == 'SQLite':
                sqlite_path = (config_data.get('sqlite_path') or '').strip()
                if not sqlite_path:
                    errors.append("Arquivo SQLite é obrigatório")
                elif not os.path.exists(sqlite_path):
                    errors.append(f"Arquivo SQLite não encontrado: {sqlite_path}")
                # Para SQLite, não exigimos host/porta/usuário
            else:
                # Validações específicas do PostgreSQL
                if not config_data.get('host'):
                    errors.append("Host é obrigatório")
                
                port = config_data.get('port')
                if not isinstance(port, int) or port <= 0 or port > 65535:
                    errors.append("Porta deve ser um número entre 1 e 65535")
                
                if not config_data.get('database'):
                    errors.append("Nome do banco é obrigatório")
                
                if not config_data.get('user'):
                    errors.append("Usuário é obrigatório")
                
                pool_size = config_data.get('pool_size', 0)
                if not isinstance(pool_size, int) or pool_size <= 0:
                    errors.append("Tamanho do pool deve ser um número positivo")
                
                timeout = config_data.get('timeout_ms', 0)
                if not isinstance(timeout, int) or timeout <= 0:
                    errors.append("Timeout deve ser um número positivo (ms)")
        
        elif config_type == 'cache':
            ttl = config_data.get('ttl_seconds', 0)
            if not isinstance(ttl, int) or ttl <= 0:
                errors.append("TTL deve ser um número positivo (segundos)")
            
            max_items = config_data.get('max_items', 0)
            if not isinstance(max_items, int) or max_items <= 0:
                errors.append("Máximo de itens deve ser um número positivo")
        
        elif config_type == 'logging':
            level = config_data.get('level', '')
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if level not in valid_levels:
                errors.append(f"Nível de log deve ser um de: {', '.join(valid_levels)}")
            
            max_size = config_data.get('max_size_mb', 0)
            if not isinstance(max_size, (int, float)) or max_size <= 0:
                errors.append("Tamanho máximo deve ser um número positivo (MB)")
        
        elif config_type == 'appearance':
            theme = config_data.get('theme', '')
            valid_themes = ['light', 'dark', 'system']
            if theme not in valid_themes:
                errors.append(f"Tema deve ser um de: {', '.join(valid_themes)}")
            
            font_size = config_data.get('font_size', 0)
            if not isinstance(font_size, (int, float)) or font_size <= 0:
                errors.append("Tamanho da fonte deve ser um número positivo")
            
            ui_scale = config_data.get('ui_scale', 0)
            if not isinstance(ui_scale, (int, float)) or ui_scale <= 0 or ui_scale > 3:
                errors.append("Escala da UI deve ser entre 0.1 e 3.0")
        
        return len(errors) == 0, errors
    
    def export_config(self, file_path: str) -> bool:
        """
        Exporta todas as configurações para um arquivo único.
        
        Args:
            file_path: Caminho do arquivo de exportação
            
        Returns:
            True se exportou com sucesso
        """
        all_configs = {}
        
        for config_type in self.config_files.keys():
            all_configs[config_type] = self.load_config(config_type)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(all_configs, f, ensure_ascii=False, indent=2)
            return True
        except (IOError, TypeError) as e:
            print(f"Erro ao exportar configurações: {e}")
            return False
    
    def import_config(self, file_path: str) -> tuple[bool, list[str]]:
        """
        Importa configurações de um arquivo.
        
        Args:
            file_path: Caminho do arquivo de importação
            
        Returns:
            Tuple (sucesso, lista de erros)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_configs = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            return False, [f"Erro ao ler arquivo: {e}"]
        
        errors = []
        success_count = 0
        
        for config_type, config_data in imported_configs.items():
            if config_type not in self.config_files:
                errors.append(f"Tipo de configuração desconhecido: {config_type}")
                continue
            
            is_valid, validation_errors = self.validate_config(config_type, config_data)
            if not is_valid:
                errors.extend(validation_errors)
                continue
            
            if self.save_config(config_type, config_data):
                success_count += 1
            else:
                errors.append(f"Falha ao salvar configuração: {config_type}")
        
        if success_count == 0:
            return False, errors
        
        return True, errors


# Instância global para uso fácil
config_manager = ConfigManager()


# Funções auxiliares
def get_config(config_type: str) -> Dict[str, Any]:
    """Obtém configurações do tipo especificado."""
    return config_manager.load_config(config_type)


def set_config(config_type: str, config_data: Dict[str, Any]) -> bool:
    """Define configurações do tipo especificado."""
    return config_manager.save_config(config_type, config_data)


def test_database_connection(config_data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Testa conexão com banco de dados.
    
    Args:
        config_data: Configurações do banco de dados
        
    Returns:
        Tuple (sucesso, mensagem)
    """
    try:
        import psycopg2
        from psycopg2 import OperationalError
        
        conn = psycopg2.connect(
            host=config_data.get('host', 'localhost'),
            port=config_data.get('port', 5432),
            dbname=config_data.get('database', 'dac_db'),
            user=config_data.get('user', 'postgres'),
            password=config_data.get('password', ''),
            connect_timeout=5
        )
        conn.close()
        return True, "Conexão bem-sucedida!"
        
    except OperationalError as e:
        return False, f"Erro de conexão: {str(e)}"
    except Exception as e:
        return False, f"Erro inesperado: {str(e)}"


if __name__ == "__main__":
    # Teste básico do módulo
    print("Configurações padrão do banco de dados:")
    db_config = get_config('database')
    print(json.dumps(db_config, indent=2, ensure_ascii=False))