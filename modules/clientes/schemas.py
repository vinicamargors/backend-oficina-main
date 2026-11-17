from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class ClienteBase(BaseModel):
    nome: str = Field(..., max_length=150)
    telefone: str = Field(..., max_length=20)
    cpf_cnpj: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = None
    empresa_id: UUID

class ClienteCreate(ClienteBase):
    pass

# Para o UPDATE, o usuário altera apenas o que quiser. Liberdade total.
class ClienteUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=150)
    telefone: Optional[str] = Field(None, max_length=20)
    cpf_cnpj: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = None

class ClienteResponse(ClienteBase):
    id: UUID

class ClientePaginatedResponse(BaseModel):
    items: list[ClienteResponse]
    total: int
    skip: int
    limit: int
