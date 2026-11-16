"""Fase 6 — hora de Brasília no servidor (#9) e vencimento da folha (#16). Sem banco: o Supabase é um fake mínimo."""
from datetime import datetime
from types import SimpleNamespace

import pytest

from core import tempo


@pytest.mark.cenario("F6-T1", "para_br: 23:30 BRT (02:30Z do dia seguinte) continua no dia certo; sem fuso é tratado como UTC")
def test_para_br():
    assert tempo.para_br("2026-11-13T02:30:00+00:00") == datetime(2026, 11, 12, 23, 30)
    assert tempo.para_br("2026-11-13T02:30:00Z") == datetime(2026, 11, 12, 23, 30)
    assert tempo.para_br("2026-11-13T02:30:00") == datetime(2026, 11, 12, 23, 30)
    assert tempo.para_br("2026-11-13T03:00:00.123456+00:00") == datetime(2026, 11, 13, 0, 0, 0, 123456)


class _Fake:
    """Responde só o que lancar_folha_contas_a_pagar consulta; guarda o insert."""

    def __init__(self, dia_folha):
        self.dia_folha, self.inserido = dia_folha, None

    def table(self, nome):
        self.nome = nome
        return self

    def select(self, *_):
        return self

    def eq(self, *_):
        return self

    def insert(self, dados):
        self.inserido = dados
        return self

    def execute(self):
        if self.inserido is not None:
            return SimpleNamespace(data=[{"id": "00000000-0000-0000-0000-000000000001"}])
        if self.nome == "usuarios":
            return SimpleNamespace(data=[{"salario_base": 1000, "vale_transporte": 0, "vale_refeicao": 0}])
        return SimpleNamespace(data=[{"dia_pagamento_folha": self.dia_folha}])


@pytest.mark.cenario("F6-T2", "Folha: dia de pagamento 31 vira o último dia do mês (fev, abril, dezembro); depois do dia, vai para o mês seguinte")
@pytest.mark.parametrize(
    "hoje, dia, esperado",
    [
        (datetime(2027, 2, 10), 31, "2027-02-28"),
        (datetime(2028, 2, 10), 31, "2028-02-29"),
        (datetime(2026, 4, 1), 31, "2026-04-30"),
        (datetime(2026, 11, 12), 5, "2026-12-05"),   # já passou do dia 5 → próximo mês
        (datetime(2026, 12, 20), 5, "2027-01-05"),   # vira o ano
        (datetime(2026, 1, 31), 31, "2026-01-31"),
        (datetime(2026, 1, 31, 23, 30), 30, "2026-02-28"),  # 31 > 30 → fev, que não tem dia 30
    ],
)
def test_vencimento_folha(monkeypatch, hoje, dia, esperado):
    from modules.equipe import service
    from modules.equipe.schemas import LancarFolhaInput

    fake = _Fake(dia)
    monkeypatch.setattr(service, "supabase", fake)
    monkeypatch.setattr(service, "agora_br", lambda: hoje)
    service.lancar_folha_contas_a_pagar("e", LancarFolhaInput(mes_referencia="x"))
    assert fake.inserido["data_vencimento"] == esperado
