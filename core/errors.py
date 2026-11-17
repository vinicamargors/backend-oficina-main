import logging
import re
from fastapi import Request
from fastapi.exceptions import RequestValidationError
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


# ------------------------------------------------------------------ 422 de validação em português da oficina
ROTULOS = {  # rota (1º trecho depois de /api/v1) → campo → nome que a oficina conhece
    "clientes": {"nome": "Nome do cliente", "telefone": "Telefone", "cpf_cnpj": "CPF/CNPJ", "endereco": "Endereço"},
    "veiculos": {"placa": "Placa", "modelo": "Modelo", "marca": "Marca", "cor": "Cor", "km_atual": "Quilometragem",
                 "ano": "Ano", "chassi": "Chassi", "cliente_id": "Cliente"},
    "estoque": {"nome": "Nome do item", "codigo": "Código", "categoria": "Categoria", "quantidade": "Quantidade",
                "custo": "Custo", "venda": "Preço de venda", "minimo_alerta": "Estoque mínimo"},
    "os": {"nome_item": "Nome do item", "quantidade": "Quantidade", "custo_unitario": "Custo unitário",
           "venda_unitario": "Valor de venda", "forma_pagamento": "Forma de pagamento", "km_atual": "Quilometragem",
           "descricao_problema": "Descrição do problema", "status": "Situação da OS", "tipo": "Tipo do item",
           "mecanico_responsavel_id": "Mecânico", "cliente_id": "Cliente", "veiculo_id": "Veículo", "estoque_id": "Item do estoque"},
    "usuarios": {"nome": "Nome do colaborador", "email": "E-mail", "senha": "Senha", "cargo": "Cargo", "telefone": "Telefone",
                 "salario_base": "Salário base", "comissao_servico_pct": "Comissão de serviço", "comissao_peca_pct": "Comissão de peça",
                 "vale_transporte": "Vale transporte", "vale_refeicao": "Vale refeição", "valor_hora_extra": "Valor da hora extra"},
    "empresas": {"nome_fantasia": "Nome fantasia", "razao_social": "Razão social", "cnpj": "CNPJ", "email": "E-mail",
                 "telefone": "Telefone", "endereco": "Endereço", "nome_dono": "Nome do dono", "email_dono": "E-mail do dono",
                 "senha_dono": "Senha do dono", "nome_exibicao": "Nome de exibição", "whatsapp": "WhatsApp",
                 "chave_pix": "Chave PIX", "inscricao_estadual": "Inscrição estadual", "latitude_gps": "Latitude da oficina",
                 "longitude_gps": "Longitude da oficina", "raio_gps_metros": "Raio do ponto (metros)",
                 "dia_pagamento_folha": "Dia do pagamento da folha", "dia_adiantamento_folha": "Dia do adiantamento"},
    "transacoes-financeiras": {"descricao": "Descrição", "categoria": "Categoria", "valor": "Valor", "tipo": "Tipo",
                               "data_vencimento": "Data de vencimento", "data_liquidacao": "Data de pagamento",
                               "status": "Situação", "forma_pagamento": "Forma de pagamento", "observacoes": "Observações"},
    "equipe": {"usuario_id": "Colaborador", "tipo": "Tipo", "data_inicio": "Data inicial", "data_fim": "Data final",
               "observacoes": "Observações", "latitude": "Latitude", "longitude": "Longitude", "mes_referencia": "Mês de referência",
               "data_vencimento": "Data de vencimento", "nota": "Nota", "comentario": "Comentário", "token": "Link de avaliação"},
    "bot": {"nome_cliente": "Nome do cliente", "telefone_cliente": "Telefone", "placa": "Placa", "km_atual": "Quilometragem"},
}
ROTULOS_GERAIS = {"skip": "Posição inicial", "limit": "Itens por página", "empresa_id": "Oficina", "busca": "Busca",
                  "data_inicio": "Data inicial", "data_fim": "Data final", "data_inicial": "Data inicial", "data_final": "Data final",
                  "valor_min": "Valor mínimo", "valor_max": "Valor máximo", "nome": "Nome", "telefone": "Telefone"}

LIMITES = {"greater_than_equal": ("ge", "não pode ser menor que"), "greater_than": ("gt", "precisa ser maior que"),
           "less_than_equal": ("le", "não pode ser maior que"), "less_than": ("lt", "precisa ser menor que")}


def _rotulo(rota: str, campo: str) -> str:
    return ROTULOS.get(rota, {}).get(campo) or ROTULOS_GERAIS.get(campo) or campo.replace("_", " ").capitalize()


def _num(v) -> str:
    return str(int(v)) if float(v) == int(v) else str(v).replace(".", ",")


def _mensagem(erro: dict, rotulo: str) -> str:
    tipo, ctx, msg = erro.get("type", ""), erro.get("ctx") or {}, erro.get("msg", "")
    if tipo == "missing":
        return f"{rotulo}: campo obrigatório."
    if tipo == "string_too_long":
        return f"{rotulo}: máximo de {ctx.get('max_length')} caracteres."
    if tipo == "string_too_short":
        n = ctx.get("min_length")
        return f"{rotulo}: precisa ter pelo menos {n} caractere{'s' if n != 1 else ''}."
    if tipo == "string_pattern_mismatch":
        if rotulo == "Mês de referência":
            return "Mês de referência: use o formato MM/AAAA, por exemplo 10/2026."
        return f"{rotulo}: formato inválido."
    if tipo in LIMITES:
        chave, texto = LIMITES[tipo]
        return f"{rotulo}: {texto} {_num(ctx.get(chave))}."
    if tipo in ("literal_error", "enum"):
        return f"{rotulo}: valor não permitido."
    if tipo == "value_error":
        texto = msg.removeprefix("Value error, ")
        if "email" in texto.lower() or "@" in texto:
            return f"{rotulo}: e-mail inválido."
        return texto  # as regras do projeto já escrevem a frase em português
    if tipo in ("int_parsing", "int_parsing_size", "int_from_float", "int_type"):
        return f"{rotulo}: informe um número inteiro."
    if tipo in ("float_parsing", "float_type", "decimal_parsing", "decimal_type"):
        return f"{rotulo}: informe um número."
    if tipo.startswith("uuid"):
        return f"{rotulo}: identificador inválido."
    if tipo.startswith(("date", "time")):
        return f"{rotulo}: data inválida (use AAAA-MM-DD)."
    if tipo in ("bool_parsing", "bool_type"):
        return f"{rotulo}: informe sim ou não."
    if tipo == "string_type":
        return f"{rotulo}: informe um texto."
    if tipo in ("json_invalid", "model_attributes_type", "dict_type", "model_type"):
        return "Os dados enviados estão em formato inválido."
    return f"{rotulo}: valor inválido."


async def validacao_exception_handler(request: Request, exc: RequestValidationError):
    """422 em português da oficina. Mesmo formato do FastAPI (detail = lista com loc/msg/type), só a msg muda;
    `input` e `ctx` ficam de fora (o input podia devolver a senha digitada)."""
    partes = request.url.path.split("/")
    rota = partes[3] if len(partes) > 3 and partes[1] == "api" else ""
    detalhe = []
    for erro in exc.errors():
        loc = list(erro.get("loc", ()))
        campo = next((p for p in reversed(loc) if isinstance(p, str)), "")
        rotulo = "" if campo in ("body", "query", "path", "") else _rotulo(rota, campo)
        detalhe.append({"loc": loc, "msg": _mensagem(erro, rotulo), "type": erro.get("type", "")})
    return JSONResponse(status_code=422, content={"detail": detalhe})


def erro_auth(e: Exception, padrao: str) -> str:
    """Texto do provedor de login (em inglês, técnico) fica no log; o cliente recebe português da oficina."""
    log.error("Erro do provedor de Auth: %s", e)
    if any(p in str(e).lower() for p in ("already", "registered", "exists", "duplicate")):
        return "Já existe um usuário com este e-mail."
    return padrao
