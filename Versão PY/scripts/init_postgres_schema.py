# Cria as tabelas do DAC no PostgreSQL com base nos modelos SQLAlchemy
import json
from pathlib import Path
from sqlalchemy import create_engine

# Import dinâmico dos modelos
project_root = Path(__file__).resolve().parents[1]
import sys
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.database.models import Base

CONFIG_PATHS = [
    project_root / "recursos" / "configuracoes" / "database_config.json",
    project_root.parent / "recursos" / "configuracoes" / "database_config.json",
]


def load_config():
    for p in CONFIG_PATHS:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError("database_config.json não encontrado nas pastas padrão")


def make_url(cfg: dict) -> str:
    db = cfg["database"]
    user = db.get("username")
    pwd = db.get("password")
    host = db.get("host", "127.0.0.1")
    port = int(db.get("port", 5432))
    name = db.get("database", "sistema_dac")
    return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{name}"


def main() -> int:
    cfg = load_config()
    url = make_url(cfg)
    engine = create_engine(url, pool_pre_ping=True)
    try:
        # Cria todas as tabelas declaradas em Base.metadata
        Base.metadata.create_all(engine)
        print("SCHEMA_OK", {"database": cfg["database"]["database"], "host": cfg["database"]["host"]})
        return 0
    except Exception as e:
        # Se já existe, consideramos OK
        msg = str(e)
        if "existe" in msg.lower() or "already exists" in msg.lower() or "DuplicateTable" in msg:
            print("SCHEMA_EXISTS", {"message": msg.split("\n")[0]})
            return 0
        print("ERROR", repr(e))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
