# Gera relatório de integridade do banco de dados e salva em data/db_integrity_report.json
import json
import sys
from pathlib import Path
from pathlib import Path

# Garantir import do pacote 'src'
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.database.database_manager import DatabaseManager


def main():
    out_path = Path(project_root) / "data" / "db_integrity_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    db = DatabaseManager()
    try:
        # Inicializa o DB se necessário
        if db.engine is None or db.Session is None:
            db.initialize_database()

        report = db.check_database_integrity()

        # Salvar relatório em JSON
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Imprimir resumo
        errors = report.get("errors") or []
        integrity = report.get("integrity_check")
        fk = report.get("foreign_key_check")
        quick = report.get("quick_check")

        print("Integridade do DB salva em:", str(out_path))
        if errors:
            print(f"STATUS: PROBLEMAS ENCONTRADOS ({len(errors)}):")
            for e in errors:
                print(" -", e)
            return 2
        else:
            print("STATUS: OK")
            print("integrity_check:", integrity)
            print("foreign_key_check:", fk)
            print("quick_check:", quick)
            return 0

    except Exception as e:
        print("ERRO ao verificar integridade:", repr(e))
        return 3
    finally:
        try:
            db.close()
        except Exception:
            pass


if __name__ == '__main__':
    raise SystemExit(main())
