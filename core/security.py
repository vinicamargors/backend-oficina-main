import os
import re
from fastapi import HTTPException, Security, Header, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.database import supabase

seguranca_armada = HTTPBearer()

def limpar_telefone(tel: str) -> str:
    """Remove caracteres não numéricos do telefone."""
    return re.sub(r"\D", "", tel) if tel else ""

def validar_token(credentials: HTTPAuthorizationCredentials = Security(seguranca_armada)):
    """Valida o JWT no Supabase Auth e devolve o usuário do Auth (sem exigir perfil)."""
    try:
        return supabase.auth.get_user(credentials.credentials).user
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Passaporte rejeitado pela matriz. Token inválido, expirado ou corrompido."
        )

def validar_passaporte(request: Request, auth_user=Depends(validar_token)):
    """
    Busca o perfil real e ativo na tabela usuarios e garante que o empresa_id
    pedido na URL/query é o da empresa do usuário (master acessa todas).
    """
    perfil = supabase.table("usuarios").select("*").eq("id", auth_user.id).execute().data
    if not perfil or not perfil[0].get("ativo"):
        raise HTTPException(status_code=403, detail="Usuário inativo ou sem perfil vinculado.")

    usuario = perfil[0]
    usuario.pop("senha_hash", None)
    usuario["sub"] = auth_user.id  # retrocompatibilidade até ajuste de /me

    empresa_pedida = request.path_params.get("empresa_id") or request.query_params.get("empresa_id")
    if (
        empresa_pedida
        and usuario.get("cargo") != "master"
        and str(empresa_pedida) != str(usuario.get("empresa_id"))
    ):
        raise HTTPException(status_code=403, detail="Acesso negado a dados de outra empresa.")
    return usuario

def empresa_do_usuario(usuario: dict, empresa_informada) -> str:
    """Para payloads com empresa_id: master escolhe; os demais sempre gravam na própria empresa."""
    if usuario.get("cargo") == "master" and empresa_informada:
        return str(empresa_informada)
    return str(usuario["empresa_id"])

def garantir_da_empresa(tabela: str, registro_id, empresa_id: str, nome: str) -> None:
    """404 se o registro (cliente, veículo, OS, usuário...) não pertence à empresa. None é ignorado."""
    if registro_id is None:
        return
    achou = supabase.table(tabela).select("id").eq("id", str(registro_id)).eq("empresa_id", str(empresa_id)).execute().data
    if not achou:
        raise HTTPException(status_code=404, detail=f"{nome} não encontrado nesta empresa.")

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
