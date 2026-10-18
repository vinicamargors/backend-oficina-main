from pydantic import BaseModel, Field
from typing import Optional, Literal, List, Any, Dict
from uuid import UUID
from datetime import datetime

class OSCreate(BaseModel):
    cliente_id: UUID
    veiculo_id: UUID
    mecanico_responsavel_id: Optional[UUID] = None
    descricao_problema: Optional[str] = ""
    km_atual: Optional[int] = None
    empresa_id: UUID

class OSUpdate(BaseModel):
    mecanico_responsavel_id: Optional[UUID] = None
    descricao_problema: Optional[str] = None
    km_atual: Optional[int] = None
    status: Optional[Literal['ORCAMENTO', 'AGUARDANDO_PECA', 'EXECUCAO', 'FINALIZADO', 'PAGO']] = None
    forma_pagamento: Optional[str] = None

class OSItemCreate(BaseModel):
    estoque_id: Optional[UUID] = None
    tipo: Literal['PECA', 'MAO_OBRA', 'TERCEIRIZADO']
    nome_item: str
    quantidade: int = Field(default=1, gt=0)
    custo_unitario: float = Field(default=0.0)
    venda_unitario: float = Field(default=0.0)

class OSDossieResponse(BaseModel):
    ordem: dict  # Vai conter os dados da OS + Join do Cliente, Veículo e Mecânico
    itens: List[dict] # Lista de peças e serviços
    empresa: dict # Dados da oficina (CNPJ, endereço, etc) para o cabeçalho

class OSListResponse(BaseModel):
    id: UUID
    status: str
    data_abertura: str
    total_geral: float
    descricao_problema: Optional[str] = None
    clientes: Optional[Dict[str, Any]] = None
    veiculos: Optional[Dict[str, Any]] = None

class OSPaginatedResponse(BaseModel):
    items: List[OSListResponse]
    total: int
    skip: int
    limit: int