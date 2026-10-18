from fastapi import APIRouter, Depends
from typing import Optional
from uuid import UUID
from . import schemas, service
from core.security import validar_passaporte

router = APIRouter(dependencies=[Depends(validar_passaporte)])

@router.get("/consulta-placa/{placa}")
async def consulta_placa(placa: str):
    return await service.consultar_placa_externa(placa)

@router.get("/{empresa_id}", response_model=list[schemas.VeiculoResponse])
def get_veiculos(empresa_id: UUID, placa: Optional[str] = None):
    return service.listar_veiculos(str(empresa_id), placa)

@router.get("/{empresa_id}/{veiculo_id}", response_model=schemas.VeiculoResponse)
def get_veiculo_por_id(empresa_id: UUID, veiculo_id: UUID):
    return service.obter_veiculo_por_id(str(veiculo_id), str(empresa_id))

@router.post("/", response_model=schemas.VeiculoResponse)
def post_veiculo(veiculo: schemas.VeiculoCreate):
    return service.criar_veiculo(veiculo)

@router.put("/{empresa_id}/{veiculo_id}", response_model=schemas.VeiculoResponse)
def put_veiculo(empresa_id: UUID, veiculo_id: UUID, veiculo: schemas.VeiculoUpdate):
    return service.atualizar_veiculo(str(veiculo_id), str(empresa_id), veiculo)

@router.delete("/{empresa_id}/{veiculo_id}")
def delete_veiculo(empresa_id: UUID, veiculo_id: UUID):
    return service.deletar_veiculo(str(veiculo_id), str(empresa_id))