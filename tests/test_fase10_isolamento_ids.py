"""T-010 — ids de OUTRA oficina no corpo da requisição são recusados e nada é gravado.

Tenant A (Oficina do tião) tenta usar ids do tenant B (TETECA). Só empresas de teste; o que o teste cria é apagado no fim.
"""
import asyncio

import pytest
from fastapi import HTTPException

from tests.conftest import integracao

pytestmark = integracao


def _h(tok):
    return {"Authorization": f"Bearer {tok}"}


def _contar(admin, tabela, **filtros):
    q = admin.table(tabela).select("id")
    for k, v in filtros.items():
        q = q.eq(k, v)
    return len(q.execute().data)


@pytest.mark.cenario("T10-1", "Escala: usuario_id da Oficina B → 404, nada gravado, nome do colaborador de B não vaza")
def test_escala_usuario_de_outra_empresa(api, token, seed_ids, admin):
    a, b = seed_ids["a"], seed_ids["b"]
    nome_b = admin.table("usuarios").select("nome").eq("id", b["MECANICO"]).execute().data[0]["nome"]
    antes = _contar(admin, "escalas_folgas", usuario_id=b["MECANICO"])
    r = api.post(f"/api/v1/equipe/escalas/{a['empresa']}", headers=_h(token("DONO", "a")),
                 json={"usuario_id": b["MECANICO"], "tipo": "FOLGA", "data_inicio": "2026-12-24", "data_fim": "2026-12-25"})
    assert r.status_code == 404, r.text
    assert nome_b not in r.text
    assert _contar(admin, "escalas_folgas", usuario_id=b["MECANICO"]) == antes


@pytest.mark.cenario("T10-2", "Escala: colaborador da própria empresa continua funcionando")
def test_escala_usuario_da_propria_empresa(api, token, seed_ids, admin):
    a = seed_ids["a"]
    r = api.post(f"/api/v1/equipe/escalas/{a['empresa']}", headers=_h(token("DONO", "a")),
                 json={"usuario_id": a["MECANICO"], "tipo": "FOLGA", "data_inicio": "2026-12-24", "data_fim": "2026-12-25"})
    try:
        assert r.status_code == 200, r.text
    finally:
        if r.status_code == 200:
            admin.table("escalas_folgas").delete().eq("id", r.json()["id"]).execute()


@pytest.mark.cenario("T10-3", "OS: cliente, veículo ou mecânico de B na criação → 404 e nenhuma OS criada; mecânico de B na edição → 404 e OS intacta")
def test_os_ids_de_outra_empresa(api, token, seed_ids, admin):
    a, b, tok = seed_ids["a"], seed_ids["b"], token("DONO", "a")
    antes = _contar(admin, "ordens_servico", empresa_id=a["empresa"])
    base = {"empresa_id": a["empresa"], "cliente_id": a["cliente"], "veiculo_id": a["veiculo"]}
    for troca in ({"cliente_id": b["cliente"]}, {"veiculo_id": b["veiculo"]}, {"mecanico_responsavel_id": b["MECANICO"]}):
        r = api.post("/api/v1/os/", headers=_h(tok), json={**base, **troca})
        assert r.status_code == 404, (troca, r.text)
    assert _contar(admin, "ordens_servico", empresa_id=a["empresa"]) == antes
    r = api.put(f"/api/v1/os/{a['empresa']}/{a['os']}", headers=_h(tok), json={"mecanico_responsavel_id": b["MECANICO"]})
    assert r.status_code == 404, r.text
    assert admin.table("ordens_servico").select("mecanico_responsavel_id").eq("id", a["os"]).execute().data[0]["mecanico_responsavel_id"] != b["MECANICO"]


@pytest.mark.cenario("T10-4", "Item da OS com estoque_id de B → recusado, estoque de B intacto, nenhum item criado")
def test_item_os_estoque_de_outra_empresa(api, token, seed_ids, admin):
    a, b, tok = seed_ids["a"], seed_ids["b"], token("DONO", "a")
    saldo = lambda: admin.table("estoque").select("quantidade").eq("id", b["estoque"]).execute().data[0]["quantidade"]
    antes_saldo, antes_itens = saldo(), _contar(admin, "os_itens", os_id=a["os"])
    item = {"estoque_id": b["estoque"], "tipo": "PECA", "nome_item": "Peça de B", "quantidade": 1, "custo_unitario": 1, "venda_unitario": 2}
    base = f"/api/v1/os/{a['empresa']}/{a['os']}"
    assert api.post(f"{base}/itens", headers=_h(tok), json=item).status_code in (400, 404)
    assert api.post(f"{base}/itens/lote", headers=_h(tok), json=[item]).status_code in (400, 404)
    assert saldo() == antes_saldo and _contar(admin, "os_itens", os_id=a["os"]) == antes_itens


@pytest.mark.cenario("T10-5", "Veículo: cliente_id de B na criação e na edição → 404, nada gravado")
def test_veiculo_cliente_de_outra_empresa(api, token, seed_ids, admin):
    a, b, tok = seed_ids["a"], seed_ids["b"], token("DONO", "a")
    r = api.post("/api/v1/veiculos/", headers=_h(tok),
                 json={"empresa_id": a["empresa"], "cliente_id": b["cliente"], "placa": "T10ZZ99", "modelo": "Teste"})
    assert r.status_code == 404, r.text
    assert _contar(admin, "veiculos", placa="T10ZZ99") == 0
    r = api.put(f"/api/v1/veiculos/{a['empresa']}/{a['veiculo']}", headers=_h(tok), json={"cliente_id": b["cliente"]})
    assert r.status_code == 404, r.text
    assert admin.table("veiculos").select("cliente_id").eq("id", a["veiculo"]).execute().data[0]["cliente_id"] == a["cliente"]


@pytest.mark.cenario("T10-6", "Bot: abrir-os com cliente/veículo/mecânico de B e cadastro-rápido com mecânico de B → 404, nada criado")
def test_bot_ids_de_outra_empresa(seed_ids, admin):
    from modules.bot import schemas, service
    a, b = seed_ids["a"], seed_ids["b"]
    antes = _contar(admin, "ordens_servico", empresa_id=a["empresa"])
    ok = {"empresa_id": a["empresa"], "mecanico_id": a["MECANICO"], "cliente_id": a["cliente"], "veiculo_id": a["veiculo"]}
    for troca in ({"cliente_id": b["cliente"]}, {"veiculo_id": b["veiculo"]}, {"mecanico_id": b["MECANICO"]}):
        with pytest.raises(HTTPException) as e:
            service.abrir_os(schemas.CriarOSRequest(**{**ok, **troca}))
        assert e.value.status_code == 404, troca
    clientes_antes = _contar(admin, "clientes", empresa_id=a["empresa"])
    with pytest.raises(HTTPException) as e:
        asyncio.run(service.executar_cadastro_rapido(schemas.CadastroRapidoRequest(
            empresa_id=a["empresa"], mecanico_id=b["MECANICO"], nome_cliente="Fulano T10", telefone_cliente="11900000010", placa="T10AA11")))
    assert e.value.status_code == 404
    assert _contar(admin, "ordens_servico", empresa_id=a["empresa"]) == antes
    assert _contar(admin, "clientes", empresa_id=a["empresa"]) == clientes_antes


@pytest.mark.cenario("T10-7", "Bot: processar-audio com os_id de B e empresa_id de A → 404 antes de baixar o áudio; OS de B sem itens novos")
def test_bot_audio_os_de_outra_empresa(seed_ids, admin):
    from modules.bot import schemas, service
    a, b = seed_ids["a"], seed_ids["b"]
    antes = _contar(admin, "os_itens", os_id=b["os"])
    with pytest.raises(HTTPException) as e:
        asyncio.run(service.processar_e_injetar_audio(
            schemas.ProcessarAudioRequest(empresa_id=a["empresa"], os_id=b["os"], url_audio="https://exemplo.invalid/a.ogg")))
    assert e.value.status_code == 404
    assert _contar(admin, "os_itens", os_id=b["os"]) == antes
