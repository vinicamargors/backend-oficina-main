from fastapi import APIRouter, Depends
from core.pagamento import FORMAS_PAGAMENTO
from core.security import validar_passaporte

router = APIRouter(dependencies=[Depends(validar_passaporte)])


@router.get("/", response_model=list[str])
def get_formas_pagamento():
    return FORMAS_PAGAMENTO
