# -*- coding: utf-8 -*-
"""
Módulo de backup automático e manual do banco de dados DAC
"""

import os
import shutil
import sqlite3
import zipfile
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import threading
import time
from ..utils.logger import get_logger
from ..database.database import get_engine
from sqlalchemy import text

class BackupManager:
    """Gerenciador de backup do banco de dados"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.logger = get_logger(__name__)
        self.engine = get_engine()
        
        # Configurações padrão
        self.max_backups = 10
        self.auto_backup_interval = 24 * 60 * 60  # 24 horas em segundos
        self.auto_backup_enabled = False
        self._backup_thread = None
        self._stop_auto_backup = False
        
        # Arquivo de configuração de backup
        self.config_file = self.backup_dir / "backup_config.json"
        self._load_config()
    
    def _load_config(self):
        """Carrega configurações de backup"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.max_backups = config.get('max_backups', 10)
                    self.auto_backup_interval = config.get('auto_backup_interval', 24 * 60 * 60)
                    self.auto_backup_enabled = config.get('auto_backup_enabled', False)
        except Exception as e:
            self.logger.warning(f"Erro ao carregar configuração de backup: {e}")
    
    def _save_config(self):
        """Salva configurações de backup"""
        try:
            config = {
                'max_backups': self.max_backups,
                'auto_backup_interval': self.auto_backup_interval,
                'auto_backup_enabled': self.auto_backup_enabled,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração de backup: {e}")
    
    def create_backup(self, backup_name: Optional[str] = None, include_metadata: bool = True) -> Tuple[bool, str]:
        """Cria um backup manual do banco de dados
        
        Args:
            backup_name: Nome personalizado para o backup
            include_metadata: Se deve incluir metadados do backup
            
        Returns:
            Tuple[bool, str]: (sucesso, caminho_do_backup)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if backup_name:
                backup_filename = f"{backup_name}_{timestamp}.zip"
            else:
                backup_filename = f"dac_backup_{timestamp}.zip"
            
            backup_path = self.backup_dir / backup_filename
            
            # Criar backup compactado
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Backup do banco de dados principal
                db_path = self._get_database_path()
                if db_path and os.path.exists(db_path):
                    zipf.write(db_path, "database.db")
                    self.logger.info(f"Banco de dados adicionado ao backup: {db_path}")
                
                # Backup de arquivos de configuração
                config_files = [
                    "config.json",
                    "settings.json",
                    "user_preferences.json"
                ]
                
                for config_file in config_files:
                    config_path = Path(config_file)
                    if config_path.exists():
                        zipf.write(config_path, f"config/{config_file}")
                
                # Incluir metadados do backup
                if include_metadata:
                    metadata = self._create_backup_metadata()
                    zipf.writestr("backup_metadata.json", json.dumps(metadata, indent=2, ensure_ascii=False))
            
            # Limpar backups antigos
            self._cleanup_old_backups()
            
            self.logger.info(f"Backup criado com sucesso: {backup_path}")
            return True, str(backup_path)
            
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {e}")
            return False, str(e)
    
    def _get_database_path(self) -> Optional[str]:
        """Obtém o caminho do arquivo de banco de dados"""
        try:
            # Para SQLite, extrair caminho da URL de conexão
            db_url = str(self.engine.url)
            if db_url.startswith('sqlite:///'):
                return db_url.replace('sqlite:///', '')
            return None
        except Exception as e:
            self.logger.error(f"Erro ao obter caminho do banco: {e}")
            return None
    
    def _create_backup_metadata(self) -> Dict:
        """Cria metadados do backup"""
        try:
            metadata = {
                'backup_date': datetime.now().isoformat(),
                'database_info': {},
                'table_counts': {},
                'backup_version': '1.0'
            }
            
            # Obter informações das tabelas
            with self.engine.connect() as conn:
                # Listar tabelas
                tables_result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in tables_result]
                
                # Contar registros em cada tabela
                for table in tables:
                    try:
                        count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = count_result.scalar()
                        metadata['table_counts'][table] = count
                    except Exception as e:
                        self.logger.warning(f"Erro ao contar registros da tabela {table}: {e}")
                        metadata['table_counts'][table] = -1
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Erro ao criar metadados: {e}")
            return {
                'backup_date': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def restore_backup(self, backup_path: str, confirm_restore: bool = False) -> Tuple[bool, str]:
        """Restaura um backup do banco de dados
        
        Args:
            backup_path: Caminho para o arquivo de backup
            confirm_restore: Confirmação de que deseja restaurar
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        if not confirm_restore:
            return False, "Restauração cancelada - confirmação necessária"
        
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                return False, f"Arquivo de backup não encontrado: {backup_path}"
            
            # Criar backup do estado atual antes de restaurar
            current_backup_success, current_backup_path = self.create_backup("pre_restore")
            if current_backup_success:
                self.logger.info(f"Backup do estado atual criado: {current_backup_path}")
            
            # Extrair backup
            temp_dir = self.backup_dir / "temp_restore"
            temp_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Restaurar banco de dados
            db_backup_path = temp_dir / "database.db"
            if db_backup_path.exists():
                current_db_path = self._get_database_path()
                if current_db_path:
                    # Fazer backup do banco atual
                    shutil.copy2(current_db_path, f"{current_db_path}.backup")
                    
                    # Restaurar banco
                    shutil.copy2(db_backup_path, current_db_path)
                    self.logger.info("Banco de dados restaurado com sucesso")
            
            # Restaurar arquivos de configuração
            config_dir = temp_dir / "config"
            if config_dir.exists():
                for config_file in config_dir.iterdir():
                    if config_file.is_file():
                        shutil.copy2(config_file, config_file.name)
                        self.logger.info(f"Configuração restaurada: {config_file.name}")
            
            # Limpar diretório temporário
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            return True, "Backup restaurado com sucesso"
            
        except Exception as e:
            self.logger.error(f"Erro ao restaurar backup: {e}")
            return False, f"Erro na restauração: {e}"
    
    def list_backups(self) -> List[Dict]:
        """Lista todos os backups disponíveis"""
        backups = []
        
        try:
            for backup_file in self.backup_dir.glob("*.zip"):
                backup_info = {
                    'filename': backup_file.name,
                    'path': str(backup_file),
                    'size': backup_file.stat().st_size,
                    'created': datetime.fromtimestamp(backup_file.stat().st_ctime),
                    'modified': datetime.fromtimestamp(backup_file.stat().st_mtime)
                }
                
                # Tentar extrair metadados
                try:
                    with zipfile.ZipFile(backup_file, 'r') as zipf:
                        if 'backup_metadata.json' in zipf.namelist():
                            metadata_content = zipf.read('backup_metadata.json')
                            metadata = json.loads(metadata_content.decode('utf-8'))
                            backup_info['metadata'] = metadata
                except Exception:
                    pass
                
                backups.append(backup_info)
            
            # Ordenar por data de criação (mais recente primeiro)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"Erro ao listar backups: {e}")
        
        return backups
    
    def _cleanup_old_backups(self):
        """Remove backups antigos baseado na configuração"""
        try:
            backups = self.list_backups()
            
            if len(backups) > self.max_backups:
                # Remover backups mais antigos
                backups_to_remove = backups[self.max_backups:]
                
                for backup in backups_to_remove:
                    backup_path = Path(backup['path'])
                    if backup_path.exists():
                        backup_path.unlink()
                        self.logger.info(f"Backup antigo removido: {backup['filename']}")
        
        except Exception as e:
            self.logger.error(f"Erro na limpeza de backups: {e}")
    
    def start_auto_backup(self):
        """Inicia backup automático"""
        if self._backup_thread and self._backup_thread.is_alive():
            self.logger.warning("Backup automático já está em execução")
            return
        
        self.auto_backup_enabled = True
        self._stop_auto_backup = False
        self._backup_thread = threading.Thread(target=self._auto_backup_worker, daemon=True)
        self._backup_thread.start()
        
        self._save_config()
        self.logger.info("Backup automático iniciado")
    
    def stop_auto_backup(self):
        """Para backup automático"""
        self.auto_backup_enabled = False
        self._stop_auto_backup = True
        
        if self._backup_thread:
            self._backup_thread.join(timeout=5)
        
        self._save_config()
        self.logger.info("Backup automático parado")
    
    def _auto_backup_worker(self):
        """Worker thread para backup automático"""
        while not self._stop_auto_backup and self.auto_backup_enabled:
            try:
                # Criar backup automático
                success, backup_path = self.create_backup("auto")
                
                if success:
                    self.logger.info(f"Backup automático criado: {backup_path}")
                else:
                    self.logger.error(f"Falha no backup automático: {backup_path}")
                
                # Aguardar próximo backup
                time.sleep(self.auto_backup_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no worker de backup automático: {e}")
                time.sleep(60)  # Aguardar 1 minuto antes de tentar novamente
    
    def configure_auto_backup(self, enabled: bool, interval_hours: int = 24, max_backups: int = 10):
        """Configura backup automático
        
        Args:
            enabled: Se o backup automático deve estar ativo
            interval_hours: Intervalo entre backups em horas
            max_backups: Número máximo de backups a manter
        """
        self.auto_backup_enabled = enabled
        self.auto_backup_interval = interval_hours * 60 * 60  # Converter para segundos
        self.max_backups = max_backups
        
        self._save_config()
        
        if enabled:
            self.start_auto_backup()
        else:
            self.stop_auto_backup()
        
        self.logger.info(f"Configuração de backup atualizada: enabled={enabled}, interval={interval_hours}h, max={max_backups}")
    
    def get_backup_status(self) -> Dict:
        """Retorna status do sistema de backup"""
        backups = self.list_backups()
        
        return {
            'auto_backup_enabled': self.auto_backup_enabled,
            'auto_backup_running': self._backup_thread and self._backup_thread.is_alive(),
            'backup_interval_hours': self.auto_backup_interval // 3600,
            'max_backups': self.max_backups,
            'total_backups': len(backups),
            'last_backup': backups[0] if backups else None,
            'backup_directory': str(self.backup_dir),
            'total_backup_size': sum(b['size'] for b in backups)
        }


# Instância global do gerenciador de backup
backup_manager = BackupManager()