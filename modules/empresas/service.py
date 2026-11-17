import logging
from fastapi import HTTPException
from postgrest.exceptions import APIError
from core.database import supabase, supabase_admin
from core.errors import erro_auth
from .schemas import EmpresaCreate, EmpresaUpdate, ConfigUpdate

def listar_empresas(cargo: str, empresa_id: str):
    # Se for Master, vê o império todo. Se for Dono, só a própria propriedade.
    query = supabase.table("empresas").select("*").order("nome_fantasia")
    if cargo != "master":
        query = query.eq("id", empresa_id)
    return query.execute().data

log = logging.getLogger("mecanify.erros")


def _com_retry(acao, tentativas: int = 3):
    """audit_logs não tem índice em empresa_id: apagar/soltar empresa varre a tabela inteira e às vezes estoura o
    statement timeout (57014) do banco. Tenta de novo; o índice definitivo é migration (fora do T-014)."""
    for i in range(tentativas):
        try:
            return acao()
        except APIError as e:
            if e.code != "57014" or i == tentativas - 1:
                raise
            log.warning("Statement timeout em %s (tentativa %s/%s); tentando de novo", acao, i + 1, tentativas)


def _desfazer(passos: list) -> bool:
    """Roda do último passo para o primeiro. True se tudo foi desfeito (falha ao desfazer vai para o log)."""
    ok = True
    for nome, acao in reversed(passos):
        try:
            _com_retry(acao)
        except Exception as e:
            ok = False
            log.error("Não consegui desfazer '%s' ao criar empresa: %s", nome, e)
    return ok


def criar_empresa(dados: EmpresaCreate):
    """Empresa + configuração + login do dono + perfil. Se qualquer passo falhar, os anteriores são desfeitos."""
    feitos = []  # (nome, ação que desfaz)
    try:
        empresa_data = dados.model_dump(exclude={"nome_dono", "email_dono", "senha_dono"}, mode='json')
        empresa_data["ativo"] = True
        empresa = supabase.table("empresas").insert(empresa_data).execute().data[0]
        empresa_id = empresa["id"]
        feitos.append(("empresa", lambda: supabase.table("empresas").delete().eq("id", empresa_id).execute()))

        supabase.table("configuracoes_empresa").insert({
            "empresa_id": empresa_id,
            "cor_primaria": "#1e3a8a",
            "cor_secundaria": "#f97316",
            "nome_exibicao": dados.nome_fantasia
        }).execute()
        feitos.append(("configuração", lambda: supabase.table("configuracoes_empresa").delete().eq("empresa_id", empresa_id).execute()))

        try:
            user_auth = supabase_admin.auth.admin.create_user({
                "email": dados.email_dono,
                "password": dados.senha_dono,
                "email_confirm": True,
            })
        except Exception as e:
            raise HTTPException(status_code=400, detail=erro_auth(e, "Não foi possível criar o acesso do dono da oficina."))
        auth_id = user_auth.user.id
        feitos.append(("login do dono", lambda: supabase_admin.auth.admin.delete_user(auth_id)))

        supabase.table("usuarios").insert({
            "id": auth_id,
            "nome": dados.nome_dono,
            "email": dados.email_dono,
            "cargo": "DONO",
            "ativo": True,
            "empresa_id": empresa_id,
        }).execute()
        return empresa
    except Exception as e:
        limpo = _desfazer(feitos)
        if isinstance(e, (HTTPException, APIError)) and limpo:
            raise  # mensagem já tratada (HTTPException em português ou APIError, que o handler global traduz)
        if not limpo:
            log.error("Criação de empresa falhou e sobrou resíduo: %s", e)
            raise HTTPException(status_code=500, detail="Não foi possível criar a oficina e algo ficou pela metade. Avise o suporte antes de tentar de novo.")
        log.exception("Falha inesperada ao criar empresa")
        raise HTTPException(status_code=500, detail="Não foi possível criar a oficina. Nada foi cadastrado; tente de novo.")


def atualizar_empresa(empresa_id: str, cargo: str, dados: EmpresaUpdate):
    campos = dados.model_dump(exclude_unset=True, mode='json')
    
    # Trava de segurança: só o dono da plataforma muda plano e desativa o inquilino
    if cargo != "master":
        campos.pop("plano", None)
        campos.pop("ativo", None)

    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum dado enviado para atualização.")

    response = supabase.table("empresas").update(campos).eq("id", empresa_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")
    return response.data[0]

# Tabelas com histórico da oficina. As quatro primeiras o banco já protege (FK sem cascade); transações o banco
# apagaria em cascata, em silêncio, por isso também travam aqui.
HISTORICO = [("clientes", "clientes"), ("veiculos", "veículos"), ("ordens_servico", "ordens de serviço"),
             ("estoque", "itens de estoque"), ("transacoes_financeiras", "lançamentos financeiros")]


def deletar_empresa(empresa_id: str):
    """Só apaga oficina SEM histórico. Remove também os logins do Auth dos usuários dela (e só deles)."""
    if not supabase.table("empresas").select("id").eq("id", empresa_id).execute().data:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")

    usuarios = supabase.table("usuarios").select("id, cargo").eq("empresa_id", empresa_id).execute().data or []
    if any(u.get("cargo") == "master" for u in usuarios):
        raise HTTPException(status_code=400, detail="Esta é a empresa da plataforma (tem usuário master) e não pode ser apagada.")

    com_historico = []
    for tabela, rotulo in HISTORICO:
        n = supabase.table(tabela).select("id", count="exact", head=True).eq("empresa_id", empresa_id).execute().count or 0
        if n:
            com_historico.append(f"{n} {rotulo}")
    if com_historico:
        raise HTTPException(status_code=400, detail=(
            "Esta oficina tem histórico (" + ", ".join(com_historico) + ") e não pode ser apagada. "
            "Para encerrar o acesso, desative a oficina."))

    # Logins primeiro: se algum falhar, nada do banco foi apagado e dá para repetir (login já inexistente conta como feito).
    for u in usuarios:
        try:
            supabase_admin.auth.admin.delete_user(str(u["id"]))
        except Exception as e:
            if "not found" not in str(e).lower():
                log.error("Falha ao remover login %s ao apagar empresa %s: %s", u["id"], empresa_id, e)
                raise HTTPException(status_code=502, detail="Não foi possível remover os acessos da oficina agora. Nada foi apagado; tente de novo.")

    supabase.table("usuarios").delete().eq("empresa_id", empresa_id).execute()
    supabase.table("configuracoes_empresa").delete().eq("empresa_id", empresa_id).execute()
    # A trilha de auditoria fica (o dado antigo está no próprio registro); só solta o vínculo, que o banco não deixa apagar a empresa com ele.
    _com_retry(lambda: supabase.table("audit_logs").update({"empresa_id": None}).eq("empresa_id", empresa_id).execute())
    _com_retry(lambda: supabase.table("empresas").delete().eq("id", empresa_id).execute())
    return {"status": "sucesso", "detail": "Empresa e acessos removidos do sistema.", "logins_removidos": len(usuarios)}


def obter_detalhes(empresa_id: str):
    emp_res = supabase.table("empresas").select("*").eq("id", empresa_id).execute().data
    if not emp_res:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")

    config = supabase.table("configuracoes_empresa").select("*").eq("empresa_id", empresa_id).execute().data
    usuarios = supabase.table("usuarios").select("id, nome, email, cargo, ativo").eq("empresa_id", empresa_id).execute().data

    stats = {
        "clientes": supabase.table("clientes").select("id", count="exact", head=True).eq("empresa_id", empresa_id).execute().count or 0,
        "veiculos": supabase.table("veiculos").select("id", count="exact", head=True).eq("empresa_id", empresa_id).execute().count or 0,
        "ordens": supabase.table("ordens_servico").select("id", count="exact", head=True).eq("empresa_id", empresa_id).execute().count or 0,
    }

    return {"empresa": emp_res[0], "configuracao": config[0] if config else {}, "usuarios": usuarios, "estatisticas": stats}

def obter_configuracoes(empresa_id: str):
    config = supabase.table("configuracoes_empresa").select("*").eq("empresa_id", empresa_id).execute().data
    if config:
        return config[0]
    return {
        "empresa_id": empresa_id,
        "cor_primaria": "#1e3a8a",
        "cor_secundaria": "#f97316",
        "raio_gps_metros": 100,
        "dia_pagamento_folha": 5,
        "dia_adiantamento_folha": 20,
        "comissao_global_servico_pct": 15.0,
        "comissao_global_peca_pct": 5.0,
        "paga_hora_extra_padrao": True,
        "valor_hora_extra_padrao": 25.0
    }

def atualizar_configuracoes(empresa_id: str, dados: ConfigUpdate):
    campos = dados.model_dump(exclude_unset=True, mode='json')
    existente = supabase.table("configuracoes_empresa").select("id").eq("empresa_id", empresa_id).execute().data

    if existente:
        resp = supabase.table("configuracoes_empresa").update(campos).eq("empresa_id", empresa_id).execute()
    else:
        campos["empresa_id"] = empresa_id
        resp = supabase.table("configuracoes_empresa").insert(campos).execute()

    return resp.data[0]

