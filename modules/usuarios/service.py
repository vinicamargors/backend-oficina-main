from fastapi import HTTPException
from core.database import supabase, supabase_admin
from core.security import limpar_telefone
from .schemas import UsuarioCreate, UsuarioUpdate

def listar_usuarios(empresa_id: str):
    return supabase.table("usuarios").select("*").eq("empresa_id", empresa_id).order("nome").execute().data

def criar_usuario(dados: UsuarioCreate, empresa_id: str):
    try:
        user_auth = supabase_admin.auth.admin.create_user({
            "email": dados.email,
            "password": dados.senha,
            "email_confirm": True
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro na provedora de Auth: {str(e)}")

    db_data = {
        "id": user_auth.user.id,
        "nome": dados.nome,
        "email": dados.email,
        "telefone": limpar_telefone(dados.telefone) if dados.telefone else None,
        "cargo": dados.cargo,
        "ativo": dados.ativo,
        "empresa_id": empresa_id,
        "salario_base": dados.salario_base if dados.salario_base is not None else 0.0,
        "comissao_servico_pct": dados.comissao_servico_pct if dados.comissao_servico_pct is not None else 0.0,
        "comissao_peca_pct": dados.comissao_peca_pct if dados.comissao_peca_pct is not None else 0.0,
        "vale_transporte": dados.vale_transporte if dados.vale_transporte is not None else 0.0,
        "vale_refeicao": dados.vale_refeicao if dados.vale_refeicao is not None else 0.0,
        "paga_hora_extra": dados.paga_hora_extra if dados.paga_hora_extra is not None else False,
        "valor_hora_extra": dados.valor_hora_extra if dados.valor_hora_extra is not None else 0.0,
        "estrelas_media": dados.estrelas_media if dados.estrelas_media is not None else 5.0,
        "total_avaliacoes": dados.total_avaliacoes if dados.total_avaliacoes is not None else 0,
    }
    response = supabase.table("usuarios").insert(db_data).execute()
    return response.data[0]

def atualizar_usuario(usuario_id: str, empresa_id: str, dados: UsuarioUpdate):
    existente = supabase.table("usuarios").select("*").eq("id", usuario_id).eq("empresa_id", empresa_id).execute().data
    if not existente:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")

    user_email = (dados.email or existente[0].get("email") or "").strip().lower()

    if dados.senha:
        senha_sincronizada = False
        # 1. Tenta atualizar direto pelo usuario_id no Supabase Auth
        try:
            supabase_admin.auth.admin.update_user_by_id(usuario_id, {"password": dados.senha})
            senha_sincronizada = True
        except Exception:
            pass

        # 2. Se não encontrou pelo ID (ex: usuário criado no banco sem ID correspondente no Auth), busca pelo email
        if not senha_sincronizada and user_email:
            try:
                users_list = supabase_admin.auth.admin.list_users()
                target_user = next((u for u in users_list if getattr(u, 'email', '').lower() == user_email), None)
                if target_user:
                    supabase_admin.auth.admin.update_user_by_id(target_user.id, {"password": dados.senha})
                    senha_sincronizada = True
                else:
                    # 3. Se o funcionário não existia no Supabase Auth, cria o acesso dele agora com a nova senha!
                    supabase_admin.auth.admin.create_user({
                        "id": usuario_id,
                        "email": user_email,
                        "password": dados.senha,
                        "email_confirm": True
                    })
                    senha_sincronizada = True
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Erro ao sincronizar senha no Supabase Auth: {str(e)}")

        if not senha_sincronizada:
            raise HTTPException(status_code=400, detail="Não foi possível sincronizar a senha com o provedor de autenticação.")

    # Só altera email no Auth se o usuário realmente forneceu um email diferente do atual
    email_mudou = False
    if dados.email:
        email_atual = (existente[0].get("email") or "").strip().lower()
        novo_email = dados.email.strip().lower()
        if novo_email != email_atual:
            email_mudou = True
            try:
                supabase_admin.auth.admin.update_user_by_id(usuario_id, {"email": dados.email, "email_confirm": True})
            except Exception:
                raise HTTPException(status_code=400, detail="Este e-mail já está sendo usado por outro usuário global.")

    campos = dados.model_dump(exclude={"senha"}, exclude_unset=True, mode='json')
    if not email_mudou and "email" in campos:
        campos.pop("email", None)

    if "telefone" in campos and campos["telefone"] is not None:
        campos["telefone"] = limpar_telefone(campos["telefone"])

    if not campos:
        return existente[0]

    response = supabase.table("usuarios").update(campos).eq("id", usuario_id).eq("empresa_id", empresa_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")
    return response.data[0]

def desativar_usuario(usuario_id: str, empresa_id: str):
    response = supabase.table("usuarios").update({"ativo": False}).eq("id", usuario_id).eq("empresa_id", empresa_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")
    return {"status": "sucesso", "detail": "Funcionário desativado com sucesso (exclusão lógica)."}

def reativar_usuario(usuario_id: str, empresa_id: str):
    response = supabase.table("usuarios").update({"ativo": True}).eq("id", usuario_id).eq("empresa_id", empresa_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")
    return {"status": "sucesso", "detail": "Funcionário reativado com sucesso."}

