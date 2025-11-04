# Script de verificação de conexão com o banco (gerado automaticamente)
import os
import sys
from pathlib import Path

# Garantir que a raiz do projeto esteja no sys.path para permitir imports relativos a 'src'
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database.database_manager import DatabaseManager
from sqlalchemy import text


def main():
    db = DatabaseManager()
    try:
        # Se o gerenciador ainda não inicializou o DB, inicializa (cria engine, tabelas e dados iniciais)
        if db.engine is None or db.Session is None:
            db.initialize_database()

        session = db.get_session()
        # Executa um SELECT simples
        result = session.execute(text("SELECT 1")).fetchall()
        print("CONNECTED", result)
        session.close()
        return 0
    except Exception as e:
        print("ERROR", repr(e))
        return 2
    finally:
        try:
            db.close()
        except Exception:
            pass

if __name__ == '__main__':
    raise SystemExit(main())
