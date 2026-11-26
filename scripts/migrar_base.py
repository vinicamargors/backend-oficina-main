"""Fase 4.2 — copia oficinas da base antiga (AutotecDB) para a nova (esquema de migrations/100_esquema_sp.sql).

Uso (as URLs de conexão vêm do ambiente, nunca da linha de comando nem do chat):
    pip install "psycopg[binary]"
    ORIGEM_DB_URL=... DESTINO_DB_URL=... python -m scripts.migrar_base --teste
    opções de escolha: --teste (só empresa_teste) | --empresa <uuid> | --todas
    --so-conferir   só valida a origem e mostra as contagens (não precisa do destino)
    --sem-auditoria não copia audit_logs (para oficinas de teste: o histórico é ruído de teste de carga e pesa no plano gratuito)
    --substituir    apaga a oficina no destino e copia de novo. NUNCA depois do corte: apaga o que entrou na base nova.

Garantias:
- a origem é aberta em modo somente leitura;
- cada oficina é uma transação no destino: entra inteira ou não entra;
- se algum dado da origem viola uma regra nova, lista os casos e para antes de gravar qualquer coisa.
O que muda na cópia: colunas que não existem mais (plano, senha_hash) ficam para trás; os_itens herda a empresa da OS;
auditoria sem empresa recupera a empresa de dentro do registro; usuário só do Flask (senha bcrypt) ganha login com a mesma senha.
"""
import argparse
import os
import sys

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

_USUARIOS = "(select id from public.usuarios where empresa_id = %(e)s)"
_AUDIT_ORIGEM = "coalesce(empresa_id::text, coalesce(dados_depois, dados_antes)->>'empresa_id') = %(e)s::text"

# (tabela, filtro na origem, filtro no destino) — na ordem das chaves estrangeiras
TABELAS = [
    ("public.empresas", "id = %(e)s", None),
    ("public.configuracoes_empresa", "empresa_id = %(e)s", None),
    ("auth.users", f"id in {_USUARIOS}", None),
    ("auth.identities", f"user_id in {_USUARIOS}", None),
    ("public.usuarios", "empresa_id = %(e)s", None),
    ("public.clientes", "empresa_id = %(e)s", None),
    ("public.veiculos", "empresa_id = %(e)s", None),
    ("public.estoque", "empresa_id = %(e)s", None),
    ("public.categorias_estoque", "empresa_id = %(e)s", None),
    ("public.ordens_servico", "empresa_id = %(e)s", None),
    ("public.os_itens", "os_id in (select id from public.ordens_servico where empresa_id = %(e)s)", "empresa_id = %(e)s"),
    ("public.avaliacoes_os", "empresa_id = %(e)s", None),
    ("public.escalas_folgas", "empresa_id = %(e)s", None),
    ("public.pontos_eletronicos", "empresa_id = %(e)s", None),
    ("public.transacoes_financeiras", "empresa_id = %(e)s", None),
    ("public.audit_logs", _AUDIT_ORIGEM, "empresa_id = %(e)s"),
]
# tabelas em que a empresa da linha é corrigida para a oficina que está sendo copiada
FORCAR_EMPRESA = {"public.os_itens", "public.audit_logs"}

# usuários da plataforma (sem empresa): copiados uma vez, sem sobrescrever
_MASTERS = "(select id from public.usuarios where empresa_id is null)"
TABELAS_MASTER = [
    ("auth.users", f"id in {_MASTERS}"),
    ("auth.identities", f"user_id in {_MASTERS}"),
    ("public.usuarios", "empresa_id is null"),
]

# apagar no destino (--substituir), dos filhos para os pais; os triggers de auditoria gravam linhas, por isso audit_logs é quase o último
APAGAR = [
    ("public.transacoes_financeiras", "empresa_id = %(e)s"), ("public.pontos_eletronicos", "empresa_id = %(e)s"),
    ("public.escalas_folgas", "empresa_id = %(e)s"), ("public.avaliacoes_os", "empresa_id = %(e)s"),
    ("public.os_itens", "empresa_id = %(e)s"), ("public.ordens_servico", "empresa_id = %(e)s"),
    ("public.categorias_estoque", "empresa_id = %(e)s"), ("public.estoque", "empresa_id = %(e)s"),
    ("public.veiculos", "empresa_id = %(e)s"), ("public.clientes", "empresa_id = %(e)s"),
    ("auth.users", f"id in {_USUARIOS}"),  # identities, sessões e tokens caem em cascata
    ("public.usuarios", "empresa_id = %(e)s"), ("public.configuracoes_empresa", "empresa_id = %(e)s"),
    ("public.audit_logs", "empresa_id = %(e)s"), ("public.empresas", "id = %(e)s"),  # assinaturas caem em cascata
]

# regras novas do esquema: cada consulta devolve os casos que violam (na origem)
REGRAS = [
    ("estoque com quantidade negativa", "select id::text from public.estoque where empresa_id = %(e)s and quantidade < 0"),
    ("transação com tipo ou status fora da lista",
     "select id::text from public.transacoes_financeiras where empresa_id = %(e)s and "
     "(tipo not in ('DESPESA','RECEITA') or status not in ('PENDENTE','LIQUIDADO','ATRASADO','CANCELADO'))"),
    ("escala com fim antes do início", "select id::text from public.escalas_folgas where empresa_id = %(e)s and data_fim < data_inicio"),
    ("mais de uma configuração para a oficina",
     "select empresa_id::text from public.configuracoes_empresa where empresa_id = %(e)s group by 1 having count(*) > 1"),
    ("plano desconhecido (o esquema novo só aceita basico e profissional)",
     "select coalesce(plano, 'vazio') from public.empresas where id = %(e)s and plano is not null and plano not in ('basico','profissional')"),
    ("item de OS sem OS", "select id::text from public.os_itens where empresa_id = %(e)s and os_id is null"),
]

_SEM_LOGIN = (
    "select u.id::text as id, u.nome, lower(u.email) as email, u.senha_hash, u.ativo from public.usuarios u "
    "where u.empresa_id = %(e)s and not exists (select 1 from auth.users a where a.id = u.id)"
)


def colunas(conn, tabela):
    """{coluna: tipo} das colunas que aceitam INSERT (fora as geradas e as identity)."""
    esquema, nome = tabela.split(".")
    return dict(conn.execute(
        "select column_name, udt_name from information_schema.columns where table_schema = %s and table_name = %s "
        "and is_generated = 'NEVER' and identity_generation is distinct from 'ALWAYS' order by ordinal_position",
        (esquema, nome)).fetchall())


def montar_insert(tabela, col_origem, col_destino, ignorar_conflito=False):
    """Só as colunas que existem dos dois lados: o que saiu do esquema fica para trás, o que é novo usa o padrão."""
    cols = [c for c in col_origem if c in col_destino]
    nomes = ", ".join('"%s"' % c for c in cols)
    sql = f"insert into {tabela} ({nomes}) values ({', '.join(['%s'] * len(cols))})"
    return cols, sql + (" on conflict do nothing" if ignorar_conflito else "")


def valores(linha, cols, tipos_destino, forcar=None):
    linha = {**linha, **(forcar or {})}
    return [Jsonb(linha[c]) if tipos_destino[c] in ("json", "jsonb") and linha[c] is not None else linha[c] for c in cols]


def copiar(origem, destino, tabela, filtro, param, forcar=None, ignorar_conflito=False):
    cur = origem.cursor(row_factory=dict_row)
    linhas = cur.execute(f"select * from {tabela} where {filtro}", param).fetchall()
    if linhas:
        tipos = colunas(destino, tabela)
        cols, sql = montar_insert(tabela, list(linhas[0]), tipos, ignorar_conflito)
        destino.cursor().executemany(sql, [valores(l, cols, tipos, forcar) for l in linhas])
    return len(linhas)


def conferir_origem(origem, empresa):
    """Devolve (problemas, usuarios_sem_login). Problema = dado que o esquema novo recusaria."""
    param = {"e": empresa}
    problemas = []
    for titulo, sql in REGRAS:
        casos = [r[0] for r in origem.execute(sql, param).fetchall()]
        if casos:
            problemas.append(f"{titulo}: {len(casos)} caso(s) — {', '.join(casos[:10])}")
    sem_login = origem.cursor(row_factory=dict_row).execute(_SEM_LOGIN, param).fetchall()
    return problemas, sem_login


def criar_login_legado(destino, usuario):
    """Usuário que só existia no Flask: cria o login no Supabase Auth com o mesmo hash bcrypt (a senha continua a mesma)."""
    destino.execute(
        "insert into auth.users (instance_id, id, aud, role, email, encrypted_password, email_confirmed_at, "
        "raw_app_meta_data, raw_user_meta_data, created_at, updated_at, confirmation_token, recovery_token, "
        "email_change_token_new, email_change) "
        "values ('00000000-0000-0000-0000-000000000000', %s, 'authenticated', 'authenticated', %s, %s, now(), "
        "%s, %s, now(), now(), '', '', '', '')",  # o GoTrue quebra com NULL nas colunas de token
        (usuario["id"], usuario["email"], usuario["senha_hash"],
         Jsonb({"provider": "email", "providers": ["email"]}), Jsonb({})))
    destino.execute(
        "insert into auth.identities (id, user_id, provider_id, provider, identity_data, created_at, updated_at) "
        "values (gen_random_uuid(), %s, %s, 'email', %s, now(), now())",
        (usuario["id"], usuario["id"], Jsonb({"sub": usuario["id"], "email": usuario["email"], "email_verified": True})))


def migrar_empresa(origem, destino, empresa, substituir, sem_auditoria=False):
    """Uma oficina = uma transação. Devolve {tabela: linhas copiadas}."""
    param = {"e": empresa}
    _, sem_login = conferir_origem(origem, empresa)
    tabelas = [t for t in TABELAS if not (sem_auditoria and t[0] == "public.audit_logs")]
    with destino.transaction():
        if destino.execute("select 1 from public.empresas where id = %(e)s", param).fetchone():
            if not substituir:
                raise SystemExit(f"Oficina {empresa} já existe no destino. Use --substituir para apagar e copiar de novo.")
            for tabela, filtro in APAGAR:
                destino.execute(f"delete from {tabela} where {filtro}", param)

        # sem triggers durante a carga: não gera auditoria da própria migração nem mexe em updated_at
        destino.execute("set local session_replication_role = replica")
        copiadas = {}
        for tabela, filtro, _ in tabelas:
            forcar = {"empresa_id": empresa} if tabela in FORCAR_EMPRESA else None
            copiadas[tabela] = copiar(origem, destino, tabela, filtro, param, forcar)
        for u in sem_login:
            if (u["senha_hash"] or "").startswith("$2"):
                criar_login_legado(destino, u)
                copiadas["auth.users"] += 1
                copiadas["auth.identities"] += 1
        plano = origem.execute("select coalesce(plano, 'basico') from public.empresas where id = %(e)s", param).fetchone()[0]
        destino.execute("insert into public.assinaturas (empresa_id, plano) values (%s, %s)", (empresa, plano))
        destino.execute("set local session_replication_role = origin")

        for tabela, filtro, filtro_destino in tabelas:
            no_destino = destino.execute(f"select count(*) from {tabela} where {filtro_destino or filtro}", param).fetchone()[0]
            if no_destino != copiadas[tabela]:
                raise RuntimeError(f"{tabela}: copiei {copiadas[tabela]} e o destino tem {no_destino}. Nada foi gravado.")
    return copiadas


def migrar_masters(origem, destino):
    with destino.transaction():
        destino.execute("set local session_replication_role = replica")
        return {t: copiar(origem, destino, t, f, {}, ignorar_conflito=True) for t, f in TABELAS_MASTER}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    alvo = ap.add_mutually_exclusive_group(required=True)
    alvo.add_argument("--teste", action="store_true", help="só as oficinas de teste (empresa_teste = true)")
    alvo.add_argument("--empresa", help="uma oficina, pelo id")
    alvo.add_argument("--todas", action="store_true")
    ap.add_argument("--so-conferir", action="store_true")
    ap.add_argument("--sem-auditoria", action="store_true")
    ap.add_argument("--substituir", action="store_true")
    args = ap.parse_args(argv)

    origem = psycopg.connect(os.environ["ORIGEM_DB_URL"], autocommit=True, options="-c default_transaction_read_only=on")
    filtro = "id = %(e)s" if args.empresa else ("empresa_teste" if args.teste else "true")
    empresas = origem.execute(f"select id::text, nome_fantasia from public.empresas where {filtro} order by created_at",
                              {"e": args.empresa}).fetchall()
    if not empresas:
        raise SystemExit("Nenhuma oficina encontrada na origem.")

    parar = False
    for eid, nome in empresas:
        problemas, sem_login = conferir_origem(origem, eid)
        for p in problemas:
            parar = True
            print(f"[PROBLEMA] {nome}: {p}")
        for u in sem_login:
            com_senha = (u["senha_hash"] or "").startswith("$2")
            print(f"[AVISO] {nome}: usuário {u['nome']} ({u['id']}) só existe no legado — "
                  + ("o login será criado com a mesma senha." if com_senha else "sem senha: não vai conseguir entrar; redefinir depois."))
    if parar:
        raise SystemExit("Há dados que o esquema novo recusa. Nada foi gravado. Decida cada caso e rode de novo.")
    if args.so_conferir:
        for eid, nome in empresas:
            print(nome, {t: origem.execute(f"select count(*) from {t} where {f}", {"e": eid}).fetchone()[0] for t, f, _ in TABELAS})
        return

    destino = psycopg.connect(os.environ["DESTINO_DB_URL"], autocommit=True)
    print("plataforma (masters):", migrar_masters(origem, destino))
    for eid, nome in empresas:
        print(f"{nome}:", migrar_empresa(origem, destino, eid, args.substituir, args.sem_auditoria))
    print(f"OK: {len(empresas)} oficina(s) copiadas e conferidas.")


if __name__ == "__main__":
    sys.exit(main())
