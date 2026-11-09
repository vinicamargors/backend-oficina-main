-- ROLLBACK de 001_fechar_rls.sql: restaura o RLS exatamente como estava em 2026-11-09 (banco aberto).
-- Use só em emergência: devolve o acesso público total via chave anon.
DO $$
DECLARE r record;
BEGIN
  FOR r IN SELECT policyname, tablename FROM pg_policies WHERE schemaname = 'public' LOOP
    EXECUTE format('DROP POLICY %I ON public.%I', r.policyname, r.tablename);
  END LOOP;
END $$;

ALTER TABLE public.empresas DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.configuracoes_empresa DISABLE ROW LEVEL SECURITY;

GRANT SELECT ON public.usuarios TO anon, authenticated;

CREATE POLICY acesso_total_logs ON public.audit_logs AS PERMISSIVE FOR ALL TO public USING (true) WITH CHECK (true);
CREATE POLICY avaliacoes_public_insert ON public.avaliacoes_os AS PERMISSIVE FOR INSERT TO anon, authenticated WITH CHECK (true);
CREATE POLICY avaliacoes_tenant_select ON public.avaliacoes_os AS PERMISSIVE FOR SELECT TO authenticated USING ((empresa_id IN ( SELECT usuarios.empresa_id FROM usuarios WHERE (usuarios.id = auth.uid()))));
CREATE POLICY acesso_total_clientes ON public.clientes AS PERMISSIVE FOR ALL TO public USING (true) WITH CHECK (true);
CREATE POLICY escalas_tenant_isolation ON public.escalas_folgas AS PERMISSIVE FOR ALL TO authenticated USING ((empresa_id IN ( SELECT usuarios.empresa_id FROM usuarios WHERE (usuarios.id = auth.uid()))));
CREATE POLICY acesso_total_estoque ON public.estoque AS PERMISSIVE FOR ALL TO public USING (true) WITH CHECK (true);
CREATE POLICY acesso_total_os ON public.ordens_servico AS PERMISSIVE FOR ALL TO public USING (true) WITH CHECK (true);
CREATE POLICY acesso_total_os_itens ON public.os_itens AS PERMISSIVE FOR ALL TO public USING (true) WITH CHECK (true);
CREATE POLICY pontos_tenant_isolation ON public.pontos_eletronicos AS PERMISSIVE FOR ALL TO authenticated USING ((empresa_id IN ( SELECT usuarios.empresa_id FROM usuarios WHERE (usuarios.id = auth.uid()))));
CREATE POLICY "Acesso por tenant" ON public.transacoes_financeiras AS PERMISSIVE FOR ALL TO public USING (true);
CREATE POLICY transacoes_tenant_isolation ON public.transacoes_financeiras AS PERMISSIVE FOR ALL TO authenticated USING ((empresa_id IN ( SELECT usuarios.empresa_id FROM usuarios WHERE (usuarios.id = auth.uid()))));
CREATE POLICY acesso_total_usuarios ON public.usuarios AS PERMISSIVE FOR ALL TO public USING (true) WITH CHECK (true);
CREATE POLICY usuarios_update_gestor_only ON public.usuarios AS PERMISSIVE FOR UPDATE TO authenticated USING ((((SELECT usuarios_1.cargo FROM usuarios usuarios_1 WHERE (usuarios_1.id = auth.uid())))::text = ANY ((ARRAY['DONO'::character varying, 'master'::character varying])::text[]))) WITH CHECK ((((SELECT usuarios_1.cargo FROM usuarios usuarios_1 WHERE (usuarios_1.id = auth.uid())))::text = ANY ((ARRAY['DONO'::character varying, 'master'::character varying])::text[])));
CREATE POLICY acesso_total_veiculos ON public.veiculos AS PERMISSIVE FOR ALL TO public USING (true) WITH CHECK (true);

GRANT EXECUTE ON FUNCTION public.fn_audit_log(), public.process_audit_log(), public.get_db_io_metrics() TO anon, authenticated;
