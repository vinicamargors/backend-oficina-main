-- Fase 6.1: categorias de estoque livres, por empresa, guardadas no servidor.
-- Antes: o CHECK `check_categoria` só aceitava 5 valores, mas o front deixava criar outras (que só existiam no localStorage).
-- Agora o backend normaliza (trim + maiúsculas, 1–40 caracteres) e a lista de categorias da oficina vive em `categorias_estoque`.
-- Dados existentes (PECAS, MAO_OBRA, FLUIDOS, PNEUS) continuam válidos. Rollback no fim do arquivo.

ALTER TABLE public.estoque DROP CONSTRAINT IF EXISTS check_categoria;

CREATE TABLE IF NOT EXISTS public.categorias_estoque (
  empresa_id uuid NOT NULL REFERENCES public.empresas(id) ON DELETE CASCADE,
  nome       varchar(40) NOT NULL CHECK (nome = upper(btrim(nome)) AND length(nome) >= 1),
  PRIMARY KEY (empresa_id, nome)
);

-- Só o backend (service_role) lê e grava, como o resto dos dados da oficina (ver 001).
ALTER TABLE public.categorias_estoque ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.categorias_estoque FROM anon, authenticated;

-- ROLLBACK (só se nenhum item usar categoria fora das 5 antigas):
-- DROP TABLE IF EXISTS public.categorias_estoque;
-- ALTER TABLE public.estoque ADD CONSTRAINT check_categoria
--   CHECK (categoria IN ('PECAS','FLUIDOS','PNEUS','ELETRICA','MAO_OBRA'));
