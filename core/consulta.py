"""O PostgREST do Supabase corta respostas em 1000 linhas. Quem precisa de todas as linhas lê por páginas."""


def todas(query, pagina: int = 1000) -> list:
    linhas, ini = [], 0
    while True:
        lote = query.range(ini, ini + pagina - 1).execute().data or []
        linhas += lote
        if len(lote) < pagina:
            return linhas
        ini += pagina
