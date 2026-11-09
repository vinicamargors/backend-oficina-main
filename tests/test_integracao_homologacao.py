"""Integração contra o AutotecDB usando só as empresas de homologação do seed."""
import os

import httpx
import pytest

from tests.conftest import integracao
from tests.homologacao import EMPRESA_A, EMPRESA_B, EmpresaProducaoError, garantir_empresa_teste

AUTOTEC_RACING = "caabdcdd-f537-42a6-8db1-35cb02257284"

pytestmark = integracao


def _h(tok):
    return {"Authorization": f"Bearer {tok}"}


def test_guarda_recusa_empresa_de_producao(admin):
    with pytest.raises(EmpresaProducaoError):
        garantir_empresa_teste(admin, AUTOTEC_RACING)
    garantir_empresa_teste(admin, EMPRESA_A)


def test_dono_ve_a_propria_empresa(api, token):
    r = api.get(f"/api/v1/clientes/{EMPRESA_A}", headers=_h(token("DONO", "a")))
    assert r.status_code == 200
    assert any(c["nome"] == "Cliente Teste A" for c in r.json())


@pytest.mark.parametrize("rota", ["clientes", "veiculos", "estoque", "dashboards"])
def test_dono_nao_ve_outra_empresa(api, token, rota):
    r = api.get(f"/api/v1/{rota}/{EMPRESA_B}", headers=_h(token("DONO", "a")))
    assert r.status_code == 403


def test_mecanico_sem_financeiro(api, token):
    r = api.get(f"/api/v1/transacoes-financeiras/{EMPRESA_A}", headers=_h(token("MECANICO", "a")))
    assert r.status_code == 403


def test_anon_nao_le_nada_pela_api_rest():
    url = f"{os.environ['SUPABASE_URL']}/rest/v1/clientes?select=id&limit=1"
    chave = os.environ["SUPABASE_ANON_KEY"]
    r = httpx.get(url, headers={"apikey": chave, "Authorization": f"Bearer {chave}"})
    assert r.status_code == 200 and r.json() == []
