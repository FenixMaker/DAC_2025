# Verifica conexão com PostgreSQL usando database_config.json
import json
from pathlib import Path
from sqlalchemy import create_engine, text

CONFIG_PATHS = [
    Path(__file__).resolve().parents[1] / "recursos" / "configuracoes" / "database_config.json",
    Path(__file__).resolve().parents[2] / "recursos" / "configuracoes" / "database_config.json",
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
        with engine.connect() as conn:
            version = conn.execute(text("select version();")).scalar()
            db_user = conn.execute(text("select current_user;")) .scalar()
            db_name = conn.execute(text("select current_database();")).scalar()
            tables = conn.execute(text("""
                select count(*)
                from information_schema.tables
                where table_schema='public' and table_type='BASE TABLE'
            """)) .scalar()
            one = conn.execute(text("select 1")).scalar()
            print("CONNECTED", {
                "version": version,
                "user": db_user,
                "database": db_name,
                "public_tables": tables,
                "select1": one
            })
        return 0
    except Exception as e:
        print("ERROR", repr(e))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
