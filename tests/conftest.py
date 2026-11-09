import json
import os
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from tests.homologacao import DOMINIO_EMAIL, EMPRESAS, carregar_env_test, email_teste

# Carrega .env.test antes de qualquer teste importar `main` (core.database lê o env no import).
TEM_ENV_TEST = carregar_env_test()

integracao = pytest.mark.skipif(
    not (TEM_ENV_TEST and os.getenv("SUPABASE_ANON_KEY") and os.getenv("SEED_SENHA")),
    reason="Integração: precisa de .env.test com SUPABASE_ANON_KEY e SEED_SENHA (rode python -m tests.seed).",
)

PASTA_RELATORIOS = Path(__file__).resolve().parent.parent / "auditorias"


# ---------------------------------------------------------------- relatório .md
_resultados = []      # um item por teste executado
_trocas_atuais = []   # request/response do teste em andamento


def _mascarar(texto: str) -> str:
    texto = re.sub(r"eyJ[\w-]+\.[\w-]+\.[\w-]+", "<JWT>", texto)
    for chave in ("SUPABASE_SERVICE_KEY", "SUPABASE_ANON_KEY", "SEED_SENHA"):
        valor = os.getenv(chave)
        if valor:
            texto = texto.replace(valor, f"<{chave}>")
    return texto


def _corpo(conteudo: bytes) -> str:
    if not conteudo:
        return ""
    try:
        texto = json.dumps(json.loads(conteudo), ensure_ascii=False, indent=2)
    except ValueError:
        texto = conteudo.decode("utf-8", "replace")
    texto = _mascarar(texto)
    return texto if len(texto) <= 3000 else texto[:3000] + "\n... (truncado)"


def _ao_responder(response):
    response.read()
    req = response.request
    headers = {k: ("<mascarado>" if k.lower() in ("authorization", "apikey") else v)
               for k, v in req.headers.items() if k.lower() in ("authorization", "apikey", "content-type")}
    _trocas_atuais.append({
        "request": f"{req.method} {_mascarar(str(req.url))}",
        "headers": headers,
        "request_body": _corpo(req.content),
        "status": response.status_code,
        "response_body": _corpo(response.content),
    })


def com_registro(client):
    """Liga a gravação de request/response num httpx.Client / TestClient."""
    client.event_hooks = {"request": [], "response": [_ao_responder]}
    return client


def pytest_configure(config):
    config.addinivalue_line("markers", "cenario(id, descricao): cenário do PLANO_CORRECAO.md coberto pelo teste")


@pytest.fixture(autouse=True)
def _limpar_trocas():
    _trocas_atuais.clear()
    yield


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    rep = (yield).get_result()
    if rep.when == "call" or (rep.when == "setup" and rep.skipped):
        marca = item.get_closest_marker("cenario")
        _resultados.append({
            "teste": item.nodeid,
            "cenario": f"{marca.args[0]} — {marca.args[1]}" if marca else "—",
            "resultado": "PASSOU" if rep.passed else ("PULADO" if rep.skipped else "FALHOU"),
            "detalhe": _mascarar(str(rep.longrepr))[-1500:] if rep.failed or rep.skipped else "",
            "trocas": list(_trocas_atuais),
        })


def pytest_sessionfinish(session, exitstatus):
    if not _resultados:
        return
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    PASTA_RELATORIOS.mkdir(exist_ok=True)
    arquivo = PASTA_RELATORIOS / f"testes-backend-{agora:%Y%m%d-%H%M%S}.md"
    total = {k: sum(r["resultado"] == k for r in _resultados) for k in ("PASSOU", "FALHOU", "PULADO")}

    linhas = [
        f"# Execução dos testes do backend — {agora:%d/%m/%Y %H:%M:%S} (BRT)",
        "",
        f"Banco: AutotecDB, só empresas `empresa_teste = true`. Tokens e chaves mascarados.",
        "",
        f"**Resumo:** {total['PASSOU']} passaram · {total['FALHOU']} falharam · {total['PULADO']} pulados",
        "",
        "| # | Teste | Cenário do plano | Resultado |",
        "|---|---|---|---|",
    ]
    for i, r in enumerate(_resultados, 1):
        linhas.append(f"| {i} | `{r['teste'].split('::', 1)[-1]}` | {r['cenario']} | {r['resultado']} |")

    for i, r in enumerate(_resultados, 1):
        linhas += ["", "---", "", f"## {i}. `{r['teste']}`", "",
                   f"- **Cenário:** {r['cenario']}", f"- **Resultado:** {r['resultado']}"]
        if r["detalhe"]:
            linhas += ["", "```", r["detalhe"], "```"]
        if not r["trocas"]:
            linhas += ["", "_Sem chamadas HTTP (teste de função/banco)._"]
        for j, t in enumerate(r["trocas"], 1):
            linhas += ["", f"### Chamada {j}", "", f"**Request:** `{t['request']}`", "",
                       f"Headers: `{json.dumps(t['headers'], ensure_ascii=False)}`"]
            if t["request_body"]:
                linhas += ["", "```json", t["request_body"], "```"]
            linhas += ["", f"**Response:** `{t['status']}`", "", "```json", t["response_body"] or "(vazio)", "```"]

    arquivo.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"\nRelatório: {arquivo}")


# ---------------------------------------------------------------- fixtures
@pytest.fixture(scope="session")
def admin():
    from tests.homologacao import client_admin
    return client_admin()


@pytest.fixture(scope="session")
def token():
    """token('DONO', 'a') → access_token de um usuário do seed (só empresas de teste)."""
    from supabase import create_client
    cache = {}

    def _login(cargo: str, letra: str) -> str:
        assert letra in EMPRESAS, "Só empresas de homologação (a/b)."
        if (cargo, letra) not in cache:
            anon = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
            sessao = anon.auth.sign_in_with_password(
                {"email": email_teste(cargo, letra), "password": os.environ["SEED_SENHA"]}
            ).session
            cache[(cargo, letra)] = sessao.access_token
        return cache[(cargo, letra)]

    return _login


@pytest.fixture(scope="session")
def seed_ids(admin):
    """IDs do seed por empresa: seed_ids['a']['cliente'|'veiculo'|'os'|'MECANICO'|...]."""
    ids = {}
    for letra, empresa_id in EMPRESAS.items():
        cli = admin.table("clientes").select("id").eq("empresa_id", empresa_id).eq("nome", f"Cliente Teste {letra.upper()}").execute().data
        vei = admin.table("veiculos").select("id").eq("empresa_id", empresa_id).eq("placa", f"TST{letra.upper()}001").execute().data
        os_ = admin.table("ordens_servico").select("id").eq("empresa_id", empresa_id).eq("veiculo_id", vei[0]["id"]).limit(1).execute().data
        est = admin.table("estoque").select("id").eq("empresa_id", empresa_id).eq("nome", "Filtro de óleo TESTE").execute().data
        ids[letra] = {"empresa": empresa_id, "cliente": cli[0]["id"], "veiculo": vei[0]["id"], "os": os_[0]["id"], "estoque": est[0]["id"]}
        for u in admin.table("usuarios").select("id, cargo").eq("empresa_id", empresa_id).like("email", f"%@{DOMINIO_EMAIL}").execute().data:
            ids[letra][u["cargo"]] = u["id"]
    return ids


@pytest.fixture(scope="session")
def api():
    from fastapi.testclient import TestClient
    from main import app
    return com_registro(TestClient(app))


@pytest.fixture
def http():
    import httpx
    with com_registro(httpx.Client(timeout=15)) as c:
        yield c
