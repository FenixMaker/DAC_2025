# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Query
from typing import Optional

from ..services.db import get_db_manager

router = APIRouter()

@router.get("/individuos")
def listar_individuos(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=200),
    idade: Optional[int] = Query(None, ge=0),
    genero: Optional[str] = Query(None),
    regiao_id: Optional[int] = Query(None, ge=1),
    db = Depends(get_db_manager),
):
    # Importar modelos aqui para evitar ciclos de import
    from src.database.models import Individual, Household, Region, DeviceUsage, InternetUsage

    # Construir filtros compatíveis com DatabaseManager
    filters = {}
    if idade is not None:
        filters["age"] = idade
    if genero:
        filters["gender"] = genero
    # Filtrar por região via join com Household
    session = db.get_session()
    try:
        query = session.query(Individual)
        if regiao_id is not None:
            query = query.join(Household).filter(Household.region_id == regiao_id)
        if idade is not None:
            query = query.filter(Individual.age == idade)
        if genero:
            query = query.filter(Individual.gender == genero)

        total = query.count()
        offset = (page - 1) * limit
        # Carregar domicílios associados para enriquecer dados
        items = query.offset(offset).limit(limit).all()

        data = []
        for i in items:
            # Obter informações do domicílio e região
            household = session.query(Household).get(i.household_id)
            regiao_nome = None
            domicilio_info = None
            internet_bool = None
            if household:
                domicilio_info = household.city
                internet_bool = household.has_internet
                regiao = session.query(Region).get(household.region_id)
                regiao_nome = regiao.name if regiao else None

            # Contar dispositivos usados pelo indivíduo (has_device = True)
            dispositivos_count = (
                session.query(DeviceUsage)
                .filter(DeviceUsage.individual_id == i.id, DeviceUsage.has_device == True)
                .count()
            )

            # Verificar uso de internet individual se existir
            iu = (
                session.query(InternetUsage)
                .filter(InternetUsage.individual_id == i.id)
                .first()
            )
            if iu is not None:
                internet_bool = bool(iu.uses_internet)

            data.append(
                {
                    "id": i.id,
                    # Fallback de nome até existir campo apropriado no modelo
                    "nome": f"Indivíduo {i.id}",
                    "idade": i.age,
                    "regiao": regiao_nome,
                    "domicilio": domicilio_info,
                    "dispositivos": dispositivos_count,
                    "internet": bool(internet_bool) if internet_bool is not None else False,
                    "genero": i.gender,
                    "household_id": i.household_id,
                    "created_at": i.created_at.isoformat() if i.created_at else None,
                }
            )

        return {
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "totalPages": (total + limit - 1) // limit,
            },
        }
    finally:
        session.close()