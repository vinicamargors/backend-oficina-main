from fastapi import HTTPException
from core.database import supabase
from core.estoque_rpc import baixar_estoque, devolver_estoque
from core.paginacao import or_ilike, pagina
from .schemas import EstoqueCreate, EstoqueUpdate, EstoqueAjuste, normalizar_categoria

# Categorias que toda oficina começa tendo. MAO_OBRA não entra: é de serviço, não de peça (a OS filtra por ela).
CATEGORIAS_PADRAO = ["PECAS", "FLUIDOS", "PNEUS", "ELETRICA", "ACESSORIOS", "FERRAMENTAS", "DIVERSOS"]
CATEGORIA_RESERVA = "DIVERSOS"  # para onde vão os itens de uma categoria excluída
CATEGORIAS_FIXAS = {CATEGORIA_RESERVA, "MAO_OBRA"}  # DIVERSOS é o destino das exclusões; MAO_OBRA é usada pela OS


def listar_categorias(empresa_id: str) -> list[str]:
    """Categorias da oficina: as cadastradas + as que algum item já usa (ex.: MAO_OBRA, ou dados antigos)."""
    cadastradas = supabase.table("categorias_estoque").select("nome").eq("empresa_id", empresa_id).execute().data
    if not cadastradas:
        # shortcut: a primeira visita semeia o padrão; quem excluir todas as categorias volta a ver o padrão. Guardar um "já semeado" por empresa se isso incomodar.
        supabase.table("categorias_estoque").upsert(
            [{"empresa_id": empresa_id, "nome": n} for n in CATEGORIAS_PADRAO], on_conflict="empresa_id,nome", ignore_duplicates=True
        ).execute()
        cadastradas = [{"nome": n} for n in CATEGORIAS_PADRAO]
    em_uso = supabase.table("estoque").select("categoria").eq("empresa_id", empresa_id).execute().data
    nomes = {c["nome"] for c in cadastradas} | {i["categoria"] for i in em_uso if i.get("categoria")}
    return sorted(nomes, key=lambda n: (n not in CATEGORIAS_PADRAO, CATEGORIAS_PADRAO.index(n) if n in CATEGORIAS_PADRAO else 0, n))


def criar_categoria(empresa_id: str, nome: str):
    supabase.table("categorias_estoque").upsert(
        {"empresa_id": empresa_id, "nome": nome}, on_conflict="empresa_id,nome", ignore_duplicates=True
    ).execute()
    return {"nome": nome}


def excluir_categoria(empresa_id: str, nome: str):
    try:
        nome = normalizar_categoria(nome)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if nome in CATEGORIAS_FIXAS:
        raise HTTPException(status_code=400, detail="Esta categoria é usada pelo sistema e não pode ser excluída.")
    # Os itens vão para DIVERSOS antes de a categoria sair; DIVERSOS é garantida para a lista não perder o destino.
    criar_categoria(empresa_id, CATEGORIA_RESERVA)
    movidos = supabase.table("estoque").update({"categoria": CATEGORIA_RESERVA}).eq("empresa_id", empresa_id).eq("categoria", nome).execute().data
    supabase.table("categorias_estoque").delete().eq("empresa_id", empresa_id).eq("nome", nome).execute()
    return {"status": "sucesso", "itens_reclassificados": len(movidos)}

def listar_estoque_paginado(empresa_id: str, categoria: str = None, busca: str = None, skip: int = 0, limit: int = 50):
    q = supabase.table("estoque").select("*", count="exact").eq("empresa_id", empresa_id)
    if categoria:
        q = q.eq("categoria", categoria.strip().upper())
    if busca and busca.strip():
        q = q.or_(or_ilike(("nome", busca), ("codigo", busca)))
    return pagina(q.order("nome").order("id"), skip, limit)


def listar_estoque(empresa_id: str, categoria: str = None):
    query = supabase.table("estoque").select("*").eq("empresa_id", empresa_id)
    if categoria:
        query = query.eq("categoria", categoria.strip().upper())

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
    obter_item(item_id, empresa_id)  # 404 se não for da empresa
    if ajuste.tipo == "entrada":
        devolver_estoque(item_id, empresa_id, ajuste.quantidade)
    else:
        baixar_estoque(item_id, empresa_id, ajuste.quantidade)
    return obter_item(item_id, empresa_id)
