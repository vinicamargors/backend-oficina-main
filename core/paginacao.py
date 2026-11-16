"""Busca e paginação feitas no banco (PostgREST), nunca em memória."""


def _pad(termo: str) -> str:
    t = termo.strip().replace("\\", "\\\\").replace("%", "\%").replace("_", "\_")
    return f"%{t}%"


def or_ilike(*pares: tuple[str, str]) -> str:
    """Valor para query.or_(): (coluna, termo)... → 'col.ilike."%termo%",...'. Aspas protegem vírgula e parênteses do termo."""
    return ",".join('{}.ilike."{}"'.format(c, _pad(t).replace("\\", "\\\\").replace('"', '\\"')) for c, t in pares)


def pagina(query, skip: int, limit: int) -> dict:
    """Executa a query (feita com count='exact') na janela pedida e devolve o envelope padrão."""
    r = query.range(skip, skip + limit - 1).execute()
    return {"items": r.data, "total": r.count or 0, "skip": skip, "limit": limit}
