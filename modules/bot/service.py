import os
import json
import httpx
from fastapi import HTTPException
from google import genai
from google.genai import types
from core.database import supabase
from core.security import limpar_telefone

from . import schemas
from modules.os.schemas import OSUpdate
from modules.os.service import recalcular_totais_os, atualizar_os
from modules.veiculos.service import consultar_placa_externa

# ==========================================
# 1. MOTORES DE INTELIGÊNCIA & HTTP
# ==========================================
CHAVE_API = os.getenv("GEMINI_API_KEY")
if not CHAVE_API:
    raise RuntimeError("🚨 ALERTA VERMELHO: GEMINI_API_KEY não encontrada no .env!")

gemini_client = genai.Client(api_key=CHAVE_API)
http_client = httpx.AsyncClient(timeout=15.0)

# ==========================================
# 2. IDENTIFICAÇÃO (A Catraca do Sistema)
# ==========================================
def identificar_mecanico(telefone: str):
    """Verifica se o número do WhatsApp é funcionário ativo e devolve as credenciais pro Typebot"""
    tel_limpo = limpar_telefone(telefone)
    usuario = supabase.table("usuarios").select("id, empresa_id, nome").eq("telefone", tel_limpo).eq("ativo", True).execute().data
    if not usuario:
        raise HTTPException(status_code=403, detail="Telefone não autorizado ou inativo.")

    return {
        "mecanico_id": usuario[0]["id"],
        "empresa_id": usuario[0]["empresa_id"],
        "nome": usuario[0]["nome"]
    }

# ==========================================
# 3. MOTORES DE BUSCA IMPLACÁVEL
# ==========================================
def buscar_cliente_veiculo_cruzado(empresa_id: str, termo_busca: str):
    clientes_data = supabase.table("clientes").select("id, nome, veiculos(id, placa, modelo, marca)").eq("empresa_id", empresa_id).execute().data
    palavras = [p.lower() for p in termo_busca.split() if len(p) > 2]

    ranking = []
    for c in clientes_data:
        nome_cliente = (c.get("nome") or "").lower()
        veiculos = c.get("veiculos") or []
        if not isinstance(veiculos, list):
            veiculos = [veiculos]

        for v in veiculos:
            score = 0
            modelo = (v.get("modelo") or "").lower()
            marca = (v.get("marca") or "").lower()
            placa = (v.get("placa") or "").lower()

            for p in palavras:
                if p in nome_cliente: score += 3
                if p in modelo or p in marca: score += 4
                if p in placa: score += 5

            if score > 0:
                ranking.append({
                    "cliente_id": c["id"],
                    "cliente_nome": c["nome"],
                    "veiculo_id": v["id"],
                    "veiculo_modelo": v["modelo"],
                    "veiculo_placa": v["placa"],
                    "score": score
                })

    return sorted(ranking, key=lambda x: x["score"], reverse=True)[:3]

def buscar_historico_os_por_veiculo(empresa_id: str, veiculo_id: str):
    return supabase.table("ordens_servico").select(
        "id, status, total_geral, data_abertura, veiculos(placa, modelo), clientes(nome)"
    ).eq("empresa_id", empresa_id).eq("veiculo_id", veiculo_id).order("data_abertura", desc=True).execute().data

def buscar_os_ativa_por_placa_cliente(empresa_id: str, termo_busca: str):
    os_ativas = supabase.table("ordens_servico").select(
        "id, status, total_geral, veiculos(placa, modelo), clientes(nome)"
    ).eq("empresa_id", empresa_id).in_("status", ["ORCAMENTO", "EXECUCAO", "AGUARDANDO_PECA"]).execute().data

    palavras = [p.lower() for p in termo_busca.split() if len(p) > 2]
    termo_limpo = termo_busca.lower().replace("-", "").replace(" ", "")

    ranking = []
    for o in os_ativas:
        score = 0
        placa_limpa = (o.get("veiculos", {}).get("placa") or "").replace("-", "").replace(" ", "").lower()
        cliente = (o.get("clientes", {}).get("nome") or "").lower()

        if termo_limpo and termo_limpo in placa_limpa: score += 10
        for p in palavras:
            if p in cliente: score += 3

        if score > 0:
            o["score"] = score
            ranking.append(o)

    return sorted(ranking, key=lambda x: x["score"], reverse=True)[:3]

# ==========================================
# 4. ABERTURA DE ORDEM DE SERVIÇO
# ==========================================
def abrir_os(req: schemas.CriarOSRequest):
    os_aberta = supabase.table("ordens_servico").select("id").eq("veiculo_id", req.veiculo_id).eq("status", "ORCAMENTO").eq("empresa_id", req.empresa_id).execute().data
    if os_aberta:
        return {"os_id": os_aberta[0]["id"]}

    nova_os = supabase.table("ordens_servico").insert({
        "empresa_id": req.empresa_id,
        "cliente_id": req.cliente_id,
        "veiculo_id": req.veiculo_id,
        "mecanico_responsavel_id": req.mecanico_id,
        "status": "ORCAMENTO"
    }).execute().data[0]
    return {"os_id": nova_os["id"]}

async def executar_cadastro_rapido(req: schemas.CadastroRapidoRequest):
    placa_limpa = req.placa.upper().replace("-", "").replace(" ", "")

    # Idempotência: se o veículo já existir na empresa, reaproveita o cadastro
    veiculo_existente = supabase.table("veiculos").select("id, cliente_id, modelo").eq("placa", placa_limpa).eq("empresa_id", req.empresa_id).execute().data
    if veiculo_existente:
        veiculo_id = veiculo_existente[0]["id"]
        cliente_id = veiculo_existente[0]["cliente_id"]
        modelo_completo = veiculo_existente[0]["modelo"]

        os_aberta = supabase.table("ordens_servico").select("id").eq("veiculo_id", veiculo_id).eq("status", "ORCAMENTO").eq("empresa_id", req.empresa_id).execute().data
        if os_aberta:
            return {"os_id": os_aberta[0]["id"], "modelo_veiculo": modelo_completo}
    else:
        cliente_db = supabase.table("clientes").insert({
            "empresa_id": req.empresa_id,
            "nome": req.nome_cliente,
            "telefone": limpar_telefone(req.telefone_cliente)
        }).execute().data[0]
        cliente_id = cliente_db["id"]

        try:
            dados_placa = await consultar_placa_externa(placa_limpa)
            modelo_completo = f"{dados_placa.get('marca', '')} {dados_placa.get('modelo', '')}".strip() or "Modelo Não Identificado na Base"
        except Exception:
            modelo_completo = f"Veículo ({placa_limpa} - Consulta Falhou)"

        veiculo_db = supabase.table("veiculos").insert({
            "empresa_id": req.empresa_id,
            "cliente_id": cliente_id,
            "modelo": modelo_completo,
            "placa": placa_limpa
        }).execute().data[0]
        veiculo_id = veiculo_db["id"]

    nova_os = supabase.table("ordens_servico").insert({
        "empresa_id": req.empresa_id,
        "cliente_id": cliente_id,
        "veiculo_id": veiculo_id,
        "mecanico_responsavel_id": req.mecanico_id,
        "status": "ORCAMENTO"
    }).execute().data[0]

    return {"os_id": nova_os["id"], "modelo_veiculo": modelo_completo}

def atualizar_dados_os(req: schemas.AtualizarOSRequest):
    os_res = supabase.table("ordens_servico").select("empresa_id").eq("id", req.os_id).execute().data
    if not os_res:
        raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada.")

    atualizar_os(
        os_id=req.os_id,
        empresa_id=os_res[0]["empresa_id"],
        dados=OSUpdate(km_atual=req.km_atual, descricao_problema=req.problema_relatado)
    )
    return {"status": "sucesso"}

# ==========================================
# 5. O DESTRUIDOR DE FRICÇÃO (Áudio In-Memory direto pro Gemini)
# ==========================================
async def processar_e_injetar_audio(req: schemas.ProcessarAudioRequest):
    resp = await http_client.get(req.url_audio)
    resp.raise_for_status()

    audio_part = types.Part.from_bytes(data=resp.content, mime_type="audio/ogg")
    prompt = """
    Você é um gerente de oficina mecânica. Escute o áudio relatado pelo mecânico e organize os itens para a Ordem de Serviço.
    1. VINCULAÇÃO DE MÃO DE OBRA: Nunca deixe o nome apenas como "Mão de obra". Amarre ao serviço. (Ex: "Mão de obra - Troca de filtro")
    2. ESPECIFICAÇÕES: Capture todos os números técnicos (Ex: "Comando 268", "Óleo 5w30").
    3. PADRONIZAÇÃO: Use formato numérico float para os preços.
    """

    response = gemini_client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=[audio_part, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schemas.ExtracaoOS,
            temperature=0.1,
        ),
    )
    dados_extraidos = json.loads(response.text)

    estoque_empresa = supabase.table("estoque").select("id, nome, custo, quantidade").eq("empresa_id", req.empresa_id).execute().data

    itens_inseridos = []
    for item in dados_extraidos.get("itens", []):
        estoque_id = None
        custo_unitario = 0.0

        if item["tipo"] == "PECA" and estoque_empresa:
            nome_lower = item["nome_item"].lower()
            match = next((e for e in estoque_empresa if e["nome"].lower() in nome_lower or nome_lower in e["nome"].lower()), None)
            if match:
                estoque_id = match["id"]
                custo_unitario = float(match.get("custo") or 0.0)
                nova_qtd = max(0, match["quantidade"] - item["quantidade"])
                supabase.table("estoque").update({"quantidade": nova_qtd}).eq("id", estoque_id).eq("empresa_id", req.empresa_id).execute()
                match["quantidade"] = nova_qtd

        db_item = {
            "os_id": req.os_id,
            "empresa_id": req.empresa_id,
            "estoque_id": estoque_id,
            "tipo": item["tipo"],
            "nome_item": item["nome_item"],
            "quantidade": item["quantidade"],
            "venda_unitario": item["venda_unitario"],
            "custo_unitario": custo_unitario
        }
        supabase.table("os_itens").insert(db_item).execute()
        itens_inseridos.append(f"🔸 {item['quantidade']}x {item['nome_item']} (R$ {item['venda_unitario']})")

    recalcular_totais_os(req.os_id)

    return {
        "status": "sucesso",
        "resumo_itens": "\n".join(itens_inseridos)
    }