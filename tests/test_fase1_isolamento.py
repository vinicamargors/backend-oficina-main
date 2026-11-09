"""Fase 1 — isolamento multi-tenant (#1, #10) com login real nas empresas de homologação.

Tudo que um teste cria é apagado no fim, e só nas empresas A/B (empresa_teste = true).
"""
import pytest

from tests.conftest import integracao

pytestmark = integracao


def _h(tok):
    return {"Authorization": f"Bearer {tok}"}


@pytest.mark.cenario("T1-R", "DONO A pede, pela rota da própria empresa, um cliente que é da Oficina B → 404")
def test_recurso_de_outra_empresa_pela_rota_propria(api, token, seed_ids):
    a, b = seed_ids["a"], seed_ids["b"]
    r = api.get(f"/api/v1/clientes/{a['empresa']}/{b['cliente']}", headers=_h(token("DONO", "a")))
    assert r.status_code == 404


@pytest.mark.cenario("F1.2", "POST de cliente com empresa_id da Oficina B no body grava na Oficina A (empresa do token)")
def test_post_cliente_grava_na_empresa_do_token(api, token, seed_ids, admin):
    a, b = seed_ids["a"], seed_ids["b"]
    r = api.post("/api/v1/clientes/", headers=_h(token("DONO", "a")),
                 json={"nome": "Cliente F1.2 (temporário)", "telefone": "11900000012", "empresa_id": b["empresa"]})
    try:
        assert r.status_code == 200
        assert r.json()["empresa_id"] == a["empresa"]
    finally:
        if r.status_code == 200:
            admin.table("clientes").delete().eq("id", r.json()["id"]).execute()


@pytest.mark.cenario("F1.3", "DONO A adiciona item numa OS da Oficina B → 404 (pela rota de A) e 403 (pela rota de B)")
def test_item_em_os_de_outra_empresa(api, token, seed_ids):
    a, b = seed_ids["a"], seed_ids["b"]
    item = {"tipo": "MAO_OBRA", "nome_item": "Invasão F1.3", "quantidade": 1, "venda_unitario": 1}
    tok = token("DONO", "a")
    assert api.post(f"/api/v1/os/{a['empresa']}/{b['os']}/itens", headers=_h(tok), json=item).status_code == 404
    assert api.post(f"/api/v1/os/{b['empresa']}/{b['os']}/itens", headers=_h(tok), json=item).status_code == 403
    assert api.post(f"/api/v1/os/{a['empresa']}/{b['os']}/itens/lote", headers=_h(tok), json=[item]).status_code == 404


@pytest.mark.cenario("F1.3b", "DONO A tenta alterar/remover item de OS da Oficina B → 404; item e estoque de B intactos")
def test_alterar_item_de_outra_empresa(api, token, seed_ids, admin):
    a, b = seed_ids["a"], seed_ids["b"]
    tok_b, tok_a = token("DONO", "b"), token("DONO", "a")
    estoque_antes = admin.table("estoque").select("quantidade").eq("id", b["estoque"]).execute().data[0]["quantidade"]
    criado = api.post(f"/api/v1/os/{b['empresa']}/{b['os']}/itens", headers=_h(tok_b),
                      json={"estoque_id": b["estoque"], "tipo": "PECA", "nome_item": "Item F1.3b", "quantidade": 1,
                            "custo_unitario": 20, "venda_unitario": 45})
    assert criado.status_code == 200
    item_id = criado.json()["id"]
    try:
        url_a = f"/api/v1/os/{a['empresa']}/{b['os']}/itens/{item_id}"
        assert api.put(url_a, headers=_h(tok_a), json={"quantidade": 9}).status_code == 404
        assert api.delete(url_a, headers=_h(tok_a)).status_code == 404
        intacto = admin.table("os_itens").select("quantidade").eq("id", item_id).execute().data
        assert intacto and intacto[0]["quantidade"] == 1
    finally:
        api.delete(f"/api/v1/os/{b['empresa']}/{b['os']}/itens/{item_id}", headers=_h(tok_b))
    estoque_depois = admin.table("estoque").select("quantidade").eq("id", b["estoque"]).execute().data[0]["quantidade"]
    assert estoque_depois == estoque_antes


@pytest.mark.cenario("F1.5", "DONO A abre OS com veículo/cliente/mecânico da Oficina B → 404")
@pytest.mark.parametrize("campo", ["veiculo", "cliente", "mecanico"])
def test_criar_os_com_vinculo_de_outra_empresa(api, token, seed_ids, campo):
    a, b = seed_ids["a"], seed_ids["b"]
    corpo = {"empresa_id": a["empresa"], "cliente_id": a["cliente"], "veiculo_id": a["veiculo"],
             "mecanico_responsavel_id": a["MECANICO"]}
    chave = {"veiculo": "veiculo_id", "cliente": "cliente_id", "mecanico": "mecanico_responsavel_id"}[campo]
    corpo[chave] = b["MECANICO" if campo == "mecanico" else campo]
    r = api.post("/api/v1/os/", headers=_h(token("DONO", "a")), json=corpo)
    assert r.status_code == 404


@pytest.mark.cenario("F1.5b", "DONO A cadastra veículo apontando para cliente da Oficina B → 404")
def test_veiculo_com_cliente_de_outra_empresa(api, token, seed_ids, admin):
    a, b = seed_ids["a"], seed_ids["b"]
    r = api.post("/api/v1/veiculos/", headers=_h(token("DONO", "a")),
                 json={"placa": "TSTF1X5", "modelo": "Invasão", "cliente_id": b["cliente"], "empresa_id": a["empresa"]})
    try:
        assert r.status_code == 404
    finally:
        admin.table("veiculos").delete().eq("placa", "TSTF1X5").execute()


@pytest.mark.cenario("F1.4", "DONO A promove o mecânico a master → 403; cargo continua MECANICO")
def test_dono_nao_promove_master(api, token, seed_ids, admin):
    a = seed_ids["a"]
    r = api.put(f"/api/v1/usuarios/{a['empresa']}/{a['MECANICO']}", headers=_h(token("DONO", "a")),
                json={"cargo": "master"})
    assert r.status_code == 403
    assert admin.table("usuarios").select("cargo").eq("id", a["MECANICO"]).execute().data[0]["cargo"] == "MECANICO"


@pytest.mark.cenario("F1.4b", "DONO A cria usuário já como master → 403; nenhum usuário criado")
def test_dono_nao_cria_master(api, token, seed_ids, admin):
    a = seed_ids["a"]
    email = "master.invasao@example.com"
    r = api.post(f"/api/v1/usuarios/{a['empresa']}", headers=_h(token("DONO", "a")),
                 json={"nome": "Invasão", "email": email, "cargo": "master", "senha": "SenhaQualquer123"})
    assert r.status_code == 403
    assert not admin.table("usuarios").select("id").eq("email", email).execute().data
