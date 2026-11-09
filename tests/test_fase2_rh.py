"""Fase 2 (#4) — RH fora da API: ninguém lê/grava salário direto no Supabase; só via backend com DONO/master."""
import os

import pytest

from tests.conftest import integracao

pytestmark = integracao


def _rest(http, tok, metodo, caminho, **kw):
    """Chama o PostgREST como o navegador faria: chave anon + JWT do usuário."""
    url = f"{os.environ['SUPABASE_URL']}/rest/v1/{caminho}"
    headers = {"apikey": os.environ["SUPABASE_ANON_KEY"], "Authorization": f"Bearer {tok}", **kw.pop("headers", {})}
    return http.request(metodo, url, headers=headers, **kw)


def _h(tok):
    return {"Authorization": f"Bearer {tok}"}


@pytest.mark.cenario("F2.1", "Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado")
@pytest.mark.parametrize("cargo", ["MECANICO", "DONO"])
@pytest.mark.parametrize("coluna", ["salario_base", "comissao_servico_pct", "vale_transporte", "senha_hash"])
def test_rh_nao_sai_pela_api_rest(http, token, cargo, coluna):
    r = _rest(http, token(cargo, "a"), "GET", f"usuarios?select={coluna}")
    assert r.status_code in (401, 403)
    assert "permission denied" in r.text


@pytest.mark.cenario("F2.2", "MECÂNICO continua lendo nome/cargo da equipe da própria oficina (e não da outra)")
def test_mecanico_le_nomes_da_equipe(http, token, seed_ids):
    r = _rest(http, token("MECANICO", "a"), "GET", "usuarios?select=id,nome,cargo,empresa_id")
    assert r.status_code == 200
    empresas = {u["empresa_id"] for u in r.json()}
    assert empresas == {seed_ids["a"]["empresa"]}
    assert {"DONO", "MECANICO"} <= {u["cargo"] for u in r.json()}


@pytest.mark.cenario("F2.3", "DONO tenta gravar salário direto no Supabase → negado; valor no banco inalterado")
def test_dono_nao_grava_rh_direto(http, token, seed_ids, admin):
    mec = seed_ids["a"]["MECANICO"]
    antes = admin.table("usuarios").select("salario_base").eq("id", mec).execute().data[0]["salario_base"]
    r = _rest(http, token("DONO", "a"), "PATCH", f"usuarios?id=eq.{mec}", json={"salario_base": 99999})
    assert r.status_code in (401, 403)
    assert admin.table("usuarios").select("salario_base").eq("id", mec).execute().data[0]["salario_base"] == antes


@pytest.mark.cenario("F2.4", "Backend: DONO lista equipe com RH (200); MECÂNICO e FINANCEIRO → 403")
def test_rh_pelo_backend_so_para_dono(api, token, seed_ids):
    emp = seed_ids["a"]["empresa"]
    r = api.get(f"/api/v1/usuarios/{emp}", headers=_h(token("DONO", "a")))
    assert r.status_code == 200 and all("salario_base" in u for u in r.json())
    assert api.get(f"/api/v1/usuarios/{emp}", headers=_h(token("MECANICO", "a"))).status_code == 403
    assert api.get(f"/api/v1/usuarios/{emp}", headers=_h(token("FINANCEIRO", "a"))).status_code == 403


@pytest.mark.cenario("F2.5", "Backend: DONO altera salário do mecânico (200) e o valor é gravado no banco")
def test_dono_altera_rh_pelo_backend(api, token, seed_ids, admin):
    emp, mec = seed_ids["a"]["empresa"], seed_ids["a"]["MECANICO"]
    antes = admin.table("usuarios").select("salario_base").eq("id", mec).execute().data[0]["salario_base"]
    try:
        r = api.put(f"/api/v1/usuarios/{emp}/{mec}", headers=_h(token("DONO", "a")), json={"salario_base": 2345.67})
        assert r.status_code == 200
        assert float(admin.table("usuarios").select("salario_base").eq("id", mec).execute().data[0]["salario_base"]) == 2345.67
    finally:
        admin.table("usuarios").update({"salario_base": antes}).eq("id", mec).execute()
