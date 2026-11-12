from datetime import date, datetime
from fastapi import HTTPException
from core.database import supabase
from core.tempo import agora_br
from .schemas import TransacaoCreate, TransacaoUpdate, TransacaoLiquidar

def listar_transacoes(
    empresa_id: str,
    tipo: str = None,
    status: str = None,
    data_inicial: str = None,
    data_final: str = None,
):
    query = (
        supabase.table("transacoes_financeiras")
        .select("*")
        .eq("empresa_id", empresa_id)
        .order("data_vencimento", desc=True)
    )

    if tipo:
        query = query.eq("tipo", tipo.upper())
    if status:
        query = query.eq("status", status.upper())
    if data_inicial:
        query = query.gte("data_vencimento", data_inicial)
    if data_final:
        query = query.lte("data_vencimento", data_final)

    res = query.execute()
    transacoes = res.data or []

    hoje = agora_br().date().isoformat()
    total_despesas_pagas = 0.0
    total_despesas_pendentes = 0.0
    total_receitas_recebidas = 0.0
    total_receitas_pendentes = 0.0

    for t in transacoes:
        # Atualiza status dinamicamente se vencida e não liquidada
        if t.get("status") == "PENDENTE" and t.get("data_vencimento") < hoje:
            t["status"] = "ATRASADO"

        val = float(t.get("valor") or 0.0)
        tp = t.get("tipo")
        st = t.get("status")

        if tp == "DESPESA":
            if st == "LIQUIDADO":
                total_despesas_pagas += val
            elif st in ["PENDENTE", "ATRASADO"]:
                total_despesas_pendentes += val
        elif tp == "RECEITA":
            if st == "LIQUIDADO":
                total_receitas_recebidas += val
            elif st in ["PENDENTE", "ATRASADO"]:
                total_receitas_pendentes += val

    saldo = total_receitas_recebidas - total_despesas_pagas

    return {
        "transacoes": transacoes,
        "resumo": {
            "total_despesas_pagas": round(total_despesas_pagas, 2),
            "total_despesas_pendentes": round(total_despesas_pendentes, 2),
            "total_receitas_recebidas": round(total_receitas_recebidas, 2),
            "total_receitas_pendentes": round(total_receitas_pendentes, 2),
            "saldo_liquido_periodo": round(saldo, 2),
        },
    }

def criar_transacao(dados: TransacaoCreate):
    dados.descricao = dados.descricao.strip()
    payload = dados.model_dump(mode="json")
    res = supabase.table("transacoes_financeiras").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Erro ao criar transação financeira.")
    return res.data[0]

def obter_transacao(item_id: str, empresa_id: str):
    res = (
        supabase.table("transacoes_financeiras")
        .select("*")
        .eq("id", item_id)
        .eq("empresa_id", empresa_id)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=404, detail="Transação financeira não encontrada.")
    return res.data[0]

def atualizar_transacao(item_id: str, empresa_id: str, dados: TransacaoUpdate):
    obter_transacao(item_id, empresa_id)
    campos = dados.model_dump(exclude_unset=True, mode="json")
    if not campos:
        return obter_transacao(item_id, empresa_id)

    res = (
        supabase.table("transacoes_financeiras")
        .update(campos)
        .eq("id", item_id)
        .eq("empresa_id", empresa_id)
        .execute()
    )
    if not res.data:
        raise HTTPException(status_code=400, detail="Falha ao atualizar transação.")
    return res.data[0]

def liquidar_transacao(item_id: str, empresa_id: str, dados: TransacaoLiquidar):
    obter_transacao(item_id, empresa_id)
    dt_liq = (dados.data_liquidacao or agora_br().date()).isoformat()
    campos = {
        "status": "LIQUIDADO",
        "data_liquidacao": dt_liq,
        "updated_at": agora_br().isoformat(),
    }
    if dados.forma_pagamento:
        campos["forma_pagamento"] = dados.forma_pagamento

    res = (
        supabase.table("transacoes_financeiras")
        .update(campos)
        .eq("id", item_id)
        .eq("empresa_id", empresa_id)
        .execute()
    )
    return res.data[0]

def deletar_transacao(item_id: str, empresa_id: str):
    obter_transacao(item_id, empresa_id)
    supabase.table("transacoes_financeiras").delete().eq("id", item_id).eq("empresa_id", empresa_id).execute()
    return {"status": "sucesso", "detail": "Transação financeira removida com sucesso."}

