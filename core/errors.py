import logging
import re
from fastapi import Request
from fastapi.responses import JSONResponse
from postgrest.exceptions import APIError

log = logging.getLogger("mecanify.erros")

ERROS_POSTGRES = {
    "23505": (409, "Conflito no mercado: Já existe um registro ativo com estes dados únicos (Ex: Placa, CPF/CNPJ, Email)."),
    "23502": (422, "Dados incompletos: Um campo obrigatório no banco não foi preenchido."),
    "23514": (400, "Regra de negócio violada: O valor inserido não é permitido pelo contrato do banco de dados."),
    "22P02": (422, "Formato de dado inválido. Verifique se os IDs estão no formato correto."),
}

async def supabase_exception_handler(request: Request, exc: APIError):
    """
    O Tribunal Privado: intercepta qualquer erro do Supabase antes
    de chegar no usuário e formata a resposta.
    """
    erro_str = str(exc)

    if "23503" in erro_str:
        msg = (
            "Operação inválida: Você está tentando vincular a um registro fantasma que não existe no sistema."
            if "is not present in table" in erro_str
            else "Bloqueio de Auditoria: Este registro possui histórico financeiro ou dependências ativas e não pode ser apagado."
        )
        return JSONResponse(status_code=400, content={"detail": msg})

    if "22001" in erro_str:  # o Postgres não diz a coluna, só o tamanho: "character varying(30)"
        m = re.search(r"varying\((\d+)\)", erro_str)
        limite = f" (máximo de {m.group(1)} caracteres)" if m else ""
        return JSONResponse(status_code=422, content={"detail": f"Um dos textos é maior que o permitido{limite}. Encurte e tente de novo."})

    for code, (status_code, msg) in ERROS_POSTGRES.items():
        if code in erro_str:
            return JSONResponse(status_code=status_code, content={"detail": msg})

    # Erro que não conhecemos: o detalhe fica só no log do servidor (nunca o texto cru do banco para o cliente).
    log.error("Erro de banco não mapeado em %s %s: %s", request.method, request.url.path, erro_str)
    return JSONResponse(status_code=400, content={"detail": "Não foi possível concluir a operação. Tente de novo; se continuar, avise o suporte."})
