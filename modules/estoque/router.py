from fastapi import APIRouter, Depends
from typing import Optional
from uuid import UUID
from . import schemas, service
from core.security import validar_passaporte

router = APIRouter(dependencies=[Depends(validar_passaporte)])

@router.get("/{empresa_id}", response_model=schemas.EstoqueListResponse)
def get_estoque(empresa_id: UUID, categoria: Optional[str] = None):
    return service.listar_estoque(str(empresa_id), categoria)

@router.get("/{empresa_id}/{item_id}", response_model=schemas.EstoqueResponse)
def get_item_estoque(empresa_id: UUID, item_id: UUID):
    return service.obter_item(str(item_id), str(empresa_id))

@router.post("/", response_model=schemas.EstoqueResponse)
def post_item(item: schemas.EstoqueCreate):
    return service.criar_item(item)

@router.put("/{empresa_id}/{item_id}", response_model=schemas.EstoqueResponse)
def put_item(empresa_id: UUID, item_id: UUID, item: schemas.EstoqueUpdate):
    return service.atualizar_item(str(item_id), str(empresa_id), item)

@router.patch("/{empresa_id}/{item_id}/ajustar", response_model=schemas.EstoqueResponse)
def patch_ajustar_estoque(empresa_id: UUID, item_id: UUID, ajuste: schemas.EstoqueAjuste):
    # Usamos PATCH porque estamos modificando parcialmente (só a quantidade) baseada numa ação
    return service.ajustar_estoque(str(item_id), str(empresa_id), ajuste)

@router.delete("/{empresa_id}/{item_id}")
def delete_item(empresa_id: UUID, item_id: UUID):
    return service.deletar_item(str(item_id), str(empresa_id))