-- Fase 2 (#4): salário, comissões, vales e hora extra saem da API para usuários logados.
-- RH passa só pelo backend (service_role), que exige DONO/master (FINANCEIRO via folha no servidor).
-- Usuário logado também não grava mais em `usuarios` direto: criar/editar/desativar só pelo backend.
-- Legado (service_role) não é afetado. Rollback no fim do arquivo.

REVOKE SELECT ON public.usuarios FROM anon, authenticated;
GRANT SELECT (id, email, nome, cargo, ativo, criado_em, empresa_id, telefone, estrelas_media, total_avaliacoes)
  ON public.usuarios TO authenticated;

REVOKE INSERT, UPDATE, DELETE ON public.usuarios FROM anon, authenticated;
DROP POLICY IF EXISTS usuarios_write ON public.usuarios;

-- Rollback:
-- GRANT SELECT (salario_base, comissao_servico_pct, comissao_peca_pct, vale_transporte, vale_refeicao,
--               paga_hora_extra, valor_hora_extra) ON public.usuarios TO authenticated;
-- GRANT INSERT, UPDATE, DELETE ON public.usuarios TO authenticated;
-- CREATE POLICY usuarios_write ON public.usuarios FOR ALL TO authenticated
--   USING ((empresa_id = public.minha_empresa() AND public.meu_cargo() = 'DONO') OR public.meu_cargo() = 'master')
--   WITH CHECK ((empresa_id = public.minha_empresa() AND public.meu_cargo() = 'DONO' AND cargo <> 'master')
--               OR public.meu_cargo() = 'master');
