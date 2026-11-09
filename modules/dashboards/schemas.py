from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class ItemCriticoResponse(BaseModel):
    id: str
    nome: str
    quantidade: int
    minimo_alerta: Optional[int] = 5
    categoria: Optional[str] = None

class UltimaOSResponse(BaseModel):
    id: str
    status: str
    data_abertura: Optional[str] = None
    total_geral: Optional[float] = 0
    descricao_problema: Optional[str] = None
    clientes: Optional[Dict[str, Any]] = None # nome, telefone
    veiculos: Optional[Dict[str, Any]] = None # placa, modelo

class DashboardOperacionalResponse(BaseModel):
    total_abertas: int
    estoque_critico_count: int
    status_counts: Dict[str, int]
    ultimas_os: List[UltimaOSResponse]
    itens_criticos: List[ItemCriticoResponse]