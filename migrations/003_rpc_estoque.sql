-- Fase 4 (#6): estoque e exclusão de OS atômicos. Só o backend (service_role) executa estas funções.
-- Antes: "ler saldo → calcular em Python → gravar" (duas baixas simultâneas gastavam a mesma peça) e
-- a exclusão de OS fazia estorno, delete de itens, delete da OS e log em chamadas separadas.
-- Rollback no fim do arquivo.

CREATE OR REPLACE FUNCTION public.baixar_estoque(p_item uuid, p_empresa uuid, p_qtd integer)
RETURNS integer LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE saldo integer;
BEGIN
  IF p_qtd IS NULL OR p_qtd <= 0 THEN RAISE EXCEPTION 'QUANTIDADE_INVALIDA'; END IF;
  UPDATE estoque SET quantidade = quantidade - p_qtd
   WHERE id = p_item AND empresa_id = p_empresa AND quantidade >= p_qtd
  RETURNING quantidade INTO saldo;
  IF NOT FOUND THEN
    SELECT quantidade INTO saldo FROM estoque WHERE id = p_item AND empresa_id = p_empresa;
    IF NOT FOUND THEN RAISE EXCEPTION 'ESTOQUE_NAO_ENCONTRADO'; END IF;
    RAISE EXCEPTION 'ESTOQUE_INSUFICIENTE:%', saldo;
  END IF;
  RETURN saldo;
END $$;

CREATE OR REPLACE FUNCTION public.devolver_estoque(p_item uuid, p_empresa uuid, p_qtd integer)
RETURNS integer LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE saldo integer;
BEGIN
  IF p_qtd IS NULL OR p_qtd <= 0 THEN RAISE EXCEPTION 'QUANTIDADE_INVALIDA'; END IF;
  UPDATE estoque SET quantidade = quantidade + p_qtd
   WHERE id = p_item AND empresa_id = p_empresa
  RETURNING quantidade INTO saldo;
  IF NOT FOUND THEN RAISE EXCEPTION 'ESTOQUE_NAO_ENCONTRADO'; END IF;
  RETURN saldo;
END $$;

-- Estorno + delete dos itens + delete da OS + audit_logs numa única transação.
CREATE OR REPLACE FUNCTION public.deletar_os_com_estorno(p_os uuid, p_empresa uuid, p_motivo text)
RETURNS jsonb LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
DECLARE os_row ordens_servico%ROWTYPE;
BEGIN
  SELECT * INTO os_row FROM ordens_servico WHERE id = p_os AND empresa_id = p_empresa FOR UPDATE;
  IF NOT FOUND THEN RAISE EXCEPTION 'OS_NAO_ENCONTRADA'; END IF;

  UPDATE estoque e SET quantidade = e.quantidade + s.qtd
    FROM (SELECT estoque_id, sum(quantidade)::integer AS qtd FROM os_itens
           WHERE os_id = p_os AND estoque_id IS NOT NULL GROUP BY estoque_id) s
   WHERE e.id = s.estoque_id AND e.empresa_id = p_empresa;

  DELETE FROM os_itens WHERE os_id = p_os;
  DELETE FROM ordens_servico WHERE id = p_os AND empresa_id = p_empresa;
  INSERT INTO audit_logs (tabela, operacao, registro_id, empresa_id, dados_antes, dados_depois)
  VALUES ('ordens_servico', 'DELETE', p_os::text, p_empresa, to_jsonb(os_row) || jsonb_build_object('motivo_exclusao', p_motivo), NULL);
  RETURN jsonb_build_object('status', 'sucesso');
END $$;

REVOKE ALL ON FUNCTION public.baixar_estoque(uuid, uuid, integer), public.devolver_estoque(uuid, uuid, integer),
  public.deletar_os_com_estorno(uuid, uuid, text) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.baixar_estoque(uuid, uuid, integer), public.devolver_estoque(uuid, uuid, integer),
  public.deletar_os_com_estorno(uuid, uuid, text) TO service_role;

-- Rollback:
-- DROP FUNCTION public.baixar_estoque(uuid, uuid, integer), public.devolver_estoque(uuid, uuid, integer),
--   public.deletar_os_com_estorno(uuid, uuid, text);
