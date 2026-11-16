from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from . import schemas, service
from core.security import validar_passaporte, empresa_do_usuario

router = APIRouter(dependencies=[Depends(validar_passaporte)])

@router.get("/consulta-placa/{placa}")
async def consulta_placa(placa: str):
    return await service.consultar_placa_externa(placa)

@router.get("/{empresa_id}", response_model=list[schemas.VeiculoResponse])
def get_veiculos(empresa_id: UUID, placa: Optional[str] = None):
    return service.listar_veiculos(str(empresa_id), placa)

# Antes de /{empresa_id}/{veiculo_id}, senão "paginado" seria lido como id
@router.get("/{empresa_id}/paginado", response_model=schemas.VeiculoPaginatedResponse)
def get_veiculos_paginado(empresa_id: UUID, busca: Optional[str] = None, cliente_id: Optional[UUID] = None,
                          skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    return service.listar_veiculos_paginado(str(empresa_id), busca, str(cliente_id) if cliente_id else None, skip, limit)

@router.get("/{empresa_id}/{veiculo_id}", response_model=schemas.VeiculoResponse)
def get_veiculo_por_id(empresa_id: UUID, veiculo_id: UUID):
    return service.obter_veiculo_por_id(str(veiculo_id), str(empresa_id))

@router.post("/", response_model=schemas.VeiculoResponse)
def post_veiculo(veiculo: schemas.VeiculoCreate, usuario: dict = Depends(validar_passaporte)):
    veiculo.empresa_id = empresa_do_usuario(usuario, veiculo.empresa_id)
    return service.criar_veiculo(veiculo)

@router.put("/{empresa_id}/{veiculo_id}", response_model=schemas.VeiculoResponse)
def put_veiculo(empresa_id: UUID, veiculo_id: UUID, veiculo: schemas.VeiculoUpdate):
    return service.atualizar_veiculo(str(veiculo_id), str(empresa_id), veiculo)

@router.delete("/{empresa_id}/{veiculo_id}")
def delete_veiculo(empresa_id: UUID, veiculo_id: UUID):
    return service.deletar_veiculo(str(veiculo_id), str(empresa_id))