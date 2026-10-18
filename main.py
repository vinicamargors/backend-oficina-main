from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from postgrest.exceptions import APIError
from core.errors import supabase_exception_handler

from modules.clientes import router as clientes_router
from modules.veiculos import router as veiculos_router
from modules.os import router as os_router
from modules.estoque import router as estoque_router
from modules.empresas import router as empresas_router
from modules.usuarios import router as usuarios_router
from modules.logs import router as logs_router
from modules.dashboards import router as dashboards_router
from modules.financeiro import router as financeiro_router
from modules.bot import router as bot_router


app = FastAPI(title="Oficina API", description="Monólito Modular focado em eficiência")

# Tradutor de erros do Supabase
app.add_exception_handler(APIError, supabase_exception_handler)

# 1. MIDDLEWARE DO CORS (Aduana de liberação do React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Registro de todas as rotas (Os galpões da fábrica)
app.include_router(clientes_router.router, prefix="/api/v1/clientes", tags=["Clientes"])
app.include_router(veiculos_router.router, prefix="/api/v1/veiculos", tags=["Veículos"])
app.include_router(os_router.router, prefix="/api/v1/os", tags=["Ordens de Serviço"])
app.include_router(estoque_router.router, prefix="/api/v1/estoque", tags=["Estoque"])
app.include_router(empresas_router.router, prefix="/api/v1/empresas", tags=["Empresas / SaaS"])
app.include_router(usuarios_router.router, prefix="/api/v1/usuarios", tags=["Usuários / RH"])
app.include_router(logs_router.router, prefix="/api/v1/logs", tags=["Auditoria e Logs"])
app.include_router(dashboards_router.router, prefix="/api/v1/dashboards", tags=["Módulo Operacional / Dashboards"])
app.include_router(financeiro_router.router, prefix="/api/v1/financeiro", tags=["Módulo Estratégico / Financeiro"])
app.include_router(bot_router.router, prefix="/api/v1/bot", tags=["Bot de Atendimento"])


@app.get("/")
def read_root():
    return {"status": "Motor rodando livre de burocracia."}