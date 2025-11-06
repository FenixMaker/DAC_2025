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
from src.database.universal import get_universal_db  # type: ignore

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_db_manager() -> DatabaseManager:
    """Retorna instância única de DatabaseManager inicializada."""
    # Usar caminho estável dentro da raiz do projeto (Versão PY/data)
    # Isso evita falhas quando a pasta "Banco de dados" não existe
    base_root = project_root or Path(__file__).resolve().parents[4]
    data_dir = Path(base_root) / "data"
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        # Se não conseguir criar, ainda tenta seguir com o caminho
        pass
    db_path = data_dir / "dac_database.db"

    db = DatabaseManager(db_path=str(db_path))
    db.initialize_database()
    logger.info(f"DatabaseManager inicializado para Web API usando: {db_path}")
    return db


def get_sqlalchemy_universal():
    """Retorna instância universal de banco (SQLAlchemy) para Postgres/MySQL/SQLite.

    Não substitui o DatabaseManager, mas pode ser usada em serviços que precisem
    de transações e pooling multi‑SGBD.
    """
    return get_universal_db()
