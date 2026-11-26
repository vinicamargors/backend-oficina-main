"""O plano da oficina vive em `assinaturas` (1 por empresa), não mais em `empresas.plano` (Fase 4.2)."""
from core.database import supabase

PLANO_PADRAO = "basico"


def planos_das_empresas(empresa_ids: list) -> dict:
    """{empresa_id: plano}. Oficina sem assinatura conta como plano padrão."""
    if not empresa_ids:
        return {}
    linhas = supabase.table("assinaturas").select("empresa_id, plano").in_("empresa_id", empresa_ids).execute().data or []
    return {l["empresa_id"]: l["plano"] for l in linhas}


def com_plano(empresas: list) -> list:
    """Devolve as mesmas empresas com o campo `plano` preenchido a partir de `assinaturas`."""
    planos = planos_das_empresas([e["id"] for e in empresas])
    return [{**e, "plano": planos.get(e["id"], PLANO_PADRAO)} for e in empresas]


def gravar_plano(empresa_id: str, plano: str = PLANO_PADRAO) -> None:
    """Cria a assinatura da oficina ou troca o plano. Não mexe no resto (status, valores)."""
    existente = supabase.table("assinaturas").select("id").eq("empresa_id", empresa_id).execute().data
    if existente:
        supabase.table("assinaturas").update({"plano": plano}).eq("empresa_id", empresa_id).execute()
    else:
        supabase.table("assinaturas").insert({"empresa_id": empresa_id, "plano": plano}).execute()
