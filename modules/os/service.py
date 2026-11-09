from fastapi import HTTPException
from core.database import supabase
from core.security import garantir_da_empresa
from datetime import datetime, timezone, timedelta
from typing import List
from .schemas import OSCreate, OSUpdate, OSItemCreate, OSItemUpdate


def listar_os(
    empresa_id: str,
    status: str = None,
    search: str = None,
    data_inicio: str = None,
    data_fim: str = None,
    valor_min: float = None,
    valor_max: float = None,
    ordenacao: str = "data_desc",
    skip: int = 0,
    limit: int = 50,
    cliente_id: str = None,
    veiculo_id: str = None,
):
    """O Radar do Pátio: Puxa as OS com paginação pesada e auditoria de volume total."""
    query = supabase.table("ordens_servico").select(
        "id, cliente_id, veiculo_id, km_atual, status, data_abertura, total_geral, descricao_problema, clientes(nome, telefone), veiculos(placa, modelo)",
        count="exact"
    ).eq("empresa_id", empresa_id)

    if status:
        query = query.eq("status", status.upper())
    if cliente_id:
        query = query.eq("cliente_id", cliente_id)
    if veiculo_id:
        query = query.eq("veiculo_id", veiculo_id)
    if data_inicio:
        query = query.gte("data_abertura", f"{data_inicio}T00:00:00")
    if data_fim:
        query = query.lte("data_abertura", f"{data_fim}T23:59:59")
    if valor_min is not None:
        query = query.gte("total_geral", valor_min)
    if valor_max is not None:
        query = query.lte("total_geral", valor_max)

    if ordenacao == "data_asc":
        query = query.order("data_abertura", desc=False)
    elif ordenacao == "valor_desc":
        query = query.order("total_geral", desc=True)
    elif ordenacao == "valor_asc":
        query = query.order("total_geral", desc=False)
    else:
        query = query.order("data_abertura", desc=True)

    # 1. MODO BUSCA ATIVADA (Mantido em memória — Armadilha #4: PostgREST não aceita .or_() em joins)
    if search:
        response = query.limit(5000).execute()
        todas_os = response.data
        termo = search.lower()
        termo_alfanum = "".join(c for c in termo if c.isalnum())
        filtradas = []

        for os in todas_os:
            clientes = os.get("clientes") or {}
            veiculos = os.get("veiculos") or {}

            cli_nome = str(clientes.get("nome", "")).lower()
            vei_placa = str(veiculos.get("placa", "")).lower()
            vei_placa_limpa = "".join(c for c in vei_placa if c.isalnum())
            vei_modelo = str(veiculos.get("modelo", "")).lower()
            os_id = str(os.get("id", "")).lower()
            desc = str(os.get("descricao_problema") or "").lower()

            if (termo in cli_nome or termo in vei_placa or termo in vei_modelo or termo in os_id or termo in desc
                    or (len(termo_alfanum) >= 2 and termo_alfanum in vei_placa_limpa)):
                filtradas.append(os)

        return {
            "items": filtradas[skip : skip + limit],
            "total": len(filtradas),
            "skip": skip,
            "limit": limit
        }

    # 2. MODO LISTAGEM PADRÃO
    response = query.range(skip, skip + limit - 1).execute()
    return {
        "items": response.data,
        "total": response.count or 0,
        "skip": skip,
        "limit": limit
    }

def recalcular_totais_os(os_id: str):
    """Mão invisível que ajusta o faturamento da OS automaticamente"""
    itens = supabase.table("os_itens").select("*").eq("os_id", os_id).execute().data

    total_pecas = sum(i["quantidade"] * i["venda_unitario"] for i in itens if i["tipo"] in ["PECA", "TERCEIRIZADO"])
    total_mao_obra = sum(i["quantidade"] * i["venda_unitario"] for i in itens if i["tipo"] == "MAO_OBRA")
    custo_total = sum(i["quantidade"] * i["custo_unitario"] for i in itens if i["tipo"] != "MAO_OBRA")

    venda_total = total_pecas + total_mao_obra
    lucro = venda_total - custo_total

    supabase.table("ordens_servico").update({
        "total_pecas": total_pecas,
        "total_mao_obra": total_mao_obra,
        "total_geral": venda_total,
        "lucro_estimado": lucro
    }).eq("id", os_id).execute()

def _sincronizar_km_veiculo(veiculo_id: str, empresa_id: str, km_novo: int):
    if not km_novo:
        return
    veiculo_res = supabase.table("veiculos").select("km_atual").eq("id", str(veiculo_id)).eq("empresa_id", str(empresa_id)).execute().data
    if veiculo_res and (not veiculo_res[0].get("km_atual") or km_novo > veiculo_res[0]["km_atual"]):
        supabase.table("veiculos").update({"km_atual": km_novo}).eq("id", str(veiculo_id)).eq("empresa_id", str(empresa_id)).execute()

def criar_os(dados: OSCreate):
    empresa_id = str(dados.empresa_id)
    garantir_da_empresa("clientes", dados.cliente_id, empresa_id, "Cliente")
    garantir_da_empresa("veiculos", dados.veiculo_id, empresa_id, "Veículo")
    garantir_da_empresa("usuarios", dados.mecanico_responsavel_id, empresa_id, "Mecânico")
    os_aberta = supabase.table("ordens_servico").select("id, data_abertura, status").eq("veiculo_id", str(dados.veiculo_id)).eq("status", "ORCAMENTO").eq("empresa_id", str(dados.empresa_id)).order("data_abertura", desc=True).execute()
    if os_aberta.data:
        orc_recente = os_aberta.data[0]
        abertura_str = orc_recente.get("data_abertura")
        if abertura_str:
            try:
                abertura_dt = datetime.fromisoformat(str(abertura_str).replace("Z", "+00:00"))
                agora = datetime.now(abertura_dt.tzinfo or timezone.utc)
                if (agora - abertura_dt) < timedelta(days=90):
                    return {**orc_recente, "reaproveitada": True}
            except ValueError:
                pass

    _sincronizar_km_veiculo(str(dados.veiculo_id), str(dados.empresa_id), dados.km_atual)

    response = supabase.table("ordens_servico").insert(dados.model_dump(mode='json')).execute()
    return response.data[0]

def atualizar_os(os_id: str, empresa_id: str, dados: OSUpdate):
    os_res = supabase.table("ordens_servico").select("*").eq("id", os_id).eq("empresa_id", empresa_id).execute().data
    if not os_res:
        raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada.")
    os_atual = os_res[0]

    campos = dados.model_dump(exclude_unset=True, mode='json')
    if not campos:
        return os_atual
    garantir_da_empresa("usuarios", campos.get("mecanico_responsavel_id"), empresa_id, "Mecânico")

    if campos.get("km_atual"):
        _sincronizar_km_veiculo(str(os_atual["veiculo_id"]), empresa_id, campos["km_atual"])

    if campos.get("status") in ["FINALIZADO", "PAGO"] and not os_atual.get("data_fechamento"):
        campos["data_fechamento"] = datetime.now().isoformat()

    response = supabase.table("ordens_servico").update(campos).eq("id", os_id).eq("empresa_id", empresa_id).execute()
    return response.data[0]

def _garantir_os_da_empresa(os_id: str, empresa_id: str):
    garantir_da_empresa("ordens_servico", os_id, empresa_id, "Ordem de Serviço")

def adicionar_item(os_id: str, empresa_id: str, item: OSItemCreate):
    _garantir_os_da_empresa(os_id, empresa_id)
    if item.estoque_id:
        estoque_res = supabase.table("estoque").select("*").eq("id", str(item.estoque_id)).eq("empresa_id", empresa_id).execute().data
        if not estoque_res:
            raise HTTPException(status_code=404, detail="Item de estoque não encontrado.")
        estoque = estoque_res[0]
        if estoque["quantidade"] < item.quantidade:
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente. Saldo atual: {estoque['quantidade']}")

        supabase.table("estoque").update({"quantidade": estoque["quantidade"] - item.quantidade}).eq("id", str(item.estoque_id)).eq("empresa_id", empresa_id).execute()

    dados_item = item.model_dump(mode='json')
    dados_item.update({"os_id": os_id, "empresa_id": empresa_id})

    response = supabase.table("os_itens").insert(dados_item).execute()
    recalcular_totais_os(os_id)
    return response.data[0]

def adicionar_itens_lote(os_id: str, empresa_id: str, itens: List[OSItemCreate]):
    if not itens:
        return []
    _garantir_os_da_empresa(os_id, empresa_id)
    inseridos = []
    for item in itens:
        if item.estoque_id:
            estoque_res = supabase.table("estoque").select("*").eq("id", str(item.estoque_id)).eq("empresa_id", empresa_id).execute().data
            if not estoque_res:
                raise HTTPException(status_code=404, detail=f"Item de estoque '{item.nome_item}' não encontrado.")
            estoque = estoque_res[0]
            if estoque["quantidade"] < item.quantidade:
                raise HTTPException(status_code=400, detail=f"Estoque insuficiente para '{item.nome_item}'. Saldo atual: {estoque['quantidade']}")
            supabase.table("estoque").update({"quantidade": estoque["quantidade"] - item.quantidade}).eq("id", str(item.estoque_id)).eq("empresa_id", empresa_id).execute()

        dados_item = item.model_dump(mode='json')
        dados_item.update({"os_id": os_id, "empresa_id": empresa_id})
        inseridos.append(dados_item)

    response = supabase.table("os_itens").insert(inseridos).execute()
    recalcular_totais_os(os_id)
    return response.data

def atualizar_item(os_id: str, item_id: str, empresa_id: str, dados: OSItemUpdate):
    # O dono do item é a OS: itens antigos do legado não têm empresa_id preenchido.
    _garantir_os_da_empresa(os_id, empresa_id)
    item_res = supabase.table("os_itens").select("*").eq("id", item_id).eq("os_id", os_id).execute().data
    if not item_res:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    item_atual = item_res[0]

    campos = dados.model_dump(exclude_unset=True, mode='json')
    if not campos:
        return item_atual

    if "quantidade" in campos and item_atual.get("estoque_id"):
        diff_qtd = campos["quantidade"] - item_atual["quantidade"]
        if diff_qtd != 0:
            est_res = supabase.table("estoque").select("quantidade").eq("id", item_atual["estoque_id"]).eq("empresa_id", empresa_id).execute().data
            if est_res:
                saldo_atual = est_res[0]["quantidade"]
                if diff_qtd > 0 and saldo_atual < diff_qtd:
                    raise HTTPException(status_code=400, detail=f"Estoque insuficiente. Saldo atual: {saldo_atual}")
                supabase.table("estoque").update({"quantidade": saldo_atual - diff_qtd}).eq("id", item_atual["estoque_id"]).eq("empresa_id", empresa_id).execute()

    response = supabase.table("os_itens").update(campos).eq("id", item_id).eq("os_id", os_id).execute()
    recalcular_totais_os(os_id)
    return response.data[0]

def remover_item(os_id: str, item_id: str, empresa_id: str):
    _garantir_os_da_empresa(os_id, empresa_id)
    item_res = supabase.table("os_itens").select("*").eq("id", item_id).eq("os_id", os_id).execute().data
    if not item_res:
        raise HTTPException(status_code=404, detail="Item não encontrado.")
    item = item_res[0]

    if item.get("estoque_id"):
        est_res = supabase.table("estoque").select("quantidade").eq("id", item["estoque_id"]).eq("empresa_id", empresa_id).execute().data
        if est_res:
            supabase.table("estoque").update({"quantidade": est_res[0]["quantidade"] + item["quantidade"]}).eq("id", item["estoque_id"]).eq("empresa_id", empresa_id).execute()

    supabase.table("os_itens").delete().eq("id", item_id).eq("os_id", os_id).execute()
    recalcular_totais_os(os_id)
    return {"status": "sucesso", "detail": "Item removido e estornado (se aplicável)."}

def deletar_os(os_id: str, empresa_id: str, motivo_exclusao: str):
    os_res = supabase.table("ordens_servico").select("*").eq("id", os_id).eq("empresa_id", empresa_id).execute().data
    if not os_res:
        raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada.")
    os_atual = os_res[0]

    # Devolve as peças pro estoque e apaga os itens direto sem recalcular totais da OS que vai morrer (Achado #6)
    itens = supabase.table("os_itens").select("id, estoque_id, quantidade").eq("os_id", os_id).execute().data
    for item in itens:
        if item.get("estoque_id"):
            est_res = supabase.table("estoque").select("quantidade").eq("id", item["estoque_id"]).eq("empresa_id", empresa_id).execute().data
            if est_res:
                supabase.table("estoque").update({"quantidade": est_res[0]["quantidade"] + item["quantidade"]}).eq("id", item["estoque_id"]).eq("empresa_id", empresa_id).execute()

    supabase.table("os_itens").delete().eq("os_id", os_id).execute()

    # Armadilha #3: Mantém insert explícito na audit_logs com motivo_exclusao
    os_atual["motivo_exclusao"] = motivo_exclusao
    supabase.table("ordens_servico").delete().eq("id", os_id).eq("empresa_id", empresa_id).execute()
    supabase.table("audit_logs").insert({
        "tabela": "ordens_servico",
        "operacao": "DELETE",
        "registro_id": str(os_id),
        "empresa_id": str(empresa_id),
        "dados_antes": os_atual,
        "dados_depois": None
    }).execute()

    return {"status": "sucesso", "detail": "OS cancelada, estoque restaurado e log gerado."}

def obter_dossie_impressao(os_id: str, empresa_id: str):
    response_os = supabase.table("ordens_servico").select(
        "*, clientes(nome, telefone, cpf_cnpj, endereco), veiculos(placa, modelo, marca, cor, ano, chassi, km_atual), usuarios(nome)"
    ).eq("id", os_id).eq("empresa_id", empresa_id).execute()

    if not response_os.data:
        raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada.")

    itens = supabase.table("os_itens").select("*").eq("os_id", os_id).execute().data
    empresa = supabase.table("empresas").select(
        "nome_fantasia, razao_social, cnpj, telefone, email, endereco"
    ).eq("id", empresa_id).execute().data

    return {
        "ordem": response_os.data[0],
        "itens": itens,
        "empresa": empresa[0] if empresa else {}
    }