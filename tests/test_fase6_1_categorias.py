"""Fase 6.1 — categorias de estoque livres (antes o CHECK do banco só aceitava 5 valores).
Cada teste cria o que usa e apaga no fim (só empresa A, empresa_teste=true)."""
import pytest

from tests.conftest import integracao

pytestmark = integracao


def _h(tok):
    return {"Authorization": f"Bearer {tok}"}


def _item(empresa, categoria, nome="Item F61"):
    return {"empresa_id": empresa, "nome": nome, "categoria": categoria, "quantidade": 1, "minimo_alerta": 0, "custo": 1, "venda": 2}


def _limpar(admin, empresa, itens=(), categorias=()):
    for i in itens:
        admin.table("estoque").delete().eq("id", i).execute()
    for c in categorias:
        admin.table("categorias_estoque").delete().eq("empresa_id", empresa).eq("nome", c).execute()


@pytest.mark.cenario("F61-1", "Item com categoria nova ('  freios  e pastilhas ') grava, normalizada em maiúsculas; editar para outra nova também (antes: 400 do CHECK)")
def test_item_com_categoria_nova(api, token, seed_ids, admin):
    a, tok, criados = seed_ids["a"], token("DONO", "a"), []
    try:
        r = api.post("/api/v1/estoque/", headers=_h(tok), json=_item(a["empresa"], "  freios  e pastilhas "))
        assert r.status_code == 200, r.text
        criados.append(r.json()["id"])
        assert r.json()["categoria"] == "FREIOS E PASTILHAS"

        r = api.put(f"/api/v1/estoque/{a['empresa']}/{criados[0]}", headers=_h(tok), json={"categoria": "acessórios de luxo"})
        assert r.status_code == 200, r.text
        assert r.json()["categoria"] == "ACESSÓRIOS DE LUXO"

        # o padrão antigo do front, que o banco recusava
        r = api.post("/api/v1/estoque/", headers=_h(tok), json=_item(a["empresa"], "FERRAMENTAS"))
        assert r.status_code == 200, r.text
        criados.append(r.json()["id"])
    finally:
        _limpar(admin, a["empresa"], criados)


@pytest.mark.cenario("F61-2", "Categoria vazia ou com mais de 30 caracteres (limite da coluna) → 422 e nada gravado")
def test_categoria_invalida(api, token, seed_ids, admin):
    a, tok = seed_ids["a"], token("DONO", "a")
    antes = len(admin.table("estoque").select("id").eq("empresa_id", a["empresa"]).execute().data)
    for ruim in ("", "   ", "X" * 31):
        assert api.post("/api/v1/estoque/", headers=_h(tok), json=_item(a["empresa"], ruim)).status_code == 422, ruim
        assert api.put(f"/api/v1/estoque/{a['empresa']}/{a['estoque']}", headers=_h(tok), json={"categoria": ruim}).status_code == 422, ruim
        assert api.post(f"/api/v1/estoque/{a['empresa']}/categorias", headers=_h(tok), json={"nome": ruim}).status_code == 422, ruim
    assert len(admin.table("estoque").select("id").eq("empresa_id", a["empresa"]).execute().data) == antes


@pytest.mark.cenario("F61-3", "Lista de categorias: padrão da oficina + criadas + as que itens já usam (MAO_OBRA); criar duplicada não duplica")
def test_listar_e_criar_categoria(api, token, seed_ids, admin):
    a, tok = seed_ids["a"], token("DONO", "a")
    try:
        r = api.get(f"/api/v1/estoque/{a['empresa']}/categorias", headers=_h(tok))
        assert r.status_code == 200, r.text
        base = r.json()
        for padrao in ("PECAS", "FLUIDOS", "PNEUS", "ELETRICA", "ACESSORIOS", "FERRAMENTAS", "DIVERSOS"):
            assert padrao in base, base

        for _ in range(2):  # a segunda é idempotente
            r = api.post(f"/api/v1/estoque/{a['empresa']}/categorias", headers=_h(tok), json={"nome": " lanternagem "})
            assert r.status_code == 200 and r.json() == {"nome": "LANTERNAGEM"}, r.text
        lista = api.get(f"/api/v1/estoque/{a['empresa']}/categorias", headers=_h(tok)).json()
        assert lista.count("LANTERNAGEM") == 1
        assert lista[: len(base)] == [c for c in lista if c in base][: len(base)]  # padrão continua na frente
    finally:
        _limpar(admin, a["empresa"], categorias=["LANTERNAGEM"])


@pytest.mark.cenario("F61-4", "Excluir categoria com itens: itens vão para DIVERSOS, a categoria some; DIVERSOS e MAO_OBRA não saem")
def test_excluir_categoria(api, token, seed_ids, admin):
    a, tok, criados = seed_ids["a"], token("DONO", "a"), []
    try:
        api.post(f"/api/v1/estoque/{a['empresa']}/categorias", headers=_h(tok), json={"nome": "Vidros"})
        for n in (1, 2):
            r = api.post("/api/v1/estoque/", headers=_h(tok), json=_item(a["empresa"], "vidros", f"Vidro F61-{n}"))
            criados.append(r.json()["id"])

        r = api.delete(f"/api/v1/estoque/{a['empresa']}/categorias/vidros", headers=_h(tok))
        assert r.status_code == 200 and r.json()["itens_reclassificados"] == 2, r.text
        assert "VIDROS" not in api.get(f"/api/v1/estoque/{a['empresa']}/categorias", headers=_h(tok)).json()
        for i in criados:
            assert admin.table("estoque").select("categoria").eq("id", i).execute().data[0]["categoria"] == "DIVERSOS"

        for fixa in ("DIVERSOS", "MAO_OBRA"):
            assert api.delete(f"/api/v1/estoque/{a['empresa']}/categorias/{fixa}", headers=_h(tok)).status_code == 400, fixa
    finally:
        _limpar(admin, a["empresa"], criados, ["VIDROS"])


@pytest.mark.cenario("F61-5", "Isolamento: DONO da empresa A não lê, cria nem exclui categorias da empresa B")
def test_categorias_de_outra_empresa(api, token, seed_ids, admin):
    b, tok = seed_ids["b"], token("DONO", "a")
    for r in (
        api.get(f"/api/v1/estoque/{b['empresa']}/categorias", headers=_h(tok)),
        api.post(f"/api/v1/estoque/{b['empresa']}/categorias", headers=_h(tok), json={"nome": "INVASORA"}),
        api.delete(f"/api/v1/estoque/{b['empresa']}/categorias/PECAS", headers=_h(tok)),
    ):
        assert r.status_code in (403, 404), r.text
    assert not admin.table("categorias_estoque").select("nome").eq("empresa_id", b["empresa"]).eq("nome", "INVASORA").execute().data


@pytest.mark.cenario("F61-6", "Anon/usuário logado não lê nem grava categorias_estoque direto pelo REST (RLS fechado, só o backend)")
def test_categorias_fechadas_no_rest(http, token):
    import os
    base = f"{os.environ['SUPABASE_URL']}/rest/v1/categorias_estoque"
    for chave in (os.environ["SUPABASE_ANON_KEY"], token("DONO", "a")):
        h = {"apikey": os.environ["SUPABASE_ANON_KEY"], "Authorization": f"Bearer {chave}"}
        r = http.get(base, headers=h)
        assert r.status_code in (401, 403) or r.json() == [], r.text
        r = http.post(base, headers={**h, "Content-Type": "application/json"}, json={"empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973", "nome": "X"})
        assert r.status_code in (401, 403), r.text
