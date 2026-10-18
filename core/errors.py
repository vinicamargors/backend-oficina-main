from fastapi import Request
from fastapi.responses import JSONResponse
from postgrest.exceptions import APIError

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

    for code, (status_code, msg) in ERROS_POSTGRES.items():
        if code in erro_str:
            return JSONResponse(status_code=status_code, content={"detail": msg})

    return JSONResponse(status_code=400, content={"detail": f"Erro interno de transação: {erro_str}"})