"""Fase 6.2 R9: escala com data_fim antes de data_inicio é recusada no backend (422), nada gravado. Sem banco."""
import os

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("GEMINI_API_KEY", "test")

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import core.security as security
from main import app
from modules.equipe import service
from tests.conftest import com_registro

EMP = "11111111-1111-1111-1111-111111111111"
USR = "33333333-3333-3333-3333-333333333333"


class _Banco:
    def __init__(self): self.inserido = []
    def table(self, nome): self.nome = nome; return self
    def select(self, *_): return self
    def eq(self, *_): return self
    def insert(self, d): self.inserido.append(d); return self
    def execute(self):
        if self.nome == "usuarios":
            return SimpleNamespace(data=[{"id": "u1", "cargo": "DONO", "empresa_id": EMP, "ativo": True, "nome": "Zé"}])
        return SimpleNamespace(data=[{**self.inserido[-1], "id": "44444444-4444-4444-4444-444444444444", "empresa_id": EMP}] if self.inserido else [])


@pytest.fixture
def api(monkeypatch):
    banco = _Banco()
    app.dependency_overrides[security.validar_token] = lambda: SimpleNamespace(id="u1")
    monkeypatch.setattr(security.supabase, "table", banco.table)
    yield com_registro(TestClient(app)), banco
    app.dependency_overrides.clear()


def _corpo(ini, fim):
    return {"usuario_id": USR, "tipo": "FERIAS", "data_inicio": ini, "data_fim": fim}


@pytest.mark.cenario("R9-1", "Escala com data_fim antes de data_inicio → 422 em português e nada gravado")
def test_datas_invertidas(api):
    c, banco = api
    r = c.post(f"/api/v1/equipe/escalas/{EMP}", json=_corpo("2026-12-25", "2026-12-24"))
    assert r.status_code == 422
    assert "A data final não pode ser antes da data inicial." in r.text
    assert banco.inserido == []


@pytest.mark.cenario("R9-2", "Mesmo dia e período normal continuam aceitos")
@pytest.mark.parametrize("ini, fim", [("2026-12-24", "2026-12-24"), ("2026-12-24", "2026-12-30")])
def test_datas_validas(api, ini, fim):
    c, banco = api
    r = c.post(f"/api/v1/equipe/escalas/{EMP}", json=_corpo(ini, fim))
    assert r.status_code == 200, r.text
    assert banco.inserido[0]["data_inicio"] == ini
