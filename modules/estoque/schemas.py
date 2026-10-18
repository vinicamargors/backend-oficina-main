from pydantic import BaseModel, Field
from typing import Optional, Literal
from uuid import UUID

class EstoqueBase(BaseModel):
    nome: str
    categoria: Literal['PECAS', 'FLUIDOS', 'PNEUS', 'ELETRICA', 'MAO_OBRA'] = 'PECAS'
    quantidade: int = Field(default=0, ge=0)
    custo: float = Field(default=0.0, ge=0.0)
    venda: float = Field(default=0.0, ge=0.0)
    minimo_alerta: int = Field(default=5, ge=0)
    codigo: Optional[str] = None
    empresa_id: UUID

class EstoqueCreate(EstoqueBase):
    pass

class EstoqueUpdate(BaseModel):
    nome: Optional[str] = None
    categoria: Optional[Literal['PECAS', 'FLUIDOS', 'PNEUS', 'ELETRICA', 'MAO_OBRA']] = None
    quantidade: Optional[int] = Field(None, ge=0)
    custo: Optional[float] = Field(None, ge=0.0)
    venda: Optional[float] = Field(None, ge=0.0)
    minimo_alerta: Optional[int] = Field(None, ge=0)
    codigo: Optional[str] = None

class EstoqueAjuste(BaseModel):
    tipo: Literal['entrada', 'saida']
    quantidade: int = Field(..., gt=0) # Tem que ser maior que zero

class EstoqueResponse(EstoqueBase):
    id: UUID

class EstoqueStats(BaseModel):
    total_itens: int
    estoque_baixo: int
    valor_total_custo: float
    valor_total_venda: float # Bônus de visão de negócio: quanto esse estoque vale no preço final

class EstoqueListResponse(BaseModel):
    itens: list[EstoqueResponse]
    stats: EstoqueStats