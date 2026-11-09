"""Seed idempotente das empresas de homologação (Oficina do tião = A, TETECA = B).

Uso:  python -m tests.seed        (lê .env.test na raiz do backend)

Cria em cada empresa: DONO, FINANCEIRO, ATENDENTE, MECANICO (Supabase Auth + usuarios),
1 cliente, 1 veículo, 1 OS em ORCAMENTO e 2 itens de estoque. Rodar de novo não duplica nada.
A senha de todos os usuários de teste fica em SEED_SENHA no .env.test (gerada na 1ª execução).
"""
import os
import secrets
import sys

from tests.homologacao import (
    CARGOS, EMPRESAS, ENV_TEST, carregar_env_test, client_admin, email_teste, garantir_empresa_teste,
)


def _senha_seed() -> str:
    senha = os.getenv("SEED_SENHA")
    if not senha:
        senha = secrets.token_urlsafe(18)
        with open(ENV_TEST, "a", encoding="utf-8") as f:
            f.write(f"\nSEED_SENHA={senha}\n")
        os.environ["SEED_SENHA"] = senha
    return senha


def _auth_id_por_email(db, email: str):
    pagina = 1
    while True:
        users = db.auth.admin.list_users(page=pagina, per_page=1000)
        for u in users:
            if (u.email or "").lower() == email:
                return u.id
        if len(users) < 1000:
            return None
        pagina += 1


def _garantir_usuario(db, empresa_id: str, cargo: str, letra: str, senha: str) -> str:
    email = email_teste(cargo, letra)
    linha = db.table("usuarios").select("id, empresa_id").eq("email", email).execute().data
    if linha:
        if linha[0]["empresa_id"] != empresa_id:
            raise RuntimeError(f"{email} existe em outra empresa ({linha[0]['empresa_id']}).")
        db.auth.admin.update_user_by_id(linha[0]["id"], {"password": senha})
        return linha[0]["id"]

    auth_id = _auth_id_por_email(db, email)
    if auth_id:
        db.auth.admin.update_user_by_id(auth_id, {"password": senha})
    else:
        auth_id = db.auth.admin.create_user({"email": email, "password": senha, "email_confirm": True}).user.id

    db.table("usuarios").insert({
        "id": auth_id, "email": email, "nome": f"{cargo.title()} Teste {letra.upper()}",
        "cargo": cargo, "ativo": True, "empresa_id": empresa_id,
    }).execute()
    return auth_id


def _um(db, tabela: str, filtros: dict, novo: dict) -> dict:
    q = db.table(tabela).select("*")
    for k, v in filtros.items():
        q = q.eq(k, v)
    achado = q.limit(1).execute().data
    return achado[0] if achado else db.table(tabela).insert({**filtros, **novo}).execute().data[0]


def seed_empresa(db, letra: str, empresa_id: str, senha: str) -> dict:
    garantir_empresa_teste(db, empresa_id)
    usuarios = {c: _garantir_usuario(db, empresa_id, c, letra, senha) for c in CARGOS}

    cliente = _um(db, "clientes", {"empresa_id": empresa_id, "telefone": f"1199999000{ord(letra) - 96}"},
                  {"nome": f"Cliente Teste {letra.upper()}"})
    veiculo = _um(db, "veiculos", {"empresa_id": empresa_id, "placa": f"TST{letra.upper()}001"},
                  {"cliente_id": cliente["id"], "modelo": "Gol 1.0", "marca": "VW", "km_atual": 50000})
    os_ = _um(db, "ordens_servico", {"empresa_id": empresa_id, "veiculo_id": veiculo["id"], "status": "ORCAMENTO"},
              {"cliente_id": cliente["id"], "mecanico_responsavel_id": usuarios["MECANICO"],
               "descricao_problema": "OS de teste (seed)"})
    for nome, custo, venda in (("Filtro de óleo TESTE", 20, 45), ("Óleo 5W30 TESTE", 30, 60)):
        _um(db, "estoque", {"empresa_id": empresa_id, "nome": nome},
            {"categoria": "PECAS", "quantidade": 10, "minimo_alerta": 2, "custo": custo, "venda": venda})

    return {"usuarios": usuarios, "cliente": cliente["id"], "veiculo": veiculo["id"], "os": os_["id"]}


def main() -> int:
    if not carregar_env_test():
        print(f"Crie {ENV_TEST} a partir de .env.test.example.", file=sys.stderr)
        return 1
    db = client_admin()
    senha = _senha_seed()
    for letra, empresa_id in EMPRESAS.items():
        r = seed_empresa(db, letra, empresa_id, senha)
        print(f"Empresa {letra.upper()} ({empresa_id}): {len(r['usuarios'])} usuários, OS {r['os']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
