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
    # Quem bate o ponto é o usuário do token e data/hora são do servidor: nada disso vem do cliente.
    tipo: TipoPonto
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
class AvaliacaoPublicaCreate(BaseModel):
    """O cliente manda só o token e a opinião; empresa, mecânico, cliente e placa vêm da OS."""
    token: str
    nota: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = Field(None, max_length=1000)

class AvaliacaoPublicaInfo(BaseModel):
    veiculo_modelo: str
    veiculo_placa: str
    ja_avaliada: bool

class LinkAvaliacaoResponse(BaseModel):
    token: str
    caminho: str  # relativo à origem do app: "/?modo=avaliar&token=..."

class AvaliacaoOSResponse(BaseModel):
    id: UUID
    empresa_id: UUID
    os_id: UUID
    mecanico_id: Optional[UUID] = None
    mecanico_nome: Optional[str] = None
    cliente_nome: str
    veiculo_modelo: str
    veiculo_placa: str
    nota: int
    comentario: Optional[str] = None
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

