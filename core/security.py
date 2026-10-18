import os
import re
from fastapi import HTTPException, Security, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.database import supabase

seguranca_armada = HTTPBearer()

def limpar_telefone(tel: str) -> str:
    """Remove caracteres não numéricos do telefone."""
    return re.sub(r"\D", "", tel) if tel else ""

def validar_passaporte(credentials: HTTPAuthorizationCredentials = Security(seguranca_armada)):
    """
    Valida o token no Supabase Auth e busca o perfil real e ativo na tabela usuarios.
    Nunca confia em headers enviados pelo cliente para definir cargo ou empresa.
    """
    token = credentials.credentials
    try:
        auth_response = supabase.auth.get_user(token)
        user_id = auth_response.user.id

        perfil = supabase.table("usuarios").select("*").eq("id", user_id).execute().data
        if not perfil or not perfil[0].get("ativo"):
            raise HTTPException(status_code=403, detail="Usuário inativo ou sem perfil vinculado.")

        usuario = perfil[0]
        usuario["sub"] = user_id  # retrocompatibilidade até ajuste de /me
        return usuario
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Passaporte rejeitado pela matriz. Token inválido, expirado ou corrompido."
        )

def exigir_cargos(*cargos_permitidos: str):
    def dependency(usuario: dict = Depends(validar_passaporte)):
        if usuario.get("cargo") not in cargos_permitidos:
            raise HTTPException(status_code=403, detail="Acesso negado para o seu perfil.")
        return usuario
    return dependency

def validar_chave_bot(x_bot_key: str = Header(...)):
    bot_key = os.getenv("BOT_API_KEY")
    if not bot_key or x_bot_key != bot_key:
        raise HTTPException(status_code=403, detail="Acesso não autorizado ao módulo do Bot.")