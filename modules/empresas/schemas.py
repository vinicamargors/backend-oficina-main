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
    inscricao_estadual: Optional[str] = None
    whatsapp: Optional[str] = None
    chave_pix: Optional[str] = None
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
