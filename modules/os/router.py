from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from uuid import UUID
from . import schemas, service
from core.security import validar_passaporte, empresa_do_usuario

router = APIRouter(dependencies=[Depends(validar_passaporte)])

@router.post("/", response_model=dict)
def criar_ordem_servico(os: schemas.OSCreate, usuario: dict = Depends(validar_passaporte)):
    os.empresa_id = empresa_do_usuario(usuario, os.empresa_id)
    return service.criar_os(os)

@router.get("/", response_model=schemas.OSPaginatedResponse)
def listar_ordens_servico(
    empresa_id: UUID = Query(..., description="ID da empresa (Obrigatório para isolar os dados)"),
    status: Optional[str] = Query(None, description="Filtra por: ORCAMENTO, EXECUCAO, FINALIZADO, PAGO"),
    search: Optional[str] = Query(None, description="Busca rápida por placa, ID ou nome do cliente"),
    data_inicio: Optional[str] = Query(None, description="Data inicial ISO (YYYY-MM-DD)"),
    data_fim: Optional[str] = Query(None, description="Data final ISO (YYYY-MM-DD)"),
    valor_min: Optional[float] = Query(None, description="Valor mínimo da OS"),
    valor_max: Optional[float] = Query(None, description="Valor máximo da OS"),
    ordenacao: Optional[str] = Query("data_desc", description="data_desc, data_asc, valor_desc, valor_asc"),
    cliente_id: Optional[UUID] = Query(None, description="Histórico de um cliente"),
    veiculo_id: Optional[UUID] = Query(None, description="Histórico de um veículo"),
    skip: int = Query(0, description="Para paginação: quantos registros pular"),
    limit: int = Query(50, description="Limite de registros por tela")
):
    """
    Retorna a esteira de valor da oficina de forma empacotada. 
    Garante o total de registros para o frontend gerenciar a paginação.
    """
    return service.listar_os(
        empresa_id=str(empresa_id), 
        status=status, 
        search=search,
        data_inicio=data_inicio,
        data_fim=data_fim,
        valor_min=valor_min,
        valor_max=valor_max,
        ordenacao=ordenacao or "data_desc",
        skip=skip, 
        limit=limit,
        cliente_id=str(cliente_id) if cliente_id else None,
        veiculo_id=str(veiculo_id) if veiculo_id else None,
    )

@router.put("/{empresa_id}/{os_id}")
def atualizar_ordem_servico(empresa_id: UUID, os_id: UUID, os: schemas.OSUpdate):
    return service.atualizar_os(str(os_id), str(empresa_id), os)

@router.delete("/{empresa_id}/{os_id}")
def deletar_ordem_servico(
    empresa_id: UUID, 
    os_id: UUID, 
    motivo_exclusao: str = Query(..., description="Motivo obrigatório para a auditoria")
):
    return service.deletar_os(str(os_id), str(empresa_id), motivo_exclusao)

# --- Sub-rotas de Itens da OS ---
@router.post("/{empresa_id}/{os_id}/itens")
def adicionar_item_os(empresa_id: UUID, os_id: UUID, item: schemas.OSItemCreate):
    return service.adicionar_item(str(os_id), str(empresa_id), item)

@router.post("/{empresa_id}/{os_id}/itens/lote")
def adicionar_itens_lote_os(empresa_id: UUID, os_id: UUID, itens: List[schemas.OSItemCreate]):
    return service.adicionar_itens_lote(str(os_id), str(empresa_id), itens)

@router.put("/{empresa_id}/{os_id}/itens/{item_id}")
def atualizar_item_os(empresa_id: UUID, os_id: UUID, item_id: UUID, item: schemas.OSItemUpdate):
    return service.atualizar_item(str(os_id), str(item_id), str(empresa_id), item)

@router.delete("/{empresa_id}/{os_id}/itens/{item_id}")
def remover_item_os(empresa_id: UUID, os_id: UUID, item_id: UUID):
    return service.remover_item(str(os_id), str(item_id), str(empresa_id))


@router.get("/{empresa_id}/{os_id}/imprimir", response_model=schemas.OSDossieResponse)
def imprimir_os(empresa_id: UUID, os_id: UUID):
    return service.obter_dossie_impressao(str(os_id), str(empresa_id))