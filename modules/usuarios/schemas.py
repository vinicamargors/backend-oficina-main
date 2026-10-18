from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from uuid import UUID

class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    cargo: Literal['master', 'DONO', 'MECANICO', 'ATENDENTE', 'FINANCEIRO']
    ativo: bool = True

class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6)

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    cargo: Optional[Literal['master', 'DONO', 'MECANICO', 'ATENDENTE', 'FINANCEIRO']] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = Field(None, min_length=6) # Só preenche se for trocar

class UsuarioResponse(UsuarioBase):
    id: UUID
    empresa_id: Optional[UUID] = None