import os
import httpx
from fastapi import HTTPException
from core.database import supabase
from .schemas import VeiculoCreate, VeiculoUpdate

http_client = httpx.AsyncClient(timeout=5.0)

async def consultar_placa_externa(placa: str):
    token = os.getenv("WDAPIPLACAS_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="Token da API de placas não configurado no .env")

    try:
        r = await http_client.get(f"https://wdapi2.com.br/consulta/{placa}/{token}")
        if r.status_code == 200:
            dados = r.json()
            return {
                "marca": dados.get("MARCA") or dados.get("marca", ""),
                "modelo": dados.get("MODELO") or dados.get("modelo", ""),
                "cor": dados.get("cor", ""),
                "ano": dados.get("ano", ""),
                "chassi": dados.get("chassi", "")
            }
        raise HTTPException(status_code=404, detail="Placa não encontrada no mercado.")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Serviço de consulta de placas indisponível.")

def listar_veiculos(empresa_id: str, placa: str = None):
    query = supabase.table("veiculos").select("*, clientes(nome, telefone)").eq("empresa_id", empresa_id)
    if placa:
        query = query.eq("placa", placa.upper())
    return query.order("placa").execute().data

def obter_veiculo_por_id(veiculo_id: str, empresa_id: str):
    response = supabase.table("veiculos").select("*").eq("id", veiculo_id).eq("empresa_id", empresa_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")
    return response.data[0]

def criar_veiculo(dados: VeiculoCreate):
    dados.placa = dados.placa.upper().strip()
    response = supabase.table("veiculos").insert(dados.model_dump(mode='json')).execute()
    return response.data[0]

def atualizar_veiculo(veiculo_id: str, empresa_id: str, dados: VeiculoUpdate):
    if dados.placa:
        dados.placa = dados.placa.upper().strip()

    campos_alterados = dados.model_dump(exclude_unset=True, mode='json')
    if not campos_alterados:
        return obter_veiculo_por_id(veiculo_id, empresa_id)

    response = supabase.table("veiculos").update(campos_alterados).eq("id", veiculo_id).eq("empresa_id", empresa_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Veículo não encontrado.")
    return response.data[0]

def deletar_veiculo(veiculo_id: str, empresa_id: str):
    obter_veiculo_por_id(veiculo_id, empresa_id)
    supabase.table("veiculos").delete().eq("id", veiculo_id).eq("empresa_id", empresa_id).execute()
    return {"status": "sucesso", "detail": "Veículo removido com sucesso."}