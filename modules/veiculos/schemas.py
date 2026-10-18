from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class VeiculoBase(BaseModel):
    placa: str
    modelo: str
    marca: Optional[str] = None
    cor: Optional[str] = None
    km_atual: Optional[int] = None
    ano: Optional[int] = None
    chassi: Optional[str] = None
    cliente_id: UUID
    empresa_id: UUID

class VeiculoCreate(VeiculoBase):
    pass

class VeiculoUpdate(BaseModel):
    placa: Optional[str] = None
    modelo: Optional[str] = None
    marca: Optional[str] = None
    cor: Optional[str] = None
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