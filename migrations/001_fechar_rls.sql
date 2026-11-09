-- Fecha o banco: anon não lê nem grava nada; authenticated só enxerga a própria empresa.
-- Backend (FastAPI) e legado (Flask) devem usar a chave service_role, que ignora RLS.
-- Rollback: 000_rollback_rls_aberto.sql

-- 1. Helpers SECURITY DEFINER (evitam a recursão de policy em usuarios)
CREATE OR REPLACE FUNCTION public.minha_empresa() RETURNS uuid
  LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public
  AS $$ SELECT empresa_id FROM public.usuarios WHERE id = auth.uid() AND ativo $$;

CREATE OR REPLACE FUNCTION public.meu_cargo() RETURNS text
  LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public
  AS $$ SELECT cargo::text FROM public.usuarios WHERE id = auth.uid() AND ativo $$;

REVOKE EXECUTE ON FUNCTION public.minha_empresa(), public.meu_cargo() FROM public, anon;
GRANT EXECUTE ON FUNCTION public.minha_empresa(), public.meu_cargo() TO authenticated;

-- 2. Remove todas as policies atuais
DO $$
DECLARE r record;
BEGIN
  FOR r IN SELECT policyname, tablename FROM pg_policies WHERE schemaname = 'public' LOOP
    EXECUTE format('DROP POLICY %I ON public.%I', r.policyname, r.tablename);
  END LOOP;
END $$;

-- 3. RLS ligado em todas as tabelas
ALTER TABLE public.empresas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.configuracoes_empresa ENABLE ROW LEVEL SECURITY;

-- 4. Tabelas de negócio: isolamento por empresa (master vê tudo)
DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY['clientes','veiculos','ordens_servico','os_itens','estoque',
                           'escalas_folgas','pontos_eletronicos','configuracoes_empresa','audit_logs'] LOOP
    EXECUTE format($p$
      CREATE POLICY tenant_all ON public.%I FOR ALL TO authenticated
        USING (empresa_id = public.minha_empresa() OR public.meu_cargo() = 'master')
        WITH CHECK (empresa_id = public.minha_empresa() OR public.meu_cargo() = 'master')
    $p$, t);
  END LOOP;
END $$;

-- 5. Financeiro: só DONO / FINANCEIRO / master
CREATE POLICY tenant_financeiro ON public.transacoes_financeiras FOR ALL TO authenticated
  USING ((empresa_id = public.minha_empresa() AND public.meu_cargo() IN ('DONO','FINANCEIRO')) OR public.meu_cargo() = 'master')
  WITH CHECK ((empresa_id = public.minha_empresa() AND public.meu_cargo() IN ('DONO','FINANCEIRO')) OR public.meu_cargo() = 'master');

-- 6. Avaliações: leitura pela empresa; insert público removido (passa pelo backend)
CREATE POLICY tenant_select ON public.avaliacoes_os FOR SELECT TO authenticated
  USING (empresa_id = public.minha_empresa() OR public.meu_cargo() = 'master');

-- 7. Empresas
CREATE POLICY empresa_select ON public.empresas FOR SELECT TO authenticated
  USING (id = public.minha_empresa() OR public.meu_cargo() = 'master');
CREATE POLICY empresa_update_dono ON public.empresas FOR UPDATE TO authenticated
  USING (id = public.minha_empresa() AND public.meu_cargo() = 'DONO')
  WITH CHECK (id = public.minha_empresa() AND public.meu_cargo() = 'DONO');
CREATE POLICY empresa_master ON public.empresas FOR ALL TO authenticated
  USING (public.meu_cargo() = 'master') WITH CHECK (public.meu_cargo() = 'master');

-- 8. Usuários: leitura pela empresa (e o próprio registro); escrita só DONO da empresa ou master;
--    DONO não cria/promove master nem move usuário para outra empresa.
CREATE POLICY usuarios_select ON public.usuarios FOR SELECT TO authenticated
  USING (id = auth.uid() OR empresa_id = public.minha_empresa() OR public.meu_cargo() = 'master');
CREATE POLICY usuarios_write ON public.usuarios FOR ALL TO authenticated
  USING ((empresa_id = public.minha_empresa() AND public.meu_cargo() = 'DONO') OR public.meu_cargo() = 'master')
  WITH CHECK ((empresa_id = public.minha_empresa() AND public.meu_cargo() = 'DONO' AND cargo <> 'master')
              OR public.meu_cargo() = 'master');

-- senha_hash do legado nunca sai pela API para usuários logados
REVOKE SELECT ON public.usuarios FROM anon, authenticated;
GRANT SELECT (id, email, nome, cargo, ativo, criado_em, empresa_id, telefone, salario_base,
              comissao_servico_pct, comissao_peca_pct, vale_transporte, vale_refeicao,
              paga_hora_extra, valor_hora_extra, estrelas_media, total_avaliacoes)
  ON public.usuarios TO authenticated;

-- 9. Funções SECURITY DEFINER antigas: fora da API pública
REVOKE EXECUTE ON FUNCTION public.fn_audit_log(), public.process_audit_log(), public.get_db_io_metrics()
  FROM public, anon, authenticated;
ALTER FUNCTION public.fn_audit_log() SET search_path = public;
ALTER FUNCTION public.process_audit_log() SET search_path = public;
ALTER FUNCTION public.fn_atualizar_media_avaliacoes_mecanico() SET search_path = public;
ALTER FUNCTION public.get_db_io_metrics() SET search_path = public;
