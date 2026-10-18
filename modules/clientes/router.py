from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from . import schemas, service
from core.security import validar_passaporte

router = APIRouter(dependencies=[Depends(validar_passaporte)])

@router.get("/{empresa_id}", response_model=list[schemas.ClienteResponse])
def get_clientes(empresa_id: UUID):
    return service.listar_clientes_por_empresa(str(empresa_id))

@router.get("/{empresa_id}/{cliente_id}", response_model=schemas.ClienteResponse)
def get_cliente_por_id(empresa_id: UUID, cliente_id: UUID):
    return service.obter_cliente_por_id(str(cliente_id), str(empresa_id))

@router.post("/", response_model=schemas.ClienteResponse)
def post_cliente(cliente: schemas.ClienteCreate):
    return service.criar_novo_cliente(cliente)

@router.put("/{empresa_id}/{cliente_id}", response_model=schemas.ClienteResponse)
def put_cliente(empresa_id: UUID, cliente_id: UUID, cliente: schemas.ClienteUpdate):
    return service.atualizar_cliente(str(cliente_id), str(empresa_id), cliente)

@router.delete("/{empresa_id}/{cliente_id}")
def delete_cliente(empresa_id: UUID, cliente_id: UUID):
    return service.deletar_cliente(str(cliente_id), str(empresa_id))