from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from uuid import UUID
from core.security import validar_passaporte, exigir_cargos
from . import schemas, service

router = APIRouter()

# ==========================================
# 1. ESCALAS E FOLGAS
# ==========================================
@router.get("/escalas/{empresa_id}", response_model=List[schemas.EscalaFolgaResponse], dependencies=[Depends(validar_passaporte)])
def get_escalas(empresa_id: UUID):
    return service.listar_escalas(str(empresa_id))

@router.post("/escalas/{empresa_id}", response_model=schemas.EscalaFolgaResponse, dependencies=[Depends(exigir_cargos("DONO", "master"))])
def post_escala(empresa_id: UUID, escala: schemas.EscalaFolgaCreate):
    return service.criar_escala(str(empresa_id), escala)

@router.delete("/escalas/{empresa_id}/{escala_id}", dependencies=[Depends(exigir_cargos("DONO", "master"))])
def delete_escala(empresa_id: UUID, escala_id: UUID):
    return service.deletar_escala(str(empresa_id), str(escala_id))


# ==========================================
# 2. PONTO ELETRÔNICO MOBILE COM GPS
# ==========================================
@router.get("/pontos/{empresa_id}", response_model=List[schemas.PontoEletronicoResponse], dependencies=[Depends(exigir_cargos("DONO", "FINANCEIRO", "master"))])
def get_pontos(empresa_id: UUID, data: Optional[str] = Query(None, description="YYYY-MM-DD")):
    return service.listar_pontos(str(empresa_id), data)

@router.post("/pontos/{empresa_id}", response_model=schemas.PontoEletronicoResponse)
def post_ponto(empresa_id: UUID, ponto: schemas.PontoEletronicoCreate, usuario: dict = Depends(validar_passaporte)):
    return service.registrar_ponto(str(empresa_id), usuario, ponto)


# ==========================================
# 3. AVALIAÇÃO DA OS (NPS & 5 ESTRELAS)
# ==========================================
@router.get("/avaliacoes/{empresa_id}", response_model=List[schemas.AvaliacaoOSResponse], dependencies=[Depends(exigir_cargos("DONO", "FINANCEIRO", "ATENDENTE", "master"))])
def get_avaliacoes(empresa_id: UUID):
    return service.listar_avaliacoes(str(empresa_id))

@router.get("/avaliacoes/{empresa_id}/link/{os_id}", response_model=schemas.LinkAvaliacaoResponse, dependencies=[Depends(exigir_cargos("DONO", "FINANCEIRO", "ATENDENTE", "master"))])
def get_link_avaliacao(empresa_id: UUID, os_id: UUID):
    return service.gerar_link_avaliacao(str(empresa_id), str(os_id))

# ROTAS PÚBLICAS (sem login): o cliente abre o link do WhatsApp. Tudo é derivado da OS que o token assinado aponta.
@router.get("/avaliar/{token}", response_model=schemas.AvaliacaoPublicaInfo)
def get_avaliacao_publica(token: str):
    return service.obter_info_avaliacao(token)

@router.post("/avaliar", response_model=schemas.AvaliacaoOSResponse)
def post_avaliacao_publica(avaliacao: schemas.AvaliacaoPublicaCreate):
    return service.registrar_avaliacao(avaliacao)


# ==========================================
# 4. LANÇAMENTO DA FOLHA NO CONTAS A PAGAR
# ==========================================
@router.post("/folha/{empresa_id}/lancar-contas-a-pagar", response_model=schemas.LancarFolhaResponse, dependencies=[Depends(exigir_cargos("DONO", "FINANCEIRO", "master"))])
def post_lancar_folha(empresa_id: UUID, dados: schemas.LancarFolhaInput):
    return service.lancar_folha_contas_a_pagar(str(empresa_id), dados)

