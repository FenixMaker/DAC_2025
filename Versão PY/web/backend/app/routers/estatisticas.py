# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends

from ..services.db import get_db_manager

router = APIRouter()

@router.get("/resumo")
def estatisticas_resumo(db = Depends(get_db_manager)):
    stats = db.get_database_stats(use_cache=False) or {}
    # Mapear para nomes em português conforme especificação
    return {
        "regioes": stats.get("regions", 0),
        "domicilios": stats.get("households", 0),
        "individuos": stats.get("individuals", 0),
        "dispositivos": stats.get("device_usage_records", 0),
        "internet": stats.get("internet_usage_records", 0),
        # Fornece estrutura de crescimento esperada pelo frontend; valores padrão 0
        "crescimento": {
            "regioes": 0,
            "domicilios": 0,
            "individuos": 0,
            "dispositivos": 0,
            "internet": 0,
        },
    }