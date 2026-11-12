"""Fase 5 — avaliação pública por token assinado (#7) e ponto eletrônico sem campos forjáveis (#8).
Cada teste cria o que usa e apaga no fim (só empresa A, empresa_teste=true)."""
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
import pytest

from tests.conftest import integracao


def _h(tok):
    return {"Authorization": f"Bearer {tok}"}


# ------------------------------------------------------------------ token (sem banco)
@pytest.mark.cenario("F5-T", "Token de avaliação: assinatura válida volta o os_id; adulterado, de outra OS, truncado ou lixo → None")
def test_token_assinado():
    from uuid import uuid4
    from core.avaliacao_token import gerar_token, ler_token

    os_id, outra = str(uuid4()), str(uuid4())
    tok = gerar_token(os_id)
    assert ler_token(tok) == os_id
    assert ler_token(tok[:-2] + ("AA" if not tok.endswith("AA") else "BB")) is None   # assinatura alterada
    assert ler_token(tok.replace(os_id, outra)) is None                               # trocou a OS, mantendo a assinatura
    for lixo in ("", "abc", "a.b.c", os_id, "." + tok.split(".")[-1]):
        assert ler_token(lixo) is None


# ------------------------------------------------------------------ avaliação (integração)
def _os_finalizada(admin, a, status="FINALIZADO"):
    return admin.table("ordens_servico").insert({
        "empresa_id": a["empresa"], "cliente_id": a["cliente"], "veiculo_id": a["veiculo"],
        "mecanico_responsavel_id": a["MECANICO"], "status": status, "descricao_problema": "OS temporária F5",
    }).execute().data[0]["id"]


def _limpar_os(admin, os_id):
    admin.table("avaliacoes_os").delete().eq("os_id", os_id).execute()
    admin.table("ordens_servico").delete().eq("id", os_id).execute()


@integracao
@pytest.mark.cenario("F7", "Link com token válido: avalia (empresa, mecânico, cliente e placa vêm da OS); segunda avaliação da mesma OS → 409; média do mecânico atualizada")
def test_avaliar_uma_vez(api, token, seed_ids, admin):
    a = seed_ids["a"]
    os_id = _os_finalizada(admin, a)
    try:
        r = api.get(f"/api/v1/equipe/avaliacoes/{a['empresa']}/link/{os_id}", headers=_h(token("DONO", "a")))
        assert r.status_code == 200, r.text
        tok = r.json()["token"]
        assert r.json()["caminho"] == f"/?modo=avaliar&token={tok}"

        info = api.get(f"/api/v1/equipe/avaliar/{tok}")           # página pública abre sem login
        assert info.status_code == 200 and info.json()["ja_avaliada"] is False
        assert info.json()["veiculo_placa"] == "TSTA001"

        # campos que o cliente tentaria forjar são ignorados
        r1 = api.post("/api/v1/equipe/avaliar", json={
            "token": tok, "nota": 4, "comentario": "Rápido e honesto",
            "empresa_id": seed_ids["b"]["empresa"], "mecanico_id": seed_ids["b"]["MECANICO"], "veiculo_placa": "FORJADA"})
        assert r1.status_code == 200, r1.text
        gravada = admin.table("avaliacoes_os").select("*").eq("os_id", os_id).execute().data
        assert len(gravada) == 1
        assert gravada[0]["empresa_id"] == a["empresa"] and gravada[0]["mecanico_id"] == a["MECANICO"]
        assert gravada[0]["veiculo_placa"] == "TSTA001" and gravada[0]["nota"] == 4
        assert admin.table("usuarios").select("total_avaliacoes").eq("id", a["MECANICO"]).execute().data[0]["total_avaliacoes"] >= 1

        r2 = api.post("/api/v1/equipe/avaliar", json={"token": tok, "nota": 1})
        assert r2.status_code == 409 and "já" in r2.json()["detail"].lower()
        assert api.get(f"/api/v1/equipe/avaliar/{tok}").json()["ja_avaliada"] is True
        assert len(admin.table("avaliacoes_os").select("id").eq("os_id", os_id).execute().data) == 1
    finally:
        _limpar_os(admin, os_id)


@integracao
@pytest.mark.cenario("F8", "Token adulterado, sem token ou de OS inexistente: erro e nada gravado")
def test_token_invalido_nao_grava(api, admin, seed_ids):
    from uuid import uuid4
    from core.avaliacao_token import gerar_token

    antes = len(admin.table("avaliacoes_os").select("id").execute().data)
    assert api.post("/api/v1/equipe/avaliar", json={"token": "adulterado.123", "nota": 5}).status_code == 404
    assert api.post("/api/v1/equipe/avaliar", json={"nota": 5}).status_code == 422
    assert api.post("/api/v1/equipe/avaliar", json={"token": gerar_token(str(uuid4())), "nota": 5}).status_code == 404  # assinatura boa, OS não existe
    assert api.post("/api/v1/equipe/avaliar", json={"token": gerar_token(seed_ids["a"]["os"]), "nota": 9}).status_code == 422
    assert api.get("/api/v1/equipe/avaliar/adulterado.123").status_code == 404
    assert len(admin.table("avaliacoes_os").select("id").execute().data) == antes


@integracao
@pytest.mark.cenario("F5-L", "Gerar link: só OS finalizada/paga e só da própria empresa; mecânico não gera")
def test_gerar_link_regras(api, token, seed_ids, admin):
    a, b = seed_ids["a"], seed_ids["b"]
    os_aberta = _os_finalizada(admin, a, status="EXECUCAO")
    os_paga = _os_finalizada(admin, a, status="PAGO")
    try:
        dono = _h(token("DONO", "a"))
        assert api.get(f"/api/v1/equipe/avaliacoes/{a['empresa']}/link/{os_aberta}", headers=dono).status_code == 400
        assert api.get(f"/api/v1/equipe/avaliacoes/{a['empresa']}/link/{os_paga}", headers=dono).status_code == 200
        assert api.get(f"/api/v1/equipe/avaliacoes/{b['empresa']}/link/{b['os']}", headers=dono).status_code == 403   # outra empresa
        assert api.get(f"/api/v1/equipe/avaliacoes/{a['empresa']}/link/{b['os']}", headers=dono).status_code == 404   # OS alheia na rota própria
        assert api.get(f"/api/v1/equipe/avaliacoes/{a['empresa']}/link/{os_paga}", headers=_h(token("MECANICO", "a"))).status_code == 403
    finally:
        _limpar_os(admin, os_aberta)
        _limpar_os(admin, os_paga)


@integracao
@pytest.mark.cenario("F5-R", "Chave anon não insere em avaliacoes_os direto pelo Supabase (policy pública removida)")
def test_anon_nao_insere_avaliacao(seed_ids):
    a = seed_ids["a"]
    r = httpx.post(os.environ["SUPABASE_URL"] + "/rest/v1/avaliacoes_os",
                   headers={"apikey": os.environ["SUPABASE_ANON_KEY"], "Content-Type": "application/json"},
                   json={"empresa_id": a["empresa"], "os_id": a["os"], "cliente_nome": "x", "veiculo_modelo": "x", "veiculo_placa": "x", "nota": 5})
    assert r.status_code in (401, 403), r.text


# ------------------------------------------------------------------ ponto
@integracao
@pytest.mark.cenario("F5-P", "Ponto ignora usuario_id/data/hora enviados: grava o usuário do token, a data e a hora do servidor (America/Sao_Paulo)")
def test_ponto_so_do_servidor(api, token, seed_ids, admin):
    a = seed_ids["a"]
    ponto_id = None
    try:
        antes = datetime.now(ZoneInfo("America/Sao_Paulo"))
        r = api.post(f"/api/v1/equipe/pontos/{a['empresa']}", headers=_h(token("MECANICO", "a")), json={
            "tipo": "ENTRADA", "usuario_id": a["DONO"], "data": "2020-01-01", "hora": "03:00:00"})
        depois = datetime.now(ZoneInfo("America/Sao_Paulo"))
        assert r.status_code == 200, r.text
        ponto_id = r.json()["id"]
        assert r.json()["usuario_id"] == a["MECANICO"]
        assert r.json()["data"] in {str(antes.date()), str(depois.date())}
        hora = datetime.strptime(r.json()["hora"][:8], "%H:%M:%S").time()
        assert antes.time().replace(microsecond=0) <= hora <= depois.time()
    finally:
        if ponto_id:
            admin.table("pontos_eletronicos").delete().eq("id", ponto_id).execute()
