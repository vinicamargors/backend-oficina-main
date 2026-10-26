from pydantic import BaseModel, Field
from typing import Optional, Literal
from uuid import UUID
from datetime import date, datetime

TipoTransacao = Literal['DESPESA', 'RECEITA']
StatusTransacao = Literal['PENDENTE', 'LIQUIDADO', 'ATRASADO', 'CANCELADO']

class TransacaoBase(BaseModel):
    tipo: TipoTransacao
    descricao: str
    categoria: str
    valor: float = Field(..., gt=0)
    data_vencimento: date
    data_liquidacao: Optional[date] = None
    status: StatusTransacao = 'PENDENTE'
    forma_pagamento: Optional[str] = None
    observacoes: Optional[str] = None
    empresa_id: UUID

class TransacaoCreate(TransacaoBase):
    pass

class TransacaoUpdate(BaseModel):
    tipo: Optional[TipoTransacao] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    valor: Optional[float] = Field(None, gt=0)
    data_vencimento: Optional[date] = None
    data_liquidacao: Optional[date] = None
    status: Optional[StatusTransacao] = None
    forma_pagamento: Optional[str] = None
    observacoes: Optional[str] = None

class TransacaoLiquidar(BaseModel):
    data_liquidacao: Optional[date] = None
    forma_pagamento: Optional[str] = None

class TransacaoResponse(TransacaoBase):
    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TransacoesResumo(BaseModel):
    total_despesas_pagas: float
    total_despesas_pendentes: float
    total_receitas_recebidas: float
    total_receitas_pendentes: float
    saldo_liquido_periodo: float

class TransacoesListResponse(BaseModel):
    transacoes: list[TransacaoResponse]
    resumo: TransacoesResumo

