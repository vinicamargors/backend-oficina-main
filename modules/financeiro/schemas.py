from pydantic import BaseModel
from typing import List, Dict

class SerieTemporalMes(BaseModel):
    mes_ano: str
    faturamento: float
    lucro: float

class FinanceiroResponse(BaseModel):
    faturamento_pago: float     # Dinheiro real no caixa (Status PAGO)
    faturamento_projetado: float # Dinheiro que vai entrar (Status EXECUCAO, FINALIZADO)
    lucro_realizado: float       # Lucro real das OS Pagas
    ticket_medio: float          # Quanto cada carro deixa em média na oficina
    historico_6_meses: List[SerieTemporalMes]

class RankingCliente(BaseModel):
    nome: str
    lucro: float
    faturamento: float
    qtd_os: int

class ProdutividadeMecanico(BaseModel):
    nome: str
    lucro_gerado: float
    faturamento_gerado: float
    qtd_os: int

class MetodoPagamento(BaseModel):
    forma: str
    qtd: int
    valor_total: float

class RentabilidadeMarca(BaseModel):
    marca: str
    lucro: float
    faturamento: float
    qtd_os: int

class InteligenciaFinanceiraResponse(BaseModel):
    top_10_clientes: List[RankingCliente]
    piores_10_clientes: List[RankingCliente]
    produtividade_mecanicos: List[ProdutividadeMecanico]
    metodos_pagamento: List[MetodoPagamento]
    rentabilidade_marcas: List[RentabilidadeMarca]
    origem_faturamento: Dict[str, float] # Peças vs Mão de Obra
    lead_time_medio_horas: float
    taxa_conversao_orcamentos: float # Em porcentagem    