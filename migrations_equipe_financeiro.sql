-- ==============================================================================
-- AUTOTEC PRO — MIGRATION: EQUIPE, RH, FINANCEIRO, ESCALAS E PONTO ELETRÔNICO
-- Execute este script no SQL Editor do Supabase para atualizar sua infraestrutura.
-- ==============================================================================

-- 1. ADICIONAR CAMPOS DE RH E COMISSÕES NA TABELA DE USUÁRIOS
ALTER TABLE public.usuarios 
  ADD COLUMN IF NOT EXISTS salario_base NUMERIC(10,2) DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS comissao_servico_pct NUMERIC(5,2) DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS comissao_peca_pct NUMERIC(5,2) DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS vale_transporte NUMERIC(10,2) DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS vale_refeicao NUMERIC(10,2) DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS paga_hora_extra BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS valor_hora_extra NUMERIC(10,2) DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS estrelas_media NUMERIC(3,2) DEFAULT 5.0,
  ADD COLUMN IF NOT EXISTS total_avaliacoes INTEGER DEFAULT 0;

-- 2. ADICIONAR CAMPOS DE FISCAL, PIX, GPS E POLÍTICAS DE FOLHA EM CONFIGURAÇÕES DA EMPRESA
ALTER TABLE public.configuracoes_empresa
  ADD COLUMN IF NOT EXISTS inscricao_estadual VARCHAR(50),
  ADD COLUMN IF NOT EXISTS whatsapp VARCHAR(30),
  ADD COLUMN IF NOT EXISTS chave_pix VARCHAR(100),
  ADD COLUMN IF NOT EXISTS latitude_gps DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS longitude_gps DOUBLE PRECISION,
  ADD COLUMN IF NOT EXISTS raio_gps_metros INTEGER DEFAULT 100,
  ADD COLUMN IF NOT EXISTS dia_pagamento_folha INTEGER DEFAULT 5,
  ADD COLUMN IF NOT EXISTS dia_adiantamento_folha INTEGER DEFAULT 20,
  ADD COLUMN IF NOT EXISTS comissao_global_servico_pct NUMERIC(5,2) DEFAULT 15.0,
  ADD COLUMN IF NOT EXISTS comissao_global_peca_pct NUMERIC(5,2) DEFAULT 5.0,
  ADD COLUMN IF NOT EXISTS paga_hora_extra_padrao BOOLEAN DEFAULT TRUE,
  ADD COLUMN IF NOT EXISTS valor_hora_extra_padrao NUMERIC(10,2) DEFAULT 25.0;

-- 3. TABELA DE TRANSAÇÕES FINANCEIRAS (CONTAS A PAGAR & RECEITAS AVULSAS)
CREATE TABLE IF NOT EXISTS public.transacoes_financeiras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES public.empresas(id) ON DELETE CASCADE,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('DESPESA', 'RECEITA')),
    descricao TEXT NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    valor NUMERIC(12,2) NOT NULL CHECK (valor > 0),
    data_vencimento DATE NOT NULL,
    data_liquidacao DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDENTE' CHECK (status IN ('PENDENTE', 'LIQUIDADO', 'ATRASADO', 'CANCELADO')),
    forma_pagamento VARCHAR(50),
    observacoes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_transacoes_empresa_vencimento 
  ON public.transacoes_financeiras (empresa_id, data_vencimento);

CREATE INDEX IF NOT EXISTS idx_transacoes_empresa_status 
  ON public.transacoes_financeiras (empresa_id, status);

-- 4. TABELA DE ESCALAS DE FOLGA, FÉRIAS E PLANTÕES
CREATE TABLE IF NOT EXISTS public.escalas_folgas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES public.empresas(id) ON DELETE CASCADE,
    usuario_id UUID NOT NULL REFERENCES public.usuarios(id) ON DELETE CASCADE,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('FERIAS', 'FOLGA', 'ATESTADO', 'PLANTAO')),
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    observacoes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_escalas_empresa_periodo 
  ON public.escalas_folgas (empresa_id, data_inicio, data_fim);

CREATE INDEX IF NOT EXISTS idx_escalas_usuario 
  ON public.escalas_folgas (usuario_id);

-- 5. TABELA DE REGISTRO DE PONTO ELETRÔNICO MOBILE COM GEOFENCING
CREATE TABLE IF NOT EXISTS public.pontos_eletronicos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES public.empresas(id) ON DELETE CASCADE,
    usuario_id UUID NOT NULL REFERENCES public.usuarios(id) ON DELETE CASCADE,
    data DATE NOT NULL DEFAULT CURRENT_DATE,
    hora TIME NOT NULL DEFAULT CURRENT_TIME,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('ENTRADA', 'ALMOCO_SAIDA', 'ALMOCO_RETORNO', 'SAIDA')),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    dentro_raio BOOLEAN NOT NULL DEFAULT TRUE,
    distancia_metros NUMERIC(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_pontos_empresa_data 
  ON public.pontos_eletronicos (empresa_id, data);

CREATE INDEX IF NOT EXISTS idx_pontos_usuario_data 
  ON public.pontos_eletronicos (usuario_id, data);

-- 6. TABELA DE AVALIAÇÕES DE OS PELOS CLIENTES (NPS & 5 ESTRELAS)
CREATE TABLE IF NOT EXISTS public.avaliacoes_os (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    empresa_id UUID NOT NULL REFERENCES public.empresas(id) ON DELETE CASCADE,
    os_id UUID NOT NULL REFERENCES public.ordens_servico(id) ON DELETE CASCADE,
    mecanico_id UUID REFERENCES public.usuarios(id) ON DELETE SET NULL,
    cliente_nome VARCHAR(255) NOT NULL,
    veiculo_modelo VARCHAR(255) NOT NULL,
    veiculo_placa VARCHAR(20) NOT NULL,
    nota INTEGER NOT NULL CHECK (nota >= 1 AND nota <= 5),
    comentario TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_avaliacoes_empresa 
  ON public.avaliacoes_os (empresa_id);

CREATE INDEX IF NOT EXISTS idx_avaliacoes_mecanico 
  ON public.avaliacoes_os (mecanico_id);

CREATE INDEX IF NOT EXISTS idx_avaliacoes_os 
  ON public.avaliacoes_os (os_id);

-- 7. TRIGGER AUTOMÁTICO: ATUALIZA NOTA MÉDIA E TOTAL DE AVALIAÇÕES DO MECÂNICO
CREATE OR REPLACE FUNCTION public.fn_atualizar_media_avaliacoes_mecanico()
RETURNS TRIGGER AS $$
DECLARE
    target_mecanico UUID;
BEGIN
    target_mecanico := COALESCE(NEW.mecanico_id, OLD.mecanico_id);
    IF target_mecanico IS NOT NULL THEN
        UPDATE public.usuarios
        SET 
            estrelas_media = ROUND(COALESCE((SELECT AVG(nota)::numeric FROM public.avaliacoes_os WHERE mecanico_id = target_mecanico), 5.0), 1),
            total_avaliacoes = COALESCE((SELECT COUNT(*)::integer FROM public.avaliacoes_os WHERE mecanico_id = target_mecanico), 0)
        WHERE id = target_mecanico;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_atualizar_media_avaliacoes ON public.avaliacoes_os;
CREATE TRIGGER trg_atualizar_media_avaliacoes
AFTER INSERT OR UPDATE OR DELETE ON public.avaliacoes_os
FOR EACH ROW
EXECUTE FUNCTION public.fn_atualizar_media_avaliacoes_mecanico();

-- 8. POLÍTICAS DE ROW LEVEL SECURITY (RLS) PARA AS NOVAS TABELAS
ALTER TABLE public.transacoes_financeiras ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.escalas_folgas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pontos_eletronicos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.avaliacoes_os ENABLE ROW LEVEL SECURITY;

-- Transações Financeiras: leitura e escrita para usuários autenticados da mesma empresa
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'transacoes_financeiras' AND policyname = 'transacoes_tenant_isolation'
    ) THEN
        CREATE POLICY transacoes_tenant_isolation ON public.transacoes_financeiras
            FOR ALL
            TO authenticated
            USING (
                empresa_id IN (
                    SELECT empresa_id FROM public.usuarios WHERE id = auth.uid()
                )
            );
    END IF;
END $$;

-- Escalas e Folgas: leitura e escrita por empresa
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'escalas_folgas' AND policyname = 'escalas_tenant_isolation'
    ) THEN
        CREATE POLICY escalas_tenant_isolation ON public.escalas_folgas
            FOR ALL
            TO authenticated
            USING (
                empresa_id IN (
                    SELECT empresa_id FROM public.usuarios WHERE id = auth.uid()
                )
            );
    END IF;
END $$;

-- Ponto Eletrônico: leitura e escrita por empresa
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'pontos_eletronicos' AND policyname = 'pontos_tenant_isolation'
    ) THEN
        CREATE POLICY pontos_tenant_isolation ON public.pontos_eletronicos
            FOR ALL
            TO authenticated
            USING (
                empresa_id IN (
                    SELECT empresa_id FROM public.usuarios WHERE id = auth.uid()
                )
            );
    END IF;
END $$;

-- Avaliações de OS: Leitura para authenticated da empresa e INSERT aberto (público do WhatsApp)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'avaliacoes_os' AND policyname = 'avaliacoes_tenant_select'
    ) THEN
        CREATE POLICY avaliacoes_tenant_select ON public.avaliacoes_os
            FOR SELECT
            TO authenticated
            USING (
                empresa_id IN (
                    SELECT empresa_id FROM public.usuarios WHERE id = auth.uid()
                )
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'avaliacoes_os' AND policyname = 'avaliacoes_public_insert'
    ) THEN
        CREATE POLICY avaliacoes_public_insert ON public.avaliacoes_os
            FOR INSERT
            TO anon, authenticated
            WITH CHECK (true);
    END IF;
END $$;

