"""Requisições paralelas (a tela dispara ~8 de uma vez) não podem falhar nem virar "token inválido".

Antes: o cliente do Supabase usava HTTP/2 numa única conexão compartilhada entre as threads do FastAPI; com
chamadas simultâneas saíam httpx.ReadError / ConnectionTerminated (500) e o backend ainda respondia 401
"Token inválido" para tokens válidos. Este teste sobe um servidor de verdade (threads reais), como em produção.
"""
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

import core.security as security
from tests.conftest import integracao, com_registro
from tests.homologacao import EMPRESA_A

RAIZ = Path(__file__).resolve().parent.parent
PORTA = 8765
LOG = RAIZ / "tests" / ".servidor.log"


@pytest.fixture(scope="module")
def servidor():
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", str(PORTA), "--log-level", "warning"],
        cwd=RAIZ, env={**os.environ, "PYTHONIOENCODING": "utf-8"}, stdout=LOG.open("w", encoding="utf-8"), stderr=subprocess.STDOUT,
    )
    base = f"http://127.0.0.1:{PORTA}"
    try:
        for _ in range(60):
            try:
                if httpx.get(f"{base}/", timeout=2).status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.5)
        else:
            pytest.fail("servidor de teste não subiu")
        yield base
    finally:
        proc.terminate()
        proc.wait(timeout=15)


@integracao
@pytest.mark.cenario("F3-P1", "60 requisições simultâneas (8 rotas) com token válido: todas 200, nenhum 401/500")
def test_requisicoes_paralelas(servidor, token):
    tok = token("DONO", "a")
    rotas = [f"/dashboards/{EMPRESA_A}", f"/os/?empresa_id={EMPRESA_A}", f"/estoque/{EMPRESA_A}",
             f"/clientes/{EMPRESA_A}", f"/veiculos/{EMPRESA_A}", "/empresas/", f"/empresas/{EMPRESA_A}/configuracoes",
             f"/transacoes-financeiras/{EMPRESA_A}"]
    chamadas = (rotas * 60)[:int(os.getenv("STRESS_N", "60"))]
    with com_registro(httpx.Client(base_url=f"{servidor}/api/v1", timeout=30, limits=httpx.Limits(max_connections=30))) as cli:
        with ThreadPoolExecutor(max_workers=30) as pool:
            def chamar(rota):
                try:
                    return cli.get(rota, headers={"Authorization": f"Bearer {tok}"}).status_code
                except httpx.HTTPError as e:  # conexão derrubada pelo servidor também é falha
                    return f"{type(e).__name__}"
            codigos = list(pool.map(chamar, chamadas))
    ruins = {c: codigos.count(c) for c in set(codigos) if c != 200}
    assert not ruins, f"respostas diferentes de 200: {ruins}"


@pytest.mark.cenario("F3-P2", "Falha de infraestrutura na checagem do token → 503 (a tela repete); token inválido → 401")
def test_erro_de_infra_nao_vira_token_invalido(monkeypatch):
    from fastapi.testclient import TestClient
    from main import app
    from supabase_auth.errors import AuthApiError

    def com_auth(erro):
        def get_user(_):
            raise erro
        monkeypatch.setattr(security, "supabase", SimpleNamespace(auth=SimpleNamespace(get_user=get_user)))
        return com_registro(TestClient(app))

    url = f"/api/v1/clientes/{EMPRESA_A}"
    h = {"Authorization": "Bearer qualquer"}
    r = com_auth(httpx.ReadError("conexão derrubada")).get(url, headers=h)
    assert r.status_code == 503 and "indisponível" in r.json()["detail"]
    r = com_auth(AuthApiError("invalid JWT", 401, "bad_jwt")).get(url, headers=h)
    assert r.status_code == 401
