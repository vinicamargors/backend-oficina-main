from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from uuid import UUID

class IdentificarRequest(BaseModel):
    telefone: str

class BuscaRequest(BaseModel):
    empresa_id: str
    termo: str

class CadastroRapidoRequest(BaseModel):
    empresa_id: str
    mecanico_id: str
    nome_cliente: str
    telefone_cliente: str
    placa: str

class CriarOSRequest(BaseModel):
    empresa_id: str
    mecanico_id: str
    cliente_id: str
    veiculo_id: str

class AtualizarOSRequest(BaseModel):
    os_id: str
    km_atual: int
    problema_relatado: Optional[str] = None

class ProcessarAudioRequest(BaseModel):
    url_audio: str # O Typebot envia um link com o ficheiro de áudio que o utilizador gravou
    os_id: str
    empresa_id: str

class ItemOS(BaseModel):
    nome_item: str = Field(description="Nome limpo do serviço ou peça")
    tipo: Literal['PECA', 'MAO_OBRA', 'TERCEIRIZADO'] = Field(description="Classifique como PECA, MAO_OBRA ou TERCEIRIZADO")
    quantidade: int = Field(description="Quantidade numérica")
    venda_unitario: float = Field(description="Valor unitário em float")

class ExtracaoOS(BaseModel):
    itens: List[ItemOS] = Field(description="Itens extraídos do áudio")
