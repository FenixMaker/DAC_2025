import os
import tempfile
import shutil

from src.database.database_manager import DatabaseManager


def test_server_status_and_metrics():
    tmpdir = tempfile.mkdtemp()
    try:
        db_path = os.path.join(tmpdir, 'test_dac.db')
        mgr = DatabaseManager(db_path=db_path)
        mgr.initialize_database()

        status = mgr.get_server_status()
        assert isinstance(status, dict)
        assert status.get('database_path') == db_path
        assert 'sqlite_version' in status
        assert 'tables_count' in status

        metrics = mgr.get_performance_metrics()
        assert isinstance(metrics, dict)
        assert 'page_count' in metrics
        assert 'journal_mode' in metrics

        top = mgr.get_top_tables_by_rows()
        assert isinstance(top, list)
        # Deve conter pelo menos a tabela regions inicial
        names = [t['name'] for t in top]
        assert 'regions' in names

        # Manutenção básica
        assert mgr.run_maintenance('VACUUM') is True
        assert mgr.run_maintenance('ANALYZE') is True
        assert mgr.run_maintenance('REINDEX') is True
        assert mgr.run_maintenance('INVALID') is False

        mgr.close()
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)