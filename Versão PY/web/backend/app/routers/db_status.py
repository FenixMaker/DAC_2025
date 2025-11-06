# -*- coding: utf-8 -*-
"""Endpoint de status do banco para consumo pelo frontend.

Tenta usar conexão universal (Postgres/MySQL/SQLite) e, na ausência,
mantém o comportamento anterior com DatabaseManager (SQLite).
"""

from fastapi import APIRouter
from pathlib import Path
from datetime import datetime

from ..services.db import get_db_manager, get_sqlalchemy_universal
from sqlalchemy import text

router = APIRouter()


@router.get("/db/status")
def db_status():
    # Primeiro tenta conexão universal (Postgres/MySQL/SQLite)
    try:
        udb = get_sqlalchemy_universal()
        st = udb.status()
        if st.get("connected"):
            dialect = st.get("dialect")
            if dialect == "postgresql":
                with udb.engine.connect() as conn:
                    basic = conn.execute(text("""
                        select version(), current_user as user, current_database() as database, now() as server_time,
                               to_char(date_trunc('second', now() - pg_postmaster_start_time()), 'DD "d" HH24:MI:SS') as uptime
                    """)) .first()
                    tables = conn.execute(text("""
                        select count(*)::int from information_schema.tables where table_schema='public' and table_type='BASE TABLE'
                    """)).scalar()
                    indexes = conn.execute(text("""
                        select count(*)::int from pg_indexes where schemaname='public'
                    """)).scalar()
                    conns = conn.execute(text("""
                        select count(*)::int from pg_stat_activity where datname = current_database()
                    """)).scalar()
                    sizes = conn.execute(text("""
                        select pg_database_size(current_database())::bigint as db_bytes,
                               coalesce(sum(pg_total_relation_size(format('%I.%I', n.nspname, c.relname))),0)::bigint as tables_bytes
                        from pg_class c
                        join pg_namespace n on n.oid = c.relnamespace
                        where n.nspname = 'public' and c.relkind='r'
                    """)).first()
                    top = conn.execute(text("""
                        select c.relname as name, pg_total_relation_size(format('%I.%I', n.nspname, c.relname))::bigint as total_bytes
                        from pg_class c
                        join pg_namespace n on n.oid = c.relnamespace
                        where n.nspname='public' and c.relkind='r'
                        order by total_bytes desc
                        limit 5
                    """)) .mappings().all()

                return {
                    "connected": True,
                    "version": basic[0],
                    "user": basic[1],
                    "database": basic[2],
                    "server_time": str(basic[3]),
                    "uptime": basic[4],
                    "totals": {
                        "tables": int(tables or 0),
                        "indexes": int(indexes or 0),
                        "connections": int(conns or 0),
                        "db_bytes": int(sizes[0] or 0),
                        "tables_bytes": int(sizes[1] or 0),
                    },
                    "top_tables": [{"name": t["name"], "total_bytes": int(t["total_bytes"] or 0)} for t in top],
                }

            # Para SQLite/MySQL, retorna status simplificado via DatabaseManager
    except Exception:
        pass

    # Fallback para SQLite via DatabaseManager
    db = get_db_manager()
    try:
        server = db.get_server_status()
        perf = db.get_performance_metrics()
        top = db.get_top_tables_by_rows(limit=5)

        data = {
            "connected": bool(server.get("connected")),
            "version": f"SQLite {server.get('sqlite_version')}",
            "user": "sqlite",
            "database": Path(server.get("database_path") or "dac_database.db").name,
            "server_time": server.get("server_time") or datetime.now().isoformat(timespec="seconds"),
            "uptime": server.get("uptime_human") or "0s",
            "totals": {
                "tables": int(server.get("tables_count") or 0),
                "indexes": int(server.get("indexes_count") or 0),
                "connections": 1,
                "db_bytes": int(perf.get("database_size_bytes") or 0),
                "tables_bytes": int(perf.get("database_size_bytes") or 0),
            },
            "top_tables": [{"name": t["name"], "total_bytes": int(t.get("rows") or 0)} for t in (top or [])],
        }
        return data
    except Exception as e:
        return {"connected": False, "error": f"Falha ao obter status do banco: {e}"}