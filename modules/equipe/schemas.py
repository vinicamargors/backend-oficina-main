from pydantic import BaseModel, Field
from typing import Optional, Literal
from uuid import UUID
from datetime import date, datetime

# Escalas e Folgas
TipoEscala = Literal['FERIAS', 'FOLGA', 'ATESTADO', 'PLANTAO']

class EscalaFolgaBase(BaseModel):
    usuario_id: UUID
    tipo: TipoEscala
    data_inicio: date
    data_fim: date
    observacoes: Optional[str] = None

class EscalaFolgaCreate(EscalaFolgaBase):
    pass

class EscalaFolgaResponse(EscalaFolgaBase):
    id: UUID
    empresa_id: UUID
    usuario_nome: Optional[str] = None
    created_at: Optional[datetime] = None


# Ponto Eletrônico
TipoPonto = Literal['ENTRADA', 'ALMOCO_SAIDA', 'ALMOCO_RETORNO', 'SAIDA']

class PontoEletronicoCreate(BaseModel):
    usuario_id: UUID
    tipo: TipoPonto
    data: Optional[date] = None
    hora: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PontoEletronicoResponse(BaseModel):
    id: UUID
    empresa_id: UUID
    usuario_id: UUID
    usuario_nome: Optional[str] = None
    data: date
    hora: str
    tipo: TipoPonto
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    dentro_raio: bool
    distancia_metros: Optional[float] = None
    created_at: Optional[datetime] = None


# Avaliação Pública OS (NPS & 5 Estrelas)
class AvaliacaoOSCreate(BaseModel):
    empresa_id: UUID
    os_id: UUID
    mecanico_id: Optional[UUID] = None
    cliente_nome: str
    veiculo_modelo: str
    veiculo_placa: str
    nota: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = None

class AvaliacaoOSResponse(AvaliacaoOSCreate):
    id: UUID
    mecanico_nome: Optional[str] = None
    data: Optional[date] = None
    created_at: Optional[datetime] = None


# Lançamento Automático da Folha no Contas a Pagar
class LancarFolhaInput(BaseModel):
    mes_referencia: str  # Ex: "10/2026"
    data_vencimento: Optional[date] = None
    incluir_vales: bool = True
    descricao_custom: Optional[str] = None

class LancarFolhaResponse(BaseModel):
    sucesso: bool
    total_funcionarios: int
    valor_total_folha: float
    transacao_id: UUID
    mensagem: str

