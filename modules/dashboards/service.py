from collections import Counter
from core.database import supabase

STATUS_VALIDOS = ('ORCAMENTO', 'AGUARDANDO_PECA', 'EXECUCAO', 'FINALIZADO', 'PAGO')

def obter_dashboard_operacional(empresa_id: str):
    os_data = supabase.table("ordens_servico").select("status").eq("empresa_id", empresa_id).execute().data
    counts = Counter(os.get("status", "ORCAMENTO") for os in os_data)
    status_counts = {st: counts[st] for st in STATUS_VALIDOS}

    total_abertas = status_counts['ORCAMENTO'] + status_counts['AGUARDANDO_PECA'] + status_counts['EXECUCAO']

    estoque_data = supabase.table("estoque").select("id, nome, quantidade, minimo_alerta, categoria").eq("empresa_id", empresa_id).execute().data
    itens_criticos = [i for i in estoque_data if i["quantidade"] <= i.get("minimo_alerta", 5)]

    ultimas_os = supabase.table("ordens_servico").select(
        "id, status, data_abertura, total_geral, clientes(nome, telefone), veiculos(placa, modelo)"
    ).eq("empresa_id", empresa_id).order("data_abertura", desc=True).limit(5).execute().data

    return {
        "total_abertas": total_abertas,
        "estoque_critico_count": len(itens_criticos),
        "status_counts": status_counts,
        "ultimas_os": ultimas_os,
        "itens_criticos": itens_criticos[:5]
    }