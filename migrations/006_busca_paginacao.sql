-- Fase 7 (T-002): busca de OS no banco. Antes: listar_os baixava até 5000 OS e filtrava em Python.
-- A view junta OS + cliente + veículo e expõe uma coluna `busca` para ilike. Só o backend (service_role) lê.
-- security_invoker: a view obedece ao RLS de quem consulta (RLS segue fechado). Rollback no fim do arquivo.
-- shortcut: ilike '%x%' faz varredura da empresa; se passar de ~50 mil OS por oficina, criar índice pg_trgm.

CREATE OR REPLACE VIEW public.os_busca WITH (security_invoker = true) AS
SELECT o.id, o.empresa_id, o.cliente_id, o.veiculo_id, o.km_atual, o.status, o.data_abertura,
       o.total_geral, o.descricao_problema,
       c.nome AS cliente_nome, c.telefone AS cliente_telefone,
       v.placa AS veiculo_placa, v.modelo AS veiculo_modelo,
       concat_ws(' ', c.nome, v.placa, v.modelo, o.id::text, o.descricao_problema) AS busca,
       regexp_replace(coalesce(v.placa, ''), '[^a-zA-Z0-9]', '', 'g') AS placa_limpa
  FROM public.ordens_servico o
  LEFT JOIN public.clientes c ON c.id = o.cliente_id
  LEFT JOIN public.veiculos v ON v.id = o.veiculo_id;

REVOKE ALL ON public.os_busca FROM anon, authenticated;
GRANT SELECT ON public.os_busca TO service_role;

-- ROLLBACK:
--   DROP VIEW IF EXISTS public.os_busca;
