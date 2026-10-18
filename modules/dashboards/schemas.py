from pydantic import BaseModel
from typing import List, Dict

class ItemCriticoResponse(BaseModel):
    id: str
    nome: str
    quantidade: int
    minimo_alerta: int
    categoria: str

class UltimaOSResponse(BaseModel):
    id: str
    status: str
    data_abertura: str
    total_geral: float
    clientes: Dict[str, str] # nome, telefone
    veiculos: Dict[str, str] # placa, modelo

class DashboardOperacionalResponse(BaseModel):
    total_abertas: int
    estoque_critico_count: int
    status_counts: Dict[str, int]
    ultimas_os: List[UltimaOSResponse]
    itens_criticos: List[ItemCriticoResponse]