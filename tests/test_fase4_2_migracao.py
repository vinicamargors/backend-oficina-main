"""Fase 4.2 — regras de cópia do scripts/migrar_base.py que não precisam de banco."""
import pytest

pytest.importorskip("psycopg")  # dependência só do script de migração, fora do requirements.txt

from scripts import migrar_base as m  # noqa: E402


@pytest.mark.cenario("F42-1", "Cópia usa só as colunas que existem dos dois lados: plano/senha_hash ficam para trás, updated_at novo usa o padrão")
def test_colunas_em_comum():
    origem = ["id", "email", "senha_hash", "nome"]
    destino = {"id": "uuid", "email": "text", "nome": "text", "updated_at": "timestamptz"}
    cols, sql = m.montar_insert("public.usuarios", origem, destino)
    assert cols == ["id", "email", "nome"]
    assert sql == 'insert into public.usuarios ("id", "email", "nome") values (%s, %s, %s)'
    assert m.montar_insert("public.usuarios", origem, destino, ignorar_conflito=True)[1].endswith(" on conflict do nothing")


@pytest.mark.cenario("F42-2", "os_itens/auditoria herdam a empresa da oficina copiada; jsonb vai embrulhado; NULL continua NULL")
def test_valores_da_linha():
    tipos = {"id": "int8", "empresa_id": "uuid", "dados_antes": "jsonb", "dados_depois": "jsonb"}
    linha = {"id": 1, "empresa_id": None, "dados_antes": None, "dados_depois": {"empresa_id": "e1"}}
    v = m.valores(linha, ["empresa_id", "dados_antes", "dados_depois"], tipos, {"empresa_id": "e1"})
    assert v[0] == "e1" and v[1] is None
    assert isinstance(v[2], m.Jsonb) and v[2].obj == {"empresa_id": "e1"}


@pytest.mark.cenario("F42-3", "Toda tabela copiada é apagada no --substituir (senão sobraria lixo da cópia anterior), e os pais só depois dos filhos")
def test_apagar_cobre_tudo():
    apagadas = [t for t, _ in m.APAGAR]
    copiadas = {t for t, _, _ in m.TABELAS} - {"auth.identities"}  # cai em cascata com auth.users
    assert copiadas <= set(apagadas)
    assert apagadas[-1] == "public.empresas"
    assert apagadas.index("public.audit_logs") > apagadas.index("public.usuarios")  # apagar usuário gera auditoria
    assert apagadas.index("public.os_itens") < apagadas.index("public.ordens_servico") < apagadas.index("public.clientes")
