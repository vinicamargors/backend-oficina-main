"""Fase 7 (T-003): período do Financeiro no banco, resumo do estoque e bot (domínios, async, match exato). Sem rede."""
import os

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("GEMINI_API_KEY", "test")

import asyncio
import json
import re
from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from core import tempo
from modules.bot import service as bot
from modules.bot.schemas import ProcessarAudioRequest
from modules.estoque import service as estoque
from modules.financeiro import service as fin

E = "11111111-1111-1111-1111-111111111111"
HOJE = datetime(2026, 11, 16, 12, 0, tzinfo=tempo.FUSO_BR)


def _ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


class _Banco:
    """Supabase falso que faz o que o banco faz: aplica eq/in_/or_ (no formato de _no_periodo) e a janela range."""
    def __init__(self, linhas):
        self.linhas, self.filtros, self.chamadas = linhas, [], []
    def table(self, _):
        self.filtros = []
        return self
    def select(self, *_): return self
    def order(self, *_): return self
    def eq(self, col, v):
        self.filtros.append(lambda r: r.get(col, v) == v); return self
    def in_(self, col, vs):
        self.filtros.append(lambda r: r.get(col) in vs); return self
    def or_(self, expr):
        self.chamadas.append(expr)
        def passa(r):
            for g in re.findall(r"and\(([^)]*)\)", expr):
                if all(self._cond(r, c) for c in g.split(",")):
                    return True
            return False
        self.filtros.append(passa); return self
    @staticmethod
    def _cond(r, c):
        col, op, *val = c.split(".", 2)
        v = r.get(col)
        if op == "is": return v is None
        if v is None: return False
        return _ts(v) >= _ts(val[0]) if op == "gte" else _ts(v) <= _ts(val[0])
    def range(self, ini, fim):
        self.ini, self.fim = ini, fim; return self
    def execute(self):
        return SimpleNamespace(data=[r for r in self.linhas if all(f(r) for f in self.filtros)][self.ini:self.fim + 1])


def _os(status, total, lucro, abertura, fechamento=None, emp=E):
    return {"empresa_id": emp, "status": status, "total_geral": total, "lucro_estimado": lucro,
            "data_abertura": abertura, "data_fechamento": fechamento}


LINHAS = [
    _os("PAGO", 100, 40, "2026-11-01T00:00:00Z", "2026-11-12T02:30:00Z"),   # 11/11 23:30 BRT
    _os("PAGO", 200, 50, "2026-11-01T00:00:00Z", "2026-11-12T03:00:00Z"),   # 12/11 00:00 BRT
    _os("EXECUCAO", 300, 0, "2026-11-10T15:00:00Z"),
    _os("FINALIZADO", 400, 100, "2026-08-01T00:00:00Z", "2026-09-01T12:00:00Z"),  # >30 dias: conta como pago
    _os("FINALIZADO", 50, 5, "2026-11-01T00:00:00Z", "2026-11-10T12:00:00Z"),     # <30 dias: projetado
    _os("PAGO", 70, 10, "2026-06-01T00:00:00Z", "2026-06-15T12:00:00Z"),
    _os("PAGO", 999, 99, "2026-03-01T00:00:00Z", "2026-03-01T12:00:00Z"),          # fora dos 6 meses
    _os("PAGO", 10, 1, "2026-11-13T01:00:00Z"),                                    # sem fechamento: 12/11 22:00 BRT
    _os("ORCAMENTO", 5, 0, "2026-11-12T20:00:00Z"),
    _os("PAGO", 60, 6, "2026-11-01T00:00:00Z", "2026-11-13T02:59:59Z"),            # 12/11 23:59:59 BRT
    _os("PAGO", 61, 6, "2026-11-01T00:00:00Z", "2026-11-13T03:00:00Z"),            # 13/11 00:00 BRT
    _os("PAGO", 7777, 1, "2026-11-12T10:00:00Z", emp="22222222-2222-2222-2222-222222222222"),
]


@pytest.fixture
def banco(monkeypatch):
    b = _Banco(LINHAS)
    monkeypatch.setattr(fin, "supabase", b)
    monkeypatch.setattr(fin, "agora_br", lambda: HOJE)
    return b


@pytest.mark.cenario("F7-F1", "Período do Financeiro vai na query com o dia de Brasília: 12/11 = 03:00Z a 02:59:59Z do dia seguinte")
def test_periodo_na_query(banco):
    fin.obter_dados_financeiros(E, "2026-11-12", "2026-11-12")
    assert "data_fechamento.gte.2026-11-12T03:00:00Z" in banco.chamadas[0]
    assert "data_abertura.lte.2026-11-13T02:59:59Z" in banco.chamadas[0]


@pytest.mark.cenario("F7-F2", "Mesmos totais de antes (valores conferidos contra o código antigo num Postgres real): 23:30 BRT fica no dia 11, 00:00 e 23:59:59 no 12")
@pytest.mark.parametrize("ini, fim, esperado", [
    (None, None, (1900.0, 355.0, 312.0, 237.5)),
    ("2026-11-12", "2026-11-12", (270.0, 5.0, 57.0, 90.0)),
    ("2026-11-01", "2026-11-30", (431.0, 355.0, 103.0, 86.2)),
    ("2026-09-01", "2026-09-30", (400.0, 0.0, 100.0, 400.0)),
    ("2026-11-13", "2026-11-13", (61.0, 0.0, 6.0, 61.0)),
    ("2026-11-12", None, (1900.0, 355.0, 312.0, 237.5)),  # só uma das datas: sem filtro (como antes)
])
def test_totais_iguais(banco, ini, fim, esperado):
    r = fin.obter_dados_financeiros(E, ini, fim)
    assert (r["faturamento_pago"], r["faturamento_projetado"], r["lucro_realizado"], r["ticket_medio"]) == esperado


@pytest.mark.cenario("F7-F3", "Histórico de 6 meses não depende do período filtrado")
def test_historico_independe_do_periodo(banco):
    sem = fin.obter_dados_financeiros(E)["historico_6_meses"]
    com = fin.obter_dados_financeiros(E, "2026-11-12", "2026-11-12")["historico_6_meses"]
    assert sem == com
    assert [m["mes_ano"] for m in sem] == ["06/2026", "07/2026", "08/2026", "09/2026", "10/2026", "11/2026"]
    assert sem[0]["faturamento"] == 70.0 and sem[3]["faturamento"] == 400.0  # 03/2026 (999) fica de fora


@pytest.mark.cenario("F7-F4", "Inteligência financeira filtra no banco e ignora OS de outra empresa")
def test_inteligencia_periodo(banco):
    r = fin.obter_inteligencia_financeira(E, "2026-11-13", "2026-11-13")
    assert r["taxa_conversao_orcamentos"] == 100.0  # só a OS PAGO de 13/11 (a de outra empresa não entra)


# ------------------------------------------------------------------ estoque
@pytest.mark.cenario("F7-E1", "Resumo do estoque = stats da listagem completa (mesmos valores)")
def test_resumo_estoque(monkeypatch):
    itens = [{"empresa_id": E, "categoria": "PECAS", "nome": "a", "quantidade": 2, "custo": 10.5, "venda": 20.0, "minimo_alerta": 5},
             {"empresa_id": E, "categoria": "PECAS", "nome": "b", "quantidade": 9, "custo": 3.0, "venda": 7.25, "minimo_alerta": None},
             {"empresa_id": E, "categoria": "PNEUS", "nome": "c", "quantidade": 1, "custo": 100.0, "venda": 150.0, "minimo_alerta": 0}]
    monkeypatch.setattr(estoque, "supabase", _Banco(itens))
    assert estoque.resumo_estoque(E) == estoque.listar_estoque(E)["stats"] == {
        "total_itens": 3, "estoque_baixo": 1, "valor_total_custo": 148.0, "valor_total_venda": 255.25}
    assert estoque.resumo_estoque(E, "pneus")["total_itens"] == 1


# ------------------------------------------------------------------ bot
@pytest.mark.cenario("F7-B1", "url_audio: só https de domínio da lista (ou subdomínio); fora da lista ou lista vazia → erro antes de baixar")
def test_dominios(monkeypatch):
    monkeypatch.setenv("BOT_AUDIO_DOMAINS", "midia.exemplo.com, wa.net")
    bot.validar_url_audio("https://midia.exemplo.com/a.ogg")
    bot.validar_url_audio("https://cdn.wa.net/a.ogg")
    for ruim in ("https://evil.com/a.ogg", "https://wa.net.evil.com/a.ogg", "http://wa.net/a.ogg",
                 "https://evil.com/?x=wa.net", "https://wa.net@evil.com/a.ogg", "file:///etc/passwd", "", "http://169.254.169.254/"):
        with pytest.raises(HTTPException) as e:
            bot.validar_url_audio(ruim)
        assert e.value.status_code == 400, ruim
    monkeypatch.delenv("BOT_AUDIO_DOMAINS")
    with pytest.raises(HTTPException) as e:
        bot.validar_url_audio("https://wa.net/a.ogg")
    assert e.value.status_code == 503


@pytest.mark.cenario("F7-B2", "Normalização de nome de peça")
def test_normalizar():
    assert bot.normalizar_nome("  Filtro  de ÓLEO! ") == "filtro de oleo" == bot.normalizar_nome("filtro de oleo")


class _Tabelas:
    def __init__(self, estoque): self.estoque, self.itens = estoque, []
    def table(self, nome): self.nome = nome; return self
    def select(self, *_): return self
    def eq(self, *_): return self
    def insert(self, d): self.itens.append(d); return self
    def execute(self): return SimpleNamespace(data=self.estoque if self.nome == "estoque" else [])


@pytest.mark.cenario("F7-B3", "processar-audio: domínio fora → 400 sem baixar; Gemini chamado com await no cliente async; match exato, sem match vai sem estoque_id")
def test_processar_audio(monkeypatch):
    monkeypatch.setenv("BOT_AUDIO_DOMAINS", "wa.net")
    baixados, chamadas_gemini, baixas = [], [], []

    async def get(url):
        baixados.append(url)
        return SimpleNamespace(content=b"x", raise_for_status=lambda: None)

    async def gerar(**kw):
        chamadas_gemini.append(kw)
        return SimpleNamespace(text=json.dumps({"itens": [
            {"tipo": "PECA", "nome_item": "Filtro de Óleo", "quantidade": 1, "venda_unitario": 50},
            {"tipo": "PECA", "nome_item": "filtro", "quantidade": 1, "venda_unitario": 10},      # parcial: não casa
            {"tipo": "MAO_OBRA", "nome_item": "Mão de obra - troca", "quantidade": 1, "venda_unitario": 80}]}))

    tabelas = _Tabelas([{"id": "est-oleo", "nome": "filtro de oleo", "custo": 20, "quantidade": 5},
                        {"id": "est-ar", "nome": "Filtro de ar", "custo": 9, "quantidade": 5}])
    monkeypatch.setattr(bot, "supabase", tabelas)
    monkeypatch.setattr(bot, "http_client", SimpleNamespace(get=get))
    monkeypatch.setattr(bot, "gemini_client", SimpleNamespace(aio=SimpleNamespace(models=SimpleNamespace(generate_content=gerar))))
    monkeypatch.setattr(bot, "baixar_estoque", lambda i, e, q: baixas.append((i, q)))
    monkeypatch.setattr(bot, "recalcular_totais_os", lambda _: None)

    ruim = ProcessarAudioRequest(empresa_id=E, os_id="os1", url_audio="https://evil.com/a.ogg")
    with pytest.raises(HTTPException) as e:
        asyncio.run(bot.processar_e_injetar_audio(ruim))
    assert e.value.status_code == 400 and baixados == [] and chamadas_gemini == []

    asyncio.run(bot.processar_e_injetar_audio(ProcessarAudioRequest(empresa_id=E, os_id="os1", url_audio="https://wa.net/a.ogg")))
    assert baixados == ["https://wa.net/a.ogg"] and len(chamadas_gemini) == 1
    assert baixas == [("est-oleo", 1)]
    assert [(i["nome_item"], i["estoque_id"], i["custo_unitario"]) for i in tabelas.itens] == [
        ("Filtro de Óleo", "est-oleo", 20.0), ("filtro", None, 0.0), ("Mão de obra - troca", None, 0.0)]
