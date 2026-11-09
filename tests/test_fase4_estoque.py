"""Fase 4 — estoque e exclusão de OS atômicos (#6). Cada teste cria o que usa e apaga no fim (só empresa A, empresa_teste=true)."""
import os
from concurrent.futures import ThreadPoolExecutor

import pytest

from tests.conftest import integracao

pytestmark = integracao


def _h(tok):
    return {"Authorization": f"Bearer {tok}"}


def _item_estoque(admin, empresa, qtd, nome):
    return admin.table("estoque").insert({"empresa_id": empresa, "nome": nome, "categoria": "PECAS", "quantidade": qtd,
                                          "minimo_alerta": 0, "custo": 1, "venda": 2}).execute().data[0]["id"]


def _saldo(admin, estoque_id):
    return admin.table("estoque").select("quantidade").eq("id", estoque_id).execute().data[0]["quantidade"]


def _os_temp(admin, a):
    return admin.table("ordens_servico").insert({"empresa_id": a["empresa"], "cliente_id": a["cliente"], "veiculo_id": a["veiculo"],
                                                 "status": "ORCAMENTO", "descricao_problema": "OS temporária F4"}).execute().data[0]["id"]


def _peca(estoque_id, qtd, nome="Peça F4"):
    return {"estoque_id": estoque_id, "tipo": "PECA", "nome_item": nome, "quantidade": qtd, "custo_unitario": 1, "venda_unitario": 2}


def _limpar(admin, os_id=None, *estoques):
    if os_id:
        admin.table("os_itens").delete().eq("os_id", os_id).execute()
        admin.table("ordens_servico").delete().eq("id", os_id).execute()
    for e in estoques:
        admin.table("estoque").delete().eq("id", e).execute()


@pytest.mark.cenario("F4-E1", "10 baixas simultâneas de 1 unidade num item com saldo 1: exatamente uma passa (200), as outras 400, saldo final 0")
def test_baixas_concorrentes(api, token, seed_ids, admin):
    a = seed_ids["a"]
    est, os_id = _item_estoque(admin, a["empresa"], 1, "Peça F4-E1"), _os_temp(admin, a)
    tok = token("DONO", "a")
    try:
        def baixar(_):
            return api.post(f"/api/v1/os/{a['empresa']}/{os_id}/itens", headers=_h(tok), json=_peca(est, 1)).status_code
        with ThreadPoolExecutor(max_workers=10) as pool:
            codigos = sorted(pool.map(baixar, range(10)))
        assert codigos == [200] + [400] * 9, codigos
        assert _saldo(admin, est) == 0
    finally:
        _limpar(admin, os_id, est)


@pytest.mark.cenario("F4-E2", "Excluir OS com itens: estoque volta, itens e OS somem e o audit_logs guarda o motivo — tudo junto")
def test_excluir_os_estorna_e_audita(api, token, seed_ids, admin):
    a = seed_ids["a"]
    est, os_id = _item_estoque(admin, a["empresa"], 5, "Peça F4-E2"), _os_temp(admin, a)
    tok = token("DONO", "a")
    try:
        assert api.post(f"/api/v1/os/{a['empresa']}/{os_id}/itens", headers=_h(tok), json=_peca(est, 3)).status_code == 200
        assert _saldo(admin, est) == 2
        r = api.delete(f"/api/v1/os/{a['empresa']}/{os_id}?motivo_exclusao=teste F4-E2", headers=_h(tok))
        assert r.status_code == 200, r.text
        assert _saldo(admin, est) == 5
        assert not admin.table("ordens_servico").select("id").eq("id", os_id).execute().data
        assert not admin.table("os_itens").select("id").eq("os_id", os_id).execute().data
        log = admin.table("audit_logs").select("dados_antes").eq("registro_id", os_id).eq("empresa_id", a["empresa"]).execute().data
        assert any((l["dados_antes"] or {}).get("motivo_exclusao") == "teste F4-E2" for l in log)
    finally:
        _limpar(admin, None, est)
        admin.table("audit_logs").delete().eq("registro_id", os_id).execute()


@pytest.mark.cenario("F4-E3", "Lote em que o 2º item não tem saldo: 400 e o 1º item NÃO fica baixado nem gravado (tudo ou nada)")
def test_lote_tudo_ou_nada(api, token, seed_ids, admin):
    a = seed_ids["a"]
    e1, e2, os_id = _item_estoque(admin, a["empresa"], 5, "Peça F4-E3a"), _item_estoque(admin, a["empresa"], 1, "Peça F4-E3b"), _os_temp(admin, a)
    try:
        r = api.post(f"/api/v1/os/{a['empresa']}/{os_id}/itens/lote", headers=_h(token("DONO", "a")),
                     json=[_peca(e1, 2, "ok"), _peca(e2, 9, "sem saldo")])
        assert r.status_code == 400 and "sem saldo" in r.json()["detail"]
        assert _saldo(admin, e1) == 5 and _saldo(admin, e2) == 1
        assert not admin.table("os_itens").select("id").eq("os_id", os_id).execute().data
    finally:
        _limpar(admin, os_id, e1, e2)


@pytest.mark.cenario("F4-E4", "Saída manual e aumento de item acima do saldo → 400 com saldo intacto; reduzir item devolve a diferença")
def test_saldo_insuficiente_e_ajuste_de_item(api, token, seed_ids, admin):
    a = seed_ids["a"]
    est, os_id = _item_estoque(admin, a["empresa"], 3, "Peça F4-E4"), _os_temp(admin, a)
    tok = token("DONO", "a")
    try:
        assert api.patch(f"/api/v1/estoque/{a['empresa']}/{est}/ajustar", headers=_h(tok), json={"tipo": "saida", "quantidade": 4}).status_code == 400
        assert _saldo(admin, est) == 3
        item = api.post(f"/api/v1/os/{a['empresa']}/{os_id}/itens", headers=_h(tok), json=_peca(est, 2)).json()
        url = f"/api/v1/os/{a['empresa']}/{os_id}/itens/{item['id']}"
        assert api.put(url, headers=_h(tok), json={"quantidade": 9}).status_code == 400
        assert _saldo(admin, est) == 1
        assert api.put(url, headers=_h(tok), json={"quantidade": 1}).status_code == 200
        assert _saldo(admin, est) == 2
        assert api.delete(url, headers=_h(tok)).status_code == 200
        assert _saldo(admin, est) == 3
    finally:
        _limpar(admin, os_id, est)


@pytest.mark.cenario("F4-E5", "Usuário logado não consegue chamar as funções de estoque direto no Supabase (só o backend)")
def test_rpc_fechada_para_logado(token, seed_ids, http, admin):
    a = seed_ids["a"]
    est = _item_estoque(admin, a["empresa"], 5, "Peça F4-E5")
    try:
        r = http.post(f"{os.environ['SUPABASE_URL']}/rest/v1/rpc/baixar_estoque",
                      headers={"apikey": os.environ["SUPABASE_ANON_KEY"], "Authorization": f"Bearer {token('DONO', 'a')}"},
                      json={"p_item": est, "p_empresa": a["empresa"], "p_qtd": 1})
        assert r.status_code in (401, 403, 404), r.text
        assert _saldo(admin, est) == 5
    finally:
        _limpar(admin, None, est)
