# -*- coding: utf-8 -*-
"""
Sistema de backup e recuperação de dados
"""

import os
import shutil
import sqlite3
import zipfile
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from .logger import get_logger
from .settings import get_setting

class BackupManager:
    """Gerenciador de backup e recuperação de dados"""
    
    def __init__(self, db_path=None, backup_dir=None):
        """
        Inicializa o gerenciador de backup
        
        Args:
            db_path (str, optional): Caminho do banco de dados
            backup_dir (str, optional): Diretório de backups
        """
        self.logger = get_logger(__name__)
        
        if db_path is None:
            data_dir = Path(__file__).parent.parent.parent / "data"
            db_path = data_dir / "dac_database.db"
        
        if backup_dir is None:
            backup_dir = Path(__file__).parent.parent.parent / "backups"
        
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações de backup
        self.max_backups = get_setting('data.max_backups', 5)
        self.auto_backup = get_setting('data.auto_backup', True)
        self.backup_interval = get_setting('data.backup_interval', 24)  # horas
    
    def create_backup(self, backup_name=None, include_logs=True, compress=True) -> Optional[str]:
        """
        Cria um backup completo do sistema
        
        Args:
            backup_name (str, optional): Nome do backup
            include_logs (bool): Se deve incluir logs
            compress (bool): Se deve comprimir o backup
            
        Returns:
            str: Caminho do arquivo de backup criado, None se falhou
        """
        try:
            if backup_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_dac_{timestamp}"
            
            # Criar diretório temporário para o backup
            temp_backup_dir = self.backup_dir / f"temp_{backup_name}"
            temp_backup_dir.mkdir(exist_ok=True)
            
            backup_info = {
                'name': backup_name,
                'timestamp': datetime.now().isoformat(),
                'version': '1.0',
                'files': [],
                'size': 0
            }
            
            try:
                # Backup do banco de dados
                if self.db_path.exists():
                    db_backup_path = temp_backup_dir / "database.db"
                    self._backup_database(self.db_path, db_backup_path)
                    backup_info['files'].append('database.db')
                    backup_info['size'] += db_backup_path.stat().st_size
                    self.logger.info("Banco de dados incluído no backup")
                
                # Backup das configurações
                config_dir = Path(__file__).parent.parent.parent / "config"
                if config_dir.exists():
                    config_backup_dir = temp_backup_dir / "config"
                    shutil.copytree(config_dir, config_backup_dir, dirs_exist_ok=True)
                    backup_info['files'].append('config/')
                    self.logger.info("Configurações incluídas no backup")
                
                # Backup dos logs (se solicitado)
                if include_logs:
                    logs_dir = Path(__file__).parent.parent.parent / "logs"
                    if logs_dir.exists():
                        logs_backup_dir = temp_backup_dir / "logs"
                        shutil.copytree(logs_dir, logs_backup_dir, dirs_exist_ok=True)
                        backup_info['files'].append('logs/')
                        self.logger.info("Logs incluídos no backup")
                
                # Salvar informações do backup
                info_file = temp_backup_dir / "backup_info.json"
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(backup_info, f, indent=4, ensure_ascii=False)
                
                # Comprimir se solicitado
                if compress:
                    backup_file = self.backup_dir / f"{backup_name}.zip"
                    self._create_zip_backup(temp_backup_dir, backup_file)
                    final_backup_path = backup_file
                else:
                    final_backup_path = self.backup_dir / backup_name
                    if final_backup_path.exists():
                        shutil.rmtree(final_backup_path)
                    shutil.move(temp_backup_dir, final_backup_path)
                
                # Limpar diretório temporário
                if temp_backup_dir.exists():
                    shutil.rmtree(temp_backup_dir)
                
                # Limpar backups antigos
                self._cleanup_old_backups()
                
                self.logger.info(f"Backup criado com sucesso: {final_backup_path}")
                return str(final_backup_path)
                
            except Exception as e:
                # Limpar em caso de erro
                if temp_backup_dir.exists():
                    shutil.rmtree(temp_backup_dir)
                raise e
                
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {e}")
            return None
    
    def _backup_database(self, source_db: Path, target_db: Path) -> None:
        """
        Cria backup do banco de dados SQLite
        
        Args:
            source_db (Path): Caminho do banco de origem
            target_db (Path): Caminho do banco de destino
        """
        try:
            # Conectar ao banco de origem
            source_conn = sqlite3.connect(str(source_db))
            
            # Criar backup usando o método backup do SQLite
            target_conn = sqlite3.connect(str(target_db))
            source_conn.backup(target_conn)
            
            # Fechar conexões
            source_conn.close()
            target_conn.close()
            
        except Exception as e:
            self.logger.error(f"Erro no backup do banco de dados: {e}")
            # Fallback: copiar arquivo
            shutil.copy2(source_db, target_db)
    
    def _create_zip_backup(self, source_dir: Path, target_file: Path) -> None:
        """
        Cria arquivo ZIP do backup
        
        Args:
            source_dir (Path): Diretório de origem
            target_file (Path): Arquivo ZIP de destino
        """
        with zipfile.ZipFile(target_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)
    
    def list_backups(self) -> List[Dict]:
        """
        Lista todos os backups disponíveis
        
        Returns:
            list: Lista de informações dos backups
        """
        backups = []
        
        try:
            for item in self.backup_dir.iterdir():
                if item.is_file() and item.suffix == '.zip':
                    # Backup comprimido
                    backup_info = self._get_zip_backup_info(item)
                elif item.is_dir() and not item.name.startswith('temp_'):
                    # Backup não comprimido
                    backup_info = self._get_dir_backup_info(item)
                else:
                    continue
                
                if backup_info:
                    backups.append(backup_info)
            
            # Ordenar por data (mais recente primeiro)
            backups.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
        except Exception as e:
            self.logger.error(f"Erro ao listar backups: {e}")
        
        return backups
    
    def _get_zip_backup_info(self, zip_path: Path) -> Optional[Dict]:
        """
        Obtém informações de um backup ZIP
        
        Args:
            zip_path (Path): Caminho do arquivo ZIP
            
        Returns:
            dict: Informações do backup
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                if 'backup_info.json' in zipf.namelist():
                    with zipf.open('backup_info.json') as f:
                        info = json.load(f)
                else:
                    # Backup sem informações, criar básicas
                    info = {
                        'name': zip_path.stem,
                        'timestamp': datetime.fromtimestamp(zip_path.stat().st_mtime).isoformat(),
                        'version': 'unknown',
                        'files': zipf.namelist(),
                        'size': zip_path.stat().st_size
                    }
                
                info['path'] = str(zip_path)
                info['type'] = 'compressed'
                info['file_size'] = zip_path.stat().st_size
                
                return info
                
        except Exception as e:
            self.logger.error(f"Erro ao ler backup ZIP {zip_path}: {e}")
            return None
    
    def _get_dir_backup_info(self, dir_path: Path) -> Optional[Dict]:
        """
        Obtém informações de um backup em diretório
        
        Args:
            dir_path (Path): Caminho do diretório
            
        Returns:
            dict: Informações do backup
        """
        try:
            info_file = dir_path / 'backup_info.json'
            
            if info_file.exists():
                with open(info_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
            else:
                # Backup sem informações, criar básicas
                info = {
                    'name': dir_path.name,
                    'timestamp': datetime.fromtimestamp(dir_path.stat().st_mtime).isoformat(),
                    'version': 'unknown',
                    'files': [f.name for f in dir_path.iterdir()],
                    'size': sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                }
            
            info['path'] = str(dir_path)
            info['type'] = 'directory'
            info['file_size'] = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
            
            return info
            
        except Exception as e:
            self.logger.error(f"Erro ao ler backup de diretório {dir_path}: {e}")
            return None
    
    def restore_backup(self, backup_path: str, restore_database=True, restore_config=True, restore_logs=False) -> bool:
        """
        Restaura um backup
        
        Args:
            backup_path (str): Caminho do backup
            restore_database (bool): Se deve restaurar o banco de dados
            restore_config (bool): Se deve restaurar as configurações
            restore_logs (bool): Se deve restaurar os logs
            
        Returns:
            bool: True se restaurou com sucesso, False caso contrário
        """
        try:
            backup_path = Path(backup_path)
            
            if not backup_path.exists():
                self.logger.error(f"Backup não encontrado: {backup_path}")
                return False
            
            # Criar backup de segurança antes da restauração
            safety_backup = self.create_backup(f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            if safety_backup:
                self.logger.info(f"Backup de segurança criado: {safety_backup}")
            
            # Extrair backup se for ZIP
            if backup_path.suffix == '.zip':
                temp_dir = self.backup_dir / f"temp_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                temp_dir.mkdir(exist_ok=True)
                
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall(temp_dir)
                
                restore_source = temp_dir
            else:
                restore_source = backup_path
            
            try:
                # Restaurar banco de dados
                if restore_database:
                    db_backup = restore_source / "database.db"
                    if db_backup.exists():
                        # Fazer backup do banco atual
                        if self.db_path.exists():
                            backup_current_db = self.db_path.with_suffix('.db.bak')
                            shutil.copy2(self.db_path, backup_current_db)
                        
                        # Restaurar banco
                        shutil.copy2(db_backup, self.db_path)
                        self.logger.info("Banco de dados restaurado")
                
                # Restaurar configurações
                if restore_config:
                    config_backup = restore_source / "config"
                    if config_backup.exists():
                        config_dir = Path(__file__).parent.parent.parent / "config"
                        if config_dir.exists():
                            shutil.rmtree(config_dir)
                        shutil.copytree(config_backup, config_dir)
                        self.logger.info("Configurações restauradas")
                
                # Restaurar logs
                if restore_logs:
                    logs_backup = restore_source / "logs"
                    if logs_backup.exists():
                        logs_dir = Path(__file__).parent.parent.parent / "logs"
                        if logs_dir.exists():
                            shutil.rmtree(logs_dir)
                        shutil.copytree(logs_backup, logs_dir)
                        self.logger.info("Logs restaurados")
                
                # Limpar diretório temporário
                if backup_path.suffix == '.zip' and restore_source.exists():
                    shutil.rmtree(restore_source)
                
                self.logger.info(f"Backup restaurado com sucesso: {backup_path}")
                return True
                
            except Exception as e:
                # Limpar em caso de erro
                if backup_path.suffix == '.zip' and restore_source.exists():
                    shutil.rmtree(restore_source)
                raise e
                
        except Exception as e:
            self.logger.error(f"Erro ao restaurar backup: {e}")
            return False
    
    def delete_backup(self, backup_path: str) -> bool:
        """
        Exclui um backup
        
        Args:
            backup_path (str): Caminho do backup
            
        Returns:
            bool: True se excluiu com sucesso, False caso contrário
        """
        try:
            backup_path = Path(backup_path)
            
            if not backup_path.exists():
                self.logger.warning(f"Backup não encontrado: {backup_path}")
                return False
            
            if backup_path.is_file():
                backup_path.unlink()
            else:
                shutil.rmtree(backup_path)
            
            self.logger.info(f"Backup excluído: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao excluir backup: {e}")
            return False
    
    def _cleanup_old_backups(self) -> None:
        """
        Remove backups antigos baseado na configuração max_backups
        """
        try:
            backups = self.list_backups()
            
            if len(backups) > self.max_backups:
                # Ordenar por data (mais antigo primeiro)
                backups.sort(key=lambda x: x.get('timestamp', ''))
                
                # Remover backups excedentes
                for backup in backups[:-self.max_backups]:
                    self.delete_backup(backup['path'])
                    self.logger.info(f"Backup antigo removido: {backup['name']}")
                    
        except Exception as e:
            self.logger.error(f"Erro na limpeza de backups antigos: {e}")
    
    def should_auto_backup(self) -> bool:
        """
        Verifica se deve fazer backup automático
        
        Returns:
            bool: True se deve fazer backup, False caso contrário
        """
        if not self.auto_backup:
            return False
        
        try:
            backups = self.list_backups()
            
            if not backups:
                return True  # Primeiro backup
            
            # Verificar o backup mais recente
            latest_backup = backups[0]
            backup_time = datetime.fromisoformat(latest_backup['timestamp'])
            
            # Verificar se passou o intervalo
            time_diff = datetime.now() - backup_time
            return time_diff.total_seconds() >= (self.backup_interval * 3600)
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar necessidade de backup: {e}")
            return False
    
    def get_backup_statistics(self) -> Dict:
        """
        Retorna estatísticas dos backups
        
        Returns:
            dict: Estatísticas dos backups
        """
        try:
            backups = self.list_backups()
            
            if not backups:
                return {
                    'total_backups': 0,
                    'total_size': 0,
                    'latest_backup': None,
                    'oldest_backup': None,
                    'average_size': 0
                }
            
            total_size = sum(backup.get('file_size', 0) for backup in backups)
            
            return {
                'total_backups': len(backups),
                'total_size': total_size,
                'latest_backup': backups[0]['timestamp'],
                'oldest_backup': backups[-1]['timestamp'],
                'average_size': total_size // len(backups) if backups else 0
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas de backup: {e}")
            return {}

# Instância global do gerenciador de backup
_backup_manager = None

def get_backup_manager() -> BackupManager:
    """
    Retorna a instância global do gerenciador de backup
    
    Returns:
        BackupManager: Instância do gerenciador
    """
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager