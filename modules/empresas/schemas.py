from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

class EmpresaCreate(BaseModel):
    nome_fantasia: str = Field(..., min_length=1, max_length=150)
    razao_social: Optional[str] = Field(None, max_length=150)
    cnpj: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = Field(None, max_length=255)
    telefone: Optional[str] = Field(None, max_length=30)
    endereco: Optional[str] = Field(None, max_length=300)
    plano: str = Field("basico", max_length=30)
    # Dados obrigatórios do Dono
    nome_dono: str = Field(..., min_length=1, max_length=100)  # usuarios.nome é varchar(100)
    email_dono: EmailStr = Field(..., max_length=255)
    senha_dono: str = Field(..., min_length=6, max_length=72)  # o Auth só lê até 72 bytes

class EmpresaUpdate(BaseModel):
    nome_fantasia: Optional[str] = Field(None, min_length=1, max_length=150)
    razao_social: Optional[str] = Field(None, max_length=150)
    cnpj: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = Field(None, max_length=255)
    telefone: Optional[str] = Field(None, max_length=30)
    endereco: Optional[str] = Field(None, max_length=300)
    plano: Optional[str] = Field(None, max_length=30)
    ativo: Optional[bool] = None

class ConfigUpdate(BaseModel):
    nome_exibicao: Optional[str] = Field(None, max_length=150)
    cor_primaria: Optional[str] = Field(None, max_length=20)
    cor_secundaria: Optional[str] = Field(None, max_length=20)
    logo_b64: Optional[str] = None
    inscricao_estadual: Optional[str] = Field(None, max_length=50)
    whatsapp: Optional[str] = Field(None, max_length=30)
    chave_pix: Optional[str] = Field(None, max_length=100)
    latitude_gps: Optional[float] = None
    longitude_gps: Optional[float] = None
    raio_gps_metros: Optional[int] = None
    dia_pagamento_folha: Optional[int] = None
    dia_adiantamento_folha: Optional[int] = None
    comissao_global_servico_pct: Optional[float] = None
    comissao_global_peca_pct: Optional[float] = None
    paga_hora_extra_padrao: Optional[bool] = None
    valor_hora_extra_padrao: Optional[float] = None

class ConfiguracoesResponse(ConfigUpdate):
    id: Optional[UUID] = None
    empresa_id: UUID

class EmpresaResponse(BaseModel):
    id: UUID
    nome_fantasia: str
    cnpj: Optional[str]
    ativo: bool
    plano: str
