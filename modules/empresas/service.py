from fastapi import HTTPException
from core.database import supabase, supabase_admin
from .schemas import EmpresaCreate, EmpresaUpdate, ConfigUpdate

def listar_empresas(cargo: str, empresa_id: str):
    # Se for Master, vê o império todo. Se for Dono, só a própria propriedade.
    query = supabase.table("empresas").select("*").order("nome_fantasia")
    if cargo != "master":
        query = query.eq("id", empresa_id)
    return query.execute().data

def criar_empresa(dados: EmpresaCreate):
    # 1. Cria a empresa na nossa base
    empresa_data = dados.model_dump(exclude={"nome_dono", "email_dono", "senha_dono"}, mode='json')
    empresa_data["ativo"] = True
    empresa = supabase.table("empresas").insert(empresa_data).execute().data[0]
    
    empresa_id = empresa["id"]

    # 2. Cria as configurações padrão
    supabase.table("configuracoes_empresa").insert({
        "empresa_id": empresa_id,
        "cor_primaria": "#1e3a8a",
        "cor_secundaria": "#f97316",
        "nome_exibicao": dados.nome_fantasia
    }).execute()

    # 3. Terceiriza o risco: Cria o usuário direto no Supabase Auth
    try:
        user_auth = supabase_admin.auth.admin.create_user({
            "email": dados.email_dono,
            "password": dados.senha_dono,
            "email_confirm": True # Já confirma o cara pra ele poder logar na hora
        })
    except Exception as e:
        # Se der pau (ex: email já existe no Auth), a gente desfaz a criação da empresa (Rollback manual)
        supabase.table("empresas").delete().eq("id", empresa_id).execute()
        raise HTTPException(status_code=400, detail=f"Erro ao registrar dono no Auth: {str(e)}")

    # 4. Cria o perfil público na NOSSA tabela, linkando com o ID do Auth
    try:
        supabase.table("usuarios").insert({
            "id": user_auth.user.id, # O Chassi do usuário vem direto da Big Tech
            "nome": dados.nome_dono,
            "email": dados.email_dono,
            "cargo": "DONO",
            "ativo": True,
            "empresa_id": empresa_id
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao salvar perfil público: {str(e)}")

    return empresa

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

def deletar_empresa(empresa_id: str):
    supabase.table("configuracoes_empresa").delete().eq("empresa_id", empresa_id).execute()
    supabase.table("usuarios").delete().eq("empresa_id", empresa_id).execute()
    supabase.table("empresas").delete().eq("id", empresa_id).execute()
    return {"status": "sucesso", "detail": "Empresa e acessos varridos do sistema."}

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

def atualizar_configuracoes(empresa_id: str, dados: ConfigUpdate):
    campos = dados.model_dump(exclude_unset=True, mode='json')
    existente = supabase.table("configuracoes_empresa").select("id").eq("empresa_id", empresa_id).execute().data

    if existente:
        resp = supabase.table("configuracoes_empresa").update(campos).eq("empresa_id", empresa_id).execute()
    else:
        campos["empresa_id"] = empresa_id
        resp = supabase.table("configuracoes_empresa").insert(campos).execute()

    return resp.data[0]