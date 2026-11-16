from core.database import supabase
from .schemas import ClienteCreate, ClienteUpdate
from fastapi import HTTPException
from core.paginacao import or_ilike, pagina

def listar_clientes_por_empresa(empresa_id: str):
    return supabase.table("clientes").select("*").eq("empresa_id", empresa_id).order("nome").execute().data

def listar_clientes_paginado(empresa_id: str, busca: str = None, skip: int = 0, limit: int = 50):
    q = supabase.table("clientes").select("*", count="exact").eq("empresa_id", empresa_id)
    if busca and busca.strip():
        q = q.or_(or_ilike(("nome", busca), ("telefone", busca), ("cpf_cnpj", busca)))
    return pagina(q.order("nome").order("id"), skip, limit)

def obter_cliente_por_id(cliente_id: str, empresa_id: str):
    response = supabase.table("clientes").select("*").eq("id", cliente_id).eq("empresa_id", empresa_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Cliente não encontrado na sua jurisdição.")
    return response.data[0]

def criar_novo_cliente(dados: ClienteCreate):
    response = supabase.table("clientes").insert(dados.model_dump(mode='json')).execute()
    if not response.data:
        raise HTTPException(status_code=400, detail="Falha ao registrar propriedade do cliente.")
    return response.data[0]

def atualizar_cliente(cliente_id: str, empresa_id: str, dados: ClienteUpdate):
    campos_alterados = dados.model_dump(exclude_unset=True, mode='json')
    if not campos_alterados:
        return obter_cliente_por_id(cliente_id, empresa_id)

    response = supabase.table("clientes").update(campos_alterados).eq("id", cliente_id).eq("empresa_id", empresa_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Cliente não encontrado na sua jurisdição.")
    return response.data[0]

def deletar_cliente(cliente_id: str, empresa_id: str):
    obter_cliente_por_id(cliente_id, empresa_id)
    supabase.table("clientes").delete().eq("id", cliente_id).eq("empresa_id", empresa_id).execute()
    return {"status": "sucesso", "detail": "Cliente removido e log gerado."}