from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ClienteBase(BaseModel):
    nome: str
    telefone: str
    cpf_cnpj: Optional[str] = None
    endereco: Optional[str] = None
    empresa_id: UUID

class ClienteCreate(ClienteBase):
    pass

# Para o UPDATE, o usuário altera apenas o que quiser. Liberdade total.
class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    endereco: Optional[str] = None

class ClienteResponse(ClienteBase):
    id: UUID