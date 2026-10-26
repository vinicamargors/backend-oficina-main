from collections import Counter
from datetime import datetime, timedelta, timezone
from core.database import supabase

STATUS_VALIDOS = ('ORCAMENTO', 'AGUARDANDO_PECA', 'EXECUCAO', 'FINALIZADO', 'PAGO')

def obter_dashboard_operacional(empresa_id: str):
    limite_30_dias = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()

    os_data = (
        supabase.table("ordens_servico")
        .select("status, data_abertura")
        .eq("empresa_id", empresa_id)
        .gte("data_abertura", limite_30_dias)
        .execute()
        .data
    )
    counts = Counter(os.get("status", "ORCAMENTO") for os in os_data)
    status_counts = {st: counts[st] for st in STATUS_VALIDOS}

    # Veículos no pátio: Aguardando Peça + Em Execução + Finalizado (últimos 30 dias)
    total_abertas = (
        status_counts['AGUARDANDO_PECA']
        + status_counts['EXECUCAO']
        + status_counts['FINALIZADO']
    )

    estoque_data = (
        supabase.table("estoque")
        .select("id, nome, quantidade, minimo_alerta, categoria")
        .eq("empresa_id", empresa_id)
        .neq("categoria", "MAO_OBRA")
        .execute()
        .data
    )
    itens_criticos = [i for i in estoque_data if i["quantidade"] <= i.get("minimo_alerta", 5)]

    ultimas_os = (
        supabase.table("ordens_servico")
        .select("id, status, data_abertura, total_geral, clientes(nome, telefone), veiculos(placa, modelo)")
        .eq("empresa_id", empresa_id)
        .gte("data_abertura", limite_30_dias)
        .order("data_abertura", desc=True)
        .limit(5)
        .execute()
        .data
    )

    return {
        "total_abertas": total_abertas,
        "estoque_critico_count": len(itens_criticos),
        "status_counts": status_counts,
        "ultimas_os": ultimas_os,
        "itens_criticos": itens_criticos[:5]
    }