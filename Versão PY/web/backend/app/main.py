# -*- coding: utf-8 -*-
"""Aplicação FastAPI principal do DAC Web v0.

Inicializa a aplicação, configura CORS e registra rotas de API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.health import router as health_router
from .routers.estatisticas import router as estatisticas_router
from .routers.individuos import router as individuos_router

app = FastAPI(title="DAC Web v0", version="0.1.0")

# CORS para permitir acesso do frontend Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rotas
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(estatisticas_router, prefix="/api/estatisticas", tags=["estatisticas"])
app.include_router(individuos_router, prefix="/api", tags=["individuos"])