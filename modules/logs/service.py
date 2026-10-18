from core.database import supabase
from fastapi import Response
from datetime import datetime

def listar_logs(empresa_id: str, tabela: str = None, operacao: str = None, data_ini: str = None, data_fim: str = None):
    query = supabase.table("audit_logs").select("*").eq("empresa_id", empresa_id).order("criado_em", desc=True).limit(500)

    # Filtros opcionais injetados dinamicamente
    if tabela: query = query.eq("tabela", tabela)
    if operacao: query = query.eq("operacao", operacao)
    if data_ini: query = query.gte("criado_em", data_ini)
    if data_fim: query = query.lte("criado_em", f"{data_fim}T23:59:59")

    return query.execute().data

def exportar_logs_txt(empresa_id: str, data_ini: str = None, data_fim: str = None):
    logs = listar_logs(empresa_id, None, None, data_ini, data_fim)

    linhas = [f"=== LOG DE AUDITORIA — {datetime.now().strftime('%d/%m/%Y %H:%M')} ===\n"]
    for log in logs:
        dt = log.get("criado_em", "")[:19].replace("T", " ")
        linhas.append(f"[{dt}] {log['operacao']:6} | Tabela: {log['tabela']:20} | ID: {log.get('registro_id', '')}")
        
        if log['operacao'] == 'DELETE' and log.get('dados_antes'):
            motivo = log['dados_antes'].get('motivo_exclusao', 'Exclusão direta no sistema')
            linhas.append(f"         Motivo: {motivo}")
        linhas.append("")

    txt = "\n".join(linhas)
    nome_arquivo = f"log_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"

    # O FastAPI empacota o texto e manda o navegador do usuário baixar como arquivo na hora.
    return Response(
        content=txt,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"}
    )