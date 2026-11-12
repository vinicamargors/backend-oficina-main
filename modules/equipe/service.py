import math
from datetime import datetime, date
from typing import Optional
from fastapi import HTTPException
from postgrest.exceptions import APIError
from core.avaliacao_token import gerar_token, ler_token
from core.database import supabase
from core.security import garantir_da_empresa
from core.tempo import agora_br
from .schemas import (
    EscalaFolgaCreate,
    PontoEletronicoCreate,
    AvaliacaoPublicaCreate,
    LancarFolhaInput,
    LancarFolhaResponse,
)

def calcular_distancia_metros(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula distância geográfica exata em metros via fórmula de Haversine."""
    R = 6371000.0  # Raio médio da Terra em metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


# ==========================================
# 1. ESCALAS E FOLGAS
# ==========================================
def listar_escalas(empresa_id: str):
    res = supabase.table("escalas_folgas").select(
        "*, usuarios(nome)"
    ).eq("empresa_id", empresa_id).order("data_inicio", desc=True).execute()

    itens = []
    for row in res.data or []:
        usuario_info = row.pop("usuarios", None) or {}
        row["usuario_nome"] = usuario_info.get("nome")
        itens.append(row)
    return itens

def criar_escala(empresa_id: str, dados: EscalaFolgaCreate):
    payload = dados.model_dump(mode="json")
    payload["empresa_id"] = empresa_id

    res = supabase.table("escalas_folgas").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Erro ao registrar escala ou folga.")

    registro = res.data[0]
    usr = supabase.table("usuarios").select("nome").eq("id", str(dados.usuario_id)).execute().data
    registro["usuario_nome"] = usr[0]["nome"] if usr else None
    return registro

def deletar_escala(empresa_id: str, escala_id: str):
    supabase.table("escalas_folgas").delete().eq("id", escala_id).eq("empresa_id", empresa_id).execute()
    return {"status": "sucesso", "detail": "Escala ou folga removida."}


# ==========================================
# 2. PONTO ELETRÔNICO MOBILE COM GPS
# ==========================================
def listar_pontos(empresa_id: str, data_filtro: Optional[str] = None):
    query = supabase.table("pontos_eletronicos").select(
        "*, usuarios(nome)"
    ).eq("empresa_id", empresa_id).order("created_at", desc=True)

    if data_filtro:
        query = query.eq("data", data_filtro)

    res = query.execute()
    itens = []
    for row in res.data or []:
        usuario_info = row.pop("usuarios", None) or {}
        row["usuario_nome"] = usuario_info.get("nome")
        itens.append(row)
    return itens

def registrar_ponto(empresa_id: str, usuario: dict, dados: PontoEletronicoCreate):
    # Usuário = quem está logado; data e hora = relógio do servidor em Brasília. Nada disso é aceito do cliente.
    agora = agora_br()
    data_registro = agora.date()
    hora_registro = agora.strftime("%H:%M:%S")
    usuario_id = str(usuario["id"])

    # Verifica configuração de GPS da oficina
    cfg_res = supabase.table("configuracoes_empresa").select(
        "latitude_gps, longitude_gps, raio_gps_metros"
    ).eq("empresa_id", empresa_id).execute().data

    dentro_raio = True
    distancia_metros = 0.0

    if cfg_res and cfg_res[0].get("latitude_gps") and cfg_res[0].get("longitude_gps"):
        lat_oficina = float(cfg_res[0]["latitude_gps"])
        lon_oficina = float(cfg_res[0]["longitude_gps"])
        raio_maximo = float(cfg_res[0].get("raio_gps_metros") or 100)

        if dados.latitude is not None and dados.longitude is not None:
            dist = calcular_distancia_metros(dados.latitude, dados.longitude, lat_oficina, lon_oficina)
            distancia_metros = round(dist, 1)
            dentro_raio = dist <= raio_maximo
        else:
            # Sem coordenadas do mobile quando a empresa exige
            dentro_raio = False
            distancia_metros = None

    payload = {
        "empresa_id": empresa_id,
        "usuario_id": usuario_id,
        "tipo": dados.tipo,
        "data": str(data_registro),
        "hora": hora_registro,
        "latitude": dados.latitude,
        "longitude": dados.longitude,
        "dentro_raio": dentro_raio,
        "distancia_metros": distancia_metros,
    }

    res = supabase.table("pontos_eletronicos").insert(payload).execute()
    if not res.data:
        raise HTTPException(status_code=400, detail="Erro ao registrar ponto eletrônico.")

    registro = res.data[0]
    registro["usuario_nome"] = usuario.get("nome")
    return registro


# ==========================================
# 3. AVALIAÇÃO DA OS (NPS & 5 ESTRELAS)
# ==========================================
def listar_avaliacoes(empresa_id: str):
    res = supabase.table("avaliacoes_os").select(
        "*, usuarios(nome)"
    ).eq("empresa_id", empresa_id).order("created_at", desc=True).execute()

    itens = []
    for row in res.data or []:
        usuario_info = row.pop("usuarios", None) or {}
        row["mecanico_nome"] = usuario_info.get("nome")
        itens.append(row)
    return itens

STATUS_AVALIAVEL = ("FINALIZADO", "PAGO")


def gerar_link_avaliacao(empresa_id: str, os_id: str):
    """Link que o atendente manda ao cliente. Só para OS da empresa já finalizada ou paga."""
    garantir_da_empresa("ordens_servico", os_id, empresa_id, "OS")
    status = supabase.table("ordens_servico").select("status").eq("id", os_id).execute().data[0]["status"]
    if status not in STATUS_AVALIAVEL:
        raise HTTPException(status_code=400, detail="A avaliação só fica disponível depois que a OS é finalizada.")
    token = gerar_token(os_id)
    return {"token": token, "caminho": f"/?modo=avaliar&token={token}"}


def _os_do_token(token: str) -> dict:
    """Resolve o token na OS (com cliente e veículo). Token ruim e OS inexistente dão o mesmo 404."""
    nao_achou = HTTPException(status_code=404, detail="Link de avaliação inválido ou expirado.")
    os_id = ler_token(token)
    if not os_id:
        raise nao_achou
    achou = supabase.table("ordens_servico").select(
        "id, empresa_id, mecanico_responsavel_id, clientes(nome), veiculos(modelo, placa)"
    ).eq("id", os_id).execute().data
    if not achou:
        raise nao_achou
    return achou[0]


def _ja_avaliada(os_id: str) -> bool:
    return bool(supabase.table("avaliacoes_os").select("id").eq("os_id", os_id).execute().data)


def obter_info_avaliacao(token: str):
    os_row = _os_do_token(token)
    veiculo = os_row.get("veiculos") or {}
    return {
        "veiculo_modelo": veiculo.get("modelo") or "",
        "veiculo_placa": veiculo.get("placa") or "",
        "ja_avaliada": _ja_avaliada(os_row["id"]),
    }


def registrar_avaliacao(dados: AvaliacaoPublicaCreate):
    os_row = _os_do_token(dados.token)
    ja_avaliada = HTTPException(status_code=409, detail="Esta OS já foi avaliada. Obrigado!")
    if _ja_avaliada(os_row["id"]):
        raise ja_avaliada

    cliente = os_row.get("clientes") or {}
    veiculo = os_row.get("veiculos") or {}
    payload = {
        "empresa_id": os_row["empresa_id"],
        "os_id": os_row["id"],
        "mecanico_id": os_row.get("mecanico_responsavel_id"),
        "cliente_nome": cliente.get("nome") or "Cliente",
        "veiculo_modelo": veiculo.get("modelo") or "",
        "veiculo_placa": veiculo.get("placa") or "",
        "nota": dados.nota,
        "comentario": (dados.comentario or "").strip() or None,
    }
    try:
        res = supabase.table("avaliacoes_os").insert(payload).execute()
    except APIError as e:
        if e.code == "23505":  # duas avaliações ao mesmo tempo: o índice único deixa passar só uma
            raise ja_avaliada
        raise
    if not res.data:
        raise HTTPException(status_code=400, detail="Erro ao salvar avaliação do cliente.")

    registro = res.data[0]
    if registro.get("mecanico_id"):  # estrelas_media/total_avaliacoes do mecânico: trigger do banco
        usr = supabase.table("usuarios").select("nome").eq("id", registro["mecanico_id"]).execute().data
        registro["mecanico_nome"] = usr[0]["nome"] if usr else None
    return registro


# ==========================================
# 4. LANÇAR FOLHA NO CONTAS A PAGAR
# ==========================================
def lancar_folha_contas_a_pagar(empresa_id: str, dados: LancarFolhaInput) -> LancarFolhaResponse:
    # Busca funcionários ativos da oficina
    usuarios = supabase.table("usuarios").select(
        "id, nome, cargo, salario_base, vale_transporte, vale_refeicao"
    ).eq("empresa_id", empresa_id).eq("ativo", True).execute().data or []

    if not usuarios:
        raise HTTPException(status_code=400, detail="Nenhum colaborador ativo cadastrado para gerar folha.")

    total_folha = 0.0
    for u in usuarios:
        salario = float(u.get("salario_base") or 0.0)
        vt = float(u.get("vale_transporte") or 0.0) if dados.incluir_vales else 0.0
        vr = float(u.get("vale_refeicao") or 0.0) if dados.incluir_vales else 0.0
        total_folha += (salario + vt + vr)

    if total_folha <= 0:
        raise HTTPException(status_code=400, detail="O valor total da folha calculada é R$ 0,00.")

    # Data de vencimento
    vencimento = dados.data_vencimento
    if not vencimento:
        cfg = supabase.table("configuracoes_empresa").select("dia_pagamento_folha").eq("empresa_id", empresa_id).execute().data
        dia_folha = int(cfg[0].get("dia_pagamento_folha") or 5) if cfg else 5

        hoje = date.today()
        # Se hoje já passou do dia_folha, lança pro próximo mês, senão pro mês atual
        ano = hoje.year
        mes = hoje.month
        if hoje.day > dia_folha:
            mes += 1
            if mes > 12:
                mes = 1
                ano += 1
        dia_safe = min(dia_folha, 28)
        vencimento = date(ano, mes, dia_safe)

    descricao = dados.descricao_custom or f"Folha de Pagamento Equipe - Ref: {dados.mes_referencia}"

    transacao_data = {
        "empresa_id": empresa_id,
        "tipo": "DESPESA",
        "categoria": "FOLHA_PAGAMENTO",
        "descricao": descricao,
        "valor": round(total_folha, 2),
        "data_vencimento": str(vencimento),
        "status": "PENDENTE",
        "observacoes": f"Lançamento automático de folha ({len(usuarios)} funcionários). Inclui vales: {'Sim' if dados.incluir_vales else 'Não'}."
    }

    res_trans = supabase.table("transacoes_financeiras").insert(transacao_data).execute()
    if not res_trans.data:
        raise HTTPException(status_code=400, detail="Erro ao gerar conta a pagar da folha no módulo financeiro.")

    transacao = res_trans.data[0]

    return LancarFolhaResponse(
        sucesso=True,
        total_funcionarios=len(usuarios),
        valor_total_folha=round(total_folha, 2),
        transacao_id=transacao["id"],
        mensagem=f"Folha de R$ {total_folha:,.2f} lançada com sucesso no Contas a Pagar com vencimento em {vencimento.strftime('%d/%m/%Y')}."
    )

