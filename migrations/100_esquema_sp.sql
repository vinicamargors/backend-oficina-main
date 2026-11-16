-- Fase 4.2: esquema revisado completo. Uma base NOVA (Supabase São Paulo) nasce deste arquivo, sozinho.
-- Não rodar na AutotecDB (lá valem 001–005). Os dados vêm depois, por scripts/migrar_base.py.
--
-- Diferenças para a base antiga:
--   * só o backend (service_role) acessa: anon/authenticated sem nenhum privilégio e nenhuma policy
--     (o front só usa o Supabase para login); somem minha_empresa(), meu_cargo(), fn_audit_log(), get_db_io_metrics()
--   * empresa_id NOT NULL + índice nas tabelas de negócio; os_itens.os_id NOT NULL
--   * varchar(n) → text (limite validado no backend)
--   * CHECKs novos: estoque.quantidade >= 0, transação tipo/status, escala data_fim >= data_inicio
--   * 1 configuração por empresa (unique); placa única por empresa (já existia)
--   * auditoria: um trigger por tabela (antes OS gravava 2 linhas e os_itens gravava sem empresa)
--   * updated_at com trigger nas tabelas principais
--   * sai usuarios.senha_hash (legado Flask) e empresas.plano (vai para assinaturas)
--   * novas: assinaturas, assinatura_pagamentos

-- ------------------------------------------------------------------ funções de trigger
CREATE FUNCTION public.set_updated_at() RETURNS trigger
  LANGUAGE plpgsql SET search_path = public
  AS $$ BEGIN NEW.updated_at = now(); RETURN NEW; END $$;

-- ------------------------------------------------------------------ plataforma
CREATE TABLE public.empresas (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  nome_fantasia text NOT NULL,
  razao_social  text,
  cnpj          text,
  email         text,
  telefone      text,
  endereco      text,
  ativo         boolean NOT NULL DEFAULT true,
  empresa_teste boolean NOT NULL DEFAULT false,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE public.configuracoes_empresa (
  id                          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id                  uuid NOT NULL UNIQUE REFERENCES public.empresas(id),
  logo_b64                    text,
  cor_primaria                text DEFAULT '#1e3a8a',
  cor_secundaria              text DEFAULT '#f97316',
  nome_exibicao               text,
  inscricao_estadual          text,
  whatsapp                    text,
  chave_pix                   text,
  latitude_gps                double precision,
  longitude_gps               double precision,
  raio_gps_metros             integer DEFAULT 100,
  dia_pagamento_folha         integer DEFAULT 5,
  dia_adiantamento_folha      integer DEFAULT 20,
  comissao_global_servico_pct numeric DEFAULT 15.0,
  comissao_global_peca_pct    numeric DEFAULT 5.0,
  paga_hora_extra_padrao      boolean DEFAULT true,
  valor_hora_extra_padrao     numeric DEFAULT 25.0,
  updated_at                  timestamptz NOT NULL DEFAULT now()
);

-- id = auth.users.id. Só os usuários da plataforma (master) ficam sem empresa.
CREATE TABLE public.usuarios (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email                text NOT NULL UNIQUE,
  nome                 text NOT NULL,
  cargo                text NOT NULL CHECK (cargo IN ('master','DONO','MECANICO','ATENDENTE','FINANCEIRO')),
  ativo                boolean DEFAULT true,
  empresa_id           uuid REFERENCES public.empresas(id),
  telefone             text,
  salario_base         numeric DEFAULT 0.0,
  comissao_servico_pct numeric DEFAULT 0.0,
  comissao_peca_pct    numeric DEFAULT 0.0,
  vale_transporte      numeric DEFAULT 0.0,
  vale_refeicao        numeric DEFAULT 0.0,
  paga_hora_extra      boolean DEFAULT false,
  valor_hora_extra     numeric DEFAULT 0.0,
  estrelas_media       numeric DEFAULT 5.0,
  total_avaliacoes     integer DEFAULT 0,
  criado_em            timestamptz DEFAULT now(),
  updated_at           timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT usuarios_empresa_ou_master CHECK (empresa_id IS NOT NULL OR cargo = 'master')
);
CREATE INDEX idx_usuarios_empresa ON public.usuarios (empresa_id);

-- ------------------------------------------------------------------ assinaturas do SaaS (sem meio de pagamento por enquanto)
CREATE TABLE public.assinaturas (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id     uuid NOT NULL UNIQUE REFERENCES public.empresas(id) ON DELETE CASCADE,
  plano          text NOT NULL DEFAULT 'basico' CHECK (plano IN ('basico','profissional')),
  status         text NOT NULL DEFAULT 'TESTE' CHECK (status IN ('TESTE','ATIVA','ATRASADA','CANCELADA')),
  valor_mensal   numeric NOT NULL DEFAULT 0 CHECK (valor_mensal >= 0),
  dia_vencimento integer CHECK (dia_vencimento BETWEEN 1 AND 31),
  inicio         date NOT NULL DEFAULT CURRENT_DATE,
  fim            date CHECK (fim >= inicio),
  gateway        text,
  gateway_id     text,
  created_at     timestamptz NOT NULL DEFAULT now(),
  updated_at     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE public.assinatura_pagamentos (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  assinatura_id uuid NOT NULL REFERENCES public.assinaturas(id) ON DELETE CASCADE,
  competencia   date NOT NULL CHECK (EXTRACT(day FROM competencia) = 1),  -- o mês, sempre no dia 1
  valor         numeric NOT NULL CHECK (valor >= 0),
  status        text NOT NULL DEFAULT 'PENDENTE' CHECK (status IN ('PENDENTE','PAGO','FALHOU','ESTORNADO')),
  pago_em       timestamptz,
  gateway_id    text,
  created_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (assinatura_id, competencia)
);

-- Toda empresa nasce com uma assinatura (básico, em teste): o backend não precisa lembrar de criar.
CREATE FUNCTION public.fn_assinatura_padrao() RETURNS trigger
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = public
  AS $$ BEGIN INSERT INTO assinaturas (empresa_id) VALUES (NEW.id) ON CONFLICT DO NOTHING; RETURN NEW; END $$;
CREATE TRIGGER trg_assinatura_padrao AFTER INSERT ON public.empresas
  FOR EACH ROW EXECUTE FUNCTION public.fn_assinatura_padrao();

-- ------------------------------------------------------------------ negócio
CREATE TABLE public.clientes (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id uuid NOT NULL REFERENCES public.empresas(id),
  nome       text NOT NULL,
  telefone   text NOT NULL,
  cpf_cnpj   text,
  endereco   text,
  criado_em  timestamptz DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_clientes_empresa ON public.clientes (empresa_id);

CREATE TABLE public.veiculos (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id uuid NOT NULL REFERENCES public.empresas(id),
  cliente_id uuid REFERENCES public.clientes(id) ON DELETE CASCADE,
  placa      text NOT NULL,
  modelo     text NOT NULL,
  marca      text,
  cor        text,
  ano        integer,
  chassi     text,
  km_atual   integer,
  criado_em  timestamptz DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT veiculos_placa_empresa_unique UNIQUE (empresa_id, placa)
);
CREATE INDEX idx_veiculos_cliente ON public.veiculos (cliente_id);

CREATE TABLE public.estoque (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id    uuid NOT NULL REFERENCES public.empresas(id),
  nome          text NOT NULL,
  codigo        text,
  categoria     text DEFAULT 'PECAS',
  custo         numeric NOT NULL DEFAULT 0.00,
  venda         numeric NOT NULL DEFAULT 0.00,
  quantidade    integer NOT NULL DEFAULT 0 CHECK (quantidade >= 0),
  minimo_alerta integer DEFAULT 5,
  updated_at    timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_estoque_empresa ON public.estoque (empresa_id);

CREATE TABLE public.categorias_estoque (
  empresa_id uuid NOT NULL REFERENCES public.empresas(id) ON DELETE CASCADE,
  nome       text NOT NULL CHECK (nome = upper(btrim(nome)) AND length(nome) >= 1),
  PRIMARY KEY (empresa_id, nome)
);

CREATE TABLE public.ordens_servico (
  id                      uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id              uuid NOT NULL REFERENCES public.empresas(id),
  cliente_id              uuid REFERENCES public.clientes(id),
  veiculo_id              uuid REFERENCES public.veiculos(id),
  mecanico_responsavel_id uuid REFERENCES public.usuarios(id),
  status                  text NOT NULL DEFAULT 'ORCAMENTO'
                          CHECK (status IN ('ORCAMENTO','AGUARDANDO_PECA','EXECUCAO','FINALIZADO','PAGO')),
  total_pecas             numeric DEFAULT 0.00,
  total_mao_obra          numeric DEFAULT 0.00,
  total_terceirizados     numeric,
  total_geral             numeric DEFAULT 0.00,
  lucro_estimado          numeric DEFAULT 0.00,
  forma_pagamento         text,
  data_abertura           timestamptz DEFAULT now(),
  data_fechamento         timestamptz,
  descricao_problema      text,
  km_atual                integer,
  motivo_exclusao         text,
  updated_at              timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_os_empresa_status_data ON public.ordens_servico (empresa_id, status, data_abertura);
CREATE INDEX idx_os_cliente ON public.ordens_servico (cliente_id);
CREATE INDEX idx_os_veiculo ON public.ordens_servico (veiculo_id);

CREATE TABLE public.os_itens (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id     uuid NOT NULL REFERENCES public.empresas(id),
  os_id          uuid NOT NULL REFERENCES public.ordens_servico(id) ON DELETE CASCADE,
  estoque_id     uuid REFERENCES public.estoque(id),
  tipo           text NOT NULL CHECK (tipo IN ('PECA','MAO_OBRA','TERCEIRIZADO')),
  nome_item      text NOT NULL,
  quantidade     integer NOT NULL DEFAULT 1,
  custo_unitario numeric NOT NULL DEFAULT 0.00,
  venda_unitario numeric NOT NULL DEFAULT 0.00,
  criado_em      timestamptz DEFAULT now()
);
CREATE INDEX idx_os_itens_os ON public.os_itens (os_id);
CREATE INDEX idx_os_itens_empresa ON public.os_itens (empresa_id);
CREATE INDEX idx_os_itens_estoque ON public.os_itens (estoque_id);

CREATE TABLE public.avaliacoes_os (
  id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id     uuid NOT NULL REFERENCES public.empresas(id) ON DELETE CASCADE,
  os_id          uuid NOT NULL UNIQUE REFERENCES public.ordens_servico(id) ON DELETE CASCADE,  -- 1 avaliação por OS
  mecanico_id    uuid REFERENCES public.usuarios(id) ON DELETE SET NULL,
  cliente_nome   text NOT NULL,
  veiculo_modelo text NOT NULL,
  veiculo_placa  text NOT NULL,
  nota           integer NOT NULL CHECK (nota BETWEEN 1 AND 5),
  comentario     text,
  created_at     timestamptz DEFAULT now()
);
CREATE INDEX idx_avaliacoes_empresa ON public.avaliacoes_os (empresa_id);
CREATE INDEX idx_avaliacoes_mecanico ON public.avaliacoes_os (mecanico_id);

CREATE TABLE public.escalas_folgas (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id  uuid NOT NULL REFERENCES public.empresas(id) ON DELETE CASCADE,
  usuario_id  uuid NOT NULL REFERENCES public.usuarios(id) ON DELETE CASCADE,
  tipo        text NOT NULL CHECK (tipo IN ('FERIAS','FOLGA','ATESTADO','PLANTAO')),
  data_inicio date NOT NULL,
  data_fim    date NOT NULL,
  observacoes text,
  created_at  timestamptz DEFAULT now(),
  CONSTRAINT escalas_periodo_valido CHECK (data_fim >= data_inicio)
);
CREATE INDEX idx_escalas_empresa_periodo ON public.escalas_folgas (empresa_id, data_inicio, data_fim);
CREATE INDEX idx_escalas_usuario ON public.escalas_folgas (usuario_id);

CREATE TABLE public.pontos_eletronicos (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id       uuid NOT NULL REFERENCES public.empresas(id) ON DELETE CASCADE,
  usuario_id       uuid NOT NULL REFERENCES public.usuarios(id) ON DELETE CASCADE,
  data             date NOT NULL DEFAULT CURRENT_DATE,
  hora             time NOT NULL DEFAULT CURRENT_TIME,
  tipo             text NOT NULL CHECK (tipo IN ('ENTRADA','ALMOCO_SAIDA','ALMOCO_RETORNO','SAIDA')),
  latitude         double precision,
  longitude        double precision,
  dentro_raio      boolean NOT NULL DEFAULT true,
  distancia_metros numeric,
  created_at       timestamptz DEFAULT now()
);
CREATE INDEX idx_pontos_empresa_data ON public.pontos_eletronicos (empresa_id, data);
CREATE INDEX idx_pontos_usuario ON public.pontos_eletronicos (usuario_id);

CREATE TABLE public.transacoes_financeiras (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  empresa_id      uuid NOT NULL REFERENCES public.empresas(id) ON DELETE CASCADE,
  tipo            text NOT NULL CHECK (tipo IN ('DESPESA','RECEITA')),
  descricao       text NOT NULL,
  categoria       text NOT NULL,
  valor           numeric NOT NULL DEFAULT 0.00,
  data_vencimento date NOT NULL,
  data_liquidacao date,
  status          text NOT NULL DEFAULT 'PENDENTE' CHECK (status IN ('PENDENTE','LIQUIDADO','ATRASADO','CANCELADO')),
  forma_pagamento text,
  observacoes     text,
  created_at      timestamptz DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_transacoes_empresa_vencimento ON public.transacoes_financeiras (empresa_id, data_vencimento);
CREATE INDEX idx_transacoes_empresa_status ON public.transacoes_financeiras (empresa_id, status);

CREATE TABLE public.audit_logs (
  id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  empresa_id   uuid REFERENCES public.empresas(id),  -- vazio só para ações em usuários da plataforma (master)
  tabela       text NOT NULL,
  operacao     text NOT NULL,
  registro_id  text,
  dados_antes  jsonb,
  dados_depois jsonb,
  criado_em    timestamptz DEFAULT now()
);
CREATE INDEX idx_audit_empresa_data ON public.audit_logs (empresa_id, criado_em DESC);

-- ------------------------------------------------------------------ triggers
DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY['empresas','configuracoes_empresa','usuarios','assinaturas','clientes','veiculos',
                           'estoque','ordens_servico','transacoes_financeiras'] LOOP
    EXECUTE format('CREATE TRIGGER trg_updated_at BEFORE UPDATE ON public.%I FOR EACH ROW EXECUTE FUNCTION public.set_updated_at()', t);
  END LOOP;
END $$;

CREATE FUNCTION public.process_audit_log() RETURNS trigger
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = public
AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    INSERT INTO audit_logs (tabela, operacao, registro_id, empresa_id, dados_antes)
    VALUES (TG_TABLE_NAME, TG_OP, OLD.id::text, OLD.empresa_id, to_jsonb(OLD));
    RETURN OLD;
  END IF;
  INSERT INTO audit_logs (tabela, operacao, registro_id, empresa_id, dados_antes, dados_depois)
  VALUES (TG_TABLE_NAME, TG_OP, NEW.id::text, NEW.empresa_id, CASE WHEN TG_OP = 'UPDATE' THEN to_jsonb(OLD) END, to_jsonb(NEW));
  RETURN NEW;
END $$;

DO $$
DECLARE t text;
BEGIN
  FOREACH t IN ARRAY ARRAY['clientes','veiculos','estoque','usuarios','os_itens'] LOOP
    EXECUTE format('CREATE TRIGGER trg_audit AFTER INSERT OR UPDATE OR DELETE ON public.%I FOR EACH ROW EXECUTE FUNCTION public.process_audit_log()', t);
  END LOOP;
END $$;
-- O DELETE da OS é registrado por deletar_os_com_estorno (com o motivo); um trigger aqui duplicaria a linha.
CREATE TRIGGER trg_audit AFTER INSERT OR UPDATE ON public.ordens_servico
  FOR EACH ROW EXECUTE FUNCTION public.process_audit_log();

CREATE FUNCTION public.fn_atualizar_media_avaliacoes_mecanico() RETURNS trigger
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = public
AS $$
DECLARE alvo uuid;
BEGIN
  FOREACH alvo IN ARRAY ARRAY[CASE WHEN TG_OP <> 'INSERT' THEN OLD.mecanico_id END, CASE WHEN TG_OP <> 'DELETE' THEN NEW.mecanico_id END] LOOP
    IF alvo IS NOT NULL THEN
      UPDATE usuarios SET
        estrelas_media   = round(coalesce((SELECT avg(nota)::numeric FROM avaliacoes_os WHERE mecanico_id = alvo), 5.0), 1),
        total_avaliacoes = (SELECT count(*)::integer FROM avaliacoes_os WHERE mecanico_id = alvo)
      WHERE id = alvo;
    END IF;
  END LOOP;
  RETURN NULL;
END $$;
CREATE TRIGGER trg_atualizar_media_avaliacoes AFTER INSERT OR UPDATE OR DELETE ON public.avaliacoes_os
  FOR EACH ROW EXECUTE FUNCTION public.fn_atualizar_media_avaliacoes_mecanico();

-- ------------------------------------------------------------------ RPCs de estoque (iguais às de 003)
CREATE FUNCTION public.baixar_estoque(p_item uuid, p_empresa uuid, p_qtd integer) RETURNS integer
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = public
AS $$
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

CREATE FUNCTION public.devolver_estoque(p_item uuid, p_empresa uuid, p_qtd integer) RETURNS integer
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = public
AS $$
DECLARE saldo integer;
BEGIN
  IF p_qtd IS NULL OR p_qtd <= 0 THEN RAISE EXCEPTION 'QUANTIDADE_INVALIDA'; END IF;
  UPDATE estoque SET quantidade = quantidade + p_qtd
   WHERE id = p_item AND empresa_id = p_empresa
  RETURNING quantidade INTO saldo;
  IF NOT FOUND THEN RAISE EXCEPTION 'ESTOQUE_NAO_ENCONTRADO'; END IF;
  RETURN saldo;
END $$;

CREATE FUNCTION public.deletar_os_com_estorno(p_os uuid, p_empresa uuid, p_motivo text) RETURNS jsonb
  LANGUAGE plpgsql SECURITY DEFINER SET search_path = public
AS $$
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
  INSERT INTO audit_logs (tabela, operacao, registro_id, empresa_id, dados_antes)
  VALUES ('ordens_servico', 'DELETE', p_os::text, p_empresa, to_jsonb(os_row) || jsonb_build_object('motivo_exclusao', p_motivo));
  RETURN jsonb_build_object('status', 'sucesso');
END $$;

-- ------------------------------------------------------------------ acesso: só o backend
-- RLS ligado sem policy + nenhum privilégio: a chave anon e o JWT do usuário não leem nem gravam nada.
DO $$
DECLARE t text;
BEGIN
  FOR t IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' LOOP
    EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', t);
  END LOOP;
END $$;

REVOKE ALL ON ALL TABLES    IN SCHEMA public FROM anon, authenticated;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM PUBLIC, anon, authenticated;
GRANT ALL ON ALL TABLES    IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO service_role;
-- tabelas e funções criadas depois (migrations futuras) também nascem fechadas
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES    FROM anon, authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon, authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON FUNCTIONS FROM PUBLIC, anon, authenticated;
