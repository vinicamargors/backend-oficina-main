from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class VeiculoBase(BaseModel):
    placa: str = Field(..., max_length=10)
    modelo: str = Field(..., max_length=100)
    marca: Optional[str] = Field(None, max_length=50)
    cor: Optional[str] = Field(None, max_length=30)
    km_atual: Optional[int] = None
    ano: Optional[int] = None
    chassi: Optional[str] = None
    cliente_id: UUID
    empresa_id: UUID

class VeiculoCreate(VeiculoBase):
    pass

class VeiculoUpdate(BaseModel):
    placa: Optional[str] = Field(None, max_length=10)
    modelo: Optional[str] = Field(None, max_length=100)
    marca: Optional[str] = Field(None, max_length=50)
    cor: Optional[str] = Field(None, max_length=30)
    km_atual: Optional[int] = None
    ano: Optional[int] = None
    chassi: Optional[str] = None
    cliente_id: Optional[UUID] = None

class ClienteResumo(BaseModel):
    nome: str
    telefone: str

class VeiculoResponse(VeiculoBase):
    id: UUID
    # O Supabase devolve o Join como um dicionário. O Pydantic mastiga pra gente.
    clientes: Optional[ClienteResumo] = None

class VeiculoPaginatedResponse(BaseModel):
    items: list[VeiculoResponse]
    total: int
    skip: int
    limit: int
