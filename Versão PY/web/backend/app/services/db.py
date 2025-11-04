# -*- coding: utf-8 -*-
"""Wrapper de serviço de DB para reaproveitar DatabaseManager do projeto Python."""

from pathlib import Path
import sys
from functools import lru_cache


def _add_project_root_to_path():
    """Adiciona a raiz do projeto ("Versão PY") ao sys.path para permitir imports."""
    current = Path(__file__).resolve()
    # Subir diretórios até encontrar uma pasta contendo "src" na raiz
    for parent in current.parents:
        src_dir = parent / "src"
        if src_dir.exists():
            project_root = parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            return project_root
    return None


project_root = _add_project_root_to_path()

from src.database.database_manager import DatabaseManager  # type: ignore
from src.utils.logger import get_logger  # type: ignore

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_db_manager() -> DatabaseManager:
    """Retorna instância única de DatabaseManager inicializada."""
    # Usar o novo caminho centralizado do banco de dados
    db_path = Path(__file__).resolve().parents[5] / "Banco de dados" / "dac_database.db"
    db = DatabaseManager(db_path=str(db_path))
    db.initialize_database()
    logger.info(f"DatabaseManager inicializado para Web API usando: {db_path}")
    return db