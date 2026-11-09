from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from . import schemas, service
from core.security import validar_passaporte, exigir_cargos, validar_token

router = APIRouter(dependencies=[Depends(validar_passaporte)])

# Sem validar_passaporte: o usuário ainda não tem perfil. Registrado antes de `router` em main.py.
onboarding_router = APIRouter()

@onboarding_router.post("/onboarding", response_model=schemas.UsuarioResponse)
def post_onboarding(auth_user=Depends(validar_token)):
    return service.onboarding_oficina(auth_user)

def _bloquear_promocao_master(logado: dict, cargo_novo):
    if cargo_novo == "master" and logado.get("cargo") != "master":
        raise HTTPException(status_code=403, detail="Só o master pode criar ou promover master.")

@router.get("/me", response_model=schemas.UsuarioResponse)
def get_me(usuario_logado: dict = Depends(validar_passaporte)):
    return usuario_logado

@router.get("/{empresa_id}", response_model=List[schemas.UsuarioResponse], dependencies=[Depends(exigir_cargos("DONO", "master"))])
def get_usuarios(empresa_id: UUID):
    return service.listar_usuarios(str(empresa_id))

@router.post("/{empresa_id}", response_model=schemas.UsuarioResponse)
def post_usuario(empresa_id: UUID, usuario: schemas.UsuarioCreate, logado: dict = Depends(exigir_cargos("DONO", "master"))):
    _bloquear_promocao_master(logado, usuario.cargo)
    return service.criar_usuario(usuario, str(empresa_id))

@router.put("/{empresa_id}/{usuario_id}", response_model=schemas.UsuarioResponse)
def put_usuario(empresa_id: UUID, usuario_id: UUID, usuario: schemas.UsuarioUpdate, logado: dict = Depends(exigir_cargos("DONO", "master"))):
    _bloquear_promocao_master(logado, usuario.cargo)
    return service.atualizar_usuario(str(usuario_id), str(empresa_id), usuario)

@router.delete("/{empresa_id}/{usuario_id}", dependencies=[Depends(exigir_cargos("DONO", "master"))])
def delete_usuario(empresa_id: UUID, usuario_id: UUID):
    return service.desativar_usuario(str(usuario_id), str(empresa_id))

@router.patch("/{empresa_id}/{usuario_id}/reativar", dependencies=[Depends(exigir_cargos("DONO", "master"))])
def patch_reativar_usuario(empresa_id: UUID, usuario_id: UUID):
    return service.reativar_usuario(str(usuario_id), str(empresa_id))

