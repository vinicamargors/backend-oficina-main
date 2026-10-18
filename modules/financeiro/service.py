from collections import defaultdict
from core.database import supabase
from datetime import datetime

def obter_dados_financeiros(empresa_id: str, data_inicial: str = None, data_final: str = None):
    hoje = datetime.now()

    os_data = supabase.table("ordens_servico").select(
        "status, total_geral, lucro_estimado, data_abertura, data_fechamento"
    ).eq("empresa_id", empresa_id).execute().data

    faturamento_pago = 0.0
    faturamento_projetado = 0.0
    lucro_realizado = 0.0
    total_os_concluidas = 0

    dt_ini = datetime.fromisoformat(f"{data_inicial}T00:00:00") if data_inicial else None
    dt_fim = datetime.fromisoformat(f"{data_final}T23:59:59") if data_final else None

    hist_map = defaultdict(lambda: [0.0, 0.0])

    for os in os_data:
        status = os.get("status")
        total = float(os.get("total_geral") or 0.0)
        lucro = float(os.get("lucro_estimado") or 0.0)

        raw_date = os.get("data_fechamento") or os.get("data_abertura")
        if not raw_date:
            continue

        dt_os = datetime.fromisoformat(raw_date.replace("Z", "+00:00")[:19])
        is_pago_real = (status == "PAGO") or (status == "FINALIZADO" and (hoje - dt_os).days >= 30)

        if is_pago_real:
            chave_mes = f"{dt_os.month:02d}/{dt_os.year}"
            hist_map[chave_mes][0] += total
            hist_map[chave_mes][1] += lucro

        if dt_ini and dt_fim and not (dt_ini <= dt_os <= dt_fim):
            continue

        if is_pago_real:
            faturamento_pago += total
            lucro_realizado += lucro
            total_os_concluidas += 1
        elif status in ["ORCAMENTO", "EXECUCAO", "FINALIZADO", "AGUARDANDO_PECA"]:
            faturamento_projetado += total

    ticket_medio = (faturamento_pago / total_os_concluidas) if total_os_concluidas > 0 else 0.0

    historico = []
    for i in range(5, -1, -1):
        m_ref = hoje.month - i
        y_ref = hoje.year
        if m_ref <= 0:
            m_ref += 12
            y_ref -= 1
        mes_ano = f"{m_ref:02d}/{y_ref}"
        fat_mes, lucro_mes = hist_map[mes_ano]
        historico.append({
            "mes_ano": mes_ano,
            "faturamento": round(fat_mes, 2),
            "lucro": round(lucro_mes, 2)
        })

    return {
        "faturamento_pago": round(faturamento_pago, 2),
        "faturamento_projetado": round(faturamento_projetado, 2),
        "lucro_realizado": round(lucro_realizado, 2),
        "ticket_medio": round(ticket_medio, 2),
        "historico_6_meses": historico
    }



def obter_inteligencia_financeira(empresa_id: str, data_inicial: str = None, data_final: str = None):
    # A inteligência estratégica já consolida FINALIZADO e PAGO porque foca na PRODUÇÃO de valor
    os_list = supabase.table("ordens_servico").select(
        "id, status, total_geral, total_pecas, total_mao_obra, lucro_estimado, data_abertura, data_fechamento, forma_pagamento",
        "clientes(id, nome)",
        "veiculos(id, placa, marca, modelo, ano)",
        "usuarios(id, nome)"
    ).eq("empresa_id", empresa_id).execute().data

    dt_ini = datetime.fromisoformat(f"{data_inicial}T00:00:00") if data_inicial else None
    dt_fim = datetime.fromisoformat(f"{data_final}T23:59:59") if data_final else None

    clientes_aggr = {}
    mecanicos_aggr = {}
    pagamentos_aggr = {}
    marcas_aggr = {}
    
    lead_times_horas = []
    total_faturado_pecas = 0.0
    total_faturado_mao_obra = 0.0
    total_orcamentos = 0
    total_aprovados = 0

    for os in os_list:
        raw_date = os.get("data_fechamento") or os.get("data_abertura")
        if not raw_date:
            continue
            
        dt_os = datetime.fromisoformat(raw_date.replace("Z", "+00:00")[:19])

        if dt_ini and dt_fim:
            if not (dt_ini <= dt_os <= dt_fim):
                continue

        status = os.get("status")
        
        total_orcamentos += 1
        if status in ["EXECUCAO", "FINALIZADO", "PAGO"]:
            total_aprovados += 1

        if status not in ["FINALIZADO", "PAGO"]:
            continue 

        lucro = float(os.get("lucro_estimado") or 0.0)
        faturamento = float(os.get("total_geral") or 0.0)
        
        total_faturado_pecas += float(os.get("total_pecas") or 0.0)
        total_faturado_mao_obra += float(os.get("total_mao_obra") or 0.0)

        cli = os.get("clientes")
        if cli:
            cid = cli["id"]
            if cid not in clientes_aggr:
                clientes_aggr[cid] = {"nome": cli["nome"], "lucro": 0.0, "faturamento": 0.0, "qtd_os": 0}
            clientes_aggr[cid]["lucro"] += lucro
            clientes_aggr[cid]["faturamento"] += faturamento
            clientes_aggr[cid]["qtd_os"] += 1

        usr = os.get("usuarios")
        if usr:
            uid = usr["id"]
            if uid not in mecanicos_aggr:
                mecanicos_aggr[uid] = {"nome": usr["nome"], "lucro_gerado": 0.0, "faturamento_gerado": 0.0, "qtd_os": 0}
            mecanicos_aggr[uid]["lucro_gerado"] += lucro
            mecanicos_aggr[uid]["faturamento_gerado"] += faturamento
            mecanicos_aggr[uid]["qtd_os"] += 1

        forma = os.get("forma_pagamento")
        if forma:
            if forma not in pagamentos_aggr:
                pagamentos_aggr[forma] = {"forma": forma, "qtd": 0, "valor_total": 0.0}
            pagamentos_aggr[forma]["qtd"] += 1
            pagamentos_aggr[forma]["valor_total"] += faturamento

        vei = os.get("veiculos")
        if vei:
            marca = vei.get("marca") or "Não Informada"
            marca = marca.upper().strip()
            if marca not in marcas_aggr:
                marcas_aggr[marca] = {"marca": marca, "lucro": 0.0, "faturamento": 0.0, "qtd_os": 0}
            marcas_aggr[marca]["lucro"] += lucro
            marcas_aggr[marca]["faturamento"] += faturamento
            marcas_aggr[marca]["qtd_os"] += 1

        dt_abertura = os.get("data_abertura")
        dt_fechamento = os.get("data_fechamento")
        if dt_abertura and dt_fechamento:
            try:
                t1 = datetime.fromisoformat(dt_abertura.replace("Z", "+00:00")[:19])
                t2 = datetime.fromisoformat(dt_fechamento.replace("Z", "+00:00")[:19])
                horas = (t2 - t1).total_seconds() / 3600.0
                if horas >= 0:
                    lead_times_horas.append(horas)
            except Exception:
                pass

    clientes_sorted = sorted(clientes_aggr.values(), key=lambda x: x["lucro"], reverse=True)
    top_10 = clientes_sorted[:10]
    piores_10 = sorted(clientes_aggr.values(), key=lambda x: x["lucro"])[:10] 

    mec_sorted = sorted(mecanicos_aggr.values(), key=lambda x: x["lucro_gerado"], reverse=True)
    marcas_sorted = sorted(marcas_aggr.values(), key=lambda x: x["lucro"], reverse=True)

    avg_lead_time = round(sum(lead_times_horas) / len(lead_times_horas), 1) if lead_times_horas else 0.0
    taxa_conversao = round((total_aprovados / total_orcamentos) * 100, 1) if total_orcamentos > 0 else 0.0

    return {
        "top_10_clientes": top_10,
        "piores_10_clientes": piores_10,
        "produtividade_mecanicos": mec_sorted,
        "metodos_pagamento": list(pagamentos_aggr.values()),
        "rentabilidade_marcas": marcas_sorted,
        "origem_faturamento": {
            "pecas": total_faturado_pecas,
            "mao_obra": total_faturado_mao_obra
        },
        "lead_time_medio_horas": avg_lead_time,
        "taxa_conversao_orcamentos": taxa_conversao
    }