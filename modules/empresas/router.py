from fastapi import APIRouter, Depends
from typing import Optional
from uuid import UUID
from . import schemas, service
from core.security import validar_passaporte, exigir_cargos

router = APIRouter(dependencies=[Depends(validar_passaporte)])

@router.get("/")
def get_empresas(empresa_id: Optional[UUID] = None, usuario: dict = Depends(validar_passaporte)):
    emp_id = str(empresa_id or usuario.get("empresa_id") or "")
    return service.listar_empresas(usuario["cargo"], emp_id)

@router.get("/{empresa_id}/detalhes", dependencies=[Depends(exigir_cargos("master"))])
def get_detalhes_empresa(empresa_id: UUID):
    return service.obter_detalhes(str(empresa_id))

@router.post("/", response_model=schemas.EmpresaResponse, dependencies=[Depends(exigir_cargos("master"))])
def post_empresa(empresa: schemas.EmpresaCreate):
    return service.criar_empresa(empresa)

@router.put("/{empresa_id}")
def put_empresa(empresa_id: UUID, empresa: schemas.EmpresaUpdate, usuario: dict = Depends(exigir_cargos("DONO", "master"))):
    return service.atualizar_empresa(str(empresa_id), usuario["cargo"], empresa)

@router.delete("/{empresa_id}", dependencies=[Depends(exigir_cargos("master"))])
def delete_empresa(empresa_id: UUID):
    return service.deletar_empresa(str(empresa_id))

@router.put("/{empresa_id}/configuracoes", dependencies=[Depends(exigir_cargos("DONO", "master"))])
def put_configuracoes(empresa_id: UUID, config: schemas.ConfigUpdate):
    return service.atualizar_configuracoes(str(empresa_id), config)