"""Regras do ambiente de homologação.

O banco de homologação é o MESMO de produção (AutotecDB). Testes, seed e o agente Playwright só podem
tocar empresas com empresas.empresa_teste = true. A Autotec Racing (empresa_teste = false) é cliente real.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

ENV_TEST = Path(__file__).resolve().parent.parent / ".env.test"

EMPRESA_A = "94334e9f-629c-4c65-92f8-e26274ba3973"  # Oficina do tião
EMPRESA_B = "b763e7f1-e35b-4aa4-baa8-c8d586caf705"  # TETECA
EMPRESAS = {"a": EMPRESA_A, "b": EMPRESA_B}
CARGOS = ("DONO", "FINANCEIRO", "ATENDENTE", "MECANICO")


class EmpresaProducaoError(RuntimeError):
    pass


def carregar_env_test() -> bool:
    """Carrega .env.test (fora do git). Devolve False se não existir."""
    if not ENV_TEST.exists():
        return False
    load_dotenv(ENV_TEST, override=True)
    return True


DOMINIO_EMAIL = "homolog-autotec.example.com"  # .test é recusado pelo EmailStr do backend


def email_teste(cargo: str, letra: str) -> str:
    return f"{cargo.lower()}.{letra}@{DOMINIO_EMAIL}"


def garantir_empresa_teste(client, empresa_id: str) -> None:
    """Aborta se a empresa não existir ou não for de teste. Chamar antes de qualquer escrita."""
    res = client.table("empresas").select("empresa_teste").eq("id", str(empresa_id)).execute().data
    if not res or res[0].get("empresa_teste") is not True:
        raise EmpresaProducaoError(
            f"Empresa {empresa_id} não é empresa_teste=true. Testes nunca tocam dados de produção."
        )


def client_admin():
    from supabase import create_client
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
