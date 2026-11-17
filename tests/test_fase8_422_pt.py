"""T-013 — todo 422 de validação sai em português da oficina, com o campo em nome legível, mantendo detail como lista. Sem rede."""
import os

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("GEMINI_API_KEY", "test")

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import core.security as security
from main import app
from tests.conftest import com_registro

E = "11111111-1111-1111-1111-111111111111"
U = "33333333-3333-3333-3333-333333333333"


class _Banco:
    def table(self, _): return self
    def select(self, *_): return self
    def eq(self, *_): return self
    def execute(self):
        return SimpleNamespace(data=[{"id": "u1", "cargo": "DONO", "empresa_id": E, "ativo": True}])


@pytest.fixture
def api(monkeypatch):
    app.dependency_overrides[security.validar_token] = lambda: SimpleNamespace(id="u1")
    monkeypatch.setattr(security.supabase, "table", _Banco().table)
    yield com_registro(TestClient(app))
    app.dependency_overrides.clear()


def _msgs(r):
    assert r.status_code == 422, r.text
    return [d["msg"] for d in r.json()["detail"]]


CASOS = [  # (método, rota, corpo/params, mensagem esperada) — um por tipo de erro do Pydantic
    ("post", "/api/v1/clientes/", {"json": {"empresa_id": E}}, "Nome do cliente: campo obrigatório."),                      # missing
    ("post", "/api/v1/clientes/", {"json": {"nome": "x" * 151, "telefone": "1", "empresa_id": E}}, "Nome do cliente: máximo de 150 caracteres."),  # string_too_long
    ("post", "/api/v1/veiculos/", {"json": {"modelo": "m", "cliente_id": U, "empresa_id": E}}, "Placa: campo obrigatório."),
    ("post", "/api/v1/estoque/", {"json": {"nome": "a", "quantidade": -1, "empresa_id": E}}, "Quantidade: não pode ser menor que 0."),  # greater_than_equal
    ("post", "/api/v1/transacoes-financeiras/", {"json": {"tipo": "DESPESA", "descricao": "d", "categoria": "c", "valor": 0,
                                                           "data_vencimento": "2026-12-01", "empresa_id": E}}, "Valor: precisa ser maior que 0."),  # greater_than
    ("post", f"/api/v1/equipe/pontos/{E}", {"json": {"tipo": "ENTRADA", "latitude": 91}}, "Latitude: não pode ser maior que 90."),  # less_than_equal
    ("post", f"/api/v1/equipe/pontos/{E}", {"json": {"tipo": "ENTRADA", "latitude": "abc"}}, "Latitude: informe um número."),  # float_parsing
    ("put", f"/api/v1/os/{E}/{U}", {"json": {"km_atual": "abc"}}, "Quilometragem: informe um número inteiro."),  # int_parsing
    ("put", f"/api/v1/os/{E}/{U}", {"json": {"status": "XYZ"}}, "Situação da OS: valor não permitido."),  # literal_error
    ("put", f"/api/v1/os/{E}/{U}", {"json": {"forma_pagamento": "Cheque"}}, None),  # value_error (regra do projeto, já em português)
    ("post", "/api/v1/clientes/", {"json": {"nome": "a", "telefone": "1", "empresa_id": "xx"}}, "Oficina: identificador inválido."),  # uuid_parsing
    ("post", "/api/v1/transacoes-financeiras/", {"json": {"tipo": "DESPESA", "descricao": "d", "categoria": "c", "valor": 1,
                                                           "data_vencimento": "ontem", "empresa_id": E}}, "Data de vencimento: data inválida (use AAAA-MM-DD)."),  # date_parsing
    ("post", f"/api/v1/usuarios/{E}", {"json": {"nome": "a", "email": "sem-arroba", "cargo": "DONO", "senha": "123456"}}, "E-mail: e-mail inválido."),
    ("post", f"/api/v1/usuarios/{E}", {"json": {"nome": "a", "email": "a@b.com", "cargo": "DONO", "senha": "zq9"}}, "Senha: precisa ter pelo menos 6 caracteres."),  # string_too_short
    ("get", f"/api/v1/clientes/{E}/paginado?limit=500", {}, "Itens por página: não pode ser maior que 200."),  # parâmetro de URL
    ("post", f"/api/v1/equipe/folha/{E}/lancar-contas-a-pagar", {"json": {"mes_referencia": "13/2026"}}, "Mês de referência: use o formato MM/AAAA, por exemplo 10/2026."),
    ("post", f"/api/v1/equipe/escalas/{E}", {"json": {"usuario_id": U, "tipo": "FOLGA", "data_inicio": "2026-12-25", "data_fim": "2026-12-24"}},
     "A data final não pode ser antes da data inicial."),
    ("post", "/api/v1/clientes/", {"content": "{", "headers": {"content-type": "application/json"}}, "Os dados enviados estão em formato inválido."),  # json_invalid
]


@pytest.mark.cenario("F8-12", "422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)")
@pytest.mark.parametrize("metodo, rota, args, esperado", CASOS, ids=[f"{c[0]}-{i}" for i, c in enumerate(CASOS)])
def test_422_em_portugues(api, metodo, rota, args, esperado):
    msgs = _msgs(getattr(api, metodo)(rota, **args))
    if esperado is None:
        assert any(m.startswith("Forma de pagamento inválida.") for m in msgs), msgs
    else:
        assert esperado in msgs, msgs
    assert not any("String should" in m or "Field required" in m or "Input should" in m or "valid" in m.lower().split() for m in msgs), msgs


@pytest.mark.cenario("F8-13", "detail continua lista de {loc,msg,type}; input e senha digitada não são devolvidos")
def test_formato_e_sem_eco(api):
    r = api.post(f"/api/v1/usuarios/{E}", json={"nome": "a", "email": "a@b.com", "cargo": "DONO", "senha": "zq9"})
    d = r.json()["detail"]
    assert isinstance(d, list) and all(set(x) == {"loc", "msg", "type"} for x in d)
    assert d[0]["loc"] == ["body", "senha"] and d[0]["type"] == "string_too_short"
    assert "zq9" not in r.text


@pytest.mark.cenario("F8-14", "Vários erros no mesmo envio vêm todos, cada um com o seu campo")
def test_varios_erros(api):
    msgs = _msgs(api.post("/api/v1/clientes/", json={"nome": "x" * 151, "empresa_id": E}))
    assert "Nome do cliente: máximo de 150 caracteres." in msgs and "Telefone: campo obrigatório." in msgs
