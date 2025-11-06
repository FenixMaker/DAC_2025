# -*- coding: utf-8 -*-
"""
Módulo de conexão universal para Python (desktop e backend).

Objetivos:
- Seleciona driver automaticamente a partir de `DATABASE_URL` (Postgres/MySQL/SQLite)
- Usa SQLAlchemy para pooling, transações e compatibilidade multi‑SGBD
- Mantém credenciais fora do código (env/.env ou recursos/configuracoes/database_config.json)
- Fornece helpers para transações e verificação de status

Exemplos de URLs suportadas:
- postgresql+psycopg://usuario:senha@host:5432/banco
- mysql+pymysql://usuario:senha@host:3306/banco
- sqlite:///caminho/arquivo.db
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Iterable, Any, Dict

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


def _read_json_config() -> Optional[Dict[str, Any]]:
    """Lê `recursos/configuracoes/database_config.json` se existir."""
    try:
        project_root = Path(__file__).resolve().parents[2]
        cfg_path = project_root / "recursos" / "configuracoes" / "database_config.json"
        if cfg_path.exists():
            import json
            return json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return None


def _make_url_from_json(cfg: Dict[str, Any]) -> Optional[str]:
    try:
        db = cfg.get("database", {})
        user = db.get("username")
        pwd = db.get("password")
        host = db.get("host", "127.0.0.1")
        port = int(db.get("port", 5432))
        name = db.get("database", "postgres")
        # default para Postgres
        return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{name}"
    except Exception:
        return None


def resolve_database_url() -> str:
    """Resolve `DATABASE_URL` com fallback para arquivo SQLite do projeto."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    cfg = _read_json_config()
    if cfg:
        url2 = _make_url_from_json(cfg)
        if url2:
            return url2
    # Fallback SQLite local
    data_dir = Path(__file__).resolve().parents[2] / "data"
    data_dir.mkdir(exist_ok=True)
    db_path = data_dir / "dac_database.db"
    return f"sqlite:///{db_path}"


@dataclass
class UniversalDB:
    """Wrapper simples de engine+Session com transações e pooling."""

    url: str
    engine: Any
    Session: Any

    @classmethod
    def create(cls, url: Optional[str] = None) -> "UniversalDB":
        url = url or resolve_database_url()

        # Pool tuning genérico; SQLAlchemy escolhe o pool apropriado por dialeto
        engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
            future=True,
        )

        Session = sessionmaker(bind=engine, expire_on_commit=False, future=True)
        return cls(url=url, engine=engine, Session=Session)

    def session(self):
        return self.Session()

    def execute(self, sql: str, params: Optional[Iterable[Any]] = None):
        with self.engine.connect() as conn:
            return conn.execute(text(sql), params or {})

    def transaction(self):
        """Context manager de transação."""
        class Tx:
            def __init__(self, Session):
                self.Session = Session
                self.session = None

            def __enter__(self):
                self.session = self.Session()
                self.session.begin()
                return self.session

            def __exit__(self, exc_type, exc, tb):
                try:
                    if exc_type is None:
                        self.session.commit()
                    else:
                        self.session.rollback()
                finally:
                    self.session.close()
        return Tx(self.Session)

    def status(self) -> Dict[str, Any]:
        """Retorna status mínimo independente do SGBD."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                dialect = self.engine.dialect.name
                info: Dict[str, Any] = {"connected": True, "dialect": dialect}
                if dialect == "postgresql":
                    info.update({
                        "version": conn.execute(text("select version()")) .scalar(),
                        "server_time": conn.execute(text("select now()")) .scalar(),
                    })
                elif dialect == "mysql":
                    info.update({
                        "version": conn.execute(text("select version()")) .scalar(),
                    })
                elif dialect == "sqlite":
                    info.update({
                        "version": conn.execute(text("select sqlite_version()")) .scalar(),
                    })
                return info
        except Exception as e:
            return {"connected": False, "error": str(e)}

    def close(self):
        try:
            self.engine.dispose()
        except Exception:
            pass


# Instância singleton (opcional) para reutilização em apps
_db_singleton: Optional[UniversalDB] = None


def get_universal_db() -> UniversalDB:
    global _db_singleton
    if _db_singleton is None:
        _db_singleton = UniversalDB.create()
    return _db_singleton
