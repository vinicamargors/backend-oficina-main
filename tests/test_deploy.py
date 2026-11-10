"""Fase 4.1 — o que a imagem de produção precisa: /health sem banco e CORS fechado pela variável ALLOWED_ORIGINS."""
import importlib
import os

import pytest
from fastapi.testclient import TestClient

import main

ORIGEM = "https://app.mecanify.com.br"


def _preflight(client, origem):
    h = {"Origin": origem, "Access-Control-Request-Method": "GET"}
    return client.options("/api/v1/health", headers=h).headers.get("access-control-allow-origin")


@pytest.mark.cenario("F41-H", "GET /api/v1/health responde 200 sem token e sem tocar o banco")
def test_health():
    r = TestClient(main.app).get("/api/v1/health")
    assert r.status_code == 200 and r.json() == {"status": "ok"}


@pytest.mark.cenario("F41-C", "Com ALLOWED_ORIGINS só o domínio do app passa no CORS; sem a variável tudo passa (compatível com o Render)")
def test_cors_por_variavel(monkeypatch):
    try:
        monkeypatch.setenv("ALLOWED_ORIGINS", ORIGEM)
        fechado = TestClient(importlib.reload(main).app)
        assert _preflight(fechado, ORIGEM) == ORIGEM
        assert _preflight(fechado, "https://evil.example") is None
        monkeypatch.delenv("ALLOWED_ORIGINS")
        aberto = TestClient(importlib.reload(main).app)
        assert _preflight(aberto, "https://qualquer.example") == "https://qualquer.example"
    finally:
        monkeypatch.undo()
        importlib.reload(main)


@pytest.mark.cenario("F41-K", "Chave do Supabase do SERVIDOR inválida (config errada) → 503 e log claro, não 401 'token inválido' que desloga todo mundo")
def test_chave_do_servidor_invalida_nao_vira_token_invalido(monkeypatch):
    from types import SimpleNamespace
    from supabase_auth.errors import AuthApiError
    import core.security as security

    def get_user(_):
        raise AuthApiError("Invalid API key", 401, None)  # o que o Supabase responde a uma service_role errada

    monkeypatch.setattr(security, "supabase", SimpleNamespace(auth=SimpleNamespace(get_user=get_user)))
    r = TestClient(main.app).get("/api/v1/usuarios/me", headers={"Authorization": "Bearer qualquer"})
    assert r.status_code == 503 and "servidor" in r.json()["detail"].lower()

    def get_user_token_ruim(_):
        raise AuthApiError("invalid JWT: unable to parse", 403, "bad_jwt")  # token do usuário inválido de verdade

    monkeypatch.setattr(security, "supabase", SimpleNamespace(auth=SimpleNamespace(get_user=get_user_token_ruim)))
    assert TestClient(main.app).get("/api/v1/usuarios/me", headers={"Authorization": "Bearer qualquer"}).status_code == 401


@pytest.mark.cenario("F41-A", "deploy/cloud-init.yaml é ASCII puro: acento colado no console da Oracle vira byte Latin-1 e o cloud-init descarta o arquivo inteiro")
def test_cloud_init_so_ascii():
    from pathlib import Path
    texto = (Path(main.__file__).parent / "deploy" / "cloud-init.yaml").read_bytes()
    fora = [(i, b) for i, b in enumerate(texto) if b > 127]
    assert not fora, f"{len(fora)} bytes fora do ASCII (primeiro na posição {fora[0][0]})"
