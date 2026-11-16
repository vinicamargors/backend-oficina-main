"""Fase 7 (T-002): busca e paginação no banco. Unitários (sem rede) + integração com 6000 OS (precisa da migration 006)."""
import os

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("GEMINI_API_KEY", "test")

import uuid
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import core.security as security
from core.paginacao import or_ilike
from main import app
from modules.os import service as os_service
from tests.conftest import com_registro, integracao
from tests.homologacao import EMPRESA_A

EMP = "11111111-1111-1111-1111-111111111111"


class _Q:
    """Query falsa: guarda cada chamada encadeada e devolve a página pedida."""
    def __init__(self, linhas=()):
        self.chamadas, self.linhas = [], list(linhas)
    def __getattr__(self, nome):
        def f(*a, **k):
            self.chamadas.append((nome, a, k))
            return self
        return f
    def range(self, ini, fim):
        self.chamadas.append(("range", (ini, fim), {}))
        return self
    def execute(self):
        return SimpleNamespace(data=self.linhas, count=6000)
    def achou(self, nome):
        return [c for c in self.chamadas if c[0] == nome]


@pytest.fixture
def banco(monkeypatch):
    q = _Q()
    tabelas = []
    monkeypatch.setattr(os_service.supabase, "table", lambda n: tabelas.append(n) or q)
    return q, tabelas


@pytest.mark.cenario("F7-1", "Unitário: busca de OS vai para a view os_busca com ilike e janela no banco (sem limit(5000))")
def test_busca_os_no_banco(banco):
    q, tabelas = banco
    q.linhas = [{"id": "x", "cliente_nome": "João", "cliente_telefone": "1", "veiculo_placa": "ABC1234", "veiculo_modelo": "Gol"}]
    r = os_service.listar_os(EMP, search="abc-1234", skip=100, limit=25)
    assert tabelas == ["os_busca"]
    assert not q.achou("limit")
    (ou,) = q.achou("or_")
    assert 'busca.ilike."%abc-1234%"' in ou[1][0] and 'placa_limpa.ilike."%abc1234%"' in ou[1][0]
    assert ("eq", ("empresa_id", EMP), {}) in q.chamadas
    assert q.achou("range")[0][1] == (100, 124)
    assert r["total"] == 6000 and r["skip"] == 100 and r["limit"] == 25
    assert r["items"][0]["clientes"] == {"nome": "João", "telefone": "1"}  # mesmo formato da listagem padrão
    assert r["items"][0]["veiculos"] == {"placa": "ABC1234", "modelo": "Gol"}


@pytest.mark.cenario("F7-2", "Unitário: sem busca a listagem segue na tabela, paginada")
def test_listagem_sem_busca(banco):
    q, tabelas = banco
    os_service.listar_os(EMP, skip=0, limit=50)
    assert tabelas == ["ordens_servico"] and not q.achou("or_") and not q.achou("limit")


@pytest.mark.cenario("F7-3", "Unitário: termo com vírgula, parênteses, aspas e % não quebra o filtro")
def test_termo_hostil():
    f = or_ilike(("nome", 'a,b)"c%'))
    assert f == r'nome.ilike."%a,b)\"c\\%%"'  # o curinga literal \% vira \\% dentro das aspas


@pytest.fixture
def logado(monkeypatch):
    perfil = {"id": "u1", "cargo": "DONO", "empresa_id": EMP, "ativo": True}
    q, q2 = _Q([perfil]), _Q([])
    app.dependency_overrides[security.validar_token] = lambda: SimpleNamespace(id="u1")
    monkeypatch.setattr(security.supabase, "table", lambda n: q if n == "usuarios" else q2)  # o mesmo cliente serve todos os módulos
    yield com_registro(TestClient(app)), q2
    app.dependency_overrides.clear()


@pytest.mark.cenario("F7-4", "Unitário: /paginado de clientes, veículos e estoque devolve {items,total,skip,limit}; não é lido como id")
@pytest.mark.parametrize("rota", ["clientes", "veiculos", "estoque"])
def test_rotas_paginado(logado, rota):
    c, q = logado
    r = c.get(f"/api/v1/{rota}/{EMP}/paginado?busca=ab&skip=10&limit=5")
    assert r.status_code == 200, r.text
    assert r.json() == {"items": [], "total": 6000, "skip": 10, "limit": 5}
    assert q.achou("range")[-1][1] == (10, 14) and q.achou("or_")


@pytest.mark.cenario("F7-5", "Unitário: limit acima de 200 ou skip negativo → 422; empresa de outro tenant → 403")
def test_limites_e_tenant(logado):
    c, _ = logado
    assert c.get(f"/api/v1/clientes/{EMP}/paginado?limit=201").status_code == 422
    assert c.get(f"/api/v1/estoque/{EMP}/paginado?skip=-1").status_code == 422
    assert c.get(f"/api/v1/veiculos/{uuid.uuid4()}/paginado").status_code == 403


@pytest.mark.cenario("F7-6", "Unitário: rotas antigas (lista completa) continuam iguais")
def test_rotas_antigas(logado):
    c, _ = logado
    assert c.get(f"/api/v1/clientes/{EMP}").json() == []
    assert c.get(f"/api/v1/veiculos/{EMP}").json() == []


# ------------------------------------------------------------------ integração (6000 OS)
def _view_existe(admin) -> bool:
    try:
        admin.table("os_busca").select("id").limit(1).execute()
        return True
    except Exception:
        return False


@integracao
@pytest.mark.cenario("F7-7", "Integração: 6000 OS na Oficina do tião; busca acha a OS nº 5999 e a OS de 6000 itens pagina com total correto")
def test_busca_acha_os_5999(api, token, seed_ids, admin):
    if not _view_existe(admin):
        pytest.skip("migration 006 ainda não aplicada neste banco")
    a, tok = seed_ids["a"], token("DONO", "a")
    marca = f"T002-{uuid.uuid4().hex[:6]}"
    ids = [str(uuid.uuid4()) for _ in range(6000)]
    try:
        for i in range(0, 6000, 1000):
            admin.table("ordens_servico").insert([
                {"id": ids[n], "empresa_id": a["empresa"], "cliente_id": a["cliente"], "veiculo_id": a["veiculo"],
                 "descricao_problema": f"{marca} OS {n + 1}"} for n in range(i, i + 1000)]).execute()
        h = {"Authorization": f"Bearer {tok}"}
        r = api.get("/api/v1/os/", headers=h, params={"empresa_id": a["empresa"], "search": f"{marca} OS 5999", "limit": 10})
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["total"] == 1 and j["items"][0]["id"] == ids[5998]
        r = api.get("/api/v1/os/", headers=h, params={"empresa_id": a["empresa"], "search": marca, "skip": 5990, "limit": 50})
        assert r.json()["total"] == 6000 and len(r.json()["items"]) == 10
    finally:
        for i in range(0, 6000, 500):
            admin.table("ordens_servico").delete().in_("id", ids[i:i + 500]).execute()
