"""T-013 — Fase 8: erro do banco nunca vaza, limites das colunas varchar (R5), ponto, folha, escala e formas de pagamento (R7). Sem rede."""
import os

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("GEMINI_API_KEY", "test")

import asyncio
import json
import logging
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from postgrest.exceptions import APIError
from pydantic import ValidationError

import core.security as security
from core.errors import supabase_exception_handler
from core.pagamento import FORMAS_PAGAMENTO
from main import app
from modules.bot.schemas import CadastroRapidoRequest
from modules.clientes.schemas import ClienteCreate, ClienteUpdate
from modules.empresas.schemas import ConfigUpdate
from modules.equipe.schemas import EscalaFolgaCreate, LancarFolhaInput, PontoEletronicoCreate
from modules.estoque.schemas import EstoqueCreate, EstoqueUpdate
from modules.os.schemas import OSItemCreate, OSItemUpdate, OSUpdate
from modules.transacoes_financeiras.schemas import TransacaoCreate, TransacaoLiquidar, TransacaoResponse, TransacaoUpdate
from modules.usuarios.schemas import UsuarioCreate, UsuarioUpdate
from modules.veiculos.schemas import VeiculoCreate, VeiculoUpdate
from tests.conftest import com_registro

E = "11111111-1111-1111-1111-111111111111"
U = "33333333-3333-3333-3333-333333333333"


def _resposta(exc):
    r = asyncio.run(supabase_exception_handler(SimpleNamespace(method="POST", url=SimpleNamespace(path="/x")), exc))
    return r.status_code, json.loads(r.body)["detail"]


# ------------------------------------------------------------------ errors.py
@pytest.mark.cenario("F8-1", "Erro de banco desconhecido: mensagem genérica em português para o cliente, texto cru só no log")
def test_erro_nao_mapeado(caplog):
    cru = 'relation "tabela_secreta" does not exist (SQLSTATE 42P01)'
    with caplog.at_level(logging.ERROR, logger="mecanify.erros"):
        status, msg = _resposta(APIError({"message": cru, "code": "42P01"}))
    assert status == 400 and "tabela_secreta" not in msg and "42P01" not in msg and "Postgres" not in msg
    assert "Não foi possível concluir a operação" in msg
    assert "tabela_secreta" in caplog.text and "POST /x" in caplog.text


@pytest.mark.cenario("F8-2", "22001 (texto grande demais) → 422 em português com o limite")
def test_22001():
    status, msg = _resposta(APIError({"message": "value too long for type character varying(30)", "code": "22001"}))
    assert status == 422 and "máximo de 30 caracteres" in msg and "varying" not in msg
    assert _resposta(APIError({"message": "value too long", "code": "22001"}))[0] == 422


@pytest.mark.cenario("F8-3", "Erros já mapeados continuam iguais (duplicado 409, obrigatório 422)")
def test_mapeados_continuam():
    assert _resposta(APIError({"message": "dup", "code": "23505"}))[0] == 409
    assert _resposta(APIError({"message": "null", "code": "23502"}))[0] == 422


# ------------------------------------------------------------------ limites (colunas conferidas no AutotecDB)
BASE = {
    ClienteCreate: dict(nome="a", telefone="1", empresa_id=E),
    VeiculoCreate: dict(placa="A", modelo="m", cliente_id=U, empresa_id=E),
    EstoqueCreate: dict(nome="a", empresa_id=E),
    UsuarioCreate: dict(nome="a", email="a@b.com", cargo="DONO", senha="123456"),
    OSItemCreate: dict(tipo="PECA", nome_item="a"),
    CadastroRapidoRequest: dict(empresa_id=E, mecanico_id=U, nome_cliente="a", telefone_cliente="1", placa="A"),
}
LIMITES = [  # (modelo, campo, limite)
    (ClienteCreate, "nome", 150), (ClienteCreate, "telefone", 20), (ClienteCreate, "cpf_cnpj", 20),
    (ClienteUpdate, "nome", 150), (ClienteUpdate, "telefone", 20), (ClienteUpdate, "cpf_cnpj", 20),
    (VeiculoCreate, "placa", 10), (VeiculoCreate, "modelo", 100), (VeiculoCreate, "marca", 50), (VeiculoCreate, "cor", 30),
    (VeiculoUpdate, "placa", 10), (VeiculoUpdate, "modelo", 100), (VeiculoUpdate, "marca", 50), (VeiculoUpdate, "cor", 30),
    (EstoqueCreate, "nome", 200), (EstoqueCreate, "codigo", 50), (EstoqueCreate, "categoria", 30),
    (EstoqueUpdate, "nome", 200), (EstoqueUpdate, "codigo", 50), (EstoqueUpdate, "categoria", 30),
    (UsuarioCreate, "nome", 100), (UsuarioUpdate, "nome", 100),
    (OSItemCreate, "nome_item", 200), (OSItemUpdate, "nome_item", 200),
    (ConfigUpdate, "whatsapp", 30), (ConfigUpdate, "chave_pix", 100), (ConfigUpdate, "inscricao_estadual", 50),
    (CadastroRapidoRequest, "nome_cliente", 150), (CadastroRapidoRequest, "telefone_cliente", 20), (CadastroRapidoRequest, "placa", 10),
    (EscalaFolgaCreate, "observacoes", 500),
]


@pytest.mark.cenario("F8-4", "Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update")
@pytest.mark.parametrize("modelo, campo, limite", LIMITES, ids=[f"{m.__name__}.{c}" for m, c, _ in LIMITES])
def test_limite(modelo, campo, limite):
    base = {**BASE.get(modelo, {}), **(dict(usuario_id=U, tipo="FOLGA", data_inicio="2026-12-01", data_fim="2026-12-02") if modelo is EscalaFolgaCreate else {})}
    modelo(**{**base, campo: "x" * limite}) if campo != "categoria" else modelo(**{**base, campo: "X" * limite})
    with pytest.raises(ValidationError):
        modelo(**{**base, campo: "x" * (limite + 1)})


@pytest.mark.cenario("F8-5", "E-mail de usuário acima de 255 → 422")
def test_email_limite():
    ok = "a" * 60 + "@b.com"
    UsuarioCreate(nome="a", email=ok, cargo="DONO", senha="123456")
    with pytest.raises(ValidationError):
        UsuarioUpdate(email="a" * 250 + "@b.com")


# ------------------------------------------------------------------ ponto, folha, escala
@pytest.mark.cenario("F8-6", "Ponto: latitude -90..90 e longitude -180..180; fora → 422")
@pytest.mark.parametrize("lat, lon, ok", [(-90, -180, True), (90, 180, True), (-23.5, -46.6, True), (None, None, True),
                                          (90.1, 0, False), (-90.1, 0, False), (0, 180.1, False), (0, -180.1, False)])
def test_ponto(lat, lon, ok):
    if ok:
        PontoEletronicoCreate(tipo="ENTRADA", latitude=lat, longitude=lon)
    else:
        with pytest.raises(ValidationError):
            PontoEletronicoCreate(tipo="ENTRADA", latitude=lat, longitude=lon)


@pytest.mark.cenario("F8-7", "Folha: mes_referencia só MM/AAAA válido")
@pytest.mark.parametrize("valor, ok", [("01/2026", True), ("12/2026", True), ("10/2099", True),
                                       ("13/2026", False), ("00/2026", False), ("1/2026", False), ("2026-10", False),
                                       ("10/26", False), ("outubro", False), ("", False), ("10/2026 ", False), ("10/1999", False)])
def test_folha(valor, ok):
    if ok:
        LancarFolhaInput(mes_referencia=valor)
    else:
        with pytest.raises(ValidationError):
            LancarFolhaInput(mes_referencia=valor)


# ------------------------------------------------------------------ R7 formas de pagamento
@pytest.mark.cenario("F8-8", "Formas de pagamento: lista única (inclui TED e as do front); fora da lista → 422 em OS, lançamento, edição e baixa")
def test_formas_pagamento():
    assert FORMAS_PAGAMENTO == ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro", "Boleto / Faturado", "TED / Transferência"]
    lanc = dict(tipo="DESPESA", descricao="d", categoria="c", valor=1, data_vencimento="2026-12-01", empresa_id=E)
    for f in FORMAS_PAGAMENTO:
        OSUpdate(forma_pagamento=f)
        TransacaoCreate(**lanc, forma_pagamento=f)
        TransacaoUpdate(forma_pagamento=f)
        TransacaoLiquidar(forma_pagamento=f)
    OSUpdate(forma_pagamento=None), TransacaoLiquidar(), TransacaoCreate(**lanc)
    for ruim in ("Cheque", "pix", "", "TED"):
        for criar in (lambda: OSUpdate(forma_pagamento=ruim), lambda: TransacaoCreate(**lanc, forma_pagamento=ruim),
                      lambda: TransacaoUpdate(forma_pagamento=ruim), lambda: TransacaoLiquidar(forma_pagamento=ruim)):
            with pytest.raises(ValidationError):
                criar()


@pytest.mark.cenario("F8-9", "Dado antigo com forma fora da lista continua sendo lido sem erro")
def test_leitura_de_dado_antigo():
    r = TransacaoResponse(id=U, tipo="DESPESA", descricao="d", categoria="c", valor=1, data_vencimento="2026-12-01",
                          empresa_id=E, forma_pagamento="Cheque antigo")
    assert r.forma_pagamento == "Cheque antigo"


class _Banco:
    def table(self, _): return self
    def select(self, *_): return self
    def eq(self, *_): return self
    def execute(self):
        return SimpleNamespace(data=[{"id": "u1", "cargo": "ATENDENTE", "empresa_id": E, "ativo": True}])


@pytest.fixture
def api(monkeypatch):
    app.dependency_overrides[security.validar_token] = lambda: SimpleNamespace(id="u1")
    monkeypatch.setattr(security.supabase, "table", _Banco().table)
    yield com_registro(TestClient(app))
    app.dependency_overrides.clear()


@pytest.mark.cenario("F8-10", "GET /api/v1/formas-pagamento devolve a lista (qualquer perfil logado)")
def test_rota_formas(api):
    r = api.get("/api/v1/formas-pagamento/")
    assert r.status_code == 200 and r.json() == FORMAS_PAGAMENTO


@pytest.mark.cenario("F8-11", "HTTP: texto acima do limite e forma inválida chegam como 422 com mensagem")
def test_http_422(api):
    r = api.post("/api/v1/clientes/", json={"nome": "x" * 151, "telefone": "1", "empresa_id": E})
    assert r.status_code == 422 and "150" in r.text
    r = api.put(f"/api/v1/os/{E}/{U}", json={"forma_pagamento": "Cheque"})
    assert r.status_code == 422 and "Forma de pagamento inválida" in r.text
