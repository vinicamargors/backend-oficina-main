from fastapi import APIRouter, Depends
from typing import List
from uuid import UUID
from . import schemas, service
from core.security import validar_passaporte, exigir_cargos

router = APIRouter(dependencies=[Depends(validar_passaporte)])

@router.get("/me", response_model=schemas.UsuarioResponse)
def get_me(usuario_logado: dict = Depends(validar_passaporte)):
    return usuario_logado

@router.get("/{empresa_id}", response_model=List[schemas.UsuarioResponse], dependencies=[Depends(exigir_cargos("DONO", "master"))])
def get_usuarios(empresa_id: UUID):
    return service.listar_usuarios(str(empresa_id))

@router.post("/{empresa_id}", response_model=schemas.UsuarioResponse, dependencies=[Depends(exigir_cargos("DONO", "master"))])
def post_usuario(empresa_id: UUID, usuario: schemas.UsuarioCreate):
    return service.criar_usuario(usuario, str(empresa_id))

@router.put("/{empresa_id}/{usuario_id}", response_model=schemas.UsuarioResponse, dependencies=[Depends(exigir_cargos("DONO", "master"))])
def put_usuario(empresa_id: UUID, usuario_id: UUID, usuario: schemas.UsuarioUpdate):
    return service.atualizar_usuario(str(usuario_id), str(empresa_id), usuario)
