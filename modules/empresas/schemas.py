from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

class EmpresaCreate(BaseModel):
    nome_fantasia: str
    razao_social: Optional[str] = None
    cnpj: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    plano: str = "basico"
    # Dados obrigatórios do Dono
    nome_dono: str
    email_dono: EmailStr
    senha_dono: str = Field(..., min_length=6)

class EmpresaUpdate(BaseModel):
    nome_fantasia: Optional[str] = None
    razao_social: Optional[str] = None
    cnpj: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    plano: Optional[str] = None
    ativo: Optional[bool] = None

class ConfigUpdate(BaseModel):
    nome_exibicao: Optional[str] = None
    cor_primaria: Optional[str] = None
    cor_secundaria: Optional[str] = None
    logo_b64: Optional[str] = None

class EmpresaResponse(BaseModel):
    id: UUID
    nome_fantasia: str
    cnpj: Optional[str]
    ativo: bool
    plano: str