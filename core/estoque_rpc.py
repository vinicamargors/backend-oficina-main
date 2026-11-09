"""Baixa/devolução de estoque atômicas (migrations/003_rpc_estoque.sql). Nunca ler-e-gravar o saldo em Python."""
from fastapi import HTTPException
from postgrest.exceptions import APIError

from core.database import supabase


def _chamar(nome: str, item_id: str, empresa_id: str, qtd: int, rotulo: str) -> int:
    try:
        return supabase.rpc(nome, {"p_item": str(item_id), "p_empresa": str(empresa_id), "p_qtd": qtd}).execute().data
    except APIError as e:
        msg = e.message or ""
        if "ESTOQUE_INSUFICIENTE" in msg:
            saldo = msg.split(":")[-1].strip()
            raise HTTPException(status_code=400, detail=f"Estoque insuficiente{rotulo}. Saldo atual: {saldo}")
        if "ESTOQUE_NAO_ENCONTRADO" in msg:
            raise HTTPException(status_code=404, detail=f"Item de estoque{rotulo} não encontrado.")
        raise


def baixar_estoque(item_id: str, empresa_id: str, qtd: int, rotulo: str = "") -> int:
    return _chamar("baixar_estoque", item_id, empresa_id, qtd, rotulo)


def devolver_estoque(item_id: str, empresa_id: str, qtd: int) -> int:
    return _chamar("devolver_estoque", item_id, empresa_id, qtd, "")
