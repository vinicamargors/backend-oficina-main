from fastapi import APIRouter, Depends
from typing import Optional
from uuid import UUID
from . import service
from core.security import exigir_cargos

router = APIRouter(dependencies=[Depends(exigir_cargos("DONO", "master"))])

@router.get("/{empresa_id}")
def get_logs(
    empresa_id: UUID,
    tabela: Optional[str] = None,
    operacao: Optional[str] = None,
    data_ini: Optional[str] = None,
    data_fim: Optional[str] = None,
):
    return service.listar_logs(str(empresa_id), tabela, operacao, data_ini, data_fim)

@router.get("/{empresa_id}/exportar")
def exportar_logs(
    empresa_id: UUID,
    data_ini: Optional[str] = None,
    data_fim: Optional[str] = None,
):
    return service.exportar_logs_txt(str(empresa_id), data_ini, data_fim)