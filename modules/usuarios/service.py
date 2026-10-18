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
        "empresa_id": empresa_id
    }
    response = supabase.table("usuarios").insert(db_data).execute()
    return response.data[0]

def atualizar_usuario(usuario_id: str, empresa_id: str, dados: UsuarioUpdate):
    existente = supabase.table("usuarios").select("*").eq("id", usuario_id).eq("empresa_id", empresa_id).execute().data
    if not existente:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")

    if dados.senha:
        try:
            supabase_admin.auth.admin.update_user_by_id(usuario_id, {"password": dados.senha})
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erro ao trocar senha no cofre: {str(e)}")

    if dados.email:
        try:
            supabase_admin.auth.admin.update_user_by_id(usuario_id, {"email": dados.email, "email_confirm": True})
        except Exception:
            raise HTTPException(status_code=400, detail="Este e-mail já está sendo usado por outro usuário global.")

    campos = dados.model_dump(exclude={"senha"}, exclude_unset=True, mode='json')
    if "telefone" in campos and campos["telefone"] is not None:
        campos["telefone"] = limpar_telefone(campos["telefone"])

    if not campos:
        return existente[0]

    response = supabase.table("usuarios").update(campos).eq("id", usuario_id).eq("empresa_id", empresa_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado.")
    return response.data[0]