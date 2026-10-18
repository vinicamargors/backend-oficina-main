from fastapi import HTTPException
from core.database import supabase
from .schemas import EstoqueCreate, EstoqueUpdate, EstoqueAjuste

def listar_estoque(empresa_id: str, categoria: str = None):
    query = supabase.table("estoque").select("*").eq("empresa_id", empresa_id)
    if categoria:
        query = query.eq("categoria", categoria.upper())

    itens = query.order("nome").execute().data

    estoque_baixo = 0
    valor_custo = 0.0
    valor_venda = 0.0
    for i in itens:
        qtd = i["quantidade"]
        if qtd <= i.get("minimo_alerta", 5):
            estoque_baixo += 1
        valor_custo += qtd * i["custo"]
        valor_venda += qtd * i["venda"]

    return {
        "itens": itens,
        "stats": {
            "total_itens": len(itens),
            "estoque_baixo": estoque_baixo,
            "valor_total_custo": round(valor_custo, 2),
            "valor_total_venda": round(valor_venda, 2)
        }
    }

def obter_item(item_id: str, empresa_id: str):
    response = supabase.table("estoque").select("*").eq("id", item_id).eq("empresa_id", empresa_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Item não encontrado no estoque.")
    return response.data[0]

def criar_item(dados: EstoqueCreate):
    dados.nome = dados.nome.strip()
    response = supabase.table("estoque").insert(dados.model_dump(mode='json')).execute()
    return response.data[0]

def atualizar_item(item_id: str, empresa_id: str, dados: EstoqueUpdate):
    if dados.nome:
        dados.nome = dados.nome.strip()

    campos_alterados = dados.model_dump(exclude_unset=True, mode='json')
    if not campos_alterados:
        return obter_item(item_id, empresa_id)

    response = supabase.table("estoque").update(campos_alterados).eq("id", item_id).eq("empresa_id", empresa_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Item não encontrado no estoque.")
    return response.data[0]

def deletar_item(item_id: str, empresa_id: str):
    obter_item(item_id, empresa_id)
    supabase.table("estoque").delete().eq("id", item_id).eq("empresa_id", empresa_id).execute()
    return {"status": "sucesso", "detail": "Item varrido do mapa logístico."}

def ajustar_estoque(item_id: str, empresa_id: str, ajuste: EstoqueAjuste):
    estado_anterior = obter_item(item_id, empresa_id)
    qtd_atual = estado_anterior["quantidade"]

    nova_qtd = qtd_atual + ajuste.quantidade if ajuste.tipo == "entrada" else max(0, qtd_atual - ajuste.quantidade)

    response = supabase.table("estoque").update({"quantidade": nova_qtd}).eq("id", item_id).eq("empresa_id", empresa_id).execute()
    return response.data[0]