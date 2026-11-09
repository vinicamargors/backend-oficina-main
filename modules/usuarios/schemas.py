from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from uuid import UUID

class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    cargo: Literal['master', 'DONO', 'MECANICO', 'ATENDENTE', 'FINANCEIRO']
    ativo: bool = True
    salario_base: Optional[float] = 0.0
    comissao_servico_pct: Optional[float] = 0.0
    comissao_peca_pct: Optional[float] = 0.0
    vale_transporte: Optional[float] = 0.0
    vale_refeicao: Optional[float] = 0.0
    paga_hora_extra: Optional[bool] = False
    valor_hora_extra: Optional[float] = 0.0
    estrelas_media: Optional[float] = 5.0
    total_avaliacoes: Optional[int] = 0

class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6)

class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    cargo: Optional[Literal['master', 'DONO', 'MECANICO', 'ATENDENTE', 'FINANCEIRO']] = None
    ativo: Optional[bool] = None
    senha: Optional[str] = Field(None, min_length=6)  # Só preenche se for trocar
    salario_base: Optional[float] = None
    comissao_servico_pct: Optional[float] = None
    comissao_peca_pct: Optional[float] = None
    vale_transporte: Optional[float] = None
    vale_refeicao: Optional[float] = None
    paga_hora_extra: Optional[bool] = None
    valor_hora_extra: Optional[float] = None
    estrelas_media: Optional[float] = None
    total_avaliacoes: Optional[int] = None

class UsuarioEquipeResponse(BaseModel):
    """Nomes e cargos da equipe, para qualquer perfil da empresa. Sem salário/comissão/vales (RH)."""
    id: UUID
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    cargo: str
    ativo: bool = True
    empresa_id: Optional[UUID] = None
    estrelas_media: Optional[float] = None
    total_avaliacoes: Optional[int] = None

class UsuarioResponse(UsuarioBase):
    id: UUID
    empresa_id: Optional[UUID] = None
