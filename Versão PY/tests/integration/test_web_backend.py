# -*- coding: utf-8 -*-
import sys
from pathlib import Path


def _add_project_root_to_path():
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "Versão PY").exists():
            # Entrar em "Versão PY" para ter acesso ao backend e src
            vp = parent / "Versão PY"
            if str(vp) not in sys.path:
                sys.path.insert(0, str(vp))
            # Também adicionar raiz contendo src para imports do app
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            break


_add_project_root_to_path()

from web.backend.app.main import app
from fastapi.testclient import TestClient
from src.database.database_manager import DatabaseManager


client = TestClient(app)


def test_health_endpoint_ok():
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data == {"status": "ok"}


def test_estatisticas_resumo_matches_db():
    db = DatabaseManager()
    db.initialize_database()
    stats = db.get_database_stats(use_cache=False)

    r = client.get("/api/estatisticas/resumo")
    assert r.status_code == 200
    data = r.json()

    assert data["regioes"] == stats.get("regions", 0)
    assert data["domicilios"] == stats.get("households", 0)
    assert data["individuos"] == stats.get("individuals", 0)
    assert data["dispositivos"] == stats.get("device_usage_records", 0)
    assert data["internet"] == stats.get("internet_usage_records", 0)


def test_individuos_paginacao_total_matches_db():
    db = DatabaseManager()
    db.initialize_database()
    total_individuos = db.count_records("Individual")

    r = client.get("/api/individuos", params={"page": 1, "limit": 5})
    assert r.status_code == 200
    body = r.json()
    assert "data" in body and isinstance(body["data"], list)
    assert "pagination" in body
    assert body["pagination"]["total"] == total_individuos
    # Consistência de totalPages
    tp = body["pagination"]["totalPages"]
    assert tp == (total_individuos + 5 - 1) // 5