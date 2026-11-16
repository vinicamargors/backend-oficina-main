from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from . import schemas, service
from core.security import validar_passaporte, empresa_do_usuario

router = APIRouter(dependencies=[Depends(validar_passaporte)])

@router.get("/{empresa_id}", response_model=schemas.EstoqueListResponse)
def get_estoque(empresa_id: UUID, categoria: Optional[str] = None):
    return service.listar_estoque(str(empresa_id), categoria)

# Antes de /{empresa_id}/{item_id}, senão "categorias" seria lido como id do item
@router.get("/{empresa_id}/categorias", response_model=list[str])
def get_categorias(empresa_id: UUID):
    return service.listar_categorias(str(empresa_id))

@router.post("/{empresa_id}/categorias", response_model=schemas.CategoriaResponse)
def post_categoria(empresa_id: UUID, dados: schemas.CategoriaCreate):
    return service.criar_categoria(str(empresa_id), dados.nome)

@router.delete("/{empresa_id}/categorias/{nome}")
def delete_categoria(empresa_id: UUID, nome: str):
    return service.excluir_categoria(str(empresa_id), nome)

@router.get("/{empresa_id}/paginado", response_model=schemas.EstoquePaginatedResponse)
def get_estoque_paginado(empresa_id: UUID, categoria: Optional[str] = None, busca: Optional[str] = None,
                         skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    return service.listar_estoque_paginado(str(empresa_id), categoria, busca, skip, limit)

@router.get("/{empresa_id}/{item_id}", response_model=schemas.EstoqueResponse)
def get_item_estoque(empresa_id: UUID, item_id: UUID):
    return service.obter_item(str(item_id), str(empresa_id))

@router.post("/", response_model=schemas.EstoqueResponse)
def post_item(item: schemas.EstoqueCreate, usuario: dict = Depends(validar_passaporte)):
    item.empresa_id = empresa_do_usuario(usuario, item.empresa_id)
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