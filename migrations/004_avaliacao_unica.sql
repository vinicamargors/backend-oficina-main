-- Fase 5 (#7): uma avaliação por OS e inserção só pelo backend (service_role).
-- A policy pública de insert já tinha caído com o RLS fechado (001); o DROP IF EXISTS garante que não volta.
-- A tabela estava vazia na aplicação (2026-11-12); se houver duplicatas antes de aplicar, o CREATE falha de propósito.
-- Rollback no fim do arquivo.

DROP POLICY IF EXISTS avaliacoes_public_insert ON public.avaliacoes_os;

CREATE UNIQUE INDEX IF NOT EXISTS avaliacoes_os_os_id_key ON public.avaliacoes_os (os_id);

-- ROLLBACK:
-- DROP INDEX IF EXISTS public.avaliacoes_os_os_id_key;
