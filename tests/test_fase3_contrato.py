"""Fase 3 — contrato backend ↔ frontend.

O frontend deixa de ter caminho alternativo direto no Supabase: toda leitura e escrita passa por estas rotas.
Cada teste usa o mesmo corpo que as telas enviam e confere o efeito no banco. Só empresas A/B (empresa_teste = true);
tudo que é criado é removido no fim.
"""
import uuid

import pytest

from tests.conftest import integracao

pytestmark = integracao


def _h(tok):
    return {"Authorization": f"Bearer {tok}"}


def _estoque(admin, estoque_id):
    return admin.table("estoque").select("quantidade").eq("id", estoque_id).execute().data[0]["quantidade"]


# ------------------------------------------------------------------ leituras
LEITURAS = [
    # (rota, cargo, chaves esperadas no JSON — dict ou item de lista)
    ("/dashboards/{emp}", "DONO", {"total_abertas", "status_counts", "ultimas_os", "itens_criticos", "estoque_critico_count"}),
    ("/clientes/{emp}", "ATENDENTE", {"id", "nome", "telefone", "cpf_cnpj", "endereco", "empresa_id"}),
    ("/veiculos/{emp}", "ATENDENTE", {"id", "placa", "modelo", "cliente_id", "clientes"}),
    ("/estoque/{emp}", "MECANICO", {"itens", "stats"}),
    ("/os/?empresa_id={emp}", "MECANICO", {"items", "total", "skip", "limit"}),
    ("/os/{emp}/{os}/imprimir", "ATENDENTE", {"ordem", "itens", "empresa"}),
    ("/usuarios/{emp}", "DONO", {"id", "nome", "cargo", "salario_base"}),
    ("/empresas/?empresa_id={emp}", "DONO", {"id", "nome_fantasia"}),
    ("/empresas/{emp}/configuracoes", "ATENDENTE", {"cor_primaria", "cor_secundaria"}),
    ("/equipe/escalas/{emp}", "ATENDENTE", None),
    ("/equipe/pontos/{emp}", "DONO", None),
    ("/equipe/avaliacoes/{emp}", "ATENDENTE", None),
    ("/transacoes-financeiras/{emp}", "FINANCEIRO", {"transacoes", "resumo"}),
    ("/financeiro/{emp}", "FINANCEIRO", {"faturamento_pago", "faturamento_projetado", "lucro_realizado", "ticket_medio", "historico_6_meses"}),
    ("/financeiro/inteligencia/{emp}", "FINANCEIRO", {"top_10_clientes", "produtividade_mecanicos", "metodos_pagamento", "rentabilidade_marcas", "origem_faturamento", "lead_time_medio_horas", "taxa_conversao_orcamentos"}),
]


@pytest.mark.cenario("F3-C1", "Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado")
@pytest.mark.parametrize("rota,cargo,chaves", LEITURAS, ids=[l[0] for l in LEITURAS])
def test_leituras_pelo_backend(api, token, seed_ids, rota, cargo, chaves):
    a = seed_ids["a"]
    url = "/api/v1" + rota.format(emp=a["empresa"], os=a["os"])
    r = api.get(url, headers=_h(token(cargo, "a")))
    assert r.status_code == 200, r.text
    corpo = r.json()
    if chaves:
        amostra = corpo[0] if isinstance(corpo, list) else corpo
        assert chaves <= set(amostra), f"faltam: {chaves - set(amostra)}"


@pytest.mark.cenario("F3-C2", "Histórico de OS por veículo/cliente e busca por modelo e por placa sem hífen")
def test_listagem_de_os_filtros_e_busca(api, token, seed_ids):
    a, b = seed_ids["a"], seed_ids["b"]
    tok = token("DONO", "a")
    base = f"/api/v1/os/?empresa_id={a['empresa']}"
    por_veiculo = api.get(f"{base}&veiculo_id={a['veiculo']}&limit=500", headers=_h(tok)).json()["items"]
    assert por_veiculo and {i["veiculo_id"] for i in por_veiculo} == {a["veiculo"]}
    assert {"cliente_id", "veiculo_id", "km_atual"} <= set(por_veiculo[0])
    assert all(i["cliente_id"] == a["cliente"] for i in api.get(f"{base}&cliente_id={a['cliente']}", headers=_h(tok)).json()["items"])
    assert api.get(f"{base}&veiculo_id={b['veiculo']}", headers=_h(tok)).json()["total"] == 0
    for termo in ("gol", "tsta001", "TST-A001"):
        achou = api.get(f"{base}&search={termo}", headers=_h(tok)).json()["items"]
        assert any(i["id"] == a["os"] for i in achou), termo


# ------------------------------------------------------------------ escritas
@pytest.mark.cenario("F3-W1", "Itens da OS: adicionar em lote baixa o estoque, alterar ajusta, remover estorna; totais da OS recalculados")
def test_itens_da_os_e_estoque(api, token, seed_ids, admin):
    a = seed_ids["a"]
    tok, base = token("DONO", "a"), f"/api/v1/os/{a['empresa']}/{a['os']}"
    antes = _estoque(admin, a["estoque"])
    itens = [
        {"estoque_id": a["estoque"], "tipo": "PECA", "nome_item": "Filtro F3-W1", "quantidade": 2, "custo_unitario": 20, "venda_unitario": 45},
        {"tipo": "MAO_OBRA", "nome_item": "Mão de obra F3-W1", "quantidade": 1, "custo_unitario": 0, "venda_unitario": 100},
    ]
    r = api.post(f"{base}/itens/lote", headers=_h(tok), json=itens)
    assert r.status_code == 200, r.text
    ids = [i["id"] for i in r.json()]
    try:
        assert _estoque(admin, a["estoque"]) == antes - 2
        os_ = admin.table("ordens_servico").select("total_geral,total_pecas,total_mao_obra").eq("id", a["os"]).execute().data[0]
        assert float(os_["total_pecas"]) >= 90 and float(os_["total_mao_obra"]) >= 100
        assert api.put(f"{base}/itens/{ids[0]}", headers=_h(tok), json={"quantidade": 3}).status_code == 200
        assert _estoque(admin, a["estoque"]) == antes - 3
    finally:
        for i in ids:
            api.delete(f"{base}/itens/{i}", headers=_h(tok))
    assert _estoque(admin, a["estoque"]) == antes
    assert not admin.table("os_itens").select("id").in_("id", ids).execute().data


@pytest.mark.cenario("F3-W1b", "Item antigo do legado (sem empresa_id) pode ser alterado/removido pela própria empresa; a outra recebe 403/404")
def test_item_legado_sem_empresa_id(api, token, seed_ids, admin):
    a, b = seed_ids["a"], seed_ids["b"]
    item = admin.table("os_itens").insert({"os_id": a["os"], "tipo": "MAO_OBRA", "nome_item": "Legado F3-W1b",
                                           "quantidade": 1, "custo_unitario": 0, "venda_unitario": 10}).execute().data[0]
    assert item["empresa_id"] is None
    url_a = f"/api/v1/os/{a['empresa']}/{a['os']}/itens/{item['id']}"
    try:
        assert api.put(url_a.replace(a["empresa"], b["empresa"]), headers=_h(token("DONO", "b")), json={"quantidade": 5}).status_code == 404
        assert api.put(url_a, headers=_h(token("DONO", "a")), json={"quantidade": 2}).status_code == 200
        assert api.delete(url_a, headers=_h(token("DONO", "a"))).status_code == 200
    finally:
        admin.table("os_itens").delete().eq("id", item["id"]).execute()


@pytest.mark.cenario("F3-W2", "Abrir OS: reaproveita orçamento aberto do veículo; veículo novo cria OS; status e fechamento atualizam")
def test_abrir_e_atualizar_os(api, token, seed_ids, admin):
    a = seed_ids["a"]
    tok = token("DONO", "a")
    base = {"empresa_id": a["empresa"], "cliente_id": a["cliente"], "mecanico_responsavel_id": a["MECANICO"],
            "descricao_problema": "F3-W2", "km_atual": 50100}
    reaproveitada = api.post("/api/v1/os/", headers=_h(tok), json={**base, "veiculo_id": a["veiculo"]}).json()
    assert reaproveitada["id"] == a["os"] and reaproveitada["reaproveitada"] is True

    placa = "TSTW2" + uuid.uuid4().hex[:2].upper()
    vei = admin.table("veiculos").insert({"empresa_id": a["empresa"], "cliente_id": a["cliente"], "placa": placa, "modelo": "Teste"}).execute().data[0]
    nova_id = None
    try:
        r = api.post("/api/v1/os/", headers=_h(tok), json={**base, "veiculo_id": vei["id"]})
        assert r.status_code == 200, r.text
        nova_id = r.json()["id"]
        assert nova_id != a["os"] and not r.json().get("reaproveitada")
        assert api.put(f"/api/v1/os/{a['empresa']}/{nova_id}", headers=_h(tok), json={"status": "FINALIZADO", "forma_pagamento": "PIX"}).status_code == 200
        fechada = admin.table("ordens_servico").select("status,data_fechamento").eq("id", nova_id).execute().data[0]
        assert fechada["status"] == "FINALIZADO" and fechada["data_fechamento"]
        assert api.delete(f"/api/v1/os/{a['empresa']}/{nova_id}?motivo_exclusao=teste F3-W2", headers=_h(tok)).status_code == 200
        nova_id = None
    finally:
        if nova_id:
            admin.table("ordens_servico").delete().eq("id", nova_id).execute()
        admin.table("veiculos").delete().eq("id", vei["id"]).execute()


@pytest.mark.cenario("F3-W3", "Cliente, veículo e item de estoque: criar, alterar, ajustar saldo e apagar (corpos iguais aos das telas)")
def test_crud_cliente_veiculo_estoque(api, token, seed_ids, admin):
    a = seed_ids["a"]
    tok = token("DONO", "a")
    emp = a["empresa"]
    criados = {}
    try:
        cli = api.post("/api/v1/clientes/", headers=_h(tok), json={"nome": "Cliente F3-W3", "telefone": "11900000033", "cpf_cnpj": None, "endereco": None, "empresa_id": emp})
        assert cli.status_code == 200, cli.text
        criados["cli"] = cli.json()["id"]
        assert api.put(f"/api/v1/clientes/{emp}/{criados['cli']}", headers=_h(tok), json={"nome": "Cliente F3-W3 editado", "cpf_cnpj": None}).status_code == 200

        vei = api.post("/api/v1/veiculos/", headers=_h(tok), json={"placa": "TSTW3Z9", "modelo": "Fox", "marca": "VW", "cor": None, "km_atual": 1000, "ano": None, "chassi": None, "cliente_id": criados["cli"], "empresa_id": emp})
        assert vei.status_code == 200, vei.text
        criados["vei"] = vei.json()["id"]
        assert api.put(f"/api/v1/veiculos/{emp}/{criados['vei']}", headers=_h(tok), json={"km_atual": 1200}).status_code == 200

        est = api.post("/api/v1/estoque/", headers=_h(tok), json={"nome": "Item F3-W3", "categoria": "PECAS", "quantidade": 5, "custo": 10, "venda": 20, "minimo_alerta": 2, "codigo": "F3W3", "empresa_id": emp})
        assert est.status_code == 200, est.text
        criados["est"] = est.json()["id"]
        assert api.put(f"/api/v1/estoque/{emp}/{criados['est']}", headers=_h(tok), json={"venda": 25, "codigo": None}).status_code == 200
        assert api.patch(f"/api/v1/estoque/{emp}/{criados['est']}/ajustar", headers=_h(tok), json={"tipo": "entrada", "quantidade": 3}).json()["quantidade"] == 8
        # Fase 4: saída acima do saldo é recusada (antes zerava em silêncio)
        assert api.patch(f"/api/v1/estoque/{emp}/{criados['est']}/ajustar", headers=_h(tok), json={"tipo": "saida", "quantidade": 100}).status_code == 400
        assert api.patch(f"/api/v1/estoque/{emp}/{criados['est']}/ajustar", headers=_h(tok), json={"tipo": "saida", "quantidade": 8}).json()["quantidade"] == 0
    finally:
        for tabela, chave in (("estoque", "est"), ("veiculos", "vei"), ("clientes", "cli")):
            if chave in criados:
                api.delete(f"/api/v1/{tabela}/{emp}/{criados[chave]}", headers=_h(tok))
    assert not admin.table("clientes").select("id").eq("id", criados.get("cli", "x")).execute().data


@pytest.mark.cenario("F3-W4", "Contas a pagar/receber: criar, alterar, liquidar e apagar; erro do banco aparece como erro (nada é engolido)")
def test_crud_transacoes(api, token, seed_ids, admin):
    a = seed_ids["a"]
    tok, emp = token("FINANCEIRO", "a"), a["empresa"]
    r = api.post("/api/v1/transacoes-financeiras/", headers=_h(tok), json={"tipo": "DESPESA", "descricao": "F3-W4", "categoria": "OUTROS", "valor": 123.45, "data_vencimento": "2026-12-31", "status": "PENDENTE", "empresa_id": emp})
    assert r.status_code == 200, r.text
    tid = r.json()["id"]
    try:
        assert api.put(f"/api/v1/transacoes-financeiras/{emp}/{tid}", headers=_h(tok), json={"valor": 200}).json()["valor"] == 200
        liq = api.patch(f"/api/v1/transacoes-financeiras/{emp}/{tid}/liquidar", headers=_h(tok), json={"data_liquidacao": "2026-11-09", "forma_pagamento": "PIX"})
        assert liq.status_code == 200 and liq.json()["status"] == "LIQUIDADO"
        assert api.patch(f"/api/v1/transacoes-financeiras/{emp}/{tid}/liquidar", headers=_h(tok), json={"data_liquidacao": "2026-11-09"}).status_code == 200
        assert api.post("/api/v1/transacoes-financeiras/", headers=_h(tok), json={"tipo": "DESPESA", "descricao": "x", "categoria": "OUTROS", "valor": -1, "data_vencimento": "2026-12-31", "empresa_id": emp}).status_code == 422
    finally:
        assert api.delete(f"/api/v1/transacoes-financeiras/{emp}/{tid}", headers=_h(tok)).status_code == 200
    assert not admin.table("transacoes_financeiras").select("id").eq("id", tid).execute().data


@pytest.mark.cenario("F3-W5", "Escalas e ponto com os corpos das telas: gravados no banco e listados pelo backend")
def test_escalas_e_ponto(api, token, seed_ids, admin):
    a = seed_ids["a"]
    emp = a["empresa"]
    dono, mec = token("DONO", "a"), token("MECANICO", "a")
    esc = api.post(f"/api/v1/equipe/escalas/{emp}", headers=_h(dono), json={"empresa_id": emp, "usuario_id": a["MECANICO"], "usuario_nome": "Mecanico Teste A", "tipo": "FOLGA", "data_inicio": "2026-12-24", "data_fim": "2026-12-25", "observacoes": None})
    assert esc.status_code == 200, esc.text
    ponto_id = None
    try:
        assert esc.json()["usuario_nome"]
        assert any(e["id"] == esc.json()["id"] for e in api.get(f"/api/v1/equipe/escalas/{emp}", headers=_h(mec)).json())
        p = api.post(f"/api/v1/equipe/pontos/{emp}", headers=_h(mec), json={"tipo": "ENTRADA", "latitude": -23.5, "longitude": -46.6})  # fase 5: usuário, data e hora vêm do servidor
        assert p.status_code == 200, p.text
        ponto_id = p.json()["id"]
        assert any(x["id"] == ponto_id for x in api.get(f"/api/v1/equipe/pontos/{emp}?data={p.json()['data']}", headers=_h(dono)).json())
    finally:
        api.delete(f"/api/v1/equipe/escalas/{emp}/{esc.json()['id']}", headers=_h(dono))
        if ponto_id:
            admin.table("pontos_eletronicos").delete().eq("id", ponto_id).execute()


@pytest.mark.cenario("F3-W6", "Configurações da oficina e parâmetros da folha (antes só no localStorage) gravam e voltam do servidor")
def test_configuracoes_da_oficina(api, token, seed_ids, admin):
    a = seed_ids["a"]
    emp, dono = a["empresa"], token("DONO", "a")
    cfg_antes = api.get(f"/api/v1/empresas/{emp}/configuracoes", headers=_h(dono)).json()
    emp_antes = admin.table("empresas").select("nome_fantasia,telefone,endereco").eq("id", emp).execute().data[0]
    novo = {"whatsapp": "11988887777", "chave_pix": "pix@teste.example.com", "inscricao_estadual": "123", "latitude_gps": -23.55, "longitude_gps": -46.63,
            "raio_gps_metros": 150, "dia_pagamento_folha": 7, "dia_adiantamento_folha": 22, "comissao_global_servico_pct": 12.5,
            "comissao_global_peca_pct": 4, "paga_hora_extra_padrao": False, "valor_hora_extra_padrao": 30, "cor_primaria": "#112233", "cor_secundaria": "#445566"}
    try:
        assert api.put(f"/api/v1/empresas/{emp}/configuracoes", headers=_h(dono), json=novo).status_code == 200
        assert api.put(f"/api/v1/empresas/{emp}", headers=_h(dono), json={"nome_fantasia": emp_antes["nome_fantasia"], "telefone": "1133334444", "endereco": "Rua Teste, 1"}).status_code == 200
        lido = api.get(f"/api/v1/empresas/{emp}/configuracoes", headers=_h(token("MECANICO", "a"))).json()
        for k, v in novo.items():
            assert lido[k] == v, k
        assert api.put(f"/api/v1/empresas/{emp}/configuracoes", headers=_h(token("MECANICO", "a")), json={"chave_pix": "x"}).status_code == 403
        assert api.put(f"/api/v1/empresas/{emp}", headers=_h(dono), json={"email": ""}).status_code == 422
    finally:
        restaura = {k: cfg_antes.get(k) for k in novo}
        admin.table("configuracoes_empresa").update(restaura).eq("empresa_id", emp).execute()
        admin.table("empresas").update(emp_antes).eq("id", emp).execute()


@pytest.mark.cenario("F3-C3", "Lista de clientes vem ordenada por nome (a tela dependia disso)")
def test_clientes_ordenados_por_nome(api, token, seed_ids, admin):
    a = seed_ids["a"]
    tok = token("ATENDENTE", "a")
    temp = admin.table("clientes").insert([
        {"empresa_id": a["empresa"], "nome": "ZZ F3-C3", "telefone": "11900000091"},
        {"empresa_id": a["empresa"], "nome": "AA F3-C3", "telefone": "11900000092"},
    ]).execute().data
    try:
        nomes = [c["nome"] for c in api.get(f"/api/v1/clientes/{a['empresa']}", headers=_h(tok)).json()]
        # a ordem é a do banco (ignora maiúsculas): basta o "AA" vir antes do "ZZ" e antes dos demais
        assert nomes.index("AA F3-C3") < nomes.index("ZZ F3-C3")
        assert nomes.index("AA F3-C3") == 0 or nomes[0].lower() <= "aa f3-c3"
    finally:
        admin.table("clientes").delete().in_("id", [c["id"] for c in temp]).execute()


@pytest.mark.cenario("F3-F4", "Cadastro novo (sem perfil): /me nega, onboarding cria 1 oficina DONO só uma vez e isolada das demais")
def test_onboarding_de_conta_nova(api, token, seed_ids, admin):
    import os
    import secrets
    from supabase import create_client

    a = seed_ids["a"]
    email = f"f3f4.{uuid.uuid4().hex[:8]}@homolog-autotec.example.com"
    senha = secrets.token_urlsafe(16)
    nome_oficina = f"Oficina F3-F4 {uuid.uuid4().hex[:6]}"
    auth_id = admin.auth.admin.create_user({"email": email, "password": senha, "email_confirm": True,
                                            "user_metadata": {"nome": "Teste F4", "nome_fantasia": nome_oficina}}).user.id
    try:
        anon = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
        tok = anon.auth.sign_in_with_password({"email": email, "password": senha}).session.access_token

        assert api.get("/api/v1/usuarios/me", headers=_h(tok)).status_code == 403
        r = api.post("/api/v1/usuarios/onboarding", headers=_h(tok))
        assert r.status_code == 200, r.text
        # a empresa nasce com empresa_teste=false: marca na hora para nunca valer como produção
        admin.table("empresas").update({"empresa_teste": True}).eq("id", r.json()["empresa_id"]).execute()
        assert r.json()["cargo"] == "DONO" and "senha_hash" not in r.json()

        de_novo = api.post("/api/v1/usuarios/onboarding", headers=_h(tok))
        assert de_novo.status_code == 200 and de_novo.json()["id"] == r.json()["id"]
        assert len(admin.table("empresas").select("id").eq("nome_fantasia", nome_oficina).execute().data) == 1

        assert api.get("/api/v1/usuarios/me", headers=_h(tok)).status_code == 200
        assert api.get(f"/api/v1/clientes/{a['empresa']}", headers=_h(tok)).status_code == 403
    finally:
        perfil = admin.table("usuarios").select("empresa_id").eq("id", auth_id).execute().data
        if perfil:
            emp = perfil[0]["empresa_id"]
            admin.table("empresas").update({"empresa_teste": True}).eq("id", emp).execute()
            admin.table("configuracoes_empresa").delete().eq("empresa_id", emp).execute()
            admin.table("usuarios").delete().eq("id", auth_id).execute()
            # apagar usuário gera linha em audit_logs com empresa_id, que impede apagar a empresa
            admin.table("audit_logs").delete().eq("empresa_id", emp).execute()
            admin.table("empresas").delete().eq("id", emp).execute()
        admin.auth.admin.delete_user(auth_id)


@pytest.mark.cenario("F3-E1", "Equipe (nomes/cargos) para qualquer perfil, sem RH; RH continua só para o DONO; outra empresa → 403")
@pytest.mark.parametrize("cargo", ["MECANICO", "ATENDENTE", "FINANCEIRO", "DONO"])
def test_equipe_sem_rh_para_todos(api, token, seed_ids, cargo):
    a, b = seed_ids["a"], seed_ids["b"]
    r = api.get(f"/api/v1/usuarios/{a['empresa']}/equipe", headers=_h(token(cargo, "a")))
    assert r.status_code == 200, r.text
    equipe = r.json()
    assert {"DONO", "MECANICO"} <= {u["cargo"] for u in equipe}
    assert {u["empresa_id"] for u in equipe} == {a["empresa"]}
    proibidos = {"salario_base", "comissao_servico_pct", "comissao_peca_pct", "vale_transporte", "vale_refeicao",
                 "paga_hora_extra", "valor_hora_extra", "senha_hash"}
    assert not any(proibidos & set(u) for u in equipe)
    assert api.get(f"/api/v1/usuarios/{b['empresa']}/equipe", headers=_h(token(cargo, "a"))).status_code == 403
    if cargo != "DONO":
        assert api.get(f"/api/v1/usuarios/{a['empresa']}", headers=_h(token(cargo, "a"))).status_code == 403
