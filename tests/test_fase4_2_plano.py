"""Fase 4.2 — o plano vem de `assinaturas`. Sem banco: o Supabase é um fake mínimo."""
from types import SimpleNamespace

import pytest

from core import assinaturas


class _Fake:
    def __init__(self, linhas):
        self.linhas, self.chamadas = linhas, []

    def table(self, nome):
        self.chamadas.append(("table", nome))
        return self

    def select(self, *_):
        return self

    def in_(self, *_):
        return self

    def eq(self, *_):
        return self

    def update(self, dados):
        self.chamadas.append(("update", dados))
        return self

    def insert(self, dados):
        self.chamadas.append(("insert", dados))
        return self

    def execute(self):
        return SimpleNamespace(data=self.linhas)


@pytest.mark.cenario("F42-4", "Listagem de oficinas: plano vem da assinatura; oficina sem assinatura aparece como básico")
def test_com_plano(monkeypatch):
    monkeypatch.setattr(assinaturas, "supabase", _Fake([{"empresa_id": "a", "plano": "profissional"}]))
    r = assinaturas.com_plano([{"id": "a", "nome_fantasia": "A"}, {"id": "b", "nome_fantasia": "B"}])
    assert [e["plano"] for e in r] == ["profissional", "basico"]
    assert assinaturas.com_plano([]) == []


@pytest.mark.cenario("F42-5", "gravar_plano: cria a assinatura se não existe, troca só o plano se já existe")
def test_gravar_plano(monkeypatch):
    novo = _Fake([])
    monkeypatch.setattr(assinaturas, "supabase", novo)
    assinaturas.gravar_plano("e1", "profissional")
    assert ("insert", {"empresa_id": "e1", "plano": "profissional"}) in novo.chamadas

    existente = _Fake([{"id": "x"}])
    monkeypatch.setattr(assinaturas, "supabase", existente)
    assinaturas.gravar_plano("e1", "profissional")
    assert ("update", {"plano": "profissional"}) in existente.chamadas
    assert not any(c[0] == "insert" for c in existente.chamadas)
