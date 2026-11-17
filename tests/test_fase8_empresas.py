"""T-014 — empresas: criar com desfazer completo, apagar com logins do Auth, busca de login sem list_users() solto.

Unitários usam bancos falsos em memória. A integração cria a PRÓPRIA empresa (marcada empresa_teste) e a apaga no fim;
nunca chama deletar_empresa com id que o teste não criou.
"""
import os

os.environ.setdefault("SUPABASE_URL", "http://localhost")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test")
os.environ.setdefault("GEMINI_API_KEY", "test")

import uuid
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from postgrest.exceptions import APIError
from pydantic import ValidationError

from modules.empresas import service as emp
from modules.empresas.schemas import ConfigUpdate, EmpresaCreate, EmpresaUpdate
from modules.usuarios import service as usu
from tests.conftest import integracao

DADOS = dict(nome_fantasia="Oficina T014", nome_dono="Dono T014", email_dono="dono@t014.example.com", senha_dono="senha123")


# ------------------------------------------------------------------ bancos falsos
class _Tabela:
    def __init__(self, banco, nome):
        self.b, self.nome, self.filtros, self.op, self.payload, self.count_head = banco, nome, [], "select", None, False

    def select(self, *_, count=None, head=False): self.count_head = head; return self
    def insert(self, d): self.op, self.payload = "insert", d; return self
    def update(self, d): self.op, self.payload = "update", d; return self
    def delete(self): self.op = "delete"; return self
    def eq(self, c, v): self.filtros.append((c, v)); return self

    def execute(self):
        b, linhas = self.b, self.b.t[self.nome]
        if self.op == "insert":
            b.chamada(f"insert:{self.nome}")
            row = {"id": str(uuid.uuid4()), **self.payload}
            linhas.append(row)
            return SimpleNamespace(data=[row], count=None)
        alvo = [r for r in linhas if all(r.get(c) == v for c, v in self.filtros)]
        if self.op == "delete":
            b.chamada(f"delete:{self.nome}")
            for r in alvo:
                linhas.remove(r)
        elif self.op == "update":
            for r in alvo:
                r.update(self.payload)
        return SimpleNamespace(data=[] if self.count_head else alvo, count=len(alvo))


class _Admin:
    def __init__(self, banco): self.b = banco
    def create_user(self, d):
        self.b.chamada("auth:create")
        uid = str(uuid.uuid4()); self.b.auth[uid] = d["email"]
        return SimpleNamespace(user=SimpleNamespace(id=uid))
    def delete_user(self, uid):
        self.b.chamada("auth:delete")
        if uid not in self.b.auth:
            raise Exception("User not found")
        del self.b.auth[uid]


class _Banco:
    """Estado em memória + falha injetada num passo. `falhar` = 'insert:empresas' | 'insert:configuracoes_empresa' |
    'auth:create' | 'insert:usuarios' | 'auth:delete' | 'delete:<tabela>'."""
    def __init__(self):
        self.t = {n: [] for n in ("empresas", "configuracoes_empresa", "usuarios", "clientes", "veiculos", "ordens_servico",
                                  "estoque", "transacoes_financeiras", "audit_logs")}
        self.auth, self.falhar, self.log = {}, None, []
        self.auth_api = SimpleNamespace(admin=_Admin(self))
    def chamada(self, nome):
        self.log.append(nome)
        if nome == self.falhar:
            raise Exception("falha simulada em " + nome)
    def table(self, nome): return _Tabela(self, nome)


@pytest.fixture
def banco(monkeypatch):
    b = _Banco()
    monkeypatch.setattr(emp, "supabase", SimpleNamespace(table=b.table))
    monkeypatch.setattr(emp, "supabase_admin", SimpleNamespace(auth=b.auth_api))
    return b


def _vazio(b):
    return not (b.t["empresas"] or b.t["configuracoes_empresa"] or b.t["usuarios"] or b.auth)


# ------------------------------------------------------------------ criar_empresa
@pytest.mark.cenario("T14-1", "criar_empresa feliz: empresa, configuração, login do Auth e perfil DONO criados")
def test_criar_ok(banco):
    e = emp.criar_empresa(EmpresaCreate(**DADOS))
    assert banco.t["empresas"][0]["id"] == e["id"] and len(banco.t["configuracoes_empresa"]) == 1
    assert banco.t["usuarios"][0]["cargo"] == "DONO" and banco.t["usuarios"][0]["id"] in banco.auth


@pytest.mark.cenario("T14-2", "Falha em QUALQUER passo desfaz os anteriores (empresa, configuração, login, perfil) e responde em português")
@pytest.mark.parametrize("passo, status", [("insert:empresas", 500), ("insert:configuracoes_empresa", 500),
                                           ("auth:create", 400), ("insert:usuarios", 500)])
def test_criar_desfaz(banco, passo, status):
    banco.falhar = passo
    with pytest.raises(HTTPException) as e:
        emp.criar_empresa(EmpresaCreate(**DADOS))
    assert e.value.status_code == status
    assert "falha simulada" not in e.value.detail and "Nada foi cadastrado" in e.value.detail or status == 400
    assert _vazio(banco), banco.log


@pytest.mark.cenario("T14-3", "E-mail do dono já existente no Auth: 400 'Já existe um usuário com este e-mail.' e nada fica")
def test_criar_email_existente(banco, monkeypatch):
    def create_user(_):
        raise Exception("A user with this email address has already been registered")
    monkeypatch.setattr(banco.auth_api.admin, "create_user", create_user)
    with pytest.raises(HTTPException) as e:
        emp.criar_empresa(EmpresaCreate(**DADOS))
    assert e.value.status_code == 400 and e.value.detail == "Já existe um usuário com este e-mail."
    assert _vazio(banco)


@pytest.mark.cenario("T14-4", "Se o desfazer também falhar, o erro avisa que ficou pela metade (e vai para o log)")
def test_criar_desfazer_falha(banco, monkeypatch, caplog):
    banco.falhar = "insert:usuarios"
    monkeypatch.setattr(banco.auth_api.admin, "delete_user", lambda uid: (_ for _ in ()).throw(Exception("auth fora do ar")))
    with pytest.raises(HTTPException) as e:
        emp.criar_empresa(EmpresaCreate(**DADOS))
    assert e.value.status_code == 500 and "ficou pela metade" in e.value.detail
    assert "auth fora do ar" in caplog.text and "auth fora do ar" not in e.value.detail


@pytest.mark.cenario("T14-5", "APIError do banco no passo 1 continua indo para o handler global (mensagem mapeada)")
def test_criar_apierror(banco, monkeypatch):
    def boom(_):
        raise APIError({"message": "dup", "code": "23505"})
    monkeypatch.setattr(emp, "supabase", SimpleNamespace(table=lambda n: SimpleNamespace(insert=boom)))
    with pytest.raises(APIError):
        emp.criar_empresa(EmpresaCreate(**DADOS))


# ------------------------------------------------------------------ deletar_empresa
def _empresa_com_usuarios(b, n=2, cargos=("DONO", "MECANICO")):
    eid, outro = str(uuid.uuid4()), str(uuid.uuid4())
    b.t["empresas"] += [{"id": eid}, {"id": outro}]
    ids = []
    for i in range(n):
        uid = str(uuid.uuid4()); ids.append(uid)
        b.auth[uid] = f"u{i}@x"; b.t["usuarios"].append({"id": uid, "empresa_id": eid, "cargo": cargos[i]})
    vizinho = str(uuid.uuid4()); b.auth[vizinho] = "vizinho@x"
    b.t["usuarios"].append({"id": vizinho, "empresa_id": outro, "cargo": "DONO"})
    b.t["configuracoes_empresa"] += [{"empresa_id": eid}, {"empresa_id": outro}]
    return eid, outro, ids, vizinho


@pytest.mark.cenario("T14-6", "deletar_empresa remove os logins do Auth dos usuários DELA e só deles; solta o vínculo da auditoria")
def test_deletar_ok(banco):
    eid, outro, ids, vizinho = _empresa_com_usuarios(banco)
    banco.t["audit_logs"].append({"empresa_id": eid, "tabela": "usuarios"})
    r = emp.deletar_empresa(eid)
    assert r["logins_removidos"] == 2
    assert not any(u in banco.auth for u in ids) and vizinho in banco.auth      # só os dela
    assert [e["id"] for e in banco.t["empresas"]] == [outro]
    assert [u["id"] for u in banco.t["usuarios"]] == [vizinho]
    assert banco.t["audit_logs"] == [{"empresa_id": None, "tabela": "usuarios"}]  # trilha preservada


@pytest.mark.cenario("T14-7", "Empresa com histórico (clientes, OS, lançamentos...) → 400 explicando e NADA é apagado (nem logins)")
@pytest.mark.parametrize("tabela", ["clientes", "veiculos", "ordens_servico", "estoque", "transacoes_financeiras"])
def test_deletar_com_historico(banco, tabela):
    eid, outro, ids, vizinho = _empresa_com_usuarios(banco)
    banco.t[tabela].append({"empresa_id": eid})
    with pytest.raises(HTTPException) as e:
        emp.deletar_empresa(eid)
    assert e.value.status_code == 400 and "histórico" in e.value.detail and "desative" in e.value.detail
    assert len(banco.t["empresas"]) == 2 and len(banco.t["usuarios"]) == 3 and len(banco.auth) == 3
    assert not any(c.startswith(("delete", "auth:delete")) for c in banco.log)


@pytest.mark.cenario("T14-8", "Empresa inexistente → 404; empresa com usuário master → 400; nada apagado")
def test_deletar_404_e_master(banco):
    with pytest.raises(HTTPException) as e:
        emp.deletar_empresa(str(uuid.uuid4()))
    assert e.value.status_code == 404
    eid, *_ = _empresa_com_usuarios(banco, cargos=("master", "DONO"))
    with pytest.raises(HTTPException) as e:
        emp.deletar_empresa(eid)
    assert e.value.status_code == 400 and "plataforma" in e.value.detail
    assert len(banco.auth) == 3 and len(banco.t["empresas"]) == 2


@pytest.mark.cenario("T14-9", "Falha ao remover um login: 502 em português, nada do banco apagado; repetir funciona (login já removido conta como feito)")
def test_deletar_falha_no_auth_e_repete(banco):
    eid, outro, ids, vizinho = _empresa_com_usuarios(banco)
    banco.falhar = "auth:delete"
    with pytest.raises(HTTPException) as e:
        emp.deletar_empresa(eid)
    assert e.value.status_code == 502 and "falha simulada" not in e.value.detail
    assert len(banco.t["empresas"]) == 2 and len(banco.t["usuarios"]) == 3
    banco.falhar = None
    del banco.auth[ids[0]]  # um login já tinha sido removido antes: "not found" não trava
    assert emp.deletar_empresa(eid)["status"] == "sucesso"
    assert not any(u in banco.auth for u in ids) and vizinho in banco.auth


# ------------------------------------------------------------------ usuarios: busca de login
@pytest.mark.cenario("T14-10", "Busca de login por e-mail lê página a página (page/per_page) e PARA ao achar; nunca list_users() solto")
def test_achar_auth_por_email(monkeypatch):
    chamadas = []
    paginas = {1: [SimpleNamespace(id=str(i), email=f"x{i}@a") for i in range(200)],
               2: [SimpleNamespace(id="alvo", email="Alvo@A.com")] + [SimpleNamespace(id=f"y{i}", email=f"y{i}@a") for i in range(199)],
               3: [SimpleNamespace(id="nunca", email="z@a")]}
    def list_users(page=None, per_page=None):
        chamadas.append((page, per_page))
        return paginas.get(page, [])
    monkeypatch.setattr(usu, "supabase_admin", SimpleNamespace(auth=SimpleNamespace(admin=SimpleNamespace(list_users=list_users))))
    assert usu._achar_auth_por_email("alvo@a.com").id == "alvo"
    assert chamadas == [(1, 200), (2, 200)]
    chamadas.clear()
    assert usu._achar_auth_por_email("naoexiste@a.com") is None  # página 3 tem 1 item (<200): acabou
    assert chamadas == [(1, 200), (2, 200), (3, 200)]


@pytest.mark.cenario("T14-11", "atualizar_usuario: senha de usuário sem login com este id usa a busca por e-mail (sem list_users solto)")
def test_trocar_senha_usa_busca(monkeypatch):
    achados, atualizados = [], []
    class Admin:
        def update_user_by_id(self, uid, d):
            if uid == "id-do-perfil":
                raise Exception("User not found")
            atualizados.append((uid, d))
        def list_users(self, page=None, per_page=None):
            achados.append((page, per_page))
            return [SimpleNamespace(id="id-do-auth", email="fulano@x.com")]
    monkeypatch.setattr(usu, "supabase_admin", SimpleNamespace(auth=SimpleNamespace(admin=Admin())))
    tab = SimpleNamespace(select=lambda *a: tab, eq=lambda *a: tab, update=lambda d: tab,
                          execute=lambda: SimpleNamespace(data=[{"id": "id-do-perfil", "email": "fulano@x.com"}]))
    monkeypatch.setattr(usu, "supabase", SimpleNamespace(table=lambda n: tab))
    usu.atualizar_usuario("id-do-perfil", "emp", usu.UsuarioUpdate(senha="nova123"))
    assert achados == [(1, 200)] and atualizados == [("id-do-auth", {"password": "nova123"})]


# ------------------------------------------------------------------ schemas
@pytest.mark.cenario("T14-12", "Schemas de empresa: limites no create, update e config; senha do dono 6..72")
@pytest.mark.parametrize("modelo, campo, limite", [
    (EmpresaCreate, "nome_fantasia", 150), (EmpresaCreate, "razao_social", 150), (EmpresaCreate, "cnpj", 20),
    (EmpresaCreate, "telefone", 30), (EmpresaCreate, "endereco", 300), (EmpresaCreate, "nome_dono", 100),
    (EmpresaCreate, "senha_dono", 72), (EmpresaUpdate, "nome_fantasia", 150), (EmpresaUpdate, "cnpj", 20),
    (EmpresaUpdate, "telefone", 30), (EmpresaUpdate, "endereco", 300), (ConfigUpdate, "nome_exibicao", 150),
    (ConfigUpdate, "cor_primaria", 20),
])
def test_limites_empresa(modelo, campo, limite):
    base = DADOS if modelo is EmpresaCreate else {}
    modelo(**{**base, campo: "x" * limite})
    with pytest.raises(ValidationError):
        modelo(**{**base, campo: "x" * (limite + 1)})


# ------------------------------------------------------------------ integração: banco e Auth reais, empresa do próprio teste
def _marca_teste(admin, empresa_id):
    admin.table("empresas").update({"empresa_teste": True}).eq("id", empresa_id).execute()


def _auth_existe(admin, uid):
    try:
        return bool(admin.auth.admin.get_user_by_id(uid).user)
    except Exception:
        return False


@integracao
@pytest.mark.cenario("T14-13", "Integração: cria empresa de verdade, confere os 4 registros, apaga: tudo some (inclusive o login) e a auditoria fica sem vínculo")
def test_integracao_criar_e_apagar(admin):
    from tests.homologacao import email_teste
    nome = f"Oficina T014 {uuid.uuid4().hex[:8]}"
    dados = EmpresaCreate(nome_fantasia=nome, nome_dono="Dono T014", email_dono=f"t014-{uuid.uuid4().hex[:8]}@homolog-autotec.example.com", senha_dono="Senha-T014-ok")
    criada = emp.criar_empresa(dados)
    eid = criada["id"]
    try:
        _marca_teste(admin, eid)
        dono = admin.table("usuarios").select("id, cargo").eq("empresa_id", eid).execute().data
        assert len(dono) == 1 and dono[0]["cargo"] == "DONO" and _auth_existe(admin, dono[0]["id"])
        assert admin.table("configuracoes_empresa").select("empresa_id").eq("empresa_id", eid).execute().data
        assert admin.table("empresas").select("empresa_teste").eq("id", eid).execute().data[0]["empresa_teste"] is True

        r = emp.deletar_empresa(eid)  # eid foi criado AQUI, neste teste
        assert r["logins_removidos"] == 1
        assert not admin.table("empresas").select("id").eq("id", eid).execute().data
        assert not admin.table("usuarios").select("id").eq("empresa_id", eid).execute().data
        assert not admin.table("configuracoes_empresa").select("empresa_id").eq("empresa_id", eid).execute().data
        assert not _auth_existe(admin, dono[0]["id"])
        assert not admin.table("audit_logs").select("id").eq("empresa_id", eid).execute().data
    finally:
        if admin.table("empresas").select("id").eq("id", eid).execute().data:
            emp.deletar_empresa(eid)


@integracao
@pytest.mark.cenario("T14-14", "Integração: e-mail do dono que já existe no Auth → 400 em português e nenhuma empresa nem login sobra")
def test_integracao_email_existente(admin):
    from tests.homologacao import email_teste
    nome = f"Oficina T014 dup {uuid.uuid4().hex[:8]}"
    dados = EmpresaCreate(nome_fantasia=nome, nome_dono="Dono T014", email_dono=email_teste("DONO", "a"), senha_dono="Senha-T014-ok")
    with pytest.raises(HTTPException) as e:
        emp.criar_empresa(dados)
    assert e.value.status_code == 400 and e.value.detail == "Já existe um usuário com este e-mail."
    assert not admin.table("empresas").select("id").eq("nome_fantasia", nome).execute().data


@pytest.mark.cenario("T14-15", "Statement timeout (57014) ao desfazer/apagar: tenta de novo e conclui; outro erro não é repetido")
def test_retry_timeout():
    n = {"v": 0}
    def acao():
        n["v"] += 1
        if n["v"] < 3:
            raise APIError({"message": "canceling statement due to statement timeout", "code": "57014"})
        return "ok"
    assert emp._com_retry(acao) == "ok" and n["v"] == 3
    n["v"] = 0
    def sempre():
        n["v"] += 1
        raise APIError({"message": "x", "code": "23503"})
    with pytest.raises(APIError):
        emp._com_retry(sempre)
    assert n["v"] == 1
