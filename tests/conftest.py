import os

import pytest

from tests.homologacao import EMPRESAS, carregar_env_test, email_teste

# Carrega .env.test antes de qualquer teste importar `main` (core.database lê o env no import).
TEM_ENV_TEST = carregar_env_test()

integracao = pytest.mark.skipif(
    not (TEM_ENV_TEST and os.getenv("SUPABASE_ANON_KEY") and os.getenv("SEED_SENHA")),
    reason="Integração: precisa de .env.test com SUPABASE_ANON_KEY e SEED_SENHA (rode python -m tests.seed).",
)


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
def api():
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)
