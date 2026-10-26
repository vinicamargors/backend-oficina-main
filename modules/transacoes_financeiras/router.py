from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from core.security import exigir_cargos
from . import schemas, service

router = APIRouter(dependencies=[Depends(exigir_cargos("DONO", "FINANCEIRO", "master"))])

@router.get("/{empresa_id}", response_model=schemas.TransacoesListResponse)
def get_transacoes(
    empresa_id: UUID,
    tipo: Optional[str] = Query(None, description="DESPESA ou RECEITA"),
    status: Optional[str] = Query(None, description="PENDENTE, LIQUIDADO, ATRASADO, CANCELADO"),
    data_inicial: Optional[str] = Query(None, description="YYYY-MM-DD"),
    data_final: Optional[str] = Query(None, description="YYYY-MM-DD"),
):
    return service.listar_transacoes(str(empresa_id), tipo, status, data_inicial, data_final)

@router.post("/", response_model=schemas.TransacaoResponse)
def post_transacao(dados: schemas.TransacaoCreate):
    return service.criar_transacao(dados)

@router.put("/{empresa_id}/{item_id}", response_model=schemas.TransacaoResponse)
def put_transacao(empresa_id: UUID, item_id: UUID, dados: schemas.TransacaoUpdate):
    return service.atualizar_transacao(str(item_id), str(empresa_id), dados)

@router.patch("/{empresa_id}/{item_id}/liquidar", response_model=schemas.TransacaoResponse)
def patch_liquidar_transacao(empresa_id: UUID, item_id: UUID, dados: schemas.TransacaoLiquidar):
    return service.liquidar_transacao(str(item_id), str(empresa_id), dados)

@router.delete("/{empresa_id}/{item_id}")
def delete_transacao(empresa_id: UUID, item_id: UUID):
    return service.deletar_transacao(str(item_id), str(empresa_id))

