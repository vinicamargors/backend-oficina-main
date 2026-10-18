from fastapi import APIRouter, Depends
from uuid import UUID
from core.security import validar_passaporte
from . import schemas, service

# Módulo inteiro trancado pelo segurança da Big Tech. Só entra logado!
router = APIRouter(dependencies=[Depends(validar_passaporte)])

@router.get("/{empresa_id}", response_model=schemas.DashboardOperacionalResponse)
def get_dashboard_operacional(empresa_id: UUID):
    return service.obter_dashboard_operacional(str(empresa_id))