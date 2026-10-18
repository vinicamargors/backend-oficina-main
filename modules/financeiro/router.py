from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from core.security import exigir_cargos
from . import schemas, service

router = APIRouter(dependencies=[Depends(exigir_cargos("DONO", "FINANCEIRO", "master"))])

@router.get("/{empresa_id}", response_model=schemas.FinanceiroResponse)
def get_dados_financeiros(
    empresa_id: UUID,
    data_inicial: Optional[str] = Query(None, description="Filtro de data inicial (YYYY-MM-DD)"),
    data_final: Optional[str] = Query(None, description="Filtro de data final (YYYY-MM-DD)"),
):
    return service.obter_dados_financeiros(str(empresa_id), data_inicial, data_final)

@router.get("/inteligencia/{empresa_id}", response_model=schemas.InteligenciaFinanceiraResponse)
def get_inteligencia_financeira(
    empresa_id: UUID,
    data_inicial: Optional[str] = Query(None, description="YYYY-MM-DD"),
    data_final: Optional[str] = Query(None, description="YYYY-MM-DD"),
):
    return service.obter_inteligencia_financeira(str(empresa_id), data_inicial, data_final)