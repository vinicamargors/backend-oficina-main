"""Isolamento por empresa: usuário de A não acessa rotas com empresa_id de B."""
import os
from types import SimpleNamespace

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("GEMINI_API_KEY", "test")

import pytest
from fastapi.testclient import TestClient

import core.security as security
from tests.conftest import com_registro
from main import app
from modules.clientes import service as clientes_service

EMPRESA_A = "11111111-1111-1111-1111-111111111111"
EMPRESA_B = "22222222-2222-2222-2222-222222222222"


class _Query:
    def __init__(self, data): self.data = data
    def select(self, *a, **k): return self
    def eq(self, *a, **k): return self
    def execute(self): return self


@pytest.fixture
def cliente(monkeypatch):
    def logar(cargo, empresa_id=EMPRESA_A):
        perfil = {"id": "u1", "cargo": cargo, "empresa_id": empresa_id, "ativo": True, "senha_hash": "x"}
        app.dependency_overrides[security.validar_token] = lambda: SimpleNamespace(id="u1")
        monkeypatch.setattr(security.supabase, "table", lambda nome: _Query([perfil]))
        return com_registro(TestClient(app))
    monkeypatch.setattr(clientes_service, "listar_clientes_por_empresa", lambda emp: [])
    yield logar
    app.dependency_overrides.clear()


@pytest.mark.cenario("T1", "Unitário: perfil da empresa A em rota da empresa B → 403")
def test_bloqueia_outra_empresa(cliente):
    assert cliente("DONO").get(f"/api/v1/clientes/{EMPRESA_B}").status_code == 403


@pytest.mark.cenario("T1+", "Unitário: MECÂNICO na própria empresa → 200")
def test_permite_propria_empresa(cliente):
    assert cliente("MECANICO").get(f"/api/v1/clientes/{EMPRESA_A}").status_code == 200


@pytest.mark.cenario("T1", "Unitário: empresa_id de outra empresa na query string → 403")
def test_bloqueia_query_param_de_outra_empresa(cliente):
    assert cliente("DONO").get(f"/api/v1/os/?empresa_id={EMPRESA_B}").status_code == 403


@pytest.mark.cenario("T1-M", "Unitário: master acessa qualquer empresa → 200")
def test_master_acessa_qualquer_empresa(cliente):
    assert cliente("master", None).get(f"/api/v1/clientes/{EMPRESA_B}").status_code == 200


@pytest.mark.cenario("F1.2", "POST grava na empresa do token, não na do body")
def test_post_usa_empresa_do_token():
    usuario = {"cargo": "DONO", "empresa_id": EMPRESA_A}
    assert security.empresa_do_usuario(usuario, EMPRESA_B) == EMPRESA_A
    assert security.empresa_do_usuario({"cargo": "master", "empresa_id": None}, EMPRESA_B) == EMPRESA_B
