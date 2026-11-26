# Fase 4.2 — suíte inteira contra o projeto novo (mecanify, sa-east-1) — 2026-11-25

Comando: `TESTES_BASE=mecanify pytest` (URL/chaves MECANIFY_* do .env.test; nenhuma chave neste arquivo).
Resultado: **245 passed, 1 skipped, 0 failed** (4 min). O skip é o F3-W1b: item de OS sem empresa não existe mais na base nova (empresa_id NOT NULL).
Os logins dos usuários de teste usam os hashes copiados da AutotecDB pelo migrar_base.py: passaram no GoTrue do projeto novo.

---

# Execução dos testes do backend — 25/11/2026 21:57:13 (BRT)

Banco: AutotecDB, só empresas `empresa_teste = true`. Tokens e chaves mascarados.

**Resumo:** 245 passaram · 0 falharam · 1 pulados

| # | Teste | Cenário do plano | Resultado |
|---|---|---|---|
| 1 | `test_health` | F41-H — GET /api/v1/health responde 200 sem token e sem tocar o banco | PASSOU |
| 2 | `test_cors_por_variavel` | F41-C — Com ALLOWED_ORIGINS só o domínio do app passa no CORS; sem a variável tudo passa (compatível com o Render) | PASSOU |
| 3 | `test_chave_do_servidor_invalida_nao_vira_token_invalido` | F41-K — Chave do Supabase do SERVIDOR inválida (config errada) → 503 e log claro, não 401 'token inválido' que desloga todo mundo | PASSOU |
| 4 | `test_cloud_init_so_ascii` | F41-A — deploy/cloud-init.yaml é ASCII puro: acento colado no console da Oracle vira byte Latin-1 e o cloud-init descarta o arquivo inteiro | PASSOU |
| 5 | `test_api_sobe_sem_chave_do_gemini` | F41-G — Sem GEMINI_API_KEY a API sobe (só a rota de áudio do bot fica 503); antes o processo inteiro morria no import | PASSOU |
| 6 | `test_escala_usuario_de_outra_empresa` | T10-1 — Escala: usuario_id da Oficina B → 404, nada gravado, nome do colaborador de B não vaza | PASSOU |
| 7 | `test_escala_usuario_da_propria_empresa` | T10-2 — Escala: colaborador da própria empresa continua funcionando | PASSOU |
| 8 | `test_os_ids_de_outra_empresa` | T10-3 — OS: cliente, veículo ou mecânico de B na criação → 404 e nenhuma OS criada; mecânico de B na edição → 404 e OS intacta | PASSOU |
| 9 | `test_item_os_estoque_de_outra_empresa` | T10-4 — Item da OS com estoque_id de B → recusado, estoque de B intacto, nenhum item criado | PASSOU |
| 10 | `test_veiculo_cliente_de_outra_empresa` | T10-5 — Veículo: cliente_id de B na criação e na edição → 404, nada gravado | PASSOU |
| 11 | `test_bot_ids_de_outra_empresa` | T10-6 — Bot: abrir-os com cliente/veículo/mecânico de B e cadastro-rápido com mecânico de B → 404, nada criado | PASSOU |
| 12 | `test_bot_audio_os_de_outra_empresa` | T10-7 — Bot: processar-audio com os_id de B e empresa_id de A → 404 antes de baixar o áudio; OS de B sem itens novos | PASSOU |
| 13 | `test_recurso_de_outra_empresa_pela_rota_propria` | T1-R — DONO A pede, pela rota da própria empresa, um cliente que é da Oficina B → 404 | PASSOU |
| 14 | `test_post_cliente_grava_na_empresa_do_token` | F1.2 — POST de cliente com empresa_id da Oficina B no body grava na Oficina A (empresa do token) | PASSOU |
| 15 | `test_item_em_os_de_outra_empresa` | F1.3 — DONO A adiciona item numa OS da Oficina B → 404 (pela rota de A) e 403 (pela rota de B) | PASSOU |
| 16 | `test_alterar_item_de_outra_empresa` | F1.3b — DONO A tenta alterar/remover item de OS da Oficina B → 404; item e estoque de B intactos | PASSOU |
| 17 | `test_criar_os_com_vinculo_de_outra_empresa[veiculo]` | F1.5 — DONO A abre OS com veículo/cliente/mecânico da Oficina B → 404 | PASSOU |
| 18 | `test_criar_os_com_vinculo_de_outra_empresa[cliente]` | F1.5 — DONO A abre OS com veículo/cliente/mecânico da Oficina B → 404 | PASSOU |
| 19 | `test_criar_os_com_vinculo_de_outra_empresa[mecanico]` | F1.5 — DONO A abre OS com veículo/cliente/mecânico da Oficina B → 404 | PASSOU |
| 20 | `test_veiculo_com_cliente_de_outra_empresa` | F1.5b — DONO A cadastra veículo apontando para cliente da Oficina B → 404 | PASSOU |
| 21 | `test_dono_nao_promove_master` | F1.4 — DONO A promove o mecânico a master → 403; cargo continua MECANICO | PASSOU |
| 22 | `test_dono_nao_cria_master` | F1.4b — DONO A cria usuário já como master → 403; nenhum usuário criado | PASSOU |
| 23 | `test_rh_nao_sai_pela_api_rest[salario_base-MECANICO]` | F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado | PASSOU |
| 24 | `test_rh_nao_sai_pela_api_rest[salario_base-DONO]` | F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado | PASSOU |
| 25 | `test_rh_nao_sai_pela_api_rest[comissao_servico_pct-MECANICO]` | F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado | PASSOU |
| 26 | `test_rh_nao_sai_pela_api_rest[comissao_servico_pct-DONO]` | F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado | PASSOU |
| 27 | `test_rh_nao_sai_pela_api_rest[vale_transporte-MECANICO]` | F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado | PASSOU |
| 28 | `test_rh_nao_sai_pela_api_rest[vale_transporte-DONO]` | F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado | PASSOU |
| 29 | `test_rh_nao_sai_pela_api_rest[senha_hash-MECANICO]` | F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado | PASSOU |
| 30 | `test_rh_nao_sai_pela_api_rest[senha_hash-DONO]` | F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado | PASSOU |
| 31 | `test_mecanico_le_nomes_da_equipe` | F2.2 — MECÂNICO continua lendo nome/cargo da equipe da própria oficina (e não da outra) | PASSOU |
| 32 | `test_dono_nao_grava_rh_direto` | F2.3 — DONO tenta gravar salário direto no Supabase → negado; valor no banco inalterado | PASSOU |
| 33 | `test_rh_pelo_backend_so_para_dono` | F2.4 — Backend: DONO lista equipe com RH (200); MECÂNICO e FINANCEIRO → 403 | PASSOU |
| 34 | `test_dono_altera_rh_pelo_backend` | F2.5 — Backend: DONO altera salário do mecânico (200) e o valor é gravado no banco | PASSOU |
| 35 | `test_leituras_pelo_backend[/dashboards/{emp}]` | F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado | PASSOU |
| 36 | `test_leituras_pelo_backend[/clientes/{emp}]` | F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado | PASSOU |
| 37 | `test_leituras_pelo_backend[/veiculos/{emp}]` | F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado | PASSOU |
| 38 | `test_leituras_pelo_backend[/estoque/{emp}]` | F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado | PASSOU |
| 39 | `test_leituras_pelo_backend[/os/?empresa_id={emp}]` | F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado | PASSOU |
| 40 | `test_leituras_pelo_backend[/os/{emp}/{os}/imprimir]` | F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado | PASSOU |
| 41 | `test_leituras_pelo_backend[/usuarios/{emp}]` | F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado | PASSOU |
| 42 | `test_leituras_pelo_backend[/empresas/?empresa_id={emp}]` | F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado | PASSOU |
| 43 | `test_leituras_pelo_backend[/empresas/{emp}/configuracoes]` | F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado | PASSOU |
| 44 | `test_leituras_pelo_backend[/equipe/escalas/{emp}]` | F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado | PASSOU |
| 45 | `test_leituras_pelo_backend[/equipe/pontos/{emp}]` | F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado | PASSOU |
| 46 | `test_leituras_pelo_backend[/equipe/avaliacoes/{emp}]` | F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado | PASSOU |
| 47 | `test_leituras_pelo_backend[/transacoes-financeiras/{emp}]` | F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado | PASSOU |
| 48 | `test_leituras_pelo_backend[/financeiro/{emp}]` | F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado | PASSOU |
| 49 | `test_leituras_pelo_backend[/financeiro/inteligencia/{emp}]` | F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado | PASSOU |
| 50 | `test_listagem_de_os_filtros_e_busca` | F3-C2 — Histórico de OS por veículo/cliente e busca por modelo e por placa sem hífen | PASSOU |
| 51 | `test_itens_da_os_e_estoque` | F3-W1 — Itens da OS: adicionar em lote baixa o estoque, alterar ajusta, remover estorna; totais da OS recalculados | PASSOU |
| 52 | `test_item_legado_sem_empresa_id` | F3-W1b — Item antigo do legado (sem empresa_id) pode ser alterado/removido pela própria empresa; a outra recebe 403/404 | PULADO |
| 53 | `test_abrir_e_atualizar_os` | F3-W2 — Abrir OS: reaproveita orçamento aberto do veículo; veículo novo cria OS; status e fechamento atualizam | PASSOU |
| 54 | `test_crud_cliente_veiculo_estoque` | F3-W3 — Cliente, veículo e item de estoque: criar, alterar, ajustar saldo e apagar (corpos iguais aos das telas) | PASSOU |
| 55 | `test_crud_transacoes` | F3-W4 — Contas a pagar/receber: criar, alterar, liquidar e apagar; erro do banco aparece como erro (nada é engolido) | PASSOU |
| 56 | `test_escalas_e_ponto` | F3-W5 — Escalas e ponto com os corpos das telas: gravados no banco e listados pelo backend | PASSOU |
| 57 | `test_configuracoes_da_oficina` | F3-W6 — Configurações da oficina e parâmetros da folha (antes só no localStorage) gravam e voltam do servidor | PASSOU |
| 58 | `test_clientes_ordenados_por_nome` | F3-C3 — Lista de clientes vem ordenada por nome (a tela dependia disso) | PASSOU |
| 59 | `test_onboarding_de_conta_nova` | F3-F4 — Cadastro novo (sem perfil): /me nega, onboarding cria 1 oficina DONO só uma vez e isolada das demais | PASSOU |
| 60 | `test_equipe_sem_rh_para_todos[MECANICO]` | F3-E1 — Equipe (nomes/cargos) para qualquer perfil, sem RH; RH continua só para o DONO; outra empresa → 403 | PASSOU |
| 61 | `test_equipe_sem_rh_para_todos[ATENDENTE]` | F3-E1 — Equipe (nomes/cargos) para qualquer perfil, sem RH; RH continua só para o DONO; outra empresa → 403 | PASSOU |
| 62 | `test_equipe_sem_rh_para_todos[FINANCEIRO]` | F3-E1 — Equipe (nomes/cargos) para qualquer perfil, sem RH; RH continua só para o DONO; outra empresa → 403 | PASSOU |
| 63 | `test_equipe_sem_rh_para_todos[DONO]` | F3-E1 — Equipe (nomes/cargos) para qualquer perfil, sem RH; RH continua só para o DONO; outra empresa → 403 | PASSOU |
| 64 | `test_colunas_em_comum` | F42-1 — Cópia usa só as colunas que existem dos dois lados: plano/senha_hash ficam para trás, updated_at novo usa o padrão | PASSOU |
| 65 | `test_valores_da_linha` | F42-2 — os_itens/auditoria herdam a empresa da oficina copiada; jsonb vai embrulhado; NULL continua NULL | PASSOU |
| 66 | `test_apagar_cobre_tudo` | F42-3 — Toda tabela copiada é apagada no --substituir (senão sobraria lixo da cópia anterior), e os pais só depois dos filhos | PASSOU |
| 67 | `test_com_plano` | F42-4 — Listagem de oficinas: plano vem da assinatura; oficina sem assinatura aparece como básico | PASSOU |
| 68 | `test_gravar_plano` | F42-5 — gravar_plano: cria a assinatura se não existe, troca só o plano se já existe | PASSOU |
| 69 | `test_baixas_concorrentes` | F4-E1 — 10 baixas simultâneas de 1 unidade num item com saldo 1: exatamente uma passa (200), as outras 400, saldo final 0 | PASSOU |
| 70 | `test_excluir_os_estorna_e_audita` | F4-E2 — Excluir OS com itens: estoque volta, itens e OS somem e o audit_logs guarda o motivo — tudo junto | PASSOU |
| 71 | `test_lote_tudo_ou_nada` | F4-E3 — Lote em que o 2º item não tem saldo: 400 e o 1º item NÃO fica baixado nem gravado (tudo ou nada) | PASSOU |
| 72 | `test_saldo_insuficiente_e_ajuste_de_item` | F4-E4 — Saída manual e aumento de item acima do saldo → 400 com saldo intacto; reduzir item devolve a diferença | PASSOU |
| 73 | `test_rpc_fechada_para_logado` | F4-E5 — Usuário logado não consegue chamar as funções de estoque direto no Supabase (só o backend) | PASSOU |
| 74 | `test_token_assinado` | F5-T — Token de avaliação: assinatura válida volta o os_id; adulterado, de outra OS, truncado ou lixo → None | PASSOU |
| 75 | `test_avaliar_uma_vez` | F7 — Link com token válido: avalia (empresa, mecânico, cliente e placa vêm da OS); segunda avaliação da mesma OS → 409; média do mecânico atualizada | PASSOU |
| 76 | `test_token_invalido_nao_grava` | F8 — Token adulterado, sem token ou de OS inexistente: erro e nada gravado | PASSOU |
| 77 | `test_gerar_link_regras` | F5-L — Gerar link: só OS finalizada/paga e só da própria empresa; mecânico não gera | PASSOU |
| 78 | `test_anon_nao_insere_avaliacao` | F5-R — Chave anon não insere em avaliacoes_os direto pelo Supabase (policy pública removida) | PASSOU |
| 79 | `test_ponto_so_do_servidor` | F5-P — Ponto ignora usuario_id/data/hora enviados: grava o usuário do token, a data e a hora do servidor (America/Sao_Paulo) | PASSOU |
| 80 | `test_item_com_categoria_nova` | F61-1 — Item com categoria nova ('  freios  e pastilhas ') grava, normalizada em maiúsculas; editar para outra nova também (antes: 400 do CHECK) | PASSOU |
| 81 | `test_categoria_invalida` | F61-2 — Categoria vazia ou com mais de 30 caracteres (limite da coluna) → 422 e nada gravado | PASSOU |
| 82 | `test_listar_e_criar_categoria` | F61-3 — Lista de categorias: padrão da oficina + criadas + as que itens já usam (MAO_OBRA); criar duplicada não duplica | PASSOU |
| 83 | `test_excluir_categoria` | F61-4 — Excluir categoria com itens: itens vão para DIVERSOS, a categoria some; DIVERSOS e MAO_OBRA não saem | PASSOU |
| 84 | `test_categorias_de_outra_empresa` | F61-5 — Isolamento: DONO da empresa A não lê, cria nem exclui categorias da empresa B | PASSOU |
| 85 | `test_categorias_fechadas_no_rest` | F61-6 — Anon/usuário logado não lê nem grava categorias_estoque direto pelo REST (RLS fechado, só o backend) | PASSOU |
| 86 | `test_datas_invertidas` | R9-1 — Escala com data_fim antes de data_inicio → 422 em português e nada gravado | PASSOU |
| 87 | `test_datas_validas[2026-12-24-2026-12-24]` | R9-2 — Mesmo dia e período normal continuam aceitos | PASSOU |
| 88 | `test_datas_validas[2026-12-24-2026-12-30]` | R9-2 — Mesmo dia e período normal continuam aceitos | PASSOU |
| 89 | `test_para_br` | F6-T1 — para_br: 23:30 BRT (02:30Z do dia seguinte) continua no dia certo; sem fuso é tratado como UTC | PASSOU |
| 90 | `test_vencimento_folha[hoje0-31-2027-02-28]` | F6-T2 — Folha: dia de pagamento 31 vira o último dia do mês (fev, abril, dezembro); depois do dia, vai para o mês seguinte | PASSOU |
| 91 | `test_vencimento_folha[hoje1-31-2028-02-29]` | F6-T2 — Folha: dia de pagamento 31 vira o último dia do mês (fev, abril, dezembro); depois do dia, vai para o mês seguinte | PASSOU |
| 92 | `test_vencimento_folha[hoje2-31-2026-04-30]` | F6-T2 — Folha: dia de pagamento 31 vira o último dia do mês (fev, abril, dezembro); depois do dia, vai para o mês seguinte | PASSOU |
| 93 | `test_vencimento_folha[hoje3-5-2026-12-05]` | F6-T2 — Folha: dia de pagamento 31 vira o último dia do mês (fev, abril, dezembro); depois do dia, vai para o mês seguinte | PASSOU |
| 94 | `test_vencimento_folha[hoje4-5-2027-01-05]` | F6-T2 — Folha: dia de pagamento 31 vira o último dia do mês (fev, abril, dezembro); depois do dia, vai para o mês seguinte | PASSOU |
| 95 | `test_vencimento_folha[hoje5-31-2026-01-31]` | F6-T2 — Folha: dia de pagamento 31 vira o último dia do mês (fev, abril, dezembro); depois do dia, vai para o mês seguinte | PASSOU |
| 96 | `test_vencimento_folha[hoje6-30-2026-02-28]` | F6-T2 — Folha: dia de pagamento 31 vira o último dia do mês (fev, abril, dezembro); depois do dia, vai para o mês seguinte | PASSOU |
| 97 | `test_busca_os_no_banco` | F7-1 — Unitário: busca de OS vai para a view os_busca com ilike e janela no banco (sem limit(5000)) | PASSOU |
| 98 | `test_listagem_sem_busca` | F7-2 — Unitário: sem busca a listagem segue na tabela, paginada | PASSOU |
| 99 | `test_termo_hostil` | F7-3 — Unitário: termo com vírgula, parênteses, aspas e % não quebra o filtro | PASSOU |
| 100 | `test_rotas_paginado[clientes]` | F7-4 — Unitário: /paginado de clientes, veículos e estoque devolve {items,total,skip,limit}; não é lido como id | PASSOU |
| 101 | `test_rotas_paginado[veiculos]` | F7-4 — Unitário: /paginado de clientes, veículos e estoque devolve {items,total,skip,limit}; não é lido como id | PASSOU |
| 102 | `test_rotas_paginado[estoque]` | F7-4 — Unitário: /paginado de clientes, veículos e estoque devolve {items,total,skip,limit}; não é lido como id | PASSOU |
| 103 | `test_limites_e_tenant` | F7-5 — Unitário: limit acima de 200 ou skip negativo → 422; empresa de outro tenant → 403 | PASSOU |
| 104 | `test_rotas_antigas` | F7-6 — Unitário: rotas antigas (lista completa) continuam iguais | PASSOU |
| 105 | `test_busca_acha_os_5999` | F7-7 — Integração: 6000 OS na Oficina do tião; busca acha a OS nº 5999 e a OS de 6000 itens pagina com total correto | PASSOU |
| 106 | `test_periodo_na_query` | F7-F1 — Período do Financeiro vai na query com o dia de Brasília: 12/11 = 03:00Z a 02:59:59Z do dia seguinte | PASSOU |
| 107 | `test_totais_iguais[None-None-esperado0]` | F7-F2 — Mesmos totais de antes (valores conferidos contra o código antigo num Postgres real): 23:30 BRT fica no dia 11, 00:00 e 23:59:59 no 12 | PASSOU |
| 108 | `test_totais_iguais[2026-11-12-2026-11-12-esperado1]` | F7-F2 — Mesmos totais de antes (valores conferidos contra o código antigo num Postgres real): 23:30 BRT fica no dia 11, 00:00 e 23:59:59 no 12 | PASSOU |
| 109 | `test_totais_iguais[2026-11-01-2026-11-30-esperado2]` | F7-F2 — Mesmos totais de antes (valores conferidos contra o código antigo num Postgres real): 23:30 BRT fica no dia 11, 00:00 e 23:59:59 no 12 | PASSOU |
| 110 | `test_totais_iguais[2026-09-01-2026-09-30-esperado3]` | F7-F2 — Mesmos totais de antes (valores conferidos contra o código antigo num Postgres real): 23:30 BRT fica no dia 11, 00:00 e 23:59:59 no 12 | PASSOU |
| 111 | `test_totais_iguais[2026-11-13-2026-11-13-esperado4]` | F7-F2 — Mesmos totais de antes (valores conferidos contra o código antigo num Postgres real): 23:30 BRT fica no dia 11, 00:00 e 23:59:59 no 12 | PASSOU |
| 112 | `test_totais_iguais[2026-11-12-None-esperado5]` | F7-F2 — Mesmos totais de antes (valores conferidos contra o código antigo num Postgres real): 23:30 BRT fica no dia 11, 00:00 e 23:59:59 no 12 | PASSOU |
| 113 | `test_historico_independe_do_periodo` | F7-F3 — Histórico de 6 meses não depende do período filtrado | PASSOU |
| 114 | `test_inteligencia_periodo` | F7-F4 — Inteligência financeira filtra no banco e ignora OS de outra empresa | PASSOU |
| 115 | `test_resumo_estoque` | F7-E1 — Resumo do estoque = stats da listagem completa (mesmos valores) | PASSOU |
| 116 | `test_dominios` | F7-B1 — url_audio: só https de domínio da lista (ou subdomínio); fora da lista ou lista vazia → erro antes de baixar | PASSOU |
| 117 | `test_normalizar` | F7-B2 — Normalização de nome de peça | PASSOU |
| 118 | `test_processar_audio` | F7-B3 — processar-audio: domínio fora → 400 sem baixar; Gemini chamado com await no cliente async; match exato, sem match vai sem estoque_id | PASSOU |
| 119 | `test_422_em_portugues[post-0]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 120 | `test_422_em_portugues[post-1]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 121 | `test_422_em_portugues[post-2]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 122 | `test_422_em_portugues[post-3]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 123 | `test_422_em_portugues[post-4]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 124 | `test_422_em_portugues[post-5]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 125 | `test_422_em_portugues[post-6]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 126 | `test_422_em_portugues[put-7]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 127 | `test_422_em_portugues[put-8]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 128 | `test_422_em_portugues[put-9]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 129 | `test_422_em_portugues[post-10]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 130 | `test_422_em_portugues[post-11]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 131 | `test_422_em_portugues[post-12]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 132 | `test_422_em_portugues[post-13]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 133 | `test_422_em_portugues[get-14]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 134 | `test_422_em_portugues[post-15]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 135 | `test_422_em_portugues[post-16]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 136 | `test_422_em_portugues[post-17]` | F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON) | PASSOU |
| 137 | `test_formato_e_sem_eco` | F8-13 — detail continua lista de {loc,msg,type}; input e senha digitada não são devolvidos | PASSOU |
| 138 | `test_varios_erros` | F8-14 — Vários erros no mesmo envio vêm todos, cada um com o seu campo | PASSOU |
| 139 | `test_criar_ok` | T14-1 — criar_empresa feliz: empresa, configuração, login do Auth e perfil DONO criados | PASSOU |
| 140 | `test_criar_desfaz[insert:empresas-500]` | T14-2 — Falha em QUALQUER passo desfaz os anteriores (empresa, configuração, login, perfil) e responde em português | PASSOU |
| 141 | `test_criar_desfaz[insert:configuracoes_empresa-500]` | T14-2 — Falha em QUALQUER passo desfaz os anteriores (empresa, configuração, login, perfil) e responde em português | PASSOU |
| 142 | `test_criar_desfaz[auth:create-400]` | T14-2 — Falha em QUALQUER passo desfaz os anteriores (empresa, configuração, login, perfil) e responde em português | PASSOU |
| 143 | `test_criar_desfaz[insert:usuarios-500]` | T14-2 — Falha em QUALQUER passo desfaz os anteriores (empresa, configuração, login, perfil) e responde em português | PASSOU |
| 144 | `test_criar_email_existente` | T14-3 — E-mail do dono já existente no Auth: 400 'Já existe um usuário com este e-mail.' e nada fica | PASSOU |
| 145 | `test_criar_desfazer_falha` | T14-4 — Se o desfazer também falhar, o erro avisa que ficou pela metade (e vai para o log) | PASSOU |
| 146 | `test_criar_apierror` | T14-5 — APIError do banco no passo 1 continua indo para o handler global (mensagem mapeada) | PASSOU |
| 147 | `test_deletar_ok` | T14-6 — deletar_empresa remove os logins do Auth dos usuários DELA e só deles; solta o vínculo da auditoria | PASSOU |
| 148 | `test_deletar_com_historico[clientes]` | T14-7 — Empresa com histórico (clientes, OS, lançamentos...) → 400 explicando e NADA é apagado (nem logins) | PASSOU |
| 149 | `test_deletar_com_historico[veiculos]` | T14-7 — Empresa com histórico (clientes, OS, lançamentos...) → 400 explicando e NADA é apagado (nem logins) | PASSOU |
| 150 | `test_deletar_com_historico[ordens_servico]` | T14-7 — Empresa com histórico (clientes, OS, lançamentos...) → 400 explicando e NADA é apagado (nem logins) | PASSOU |
| 151 | `test_deletar_com_historico[estoque]` | T14-7 — Empresa com histórico (clientes, OS, lançamentos...) → 400 explicando e NADA é apagado (nem logins) | PASSOU |
| 152 | `test_deletar_com_historico[transacoes_financeiras]` | T14-7 — Empresa com histórico (clientes, OS, lançamentos...) → 400 explicando e NADA é apagado (nem logins) | PASSOU |
| 153 | `test_deletar_404_e_master` | T14-8 — Empresa inexistente → 404; empresa com usuário master → 400; nada apagado | PASSOU |
| 154 | `test_deletar_falha_no_auth_e_repete` | T14-9 — Falha ao remover um login: 502 em português, nada do banco apagado; repetir funciona (login já removido conta como feito) | PASSOU |
| 155 | `test_achar_auth_por_email` | T14-10 — Busca de login por e-mail lê página a página (page/per_page) e PARA ao achar; nunca list_users() solto | PASSOU |
| 156 | `test_trocar_senha_usa_busca` | T14-11 — atualizar_usuario: senha de usuário sem login com este id usa a busca por e-mail (sem list_users solto) | PASSOU |
| 157 | `test_limites_empresa[EmpresaCreate-nome_fantasia-150]` | T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72 | PASSOU |
| 158 | `test_limites_empresa[EmpresaCreate-razao_social-150]` | T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72 | PASSOU |
| 159 | `test_limites_empresa[EmpresaCreate-cnpj-20]` | T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72 | PASSOU |
| 160 | `test_limites_empresa[EmpresaCreate-telefone-30]` | T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72 | PASSOU |
| 161 | `test_limites_empresa[EmpresaCreate-endereco-300]` | T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72 | PASSOU |
| 162 | `test_limites_empresa[EmpresaCreate-nome_dono-100]` | T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72 | PASSOU |
| 163 | `test_limites_empresa[EmpresaCreate-senha_dono-72]` | T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72 | PASSOU |
| 164 | `test_limites_empresa[EmpresaUpdate-nome_fantasia-150]` | T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72 | PASSOU |
| 165 | `test_limites_empresa[EmpresaUpdate-cnpj-20]` | T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72 | PASSOU |
| 166 | `test_limites_empresa[EmpresaUpdate-telefone-30]` | T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72 | PASSOU |
| 167 | `test_limites_empresa[EmpresaUpdate-endereco-300]` | T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72 | PASSOU |
| 168 | `test_limites_empresa[ConfigUpdate-nome_exibicao-150]` | T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72 | PASSOU |
| 169 | `test_limites_empresa[ConfigUpdate-cor_primaria-20]` | T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72 | PASSOU |
| 170 | `test_integracao_criar_e_apagar` | T14-13 — Integração: cria empresa de verdade, confere os 4 registros, apaga: tudo some (inclusive o login) e a auditoria fica sem vínculo | PASSOU |
| 171 | `test_integracao_email_existente` | T14-14 — Integração: e-mail do dono que já existe no Auth → 400 em português e nenhuma empresa nem login sobra | PASSOU |
| 172 | `test_retry_timeout` | T14-15 — Statement timeout (57014) ao desfazer/apagar: tenta de novo e conclui; outro erro não é repetido | PASSOU |
| 173 | `test_erro_nao_mapeado` | F8-1 — Erro de banco desconhecido: mensagem genérica em português para o cliente, texto cru só no log | PASSOU |
| 174 | `test_22001` | F8-2 — 22001 (texto grande demais) → 422 em português com o limite | PASSOU |
| 175 | `test_mapeados_continuam` | F8-3 — Erros já mapeados continuam iguais (duplicado 409, obrigatório 422) | PASSOU |
| 176 | `test_limite[ClienteCreate.nome]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 177 | `test_limite[ClienteCreate.telefone]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 178 | `test_limite[ClienteCreate.cpf_cnpj]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 179 | `test_limite[ClienteUpdate.nome]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 180 | `test_limite[ClienteUpdate.telefone]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 181 | `test_limite[ClienteUpdate.cpf_cnpj]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 182 | `test_limite[VeiculoCreate.placa]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 183 | `test_limite[VeiculoCreate.modelo]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 184 | `test_limite[VeiculoCreate.marca]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 185 | `test_limite[VeiculoCreate.cor]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 186 | `test_limite[VeiculoUpdate.placa]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 187 | `test_limite[VeiculoUpdate.modelo]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 188 | `test_limite[VeiculoUpdate.marca]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 189 | `test_limite[VeiculoUpdate.cor]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 190 | `test_limite[EstoqueCreate.nome]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 191 | `test_limite[EstoqueCreate.codigo]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 192 | `test_limite[EstoqueCreate.categoria]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 193 | `test_limite[EstoqueUpdate.nome]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 194 | `test_limite[EstoqueUpdate.codigo]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 195 | `test_limite[EstoqueUpdate.categoria]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 196 | `test_limite[UsuarioCreate.nome]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 197 | `test_limite[UsuarioUpdate.nome]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 198 | `test_limite[OSItemCreate.nome_item]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 199 | `test_limite[OSItemUpdate.nome_item]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 200 | `test_limite[ConfigUpdate.whatsapp]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 201 | `test_limite[ConfigUpdate.chave_pix]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 202 | `test_limite[ConfigUpdate.inscricao_estadual]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 203 | `test_limite[CadastroRapidoRequest.nome_cliente]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 204 | `test_limite[CadastroRapidoRequest.telefone_cliente]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 205 | `test_limite[CadastroRapidoRequest.placa]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 206 | `test_limite[EscalaFolgaCreate.observacoes]` | F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update | PASSOU |
| 207 | `test_email_limite` | F8-5 — E-mail de usuário acima de 255 → 422 | PASSOU |
| 208 | `test_ponto[-90--180-True]` | F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422 | PASSOU |
| 209 | `test_ponto[90-180-True]` | F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422 | PASSOU |
| 210 | `test_ponto[-23.5--46.6-True]` | F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422 | PASSOU |
| 211 | `test_ponto[None-None-True]` | F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422 | PASSOU |
| 212 | `test_ponto[90.1-0-False]` | F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422 | PASSOU |
| 213 | `test_ponto[-90.1-0-False]` | F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422 | PASSOU |
| 214 | `test_ponto[0-180.1-False]` | F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422 | PASSOU |
| 215 | `test_ponto[0--180.1-False]` | F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422 | PASSOU |
| 216 | `test_folha[01/2026-True]` | F8-7 — Folha: mes_referencia só MM/AAAA válido | PASSOU |
| 217 | `test_folha[12/2026-True]` | F8-7 — Folha: mes_referencia só MM/AAAA válido | PASSOU |
| 218 | `test_folha[10/2099-True]` | F8-7 — Folha: mes_referencia só MM/AAAA válido | PASSOU |
| 219 | `test_folha[13/2026-False]` | F8-7 — Folha: mes_referencia só MM/AAAA válido | PASSOU |
| 220 | `test_folha[00/2026-False]` | F8-7 — Folha: mes_referencia só MM/AAAA válido | PASSOU |
| 221 | `test_folha[1/2026-False]` | F8-7 — Folha: mes_referencia só MM/AAAA válido | PASSOU |
| 222 | `test_folha[2026-10-False]` | F8-7 — Folha: mes_referencia só MM/AAAA válido | PASSOU |
| 223 | `test_folha[10/26-False]` | F8-7 — Folha: mes_referencia só MM/AAAA válido | PASSOU |
| 224 | `test_folha[outubro-False]` | F8-7 — Folha: mes_referencia só MM/AAAA válido | PASSOU |
| 225 | `test_folha[-False]` | F8-7 — Folha: mes_referencia só MM/AAAA válido | PASSOU |
| 226 | `test_folha[10/2026 -False]` | F8-7 — Folha: mes_referencia só MM/AAAA válido | PASSOU |
| 227 | `test_folha[10/1999-False]` | F8-7 — Folha: mes_referencia só MM/AAAA válido | PASSOU |
| 228 | `test_formas_pagamento` | F8-8 — Formas de pagamento: lista única (inclui TED e as do front); fora da lista → 422 em OS, lançamento, edição e baixa | PASSOU |
| 229 | `test_leitura_de_dado_antigo` | F8-9 — Dado antigo com forma fora da lista continua sendo lido sem erro | PASSOU |
| 230 | `test_rota_formas` | F8-10 — GET /api/v1/formas-pagamento devolve a lista (qualquer perfil logado) | PASSOU |
| 231 | `test_http_422` | F8-11 — HTTP: texto acima do limite e forma inválida chegam como 422 com mensagem | PASSOU |
| 232 | `test_guarda_recusa_empresa_de_producao` | F0-G — Guarda: testes recusam empresa de produção (Autotec Racing) | PASSOU |
| 233 | `test_dono_ve_a_propria_empresa` | T1+ — DONO da Oficina A acessa a própria empresa (controle positivo) | PASSOU |
| 234 | `test_dono_nao_ve_outra_empresa[clientes]` | T1 — DONO da Oficina A chamando rota com empresa_id da Oficina B → 403 | PASSOU |
| 235 | `test_dono_nao_ve_outra_empresa[veiculos]` | T1 — DONO da Oficina A chamando rota com empresa_id da Oficina B → 403 | PASSOU |
| 236 | `test_dono_nao_ve_outra_empresa[estoque]` | T1 — DONO da Oficina A chamando rota com empresa_id da Oficina B → 403 | PASSOU |
| 237 | `test_dono_nao_ve_outra_empresa[dashboards]` | T1 — DONO da Oficina A chamando rota com empresa_id da Oficina B → 403 | PASSOU |
| 238 | `test_mecanico_sem_financeiro` | F1 — MECÂNICO não acessa o financeiro (lado backend) | PASSOU |
| 239 | `test_anon_nao_le_nada_pela_api_rest` | F-1 — Chave anon (pública) não lê nada pela API REST do Supabase | PASSOU |
| 240 | `test_requisicoes_paralelas` | F3-P1 — 60 requisições simultâneas (8 rotas) com token válido: todas 200, nenhum 401/500 | PASSOU |
| 241 | `test_erro_de_infra_nao_vira_token_invalido` | F3-P2 — Falha de infraestrutura na checagem do token → 503 (a tela repete); token inválido → 401 | PASSOU |
| 242 | `test_bloqueia_outra_empresa` | T1 — Unitário: perfil da empresa A em rota da empresa B → 403 | PASSOU |
| 243 | `test_permite_propria_empresa` | T1+ — Unitário: MECÂNICO na própria empresa → 200 | PASSOU |
| 244 | `test_bloqueia_query_param_de_outra_empresa` | T1 — Unitário: empresa_id de outra empresa na query string → 403 | PASSOU |
| 245 | `test_master_acessa_qualquer_empresa` | T1-M — Unitário: master acessa qualquer empresa → 200 | PASSOU |
| 246 | `test_post_usa_empresa_do_token` | F1.2 — POST grava na empresa do token, não na do body | PASSOU |

---

## 1. `tests/test_deploy.py::test_health`

- **Cenário:** F41-H — GET /api/v1/health responde 200 sem token e sem tocar o banco
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 2. `tests/test_deploy.py::test_cors_por_variavel`

- **Cenário:** F41-C — Com ALLOWED_ORIGINS só o domínio do app passa no CORS; sem a variável tudo passa (compatível com o Render)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 3. `tests/test_deploy.py::test_chave_do_servidor_invalida_nao_vira_token_invalido`

- **Cenário:** F41-K — Chave do Supabase do SERVIDOR inválida (config errada) → 503 e log claro, não 401 'token inválido' que desloga todo mundo
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 4. `tests/test_deploy.py::test_cloud_init_so_ascii`

- **Cenário:** F41-A — deploy/cloud-init.yaml é ASCII puro: acento colado no console da Oracle vira byte Latin-1 e o cloud-init descarta o arquivo inteiro
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 5. `tests/test_deploy.py::test_api_sobe_sem_chave_do_gemini`

- **Cenário:** F41-G — Sem GEMINI_API_KEY a API sobe (só a rota de áudio do bot fica 503); antes o processo inteiro morria no import
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 6. `tests/test_fase10_isolamento_ids.py::test_escala_usuario_de_outra_empresa`

- **Cenário:** T10-1 — Escala: usuario_id da Oficina B → 404, nada gravado, nome do colaborador de B não vaza
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/equipe/escalas/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "usuario_id": "7051b94a-aa8e-4e95-bd7e-13c77a83b782",
  "tipo": "FOLGA",
  "data_inicio": "2026-12-24",
  "data_fim": "2026-12-25"
}
```

**Response:** `404`

```json
{
  "detail": "Colaborador não encontrado nesta empresa."
}
```

---

## 7. `tests/test_fase10_isolamento_ids.py::test_escala_usuario_da_propria_empresa`

- **Cenário:** T10-2 — Escala: colaborador da própria empresa continua funcionando
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/equipe/escalas/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "usuario_id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
  "tipo": "FOLGA",
  "data_inicio": "2026-12-24",
  "data_fim": "2026-12-25"
}
```

**Response:** `200`

```json
{
  "usuario_id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
  "tipo": "FOLGA",
  "data_inicio": "2026-12-24",
  "data_fim": "2026-12-25",
  "observacoes": null,
  "id": "9ec3389c-84ee-46bc-b10e-ca2fcf509acb",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "usuario_nome": "Mecanico Teste A",
  "created_at": "2026-11-26T00:56:28.068662Z"
}
```

---

## 8. `tests/test_fase10_isolamento_ids.py::test_os_ids_de_outra_empresa`

- **Cenário:** T10-3 — OS: cliente, veículo ou mecânico de B na criação → 404 e nenhuma OS criada; mecânico de B na edição → 404 e OS intacta
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/os/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "cliente_id": "ed38707b-3ee8-453b-945d-0ce9be890105",
  "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53"
}
```

**Response:** `404`

```json
{
  "detail": "Cliente não encontrado nesta empresa."
}
```

### Chamada 2

**Request:** `POST http://testserver/api/v1/os/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
  "veiculo_id": "2be58fc9-98b8-462b-9234-056032d52053"
}
```

**Response:** `404`

```json
{
  "detail": "Veículo não encontrado nesta empresa."
}
```

### Chamada 3

**Request:** `POST http://testserver/api/v1/os/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
  "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
  "mecanico_responsavel_id": "7051b94a-aa8e-4e95-bd7e-13c77a83b782"
}
```

**Response:** `404`

```json
{
  "detail": "Mecânico não encontrado nesta empresa."
}
```

### Chamada 4

**Request:** `PUT http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/9b45576f-8687-41de-bfff-f42cde85254e`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "mecanico_responsavel_id": "7051b94a-aa8e-4e95-bd7e-13c77a83b782"
}
```

**Response:** `404`

```json
{
  "detail": "Mecânico não encontrado nesta empresa."
}
```

---

## 9. `tests/test_fase10_isolamento_ids.py::test_item_os_estoque_de_outra_empresa`

- **Cenário:** T10-4 — Item da OS com estoque_id de B → recusado, estoque de B intacto, nenhum item criado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/9b45576f-8687-41de-bfff-f42cde85254e/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "estoque_id": "4b34e55c-4d43-4fb8-99f8-55a27885a72a",
  "tipo": "PECA",
  "nome_item": "Peça de B",
  "quantidade": 1,
  "custo_unitario": 1,
  "venda_unitario": 2
}
```

**Response:** `404`

```json
{
  "detail": "Item de estoque não encontrado."
}
```

### Chamada 2

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/9b45576f-8687-41de-bfff-f42cde85254e/itens/lote`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
[
  {
    "estoque_id": "4b34e55c-4d43-4fb8-99f8-55a27885a72a",
    "tipo": "PECA",
    "nome_item": "Peça de B",
    "quantidade": 1,
    "custo_unitario": 1,
    "venda_unitario": 2
  }
]
```

**Response:** `404`

```json
{
  "detail": "Item de estoque para 'Peça de B' não encontrado."
}
```

---

## 10. `tests/test_fase10_isolamento_ids.py::test_veiculo_cliente_de_outra_empresa`

- **Cenário:** T10-5 — Veículo: cliente_id de B na criação e na edição → 404, nada gravado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/veiculos/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "cliente_id": "ed38707b-3ee8-453b-945d-0ce9be890105",
  "placa": "T10ZZ99",
  "modelo": "Teste"
}
```

**Response:** `404`

```json
{
  "detail": "Cliente não encontrado nesta empresa."
}
```

### Chamada 2

**Request:** `PUT http://testserver/api/v1/veiculos/94334e9f-629c-4c65-92f8-e26274ba3973/522784a7-2f0f-492a-9cdd-ffa17f71cf53`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "cliente_id": "ed38707b-3ee8-453b-945d-0ce9be890105"
}
```

**Response:** `404`

```json
{
  "detail": "Cliente não encontrado nesta empresa."
}
```

---

## 11. `tests/test_fase10_isolamento_ids.py::test_bot_ids_de_outra_empresa`

- **Cenário:** T10-6 — Bot: abrir-os com cliente/veículo/mecânico de B e cadastro-rápido com mecânico de B → 404, nada criado
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 12. `tests/test_fase10_isolamento_ids.py::test_bot_audio_os_de_outra_empresa`

- **Cenário:** T10-7 — Bot: processar-audio com os_id de B e empresa_id de A → 404 antes de baixar o áudio; OS de B sem itens novos
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 13. `tests/test_fase1_isolamento.py::test_recurso_de_outra_empresa_pela_rota_propria`

- **Cenário:** T1-R — DONO A pede, pela rota da própria empresa, um cliente que é da Oficina B → 404
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/clientes/94334e9f-629c-4c65-92f8-e26274ba3973/ed38707b-3ee8-453b-945d-0ce9be890105`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `404`

```json
{
  "detail": "Cliente não encontrado na sua jurisdição."
}
```

---

## 14. `tests/test_fase1_isolamento.py::test_post_cliente_grava_na_empresa_do_token`

- **Cenário:** F1.2 — POST de cliente com empresa_id da Oficina B no body grava na Oficina A (empresa do token)
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/clientes/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "nome": "Cliente F1.2 (temporário)",
  "telefone": "11900000012",
  "empresa_id": "b763e7f1-e35b-4aa4-baa8-c8d586caf705"
}
```

**Response:** `200`

```json
{
  "nome": "Cliente F1.2 (temporário)",
  "telefone": "11900000012",
  "cpf_cnpj": null,
  "endereco": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "bd742c99-b9cd-417a-9e3f-70875df9484e"
}
```

---

## 15. `tests/test_fase1_isolamento.py::test_item_em_os_de_outra_empresa`

- **Cenário:** F1.3 — DONO A adiciona item numa OS da Oficina B → 404 (pela rota de A) e 403 (pela rota de B)
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/656cff42-7c05-47a9-ad3c-6f4ced527ccc/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "tipo": "MAO_OBRA",
  "nome_item": "Invasão F1.3",
  "quantidade": 1,
  "venda_unitario": 1
}
```

**Response:** `404`

```json
{
  "detail": "Ordem de Serviço não encontrado nesta empresa."
}
```

### Chamada 2

**Request:** `POST http://testserver/api/v1/os/b763e7f1-e35b-4aa4-baa8-c8d586caf705/656cff42-7c05-47a9-ad3c-6f4ced527ccc/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "tipo": "MAO_OBRA",
  "nome_item": "Invasão F1.3",
  "quantidade": 1,
  "venda_unitario": 1
}
```

**Response:** `403`

```json
{
  "detail": "Acesso negado a dados de outra empresa."
}
```

### Chamada 3

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/656cff42-7c05-47a9-ad3c-6f4ced527ccc/itens/lote`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
[
  {
    "tipo": "MAO_OBRA",
    "nome_item": "Invasão F1.3",
    "quantidade": 1,
    "venda_unitario": 1
  }
]
```

**Response:** `404`

```json
{
  "detail": "Ordem de Serviço não encontrado nesta empresa."
}
```

---

## 16. `tests/test_fase1_isolamento.py::test_alterar_item_de_outra_empresa`

- **Cenário:** F1.3b — DONO A tenta alterar/remover item de OS da Oficina B → 404; item e estoque de B intactos
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/os/b763e7f1-e35b-4aa4-baa8-c8d586caf705/656cff42-7c05-47a9-ad3c-6f4ced527ccc/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "estoque_id": "4b34e55c-4d43-4fb8-99f8-55a27885a72a",
  "tipo": "PECA",
  "nome_item": "Item F1.3b",
  "quantidade": 1,
  "custo_unitario": 20,
  "venda_unitario": 45
}
```

**Response:** `200`

```json
{
  "id": "131f33b1-14d8-41b9-b8f7-96f01b6a813e",
  "empresa_id": "b763e7f1-e35b-4aa4-baa8-c8d586caf705",
  "os_id": "656cff42-7c05-47a9-ad3c-6f4ced527ccc",
  "estoque_id": "4b34e55c-4d43-4fb8-99f8-55a27885a72a",
  "tipo": "PECA",
  "nome_item": "Item F1.3b",
  "quantidade": 1,
  "custo_unitario": 20.0,
  "venda_unitario": 45.0,
  "criado_em": "2026-11-26T00:56:39.031036+00:00"
}
```

### Chamada 2

**Request:** `PUT http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/656cff42-7c05-47a9-ad3c-6f4ced527ccc/itens/131f33b1-14d8-41b9-b8f7-96f01b6a813e`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "quantidade": 9
}
```

**Response:** `404`

```json
{
  "detail": "Ordem de Serviço não encontrado nesta empresa."
}
```

### Chamada 3

**Request:** `DELETE http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/656cff42-7c05-47a9-ad3c-6f4ced527ccc/itens/131f33b1-14d8-41b9-b8f7-96f01b6a813e`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `404`

```json
{
  "detail": "Ordem de Serviço não encontrado nesta empresa."
}
```

### Chamada 4

**Request:** `DELETE http://testserver/api/v1/os/b763e7f1-e35b-4aa4-baa8-c8d586caf705/656cff42-7c05-47a9-ad3c-6f4ced527ccc/itens/131f33b1-14d8-41b9-b8f7-96f01b6a813e`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "status": "sucesso",
  "detail": "Item removido e estornado (se aplicável)."
}
```

---

## 17. `tests/test_fase1_isolamento.py::test_criar_os_com_vinculo_de_outra_empresa[veiculo]`

- **Cenário:** F1.5 — DONO A abre OS com veículo/cliente/mecânico da Oficina B → 404
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/os/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
  "veiculo_id": "2be58fc9-98b8-462b-9234-056032d52053",
  "mecanico_responsavel_id": "df201096-62a8-49e8-b9bb-bb000244d4e8"
}
```

**Response:** `404`

```json
{
  "detail": "Veículo não encontrado nesta empresa."
}
```

---

## 18. `tests/test_fase1_isolamento.py::test_criar_os_com_vinculo_de_outra_empresa[cliente]`

- **Cenário:** F1.5 — DONO A abre OS com veículo/cliente/mecânico da Oficina B → 404
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/os/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "cliente_id": "ed38707b-3ee8-453b-945d-0ce9be890105",
  "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
  "mecanico_responsavel_id": "df201096-62a8-49e8-b9bb-bb000244d4e8"
}
```

**Response:** `404`

```json
{
  "detail": "Cliente não encontrado nesta empresa."
}
```

---

## 19. `tests/test_fase1_isolamento.py::test_criar_os_com_vinculo_de_outra_empresa[mecanico]`

- **Cenário:** F1.5 — DONO A abre OS com veículo/cliente/mecânico da Oficina B → 404
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/os/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
  "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
  "mecanico_responsavel_id": "7051b94a-aa8e-4e95-bd7e-13c77a83b782"
}
```

**Response:** `404`

```json
{
  "detail": "Mecânico não encontrado nesta empresa."
}
```

---

## 20. `tests/test_fase1_isolamento.py::test_veiculo_com_cliente_de_outra_empresa`

- **Cenário:** F1.5b — DONO A cadastra veículo apontando para cliente da Oficina B → 404
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/veiculos/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "placa": "TSTF1X5",
  "modelo": "Invasão",
  "cliente_id": "ed38707b-3ee8-453b-945d-0ce9be890105",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
}
```

**Response:** `404`

```json
{
  "detail": "Cliente não encontrado nesta empresa."
}
```

---

## 21. `tests/test_fase1_isolamento.py::test_dono_nao_promove_master`

- **Cenário:** F1.4 — DONO A promove o mecânico a master → 403; cargo continua MECANICO
- **Resultado:** PASSOU

### Chamada 1

**Request:** `PUT http://testserver/api/v1/usuarios/94334e9f-629c-4c65-92f8-e26274ba3973/df201096-62a8-49e8-b9bb-bb000244d4e8`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "cargo": "master"
}
```

**Response:** `403`

```json
{
  "detail": "Só o master pode criar ou promover master."
}
```

---

## 22. `tests/test_fase1_isolamento.py::test_dono_nao_cria_master`

- **Cenário:** F1.4b — DONO A cria usuário já como master → 403; nenhum usuário criado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/usuarios/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "nome": "Invasão",
  "email": "master.invasao@example.com",
  "cargo": "master",
  "senha": "SenhaQualquer123"
}
```

**Response:** `403`

```json
{
  "detail": "Só o master pode criar ou promover master."
}
```

---

## 23. `tests/test_fase2_rh.py::test_rh_nao_sai_pela_api_rest[salario_base-MECANICO]`

- **Cenário:** F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/usuarios?select=salario_base`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "code": "42501",
  "details": null,
  "hint": "Grant the required privileges to the current role with: GRANT SELECT ON public.usuarios TO authenticated;",
  "message": "permission denied for table usuarios"
}
```

---

## 24. `tests/test_fase2_rh.py::test_rh_nao_sai_pela_api_rest[salario_base-DONO]`

- **Cenário:** F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/usuarios?select=salario_base`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "code": "42501",
  "details": null,
  "hint": "Grant the required privileges to the current role with: GRANT SELECT ON public.usuarios TO authenticated;",
  "message": "permission denied for table usuarios"
}
```

---

## 25. `tests/test_fase2_rh.py::test_rh_nao_sai_pela_api_rest[comissao_servico_pct-MECANICO]`

- **Cenário:** F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/usuarios?select=comissao_servico_pct`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "code": "42501",
  "details": null,
  "hint": "Grant the required privileges to the current role with: GRANT SELECT ON public.usuarios TO authenticated;",
  "message": "permission denied for table usuarios"
}
```

---

## 26. `tests/test_fase2_rh.py::test_rh_nao_sai_pela_api_rest[comissao_servico_pct-DONO]`

- **Cenário:** F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/usuarios?select=comissao_servico_pct`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "code": "42501",
  "details": null,
  "hint": "Grant the required privileges to the current role with: GRANT SELECT ON public.usuarios TO authenticated;",
  "message": "permission denied for table usuarios"
}
```

---

## 27. `tests/test_fase2_rh.py::test_rh_nao_sai_pela_api_rest[vale_transporte-MECANICO]`

- **Cenário:** F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/usuarios?select=vale_transporte`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "code": "42501",
  "details": null,
  "hint": "Grant the required privileges to the current role with: GRANT SELECT ON public.usuarios TO authenticated;",
  "message": "permission denied for table usuarios"
}
```

---

## 28. `tests/test_fase2_rh.py::test_rh_nao_sai_pela_api_rest[vale_transporte-DONO]`

- **Cenário:** F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/usuarios?select=vale_transporte`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "code": "42501",
  "details": null,
  "hint": "Grant the required privileges to the current role with: GRANT SELECT ON public.usuarios TO authenticated;",
  "message": "permission denied for table usuarios"
}
```

---

## 29. `tests/test_fase2_rh.py::test_rh_nao_sai_pela_api_rest[senha_hash-MECANICO]`

- **Cenário:** F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/usuarios?select=senha_hash`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>"}`

**Response:** `400`

```json
{
  "code": "42703",
  "details": null,
  "hint": null,
  "message": "column usuarios.senha_hash does not exist"
}
```

---

## 30. `tests/test_fase2_rh.py::test_rh_nao_sai_pela_api_rest[senha_hash-DONO]`

- **Cenário:** F2.1 — Logado (MECÂNICO e DONO) lendo coluna de RH ou senha_hash direto no Supabase → negado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/usuarios?select=senha_hash`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>"}`

**Response:** `400`

```json
{
  "code": "42703",
  "details": null,
  "hint": null,
  "message": "column usuarios.senha_hash does not exist"
}
```

---

## 31. `tests/test_fase2_rh.py::test_mecanico_le_nomes_da_equipe`

- **Cenário:** F2.2 — MECÂNICO continua lendo nome/cargo da equipe da própria oficina (e não da outra)
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/usuarios?select=id,nome,cargo,empresa_id`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "code": "42501",
  "details": null,
  "hint": "Grant the required privileges to the current role with: GRANT SELECT ON public.usuarios TO authenticated;",
  "message": "permission denied for table usuarios"
}
```

---

## 32. `tests/test_fase2_rh.py::test_dono_nao_grava_rh_direto`

- **Cenário:** F2.3 — DONO tenta gravar salário direto no Supabase → negado; valor no banco inalterado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `PATCH https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/usuarios?id=eq.df201096-62a8-49e8-b9bb-bb000244d4e8`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "salario_base": 99999
}
```

**Response:** `403`

```json
{
  "code": "42501",
  "details": null,
  "hint": "Grant the required privileges to the current role with: GRANT SELECT, UPDATE ON public.usuarios TO authenticated;",
  "message": "permission denied for table usuarios"
}
```

---

## 33. `tests/test_fase2_rh.py::test_rh_pelo_backend_so_para_dono`

- **Cenário:** F2.4 — Backend: DONO lista equipe com RH (200); MECÂNICO e FINANCEIRO → 403
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/usuarios/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  {
    "nome": "Atendente Teste A",
    "email": "atendente.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "ATENDENTE",
    "ativo": true,
    "salario_base": 0.0,
    "comissao_servico_pct": 0.0,
    "comissao_peca_pct": 0.0,
    "vale_transporte": 0.0,
    "vale_refeicao": 0.0,
    "paga_hora_extra": false,
    "valor_hora_extra": 0.0,
    "estrelas_media": 5.0,
    "total_avaliacoes": 0,
    "id": "8b89c905-3f58-4336-8b95-cba4d04e5f70",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
  },
  {
    "nome": "Dono Teste A",
    "email": "dono.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "DONO",
    "ativo": true,
    "salario_base": 0.0,
    "comissao_servico_pct": 0.0,
    "comissao_peca_pct": 0.0,
    "vale_transporte": 0.0,
    "vale_refeicao": 0.0,
    "paga_hora_extra": false,
    "valor_hora_extra": 0.0,
    "estrelas_media": 5.0,
    "total_avaliacoes": 0,
    "id": "f3b95dfc-237c-49b1-adf1-c1b1d048140f",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
  },
  {
    "nome": "Financeiro Teste A",
    "email": "financeiro.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "FINANCEIRO",
    "ativo": true,
    "salario_base": 0.0,
    "comissao_servico_pct": 0.0,
    "comissao_peca_pct": 0.0,
    "vale_transporte": 0.0,
    "vale_refeicao": 0.0,
    "paga_hora_extra": false,
    "valor_hora_extra": 0.0,
    "estrelas_media": 5.0,
    "total_avaliacoes": 0,
    "id": "bba76da7-c154-4be7-9826-5e1a677e6eba",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
  },
  {
    "nome": "joao",
    "email": "joao@oficina.com",
    "telefone": null,
    "cargo": "DONO",
    "ativo": true,
    "salario_base": 0.0,
    "comissao_servico_pct": 0.0,
    "comissao_peca_pct": 0.0,
    "vale_transporte": 0.0,
    "vale_refeicao": 0.0,
    "paga_hora_extra": false,
    "valor_hora_extra": 0.0,
    "estrelas_media": 5.0,
    "total_avaliacoes": 0,
    "id": "5895210e-13af-47c2-a08c-ba8030d1be25",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
  },
  {
    "nome": "Mecanico Teste A",
    "email": "mecanico.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "MECANICO",
    "ativo": true,
    "salario_base": 0.0,
    "comissao_servico_pct": 0.0,
    "comissao_peca_pct": 0.0,
    "vale_transporte": 0.0,
    "vale_refeicao": 0.0,
    "paga_hora_extra": false,
    "valor_hora_extra": 0.0,
    "estrelas_media": 5.0,
    "total_avaliacoes": 0,
    "id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
  },
  {
    "nome": "Vinici",
    "email": "camargo1.v@icloud.com",
    "telefone": null,
    "cargo": "MECANICO",
    "ativo": true,
    "salario_base": 0.0,
    "comissao_servico_pct": 0.0,
    "comissao_peca_pct": 0.0,
    "vale_transporte": 0.0,
    "vale_refeicao": 0.0,
    "paga_hora_extra": false,
    "valor_hora_extra": 0.0,
    "estrelas_media": 5.0,
    "total_avaliacoes": 0,
    "id": "b84b36ee-4d8c-40b5-86a2
... (truncado)
```

### Chamada 2

**Request:** `GET http://testserver/api/v1/usuarios/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado para o seu perfil."
}
```

### Chamada 3

**Request:** `GET http://testserver/api/v1/usuarios/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado para o seu perfil."
}
```

---

## 34. `tests/test_fase2_rh.py::test_dono_altera_rh_pelo_backend`

- **Cenário:** F2.5 — Backend: DONO altera salário do mecânico (200) e o valor é gravado no banco
- **Resultado:** PASSOU

### Chamada 1

**Request:** `PUT http://testserver/api/v1/usuarios/94334e9f-629c-4c65-92f8-e26274ba3973/df201096-62a8-49e8-b9bb-bb000244d4e8`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "salario_base": 2345.67
}
```

**Response:** `200`

```json
{
  "nome": "Mecanico Teste A",
  "email": "mecanico.a@homolog-autotec.example.com",
  "telefone": null,
  "cargo": "MECANICO",
  "ativo": true,
  "salario_base": 2345.67,
  "comissao_servico_pct": 0.0,
  "comissao_peca_pct": 0.0,
  "vale_transporte": 0.0,
  "vale_refeicao": 0.0,
  "paga_hora_extra": false,
  "valor_hora_extra": 0.0,
  "estrelas_media": 5.0,
  "total_avaliacoes": 0,
  "id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
}
```

---

## 35. `tests/test_fase3_contrato.py::test_leituras_pelo_backend[/dashboards/{emp}]`

- **Cenário:** F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/dashboards/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "total_abertas": 0,
  "estoque_critico_count": 0,
  "status_counts": {
    "ORCAMENTO": 1,
    "AGUARDANDO_PECA": 0,
    "EXECUCAO": 0,
    "FINALIZADO": 0,
    "PAGO": 0
  },
  "ultimas_os": [
    {
      "id": "9b45576f-8687-41de-bfff-f42cde85254e",
      "status": "ORCAMENTO",
      "data_abertura": "2026-11-09T18:17:28.766794+00:00",
      "total_geral": 0.0,
      "descricao_problema": "OS de teste (seed)",
      "clientes": {
        "nome": "Cliente Teste A",
        "telefone": "11999990001"
      },
      "veiculos": {
        "placa": "TSTA001",
        "modelo": "Gol 1.0"
      }
    }
  ],
  "itens_criticos": []
}
```

---

## 36. `tests/test_fase3_contrato.py::test_leituras_pelo_backend[/clientes/{emp}]`

- **Cenário:** F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/clientes/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  {
    "nome": "Cliente Teste A",
    "telefone": "11999990001",
    "cpf_cnpj": null,
    "endereco": null,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "44e46577-443d-4c98-90d2-cd79e0123492"
  },
  {
    "nome": "Julya Lima Moreira",
    "telefone": "11978879957",
    "cpf_cnpj": null,
    "endereco": "Rua João de Sá, 240",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "a26df8a8-d7a6-4f81-a902-c26186ed18c2"
  },
  {
    "nome": "Marli",
    "telefone": "21323123123",
    "cpf_cnpj": "",
    "endereco": null,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "c94fb84a-fa0f-479d-adb2-5a617ed793e4"
  },
  {
    "nome": "TUNICO CARA DE PITO",
    "telefone": "string",
    "cpf_cnpj": "string",
    "endereco": "string",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "3d577831-3c9d-4cfd-8b80-e028387d1fe8"
  },
  {
    "nome": "Vinicius",
    "telefone": "7181818",
    "cpf_cnpj": null,
    "endereco": null,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "514b854e-52c0-41ba-aabb-3cd6ffff27ef"
  },
  {
    "nome": "Zezinho esquilo",
    "telefone": "11976605555",
    "cpf_cnpj": "",
    "endereco": null,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "7009affd-f0db-435e-bce7-39bdfb9f0a90"
  }
]
```

---

## 37. `tests/test_fase3_contrato.py::test_leituras_pelo_backend[/veiculos/{emp}]`

- **Cenário:** F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/veiculos/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  {
    "placa": "AAA4654",
    "modelo": "CG 150 TITAN KS",
    "marca": "HONDA",
    "cor": "Preta",
    "km_atual": 54543,
    "ano": 2007,
    "chassi": "*****80871",
    "cliente_id": "3d577831-3c9d-4cfd-8b80-e028387d1fe8",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "ad03a018-a810-4619-957c-400bd475b2fc",
    "clientes": {
      "nome": "TUNICO CARA DE PITO",
      "telefone": "string"
    }
  },
  {
    "placa": "ABC1234",
    "modelo": "GOL",
    "marca": "VW",
    "cor": "azul bebe",
    "km_atual": 32220,
    "ano": 1990,
    "chassi": "123213123",
    "cliente_id": "a26df8a8-d7a6-4f81-a902-c26186ed18c2",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "4b8a0011-c4a1-444d-b059-093444c6ea8e",
    "clientes": {
      "nome": "Julya Lima Moreira",
      "telefone": "11978879957"
    }
  },
  {
    "placa": "CEA0A53",
    "modelo": "ESCORT 1.6I GL",
    "marca": "FORD",
    "cor": "PRATA",
    "km_atual": 4444,
    "ano": 1995,
    "chassi": "*****78716",
    "cliente_id": "3d577831-3c9d-4cfd-8b80-e028387d1fe8",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "d17d609f-bb2b-436d-9688-245957aa0f8c",
    "clientes": {
      "nome": "TUNICO CARA DE PITO",
      "telefone": "string"
    }
  },
  {
    "placa": "DOS2F42",
    "modelo": "FIAT PALIO",
    "marca": "PALIO",
    "cor": "VERMELHO",
    "km_atual": null,
    "ano": 2005,
    "chassi": null,
    "cliente_id": "a26df8a8-d7a6-4f81-a902-c26186ed18c2",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "3d97a9bc-16bf-4cb6-8a64-a92c4e89bbe7",
    "clientes": {
      "nome": "Julya Lima Moreira",
      "telefone": "11978879957"
    }
  },
  {
    "placa": "DOS2F43",
    "modelo": "PALIO WK ADVEN FLEX",
    "marca": "FIAT",
    "cor": "PRETA",
    "km_atual": null,
    "ano": 2004,
    "chassi": "*****11492",
    "cliente_id": "514b854e-52c0-41ba-aabb-3cd6ffff27ef",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "20f48243-a4b8-4fe3-8af8-98c25c83e978",
    "clientes": {
      "nome": "Vinicius",
      "telefone": "7181818"
    }
  },
  {
    "placa": "FKW2333",
    "modelo": "RENAULT DUSTER 20 D 4X2A",
    "marca": null,
    "cor": "PRETA",
    "km_atual": null,
    "ano": 2013,
    "chassi": "*****72768",
    "cliente_id": "c94fb84a-fa0f-479d-adb2-5a617ed793e4",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "e7bb6a18-657a-4eb1-a3f7-72a1c48aebc7",
    "clientes": {
      "nome": "Marli",
      "telefone": "21323123123"
    }
  },
  {
    "placa": "FUK2F55",
    "modelo": "HYUNDAI HB20 1.6M 1.6M",
    "marca": null,
    "cor": "Prata",
    "km_atual": null,
    "ano": 2012,
    "chassi": "*****26272",
    "cliente_id": "7009affd-f0db-435e-bce7-39bdfb9f0a90",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "20b90a51-ea1f-4150-a2d2-67b338cd0c33",
    "clientes": {
      "nome": "Zezinho esquilo",
      "telefone": "11976605555"
    }
  },
  {
    "placa
... (truncado)
```

---

## 38. `tests/test_fase3_contrato.py::test_leituras_pelo_backend[/estoque/{emp}]`

- **Cenário:** F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "itens": [
    {
      "nome": "Filtro de óleo TESTE",
      "categoria": "PECAS",
      "quantidade": 10,
      "custo": 20.0,
      "venda": 45.0,
      "minimo_alerta": 2,
      "codigo": null,
      "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
      "id": "cc5b7212-c001-459d-bff3-f29c9fc82807"
    },
    {
      "nome": "Óleo 5W30 TESTE",
      "categoria": "PECAS",
      "quantidade": 10,
      "custo": 30.0,
      "venda": 60.0,
      "minimo_alerta": 2,
      "codigo": null,
      "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
      "id": "acdf5b30-b603-4103-9e93-64afc1acf3e0"
    }
  ],
  "stats": {
    "total_itens": 2,
    "estoque_baixo": 0,
    "valor_total_custo": 500.0,
    "valor_total_venda": 1050.0
  }
}
```

---

## 39. `tests/test_fase3_contrato.py::test_leituras_pelo_backend[/os/?empresa_id={emp}]`

- **Cenário:** F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/os/?empresa_id=94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "items": [
    {
      "id": "9b45576f-8687-41de-bfff-f42cde85254e",
      "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
      "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
      "km_atual": null,
      "status": "ORCAMENTO",
      "data_abertura": "2026-11-09T18:17:28.766794+00:00",
      "total_geral": 0.0,
      "descricao_problema": "OS de teste (seed)",
      "clientes": {
        "nome": "Cliente Teste A",
        "telefone": "11999990001"
      },
      "veiculos": {
        "placa": "TSTA001",
        "modelo": "Gol 1.0"
      }
    },
    {
      "id": "59cde1dc-6433-48a9-9961-4165ca581ce6",
      "cliente_id": "3d577831-3c9d-4cfd-8b80-e028387d1fe8",
      "veiculo_id": "d17d609f-bb2b-436d-9688-245957aa0f8c",
      "km_atual": 4444,
      "status": "EXECUCAO",
      "data_abertura": "2026-06-24T00:52:19.191276+00:00",
      "total_geral": 0.0,
      "descricao_problema": "FFFFFF",
      "clientes": {
        "nome": "TUNICO CARA DE PITO",
        "telefone": "string"
      },
      "veiculos": {
        "placa": "CEA0A53",
        "modelo": "ESCORT 1.6I GL"
      }
    },
    {
      "id": "01f2765d-6b08-4414-869a-c31da263d1a9",
      "cliente_id": "c94fb84a-fa0f-479d-adb2-5a617ed793e4",
      "veiculo_id": "e7bb6a18-657a-4eb1-a3f7-72a1c48aebc7",
      "km_atual": null,
      "status": "ORCAMENTO",
      "data_abertura": "2026-06-23T02:53:46.044265+00:00",
      "total_geral": 0.0,
      "descricao_problema": "Tá zuado",
      "clientes": {
        "nome": "Marli",
        "telefone": "21323123123"
      },
      "veiculos": {
        "placa": "FKW2333",
        "modelo": "RENAULT DUSTER 20 D 4X2A"
      }
    },
    {
      "id": "a83b8adf-6fa4-43eb-a487-e64a368aa8e0",
      "cliente_id": "3d577831-3c9d-4cfd-8b80-e028387d1fe8",
      "veiculo_id": "ad03a018-a810-4619-957c-400bd475b2fc",
      "km_atual": 54543,
      "status": "PAGO",
      "data_abertura": "2026-04-23T02:30:46.640024+00:00",
      "total_geral": 46878.22,
      "descricao_problema": "",
      "clientes": {
        "nome": "TUNICO CARA DE PITO",
        "telefone": "string"
      },
      "veiculos": {
        "placa": "AAA4654",
        "modelo": "CG 150 TITAN KS"
      }
    }
  ],
  "total": 4,
  "skip": 0,
  "limit": 50
}
```

---

## 40. `tests/test_fase3_contrato.py::test_leituras_pelo_backend[/os/{emp}/{os}/imprimir]`

- **Cenário:** F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/9b45576f-8687-41de-bfff-f42cde85254e/imprimir`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "ordem": {
    "id": "9b45576f-8687-41de-bfff-f42cde85254e",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
    "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
    "mecanico_responsavel_id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
    "status": "ORCAMENTO",
    "total_pecas": 0,
    "total_mao_obra": 0,
    "total_terceirizados": null,
    "total_geral": 0,
    "lucro_estimado": 0,
    "forma_pagamento": null,
    "data_abertura": "2026-11-09T18:17:28.766794+00:00",
    "data_fechamento": null,
    "descricao_problema": "OS de teste (seed)",
    "km_atual": null,
    "motivo_exclusao": null,
    "updated_at": "2026-11-26T00:51:40.362752+00:00",
    "clientes": {
      "nome": "Cliente Teste A",
      "cpf_cnpj": null,
      "endereco": null,
      "telefone": "11999990001"
    },
    "veiculos": {
      "ano": null,
      "cor": null,
      "marca": "VW",
      "placa": "TSTA001",
      "chassi": null,
      "modelo": "Gol 1.0",
      "km_atual": 50100
    },
    "usuarios": {
      "nome": "Mecanico Teste A"
    }
  },
  "itens": [],
  "empresa": {
    "nome_fantasia": "Oficina do tião",
    "razao_social": "Joao servicos mecanicos",
    "cnpj": "45645654465611",
    "telefone": "11976608449",
    "email": "contato@joao.com",
    "endereco": "— CEP 06018-095"
  }
}
```

---

## 41. `tests/test_fase3_contrato.py::test_leituras_pelo_backend[/usuarios/{emp}]`

- **Cenário:** F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/usuarios/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  {
    "nome": "Atendente Teste A",
    "email": "atendente.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "ATENDENTE",
    "ativo": true,
    "salario_base": 0.0,
    "comissao_servico_pct": 0.0,
    "comissao_peca_pct": 0.0,
    "vale_transporte": 0.0,
    "vale_refeicao": 0.0,
    "paga_hora_extra": false,
    "valor_hora_extra": 0.0,
    "estrelas_media": 5.0,
    "total_avaliacoes": 0,
    "id": "8b89c905-3f58-4336-8b95-cba4d04e5f70",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
  },
  {
    "nome": "Dono Teste A",
    "email": "dono.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "DONO",
    "ativo": true,
    "salario_base": 0.0,
    "comissao_servico_pct": 0.0,
    "comissao_peca_pct": 0.0,
    "vale_transporte": 0.0,
    "vale_refeicao": 0.0,
    "paga_hora_extra": false,
    "valor_hora_extra": 0.0,
    "estrelas_media": 5.0,
    "total_avaliacoes": 0,
    "id": "f3b95dfc-237c-49b1-adf1-c1b1d048140f",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
  },
  {
    "nome": "Financeiro Teste A",
    "email": "financeiro.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "FINANCEIRO",
    "ativo": true,
    "salario_base": 0.0,
    "comissao_servico_pct": 0.0,
    "comissao_peca_pct": 0.0,
    "vale_transporte": 0.0,
    "vale_refeicao": 0.0,
    "paga_hora_extra": false,
    "valor_hora_extra": 0.0,
    "estrelas_media": 5.0,
    "total_avaliacoes": 0,
    "id": "bba76da7-c154-4be7-9826-5e1a677e6eba",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
  },
  {
    "nome": "joao",
    "email": "joao@oficina.com",
    "telefone": null,
    "cargo": "DONO",
    "ativo": true,
    "salario_base": 0.0,
    "comissao_servico_pct": 0.0,
    "comissao_peca_pct": 0.0,
    "vale_transporte": 0.0,
    "vale_refeicao": 0.0,
    "paga_hora_extra": false,
    "valor_hora_extra": 0.0,
    "estrelas_media": 5.0,
    "total_avaliacoes": 0,
    "id": "5895210e-13af-47c2-a08c-ba8030d1be25",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
  },
  {
    "nome": "Mecanico Teste A",
    "email": "mecanico.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "MECANICO",
    "ativo": true,
    "salario_base": 0.0,
    "comissao_servico_pct": 0.0,
    "comissao_peca_pct": 0.0,
    "vale_transporte": 0.0,
    "vale_refeicao": 0.0,
    "paga_hora_extra": false,
    "valor_hora_extra": 0.0,
    "estrelas_media": 5.0,
    "total_avaliacoes": 0,
    "id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
  },
  {
    "nome": "Vinici",
    "email": "camargo1.v@icloud.com",
    "telefone": null,
    "cargo": "MECANICO",
    "ativo": true,
    "salario_base": 0.0,
    "comissao_servico_pct": 0.0,
    "comissao_peca_pct": 0.0,
    "vale_transporte": 0.0,
    "vale_refeicao": 0.0,
    "paga_hora_extra": false,
    "valor_hora_extra": 0.0,
    "estrelas_media": 5.0,
    "total_avaliacoes": 0,
    "id": "b84b36ee-4d8c-40b5-86a2
... (truncado)
```

---

## 42. `tests/test_fase3_contrato.py::test_leituras_pelo_backend[/empresas/?empresa_id={emp}]`

- **Cenário:** F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/empresas/?empresa_id=94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  {
    "id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "nome_fantasia": "Oficina do tião",
    "razao_social": "Joao servicos mecanicos",
    "cnpj": "45645654465611",
    "email": "contato@joao.com",
    "telefone": "11976608449",
    "endereco": "— CEP 06018-095",
    "ativo": true,
    "empresa_teste": true,
    "created_at": "2026-04-23T01:50:24.218414+00:00",
    "updated_at": "2026-11-26T00:52:12.468361+00:00",
    "plano": "profissional"
  }
]
```

---

## 43. `tests/test_fase3_contrato.py::test_leituras_pelo_backend[/empresas/{emp}/configuracoes]`

- **Cenário:** F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/empresas/94334e9f-629c-4c65-92f8-e26274ba3973/configuracoes`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "id": "6ac05b1e-9377-4526-ab70-6acb7de06a20",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "logo_b64": "data:image/png;base64,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
... (truncado)
```

---

## 44. `tests/test_fase3_contrato.py::test_leituras_pelo_backend[/equipe/escalas/{emp}]`

- **Cenário:** F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/equipe/escalas/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  {
    "usuario_id": "7051b94a-aa8e-4e95-bd7e-13c77a83b782",
    "tipo": "FOLGA",
    "data_inicio": "2026-12-24",
    "data_fim": "2026-12-25",
    "observacoes": null,
    "id": "994390bd-ec2b-474d-8e6c-8c183bbdddd5",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "usuario_nome": "Mecanico Teste B",
    "created_at": "2026-11-16T22:14:45.828890Z"
  }
]
```

---

## 45. `tests/test_fase3_contrato.py::test_leituras_pelo_backend[/equipe/pontos/{emp}]`

- **Cenário:** F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/equipe/pontos/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[]
```

---

## 46. `tests/test_fase3_contrato.py::test_leituras_pelo_backend[/equipe/avaliacoes/{emp}]`

- **Cenário:** F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/equipe/avaliacoes/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[]
```

---

## 47. `tests/test_fase3_contrato.py::test_leituras_pelo_backend[/transacoes-financeiras/{emp}]`

- **Cenário:** F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/transacoes-financeiras/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "transacoes": [],
  "resumo": {
    "total_despesas_pagas": 0.0,
    "total_despesas_pendentes": 0.0,
    "total_receitas_recebidas": 0.0,
    "total_receitas_pendentes": 0.0,
    "saldo_liquido_periodo": 0.0
  }
}
```

---

## 48. `tests/test_fase3_contrato.py::test_leituras_pelo_backend[/financeiro/{emp}]`

- **Cenário:** F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/financeiro/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "faturamento_pago": 46878.22,
  "faturamento_projetado": 0.0,
  "lucro_realizado": 46756.53,
  "ticket_medio": 46878.22,
  "historico_6_meses": [
    {
      "mes_ano": "06/2026",
      "faturamento": 0.0,
      "lucro": 0.0
    },
    {
      "mes_ano": "07/2026",
      "faturamento": 0.0,
      "lucro": 0.0
    },
    {
      "mes_ano": "08/2026",
      "faturamento": 0.0,
      "lucro": 0.0
    },
    {
      "mes_ano": "09/2026",
      "faturamento": 0.0,
      "lucro": 0.0
    },
    {
      "mes_ano": "10/2026",
      "faturamento": 0.0,
      "lucro": 0.0
    },
    {
      "mes_ano": "11/2026",
      "faturamento": 46878.22,
      "lucro": 46756.53
    }
  ]
}
```

---

## 49. `tests/test_fase3_contrato.py::test_leituras_pelo_backend[/financeiro/inteligencia/{emp}]`

- **Cenário:** F3-C1 — Toda leitura que o front fazia direto no Supabase responde 200 pelo backend com o formato esperado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/financeiro/inteligencia/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "top_10_clientes": [
    {
      "nome": "TUNICO CARA DE PITO",
      "lucro": 46756.53,
      "faturamento": 46878.22,
      "qtd_os": 1
    }
  ],
  "piores_10_clientes": [
    {
      "nome": "TUNICO CARA DE PITO",
      "lucro": 46756.53,
      "faturamento": 46878.22,
      "qtd_os": 1
    }
  ],
  "produtividade_mecanicos": [
    {
      "nome": "joao",
      "lucro_gerado": 46756.53,
      "faturamento_gerado": 46878.22,
      "qtd_os": 1
    }
  ],
  "metodos_pagamento": [
    {
      "forma": "Cartão de Débito",
      "qtd": 1,
      "valor_total": 46878.22
    }
  ],
  "rentabilidade_marcas": [
    {
      "marca": "HONDA",
      "lucro": 46756.53,
      "faturamento": 46878.22,
      "qtd_os": 1
    }
  ],
  "origem_faturamento": {
    "pecas": 444.75,
    "mao_obra": 45645.47
  },
  "lead_time_medio_horas": 4843.1,
  "taxa_conversao_orcamentos": 50.0
}
```

---

## 50. `tests/test_fase3_contrato.py::test_listagem_de_os_filtros_e_busca`

- **Cenário:** F3-C2 — Histórico de OS por veículo/cliente e busca por modelo e por placa sem hífen
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/os/?empresa_id=94334e9f-629c-4c65-92f8-e26274ba3973&veiculo_id=522784a7-2f0f-492a-9cdd-ffa17f71cf53&limit=500`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "items": [
    {
      "id": "9b45576f-8687-41de-bfff-f42cde85254e",
      "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
      "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
      "km_atual": null,
      "status": "ORCAMENTO",
      "data_abertura": "2026-11-09T18:17:28.766794+00:00",
      "total_geral": 0.0,
      "descricao_problema": "OS de teste (seed)",
      "clientes": {
        "nome": "Cliente Teste A",
        "telefone": "11999990001"
      },
      "veiculos": {
        "placa": "TSTA001",
        "modelo": "Gol 1.0"
      }
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 500
}
```

### Chamada 2

**Request:** `GET http://testserver/api/v1/os/?empresa_id=94334e9f-629c-4c65-92f8-e26274ba3973&cliente_id=44e46577-443d-4c98-90d2-cd79e0123492`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "items": [
    {
      "id": "9b45576f-8687-41de-bfff-f42cde85254e",
      "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
      "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
      "km_atual": null,
      "status": "ORCAMENTO",
      "data_abertura": "2026-11-09T18:17:28.766794+00:00",
      "total_geral": 0.0,
      "descricao_problema": "OS de teste (seed)",
      "clientes": {
        "nome": "Cliente Teste A",
        "telefone": "11999990001"
      },
      "veiculos": {
        "placa": "TSTA001",
        "modelo": "Gol 1.0"
      }
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

### Chamada 3

**Request:** `GET http://testserver/api/v1/os/?empresa_id=94334e9f-629c-4c65-92f8-e26274ba3973&veiculo_id=2be58fc9-98b8-462b-9234-056032d52053`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "items": [],
  "total": 0,
  "skip": 0,
  "limit": 50
}
```

### Chamada 4

**Request:** `GET http://testserver/api/v1/os/?empresa_id=94334e9f-629c-4c65-92f8-e26274ba3973&search=gol`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "items": [
    {
      "id": "9b45576f-8687-41de-bfff-f42cde85254e",
      "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
      "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
      "km_atual": null,
      "status": "ORCAMENTO",
      "data_abertura": "2026-11-09T18:17:28.766794+00:00",
      "total_geral": 0.0,
      "descricao_problema": "OS de teste (seed)",
      "clientes": {
        "nome": "Cliente Teste A",
        "telefone": "11999990001"
      },
      "veiculos": {
        "placa": "TSTA001",
        "modelo": "Gol 1.0"
      }
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

### Chamada 5

**Request:** `GET http://testserver/api/v1/os/?empresa_id=94334e9f-629c-4c65-92f8-e26274ba3973&search=tsta001`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "items": [
    {
      "id": "9b45576f-8687-41de-bfff-f42cde85254e",
      "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
      "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
      "km_atual": null,
      "status": "ORCAMENTO",
      "data_abertura": "2026-11-09T18:17:28.766794+00:00",
      "total_geral": 0.0,
      "descricao_problema": "OS de teste (seed)",
      "clientes": {
        "nome": "Cliente Teste A",
        "telefone": "11999990001"
      },
      "veiculos": {
        "placa": "TSTA001",
        "modelo": "Gol 1.0"
      }
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

### Chamada 6

**Request:** `GET http://testserver/api/v1/os/?empresa_id=94334e9f-629c-4c65-92f8-e26274ba3973&search=TST-A001`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "items": [
    {
      "id": "9b45576f-8687-41de-bfff-f42cde85254e",
      "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
      "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
      "km_atual": null,
      "status": "ORCAMENTO",
      "data_abertura": "2026-11-09T18:17:28.766794+00:00",
      "total_geral": 0.0,
      "descricao_problema": "OS de teste (seed)",
      "clientes": {
        "nome": "Cliente Teste A",
        "telefone": "11999990001"
      },
      "veiculos": {
        "placa": "TSTA001",
        "modelo": "Gol 1.0"
      }
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

---

## 51. `tests/test_fase3_contrato.py::test_itens_da_os_e_estoque`

- **Cenário:** F3-W1 — Itens da OS: adicionar em lote baixa o estoque, alterar ajusta, remover estorna; totais da OS recalculados
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/9b45576f-8687-41de-bfff-f42cde85254e/itens/lote`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
[
  {
    "estoque_id": "cc5b7212-c001-459d-bff3-f29c9fc82807",
    "tipo": "PECA",
    "nome_item": "Filtro F3-W1",
    "quantidade": 2,
    "custo_unitario": 20,
    "venda_unitario": 45
  },
  {
    "tipo": "MAO_OBRA",
    "nome_item": "Mão de obra F3-W1",
    "quantidade": 1,
    "custo_unitario": 0,
    "venda_unitario": 100
  }
]
```

**Response:** `200`

```json
[
  {
    "id": "e5957bb4-b8fb-4a37-b6dd-9726a11bd671",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "os_id": "9b45576f-8687-41de-bfff-f42cde85254e",
    "estoque_id": "cc5b7212-c001-459d-bff3-f29c9fc82807",
    "tipo": "PECA",
    "nome_item": "Filtro F3-W1",
    "quantidade": 2,
    "custo_unitario": 20.0,
    "venda_unitario": 45.0,
    "criado_em": "2026-11-26T00:57:14.387428+00:00"
  },
  {
    "id": "bcbdd57c-765a-4536-bd67-6c0a906b08cd",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "os_id": "9b45576f-8687-41de-bfff-f42cde85254e",
    "estoque_id": null,
    "tipo": "MAO_OBRA",
    "nome_item": "Mão de obra F3-W1",
    "quantidade": 1,
    "custo_unitario": 0.0,
    "venda_unitario": 100.0,
    "criado_em": "2026-11-26T00:57:14.387428+00:00"
  }
]
```

### Chamada 2

**Request:** `PUT http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/9b45576f-8687-41de-bfff-f42cde85254e/itens/e5957bb4-b8fb-4a37-b6dd-9726a11bd671`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "quantidade": 3
}
```

**Response:** `200`

```json
{
  "id": "e5957bb4-b8fb-4a37-b6dd-9726a11bd671",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "os_id": "9b45576f-8687-41de-bfff-f42cde85254e",
  "estoque_id": "cc5b7212-c001-459d-bff3-f29c9fc82807",
  "tipo": "PECA",
  "nome_item": "Filtro F3-W1",
  "quantidade": 3,
  "custo_unitario": 20.0,
  "venda_unitario": 45.0,
  "criado_em": "2026-11-26T00:57:14.387428+00:00"
}
```

### Chamada 3

**Request:** `DELETE http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/9b45576f-8687-41de-bfff-f42cde85254e/itens/e5957bb4-b8fb-4a37-b6dd-9726a11bd671`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "status": "sucesso",
  "detail": "Item removido e estornado (se aplicável)."
}
```

### Chamada 4

**Request:** `DELETE http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/9b45576f-8687-41de-bfff-f42cde85254e/itens/bcbdd57c-765a-4536-bd67-6c0a906b08cd`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "status": "sucesso",
  "detail": "Item removido e estornado (se aplicável)."
}
```

---

## 52. `tests/test_fase3_contrato.py::test_item_legado_sem_empresa_id`

- **Cenário:** F3-W1b — Item antigo do legado (sem empresa_id) pode ser alterado/removido pela própria empresa; a outra recebe 403/404
- **Resultado:** PULADO

```
('C:\\Projects\\autotec\\backend-oficina-main\\tests\\test_fase3_contrato.py', 107, 'Skipped: empresa_id NOT NULL na base nova')
```

_Sem chamadas HTTP (teste de função/banco)._

---

## 53. `tests/test_fase3_contrato.py::test_abrir_e_atualizar_os`

- **Cenário:** F3-W2 — Abrir OS: reaproveita orçamento aberto do veículo; veículo novo cria OS; status e fechamento atualizam
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/os/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
  "mecanico_responsavel_id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
  "descricao_problema": "F3-W2",
  "km_atual": 50100,
  "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53"
}
```

**Response:** `200`

```json
{
  "id": "9b45576f-8687-41de-bfff-f42cde85254e",
  "data_abertura": "2026-11-09T18:17:28.766794+00:00",
  "status": "ORCAMENTO",
  "reaproveitada": true
}
```

### Chamada 2

**Request:** `POST http://testserver/api/v1/os/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
  "mecanico_responsavel_id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
  "descricao_problema": "F3-W2",
  "km_atual": 50100,
  "veiculo_id": "9b1ff3f5-53fc-44d5-964e-b4934907c982"
}
```

**Response:** `200`

```json
{
  "id": "1d3b4de2-9ac2-43ee-bcdd-e98dc2a89223",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
  "veiculo_id": "9b1ff3f5-53fc-44d5-964e-b4934907c982",
  "mecanico_responsavel_id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
  "status": "ORCAMENTO",
  "total_pecas": 0.0,
  "total_mao_obra": 0.0,
  "total_terceirizados": null,
  "total_geral": 0.0,
  "lucro_estimado": 0.0,
  "forma_pagamento": null,
  "data_abertura": "2026-11-26T00:57:21.648668+00:00",
  "data_fechamento": null,
  "descricao_problema": "F3-W2",
  "km_atual": 50100,
  "motivo_exclusao": null,
  "updated_at": "2026-11-26T00:57:21.648668+00:00"
}
```

### Chamada 3

**Request:** `PUT http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/1d3b4de2-9ac2-43ee-bcdd-e98dc2a89223`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "status": "FINALIZADO",
  "forma_pagamento": "PIX"
}
```

**Response:** `200`

```json
{
  "id": "1d3b4de2-9ac2-43ee-bcdd-e98dc2a89223",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
  "veiculo_id": "9b1ff3f5-53fc-44d5-964e-b4934907c982",
  "mecanico_responsavel_id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
  "status": "FINALIZADO",
  "total_pecas": 0.0,
  "total_mao_obra": 0.0,
  "total_terceirizados": null,
  "total_geral": 0.0,
  "lucro_estimado": 0.0,
  "forma_pagamento": "PIX",
  "data_abertura": "2026-11-26T00:57:21.648668+00:00",
  "data_fechamento": "2026-11-26T00:54:36.942783+00:00",
  "descricao_problema": "F3-W2",
  "km_atual": 50100,
  "motivo_exclusao": null,
  "updated_at": "2026-11-26T00:57:22.396+00:00"
}
```

### Chamada 4

**Request:** `DELETE http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/1d3b4de2-9ac2-43ee-bcdd-e98dc2a89223?motivo_exclusao=teste%20F3-W2`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "status": "sucesso",
  "detail": "OS cancelada, estoque restaurado e log gerado."
}
```

---

## 54. `tests/test_fase3_contrato.py::test_crud_cliente_veiculo_estoque`

- **Cenário:** F3-W3 — Cliente, veículo e item de estoque: criar, alterar, ajustar saldo e apagar (corpos iguais aos das telas)
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/clientes/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "nome": "Cliente F3-W3",
  "telefone": "11900000033",
  "cpf_cnpj": null,
  "endereco": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
}
```

**Response:** `200`

```json
{
  "nome": "Cliente F3-W3",
  "telefone": "11900000033",
  "cpf_cnpj": null,
  "endereco": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "f5ed45d4-82f0-4f4a-8a10-79a29f35e4bf"
}
```

### Chamada 2

**Request:** `PUT http://testserver/api/v1/clientes/94334e9f-629c-4c65-92f8-e26274ba3973/f5ed45d4-82f0-4f4a-8a10-79a29f35e4bf`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "nome": "Cliente F3-W3 editado",
  "cpf_cnpj": null
}
```

**Response:** `200`

```json
{
  "nome": "Cliente F3-W3 editado",
  "telefone": "11900000033",
  "cpf_cnpj": null,
  "endereco": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "f5ed45d4-82f0-4f4a-8a10-79a29f35e4bf"
}
```

### Chamada 3

**Request:** `POST http://testserver/api/v1/veiculos/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "placa": "TSTW3Z9",
  "modelo": "Fox",
  "marca": "VW",
  "cor": null,
  "km_atual": 1000,
  "ano": null,
  "chassi": null,
  "cliente_id": "f5ed45d4-82f0-4f4a-8a10-79a29f35e4bf",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
}
```

**Response:** `200`

```json
{
  "placa": "TSTW3Z9",
  "modelo": "Fox",
  "marca": "VW",
  "cor": null,
  "km_atual": 1000,
  "ano": null,
  "chassi": null,
  "cliente_id": "f5ed45d4-82f0-4f4a-8a10-79a29f35e4bf",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "0ab9ff25-a867-483e-a04e-9c89a10d3aaf",
  "clientes": null
}
```

### Chamada 4

**Request:** `PUT http://testserver/api/v1/veiculos/94334e9f-629c-4c65-92f8-e26274ba3973/0ab9ff25-a867-483e-a04e-9c89a10d3aaf`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "km_atual": 1200
}
```

**Response:** `200`

```json
{
  "placa": "TSTW3Z9",
  "modelo": "Fox",
  "marca": "VW",
  "cor": null,
  "km_atual": 1200,
  "ano": null,
  "chassi": null,
  "cliente_id": "f5ed45d4-82f0-4f4a-8a10-79a29f35e4bf",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "0ab9ff25-a867-483e-a04e-9c89a10d3aaf",
  "clientes": null
}
```

### Chamada 5

**Request:** `POST http://testserver/api/v1/estoque/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "nome": "Item F3-W3",
  "categoria": "PECAS",
  "quantidade": 5,
  "custo": 10,
  "venda": 20,
  "minimo_alerta": 2,
  "codigo": "F3W3",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
}
```

**Response:** `200`

```json
{
  "nome": "Item F3-W3",
  "categoria": "PECAS",
  "quantidade": 5,
  "custo": 10.0,
  "venda": 20.0,
  "minimo_alerta": 2,
  "codigo": "F3W3",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "4b869b27-9076-48ad-8720-120d97f3e765"
}
```

### Chamada 6

**Request:** `PUT http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/4b869b27-9076-48ad-8720-120d97f3e765`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "venda": 25,
  "codigo": null
}
```

**Response:** `200`

```json
{
  "nome": "Item F3-W3",
  "categoria": "PECAS",
  "quantidade": 5,
  "custo": 10.0,
  "venda": 25.0,
  "minimo_alerta": 2,
  "codigo": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "4b869b27-9076-48ad-8720-120d97f3e765"
}
```

### Chamada 7

**Request:** `PATCH http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/4b869b27-9076-48ad-8720-120d97f3e765/ajustar`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "tipo": "entrada",
  "quantidade": 3
}
```

**Response:** `200`

```json
{
  "nome": "Item F3-W3",
  "categoria": "PECAS",
  "quantidade": 8,
  "custo": 10.0,
  "venda": 25.0,
  "minimo_alerta": 2,
  "codigo": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "4b869b27-9076-48ad-8720-120d97f3e765"
}
```

### Chamada 8

**Request:** `PATCH http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/4b869b27-9076-48ad-8720-120d97f3e765/ajustar`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "tipo": "saida",
  "quantidade": 100
}
```

**Response:** `400`

```json
{
  "detail": "Estoque insuficiente. Saldo atual: 8"
}
```

### Chamada 9

**Request:** `PATCH http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/4b869b27-9076-48ad-8720-120d97f3e765/ajustar`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "tipo": "saida",
  "quantidade": 8
}
```

**Response:** `200`

```json
{
  "nome": "Item F3-W3",
  "categoria": "PECAS",
  "quantidade": 0,
  "custo": 10.0,
  "venda": 25.0,
  "minimo_alerta": 2,
  "codigo": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "4b869b27-9076-48ad-8720-120d97f3e765"
}
```

### Chamada 10

**Request:** `DELETE http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/4b869b27-9076-48ad-8720-120d97f3e765`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "status": "sucesso",
  "detail": "Item varrido do mapa logístico."
}
```

### Chamada 11

**Request:** `DELETE http://testserver/api/v1/veiculos/94334e9f-629c-4c65-92f8-e26274ba3973/0ab9ff25-a867-483e-a04e-9c89a10d3aaf`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "status": "sucesso",
  "detail": "Veículo removido com sucesso."
}
```

### Chamada 12

**Request:** `DELETE http://testserver/api/v1/clientes/94334e9f-629c-4c65-92f8-e26274ba3973/f5ed45d4-82f0-4f4a-8a10-79a29f35e4bf`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "status": "sucesso",
  "detail": "Cliente removido e log gerado."
}
```

---

## 55. `tests/test_fase3_contrato.py::test_crud_transacoes`

- **Cenário:** F3-W4 — Contas a pagar/receber: criar, alterar, liquidar e apagar; erro do banco aparece como erro (nada é engolido)
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/transacoes-financeiras/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "tipo": "DESPESA",
  "descricao": "F3-W4",
  "categoria": "OUTROS",
  "valor": 123.45,
  "data_vencimento": "2026-12-31",
  "status": "PENDENTE",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
}
```

**Response:** `200`

```json
{
  "tipo": "DESPESA",
  "descricao": "F3-W4",
  "categoria": "OUTROS",
  "valor": 123.45,
  "data_vencimento": "2026-12-31",
  "data_liquidacao": null,
  "status": "PENDENTE",
  "forma_pagamento": null,
  "observacoes": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "c3fc9f2d-cd19-49cc-a2a1-97fe230130f8",
  "created_at": "2026-11-26T00:57:32.634426Z",
  "updated_at": "2026-11-26T00:57:32.634426Z"
}
```

### Chamada 2

**Request:** `PUT http://testserver/api/v1/transacoes-financeiras/94334e9f-629c-4c65-92f8-e26274ba3973/c3fc9f2d-cd19-49cc-a2a1-97fe230130f8`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "valor": 200
}
```

**Response:** `200`

```json
{
  "tipo": "DESPESA",
  "descricao": "F3-W4",
  "categoria": "OUTROS",
  "valor": 200.0,
  "data_vencimento": "2026-12-31",
  "data_liquidacao": null,
  "status": "PENDENTE",
  "forma_pagamento": null,
  "observacoes": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "c3fc9f2d-cd19-49cc-a2a1-97fe230130f8",
  "created_at": "2026-11-26T00:57:32.634426Z",
  "updated_at": "2026-11-26T00:57:33.262220Z"
}
```

### Chamada 3

**Request:** `PATCH http://testserver/api/v1/transacoes-financeiras/94334e9f-629c-4c65-92f8-e26274ba3973/c3fc9f2d-cd19-49cc-a2a1-97fe230130f8/liquidar`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "data_liquidacao": "2026-11-09",
  "forma_pagamento": "PIX"
}
```

**Response:** `200`

```json
{
  "tipo": "DESPESA",
  "descricao": "F3-W4",
  "categoria": "OUTROS",
  "valor": 200.0,
  "data_vencimento": "2026-12-31",
  "data_liquidacao": "2026-11-09",
  "status": "LIQUIDADO",
  "forma_pagamento": "PIX",
  "observacoes": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "c3fc9f2d-cd19-49cc-a2a1-97fe230130f8",
  "created_at": "2026-11-26T00:57:32.634426Z",
  "updated_at": "2026-11-26T00:57:33.946904Z"
}
```

### Chamada 4

**Request:** `PATCH http://testserver/api/v1/transacoes-financeiras/94334e9f-629c-4c65-92f8-e26274ba3973/c3fc9f2d-cd19-49cc-a2a1-97fe230130f8/liquidar`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "data_liquidacao": "2026-11-09"
}
```

**Response:** `200`

```json
{
  "tipo": "DESPESA",
  "descricao": "F3-W4",
  "categoria": "OUTROS",
  "valor": 200.0,
  "data_vencimento": "2026-12-31",
  "data_liquidacao": "2026-11-09",
  "status": "LIQUIDADO",
  "forma_pagamento": "PIX",
  "observacoes": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "c3fc9f2d-cd19-49cc-a2a1-97fe230130f8",
  "created_at": "2026-11-26T00:57:32.634426Z",
  "updated_at": "2026-11-26T00:57:34.814226Z"
}
```

### Chamada 5

**Request:** `POST http://testserver/api/v1/transacoes-financeiras/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "tipo": "DESPESA",
  "descricao": "x",
  "categoria": "OUTROS",
  "valor": -1,
  "data_vencimento": "2026-12-31",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973"
}
```

**Response:** `422`

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "valor"
      ],
      "msg": "Valor: precisa ser maior que 0.",
      "type": "greater_than"
    }
  ]
}
```

### Chamada 6

**Request:** `DELETE http://testserver/api/v1/transacoes-financeiras/94334e9f-629c-4c65-92f8-e26274ba3973/c3fc9f2d-cd19-49cc-a2a1-97fe230130f8`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "status": "sucesso",
  "detail": "Transação financeira removida com sucesso."
}
```

---

## 56. `tests/test_fase3_contrato.py::test_escalas_e_ponto`

- **Cenário:** F3-W5 — Escalas e ponto com os corpos das telas: gravados no banco e listados pelo backend
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/equipe/escalas/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "usuario_id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
  "usuario_nome": "Mecanico Teste A",
  "tipo": "FOLGA",
  "data_inicio": "2026-12-24",
  "data_fim": "2026-12-25",
  "observacoes": null
}
```

**Response:** `200`

```json
{
  "usuario_id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
  "tipo": "FOLGA",
  "data_inicio": "2026-12-24",
  "data_fim": "2026-12-25",
  "observacoes": null,
  "id": "c9a130e7-4f50-42ca-8255-5b4d80fa1e8a",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "usuario_nome": "Mecanico Teste A",
  "created_at": "2026-11-26T00:57:36.590123Z"
}
```

### Chamada 2

**Request:** `GET http://testserver/api/v1/equipe/escalas/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  {
    "usuario_id": "7051b94a-aa8e-4e95-bd7e-13c77a83b782",
    "tipo": "FOLGA",
    "data_inicio": "2026-12-24",
    "data_fim": "2026-12-25",
    "observacoes": null,
    "id": "994390bd-ec2b-474d-8e6c-8c183bbdddd5",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "usuario_nome": "Mecanico Teste B",
    "created_at": "2026-11-16T22:14:45.828890Z"
  },
  {
    "usuario_id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
    "tipo": "FOLGA",
    "data_inicio": "2026-12-24",
    "data_fim": "2026-12-25",
    "observacoes": null,
    "id": "c9a130e7-4f50-42ca-8255-5b4d80fa1e8a",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "usuario_nome": "Mecanico Teste A",
    "created_at": "2026-11-26T00:57:36.590123Z"
  }
]
```

### Chamada 3

**Request:** `POST http://testserver/api/v1/equipe/pontos/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "tipo": "ENTRADA",
  "latitude": -23.5,
  "longitude": -46.6
}
```

**Response:** `200`

```json
{
  "id": "648e7918-ee0c-49a8-938f-d172d51ea429",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "usuario_id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
  "usuario_nome": "Mecanico Teste A",
  "data": "2026-11-25",
  "hora": "21:54:52",
  "tipo": "ENTRADA",
  "latitude": -23.5,
  "longitude": -46.6,
  "dentro_raio": true,
  "distancia_metros": 0.0,
  "created_at": "2026-11-26T00:57:37.941272Z"
}
```

### Chamada 4

**Request:** `GET http://testserver/api/v1/equipe/pontos/94334e9f-629c-4c65-92f8-e26274ba3973?data=2026-11-25`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  {
    "id": "648e7918-ee0c-49a8-938f-d172d51ea429",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "usuario_id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
    "usuario_nome": "Mecanico Teste A",
    "data": "2026-11-25",
    "hora": "21:54:52",
    "tipo": "ENTRADA",
    "latitude": -23.5,
    "longitude": -46.6,
    "dentro_raio": true,
    "distancia_metros": 0.0,
    "created_at": "2026-11-26T00:57:37.941272Z"
  }
]
```

### Chamada 5

**Request:** `DELETE http://testserver/api/v1/equipe/escalas/94334e9f-629c-4c65-92f8-e26274ba3973/c9a130e7-4f50-42ca-8255-5b4d80fa1e8a`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "status": "sucesso",
  "detail": "Escala ou folga removida."
}
```

---

## 57. `tests/test_fase3_contrato.py::test_configuracoes_da_oficina`

- **Cenário:** F3-W6 — Configurações da oficina e parâmetros da folha (antes só no localStorage) gravam e voltam do servidor
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/empresas/94334e9f-629c-4c65-92f8-e26274ba3973/configuracoes`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "id": "6ac05b1e-9377-4526-ab70-6acb7de06a20",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "logo_b64": "data:image/png;base64,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
... (truncado)
```

### Chamada 2

**Request:** `PUT http://testserver/api/v1/empresas/94334e9f-629c-4c65-92f8-e26274ba3973/configuracoes`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "whatsapp": "11988887777",
  "chave_pix": "pix@teste.example.com",
  "inscricao_estadual": "123",
  "latitude_gps": -23.55,
  "longitude_gps": -46.63,
  "raio_gps_metros": 150,
  "dia_pagamento_folha": 7,
  "dia_adiantamento_folha": 22,
  "comissao_global_servico_pct": 12.5,
  "comissao_global_peca_pct": 4,
  "paga_hora_extra_padrao": false,
  "valor_hora_extra_padrao": 30,
  "cor_primaria": "#112233",
  "cor_secundaria": "#445566"
}
```

**Response:** `200`

```json
{
  "id": "6ac05b1e-9377-4526-ab70-6acb7de06a20",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "logo_b64": "data:image/png;base64,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
... (truncado)
```

### Chamada 3

**Request:** `PUT http://testserver/api/v1/empresas/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "nome_fantasia": "Oficina do tião",
  "telefone": "1133334444",
  "endereco": "Rua Teste, 1"
}
```

**Response:** `200`

```json
{
  "id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "nome_fantasia": "Oficina do tião",
  "razao_social": "Joao servicos mecanicos",
  "cnpj": "45645654465611",
  "email": "contato@joao.com",
  "telefone": "1133334444",
  "endereco": "Rua Teste, 1",
  "ativo": true,
  "empresa_teste": true,
  "created_at": "2026-04-23T01:50:24.218414+00:00",
  "updated_at": "2026-11-26T00:57:41.303195+00:00",
  "plano": "profissional"
}
```

### Chamada 4

**Request:** `GET http://testserver/api/v1/empresas/94334e9f-629c-4c65-92f8-e26274ba3973/configuracoes`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "id": "6ac05b1e-9377-4526-ab70-6acb7de06a20",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "logo_b64": "data:image/png;base64,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
... (truncado)
```

### Chamada 5

**Request:** `PUT http://testserver/api/v1/empresas/94334e9f-629c-4c65-92f8-e26274ba3973/configuracoes`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "chave_pix": "x"
}
```

**Response:** `403`

```json
{
  "detail": "Acesso negado para o seu perfil."
}
```

### Chamada 6

**Request:** `PUT http://testserver/api/v1/empresas/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "email": ""
}
```

**Response:** `422`

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "email"
      ],
      "msg": "E-mail: e-mail inválido.",
      "type": "value_error"
    }
  ]
}
```

---

## 58. `tests/test_fase3_contrato.py::test_clientes_ordenados_por_nome`

- **Cenário:** F3-C3 — Lista de clientes vem ordenada por nome (a tela dependia disso)
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/clientes/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  {
    "nome": "AA F3-C3",
    "telefone": "11900000092",
    "cpf_cnpj": null,
    "endereco": null,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "43da1bdb-5a09-47d4-baca-c40d4e5bbb5f"
  },
  {
    "nome": "Cliente Teste A",
    "telefone": "11999990001",
    "cpf_cnpj": null,
    "endereco": null,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "44e46577-443d-4c98-90d2-cd79e0123492"
  },
  {
    "nome": "Julya Lima Moreira",
    "telefone": "11978879957",
    "cpf_cnpj": null,
    "endereco": "Rua João de Sá, 240",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "a26df8a8-d7a6-4f81-a902-c26186ed18c2"
  },
  {
    "nome": "Marli",
    "telefone": "21323123123",
    "cpf_cnpj": "",
    "endereco": null,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "c94fb84a-fa0f-479d-adb2-5a617ed793e4"
  },
  {
    "nome": "TUNICO CARA DE PITO",
    "telefone": "string",
    "cpf_cnpj": "string",
    "endereco": "string",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "3d577831-3c9d-4cfd-8b80-e028387d1fe8"
  },
  {
    "nome": "Vinicius",
    "telefone": "7181818",
    "cpf_cnpj": null,
    "endereco": null,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "514b854e-52c0-41ba-aabb-3cd6ffff27ef"
  },
  {
    "nome": "Zezinho esquilo",
    "telefone": "11976605555",
    "cpf_cnpj": "",
    "endereco": null,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "7009affd-f0db-435e-bce7-39bdfb9f0a90"
  },
  {
    "nome": "ZZ F3-C3",
    "telefone": "11900000091",
    "cpf_cnpj": null,
    "endereco": null,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "d7f30b54-b140-46a7-a34f-2d6a5650ea56"
  }
]
```

---

## 59. `tests/test_fase3_contrato.py::test_onboarding_de_conta_nova`

- **Cenário:** F3-F4 — Cadastro novo (sem perfil): /me nega, onboarding cria 1 oficina DONO só uma vez e isolada das demais
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/usuarios/me`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Usuário inativo ou sem perfil vinculado."
}
```

### Chamada 2

**Request:** `POST http://testserver/api/v1/usuarios/onboarding`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "nome": "Teste F4",
  "email": "f3f4.74422001@homolog-autotec.example.com",
  "telefone": null,
  "cargo": "DONO",
  "ativo": true,
  "salario_base": 0.0,
  "comissao_servico_pct": 0.0,
  "comissao_peca_pct": 0.0,
  "vale_transporte": 0.0,
  "vale_refeicao": 0.0,
  "paga_hora_extra": false,
  "valor_hora_extra": 0.0,
  "estrelas_media": 5.0,
  "total_avaliacoes": 0,
  "id": "9583c78c-2bb9-4ac4-8b3e-0c358e0d101c",
  "empresa_id": "240bcc4c-d0db-4e35-bc29-11a7050f94b4"
}
```

### Chamada 3

**Request:** `POST http://testserver/api/v1/usuarios/onboarding`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "nome": "Teste F4",
  "email": "f3f4.74422001@homolog-autotec.example.com",
  "telefone": null,
  "cargo": "DONO",
  "ativo": true,
  "salario_base": 0.0,
  "comissao_servico_pct": 0.0,
  "comissao_peca_pct": 0.0,
  "vale_transporte": 0.0,
  "vale_refeicao": 0.0,
  "paga_hora_extra": false,
  "valor_hora_extra": 0.0,
  "estrelas_media": 5.0,
  "total_avaliacoes": 0,
  "id": "9583c78c-2bb9-4ac4-8b3e-0c358e0d101c",
  "empresa_id": "240bcc4c-d0db-4e35-bc29-11a7050f94b4"
}
```

### Chamada 4

**Request:** `GET http://testserver/api/v1/usuarios/me`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "nome": "Teste F4",
  "email": "f3f4.74422001@homolog-autotec.example.com",
  "telefone": null,
  "cargo": "DONO",
  "ativo": true,
  "salario_base": 0.0,
  "comissao_servico_pct": 0.0,
  "comissao_peca_pct": 0.0,
  "vale_transporte": 0.0,
  "vale_refeicao": 0.0,
  "paga_hora_extra": false,
  "valor_hora_extra": 0.0,
  "estrelas_media": 5.0,
  "total_avaliacoes": 0,
  "id": "9583c78c-2bb9-4ac4-8b3e-0c358e0d101c",
  "empresa_id": "240bcc4c-d0db-4e35-bc29-11a7050f94b4"
}
```

### Chamada 5

**Request:** `GET http://testserver/api/v1/clientes/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado a dados de outra empresa."
}
```

---

## 60. `tests/test_fase3_contrato.py::test_equipe_sem_rh_para_todos[MECANICO]`

- **Cenário:** F3-E1 — Equipe (nomes/cargos) para qualquer perfil, sem RH; RH continua só para o DONO; outra empresa → 403
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/usuarios/94334e9f-629c-4c65-92f8-e26274ba3973/equipe`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  {
    "id": "8b89c905-3f58-4336-8b95-cba4d04e5f70",
    "nome": "Atendente Teste A",
    "email": "atendente.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "ATENDENTE",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "f3b95dfc-237c-49b1-adf1-c1b1d048140f",
    "nome": "Dono Teste A",
    "email": "dono.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "DONO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "bba76da7-c154-4be7-9826-5e1a677e6eba",
    "nome": "Financeiro Teste A",
    "email": "financeiro.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "FINANCEIRO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "5895210e-13af-47c2-a08c-ba8030d1be25",
    "nome": "joao",
    "email": "joao@oficina.com",
    "telefone": null,
    "cargo": "DONO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
    "nome": "Mecanico Teste A",
    "email": "mecanico.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "MECANICO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "b84b36ee-4d8c-40b5-86a2-9d654b74cf9d",
    "nome": "Vinici",
    "email": "camargo1.v@icloud.com",
    "telefone": null,
    "cargo": "MECANICO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  }
]
```

### Chamada 2

**Request:** `GET http://testserver/api/v1/usuarios/b763e7f1-e35b-4aa4-baa8-c8d586caf705/equipe`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado a dados de outra empresa."
}
```

### Chamada 3

**Request:** `GET http://testserver/api/v1/usuarios/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado para o seu perfil."
}
```

---

## 61. `tests/test_fase3_contrato.py::test_equipe_sem_rh_para_todos[ATENDENTE]`

- **Cenário:** F3-E1 — Equipe (nomes/cargos) para qualquer perfil, sem RH; RH continua só para o DONO; outra empresa → 403
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/usuarios/94334e9f-629c-4c65-92f8-e26274ba3973/equipe`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  {
    "id": "8b89c905-3f58-4336-8b95-cba4d04e5f70",
    "nome": "Atendente Teste A",
    "email": "atendente.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "ATENDENTE",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "f3b95dfc-237c-49b1-adf1-c1b1d048140f",
    "nome": "Dono Teste A",
    "email": "dono.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "DONO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "bba76da7-c154-4be7-9826-5e1a677e6eba",
    "nome": "Financeiro Teste A",
    "email": "financeiro.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "FINANCEIRO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "5895210e-13af-47c2-a08c-ba8030d1be25",
    "nome": "joao",
    "email": "joao@oficina.com",
    "telefone": null,
    "cargo": "DONO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
    "nome": "Mecanico Teste A",
    "email": "mecanico.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "MECANICO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "b84b36ee-4d8c-40b5-86a2-9d654b74cf9d",
    "nome": "Vinici",
    "email": "camargo1.v@icloud.com",
    "telefone": null,
    "cargo": "MECANICO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  }
]
```

### Chamada 2

**Request:** `GET http://testserver/api/v1/usuarios/b763e7f1-e35b-4aa4-baa8-c8d586caf705/equipe`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado a dados de outra empresa."
}
```

### Chamada 3

**Request:** `GET http://testserver/api/v1/usuarios/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado para o seu perfil."
}
```

---

## 62. `tests/test_fase3_contrato.py::test_equipe_sem_rh_para_todos[FINANCEIRO]`

- **Cenário:** F3-E1 — Equipe (nomes/cargos) para qualquer perfil, sem RH; RH continua só para o DONO; outra empresa → 403
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/usuarios/94334e9f-629c-4c65-92f8-e26274ba3973/equipe`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  {
    "id": "8b89c905-3f58-4336-8b95-cba4d04e5f70",
    "nome": "Atendente Teste A",
    "email": "atendente.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "ATENDENTE",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "f3b95dfc-237c-49b1-adf1-c1b1d048140f",
    "nome": "Dono Teste A",
    "email": "dono.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "DONO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "bba76da7-c154-4be7-9826-5e1a677e6eba",
    "nome": "Financeiro Teste A",
    "email": "financeiro.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "FINANCEIRO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "5895210e-13af-47c2-a08c-ba8030d1be25",
    "nome": "joao",
    "email": "joao@oficina.com",
    "telefone": null,
    "cargo": "DONO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
    "nome": "Mecanico Teste A",
    "email": "mecanico.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "MECANICO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "b84b36ee-4d8c-40b5-86a2-9d654b74cf9d",
    "nome": "Vinici",
    "email": "camargo1.v@icloud.com",
    "telefone": null,
    "cargo": "MECANICO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  }
]
```

### Chamada 2

**Request:** `GET http://testserver/api/v1/usuarios/b763e7f1-e35b-4aa4-baa8-c8d586caf705/equipe`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado a dados de outra empresa."
}
```

### Chamada 3

**Request:** `GET http://testserver/api/v1/usuarios/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado para o seu perfil."
}
```

---

## 63. `tests/test_fase3_contrato.py::test_equipe_sem_rh_para_todos[DONO]`

- **Cenário:** F3-E1 — Equipe (nomes/cargos) para qualquer perfil, sem RH; RH continua só para o DONO; outra empresa → 403
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/usuarios/94334e9f-629c-4c65-92f8-e26274ba3973/equipe`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  {
    "id": "8b89c905-3f58-4336-8b95-cba4d04e5f70",
    "nome": "Atendente Teste A",
    "email": "atendente.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "ATENDENTE",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "f3b95dfc-237c-49b1-adf1-c1b1d048140f",
    "nome": "Dono Teste A",
    "email": "dono.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "DONO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "bba76da7-c154-4be7-9826-5e1a677e6eba",
    "nome": "Financeiro Teste A",
    "email": "financeiro.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "FINANCEIRO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "5895210e-13af-47c2-a08c-ba8030d1be25",
    "nome": "joao",
    "email": "joao@oficina.com",
    "telefone": null,
    "cargo": "DONO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
    "nome": "Mecanico Teste A",
    "email": "mecanico.a@homolog-autotec.example.com",
    "telefone": null,
    "cargo": "MECANICO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  },
  {
    "id": "b84b36ee-4d8c-40b5-86a2-9d654b74cf9d",
    "nome": "Vinici",
    "email": "camargo1.v@icloud.com",
    "telefone": null,
    "cargo": "MECANICO",
    "ativo": true,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "estrelas_media": 5.0,
    "total_avaliacoes": 0
  }
]
```

### Chamada 2

**Request:** `GET http://testserver/api/v1/usuarios/b763e7f1-e35b-4aa4-baa8-c8d586caf705/equipe`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado a dados de outra empresa."
}
```

---

## 64. `tests/test_fase4_2_migracao.py::test_colunas_em_comum`

- **Cenário:** F42-1 — Cópia usa só as colunas que existem dos dois lados: plano/senha_hash ficam para trás, updated_at novo usa o padrão
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 65. `tests/test_fase4_2_migracao.py::test_valores_da_linha`

- **Cenário:** F42-2 — os_itens/auditoria herdam a empresa da oficina copiada; jsonb vai embrulhado; NULL continua NULL
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 66. `tests/test_fase4_2_migracao.py::test_apagar_cobre_tudo`

- **Cenário:** F42-3 — Toda tabela copiada é apagada no --substituir (senão sobraria lixo da cópia anterior), e os pais só depois dos filhos
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 67. `tests/test_fase4_2_plano.py::test_com_plano`

- **Cenário:** F42-4 — Listagem de oficinas: plano vem da assinatura; oficina sem assinatura aparece como básico
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 68. `tests/test_fase4_2_plano.py::test_gravar_plano`

- **Cenário:** F42-5 — gravar_plano: cria a assinatura se não existe, troca só o plano se já existe
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 69. `tests/test_fase4_estoque.py::test_baixas_concorrentes`

- **Cenário:** F4-E1 — 10 baixas simultâneas de 1 unidade num item com saldo 1: exatamente uma passa (200), as outras 400, saldo final 0
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/93326bc3-32e9-48ec-939b-a2c554b3a045/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "estoque_id": "91589033-94c2-4d25-8285-efbcc640a7b7",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 1,
  "custo_unitario": 1,
  "venda_unitario": 2
}
```

**Response:** `400`

```json
{
  "detail": "Estoque insuficiente. Saldo atual: 0"
}
```

### Chamada 2

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/93326bc3-32e9-48ec-939b-a2c554b3a045/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "estoque_id": "91589033-94c2-4d25-8285-efbcc640a7b7",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 1,
  "custo_unitario": 1,
  "venda_unitario": 2
}
```

**Response:** `400`

```json
{
  "detail": "Estoque insuficiente. Saldo atual: 0"
}
```

### Chamada 3

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/93326bc3-32e9-48ec-939b-a2c554b3a045/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "estoque_id": "91589033-94c2-4d25-8285-efbcc640a7b7",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 1,
  "custo_unitario": 1,
  "venda_unitario": 2
}
```

**Response:** `200`

```json
{
  "id": "9aaa6731-7801-4196-ab0b-e2024c6a76dc",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "os_id": "93326bc3-32e9-48ec-939b-a2c554b3a045",
  "estoque_id": "91589033-94c2-4d25-8285-efbcc640a7b7",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 1,
  "custo_unitario": 1.0,
  "venda_unitario": 2.0,
  "criado_em": "2026-11-26T00:57:59.488282+00:00"
}
```

### Chamada 4

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/93326bc3-32e9-48ec-939b-a2c554b3a045/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "estoque_id": "91589033-94c2-4d25-8285-efbcc640a7b7",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 1,
  "custo_unitario": 1,
  "venda_unitario": 2
}
```

**Response:** `400`

```json
{
  "detail": "Estoque insuficiente. Saldo atual: 0"
}
```

### Chamada 5

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/93326bc3-32e9-48ec-939b-a2c554b3a045/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "estoque_id": "91589033-94c2-4d25-8285-efbcc640a7b7",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 1,
  "custo_unitario": 1,
  "venda_unitario": 2
}
```

**Response:** `400`

```json
{
  "detail": "Estoque insuficiente. Saldo atual: 0"
}
```

### Chamada 6

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/93326bc3-32e9-48ec-939b-a2c554b3a045/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "estoque_id": "91589033-94c2-4d25-8285-efbcc640a7b7",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 1,
  "custo_unitario": 1,
  "venda_unitario": 2
}
```

**Response:** `400`

```json
{
  "detail": "Estoque insuficiente. Saldo atual: 0"
}
```

### Chamada 7

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/93326bc3-32e9-48ec-939b-a2c554b3a045/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "estoque_id": "91589033-94c2-4d25-8285-efbcc640a7b7",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 1,
  "custo_unitario": 1,
  "venda_unitario": 2
}
```

**Response:** `400`

```json
{
  "detail": "Estoque insuficiente. Saldo atual: 0"
}
```

### Chamada 8

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/93326bc3-32e9-48ec-939b-a2c554b3a045/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "estoque_id": "91589033-94c2-4d25-8285-efbcc640a7b7",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 1,
  "custo_unitario": 1,
  "venda_unitario": 2
}
```

**Response:** `400`

```json
{
  "detail": "Estoque insuficiente. Saldo atual: 0"
}
```

### Chamada 9

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/93326bc3-32e9-48ec-939b-a2c554b3a045/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "estoque_id": "91589033-94c2-4d25-8285-efbcc640a7b7",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 1,
  "custo_unitario": 1,
  "venda_unitario": 2
}
```

**Response:** `400`

```json
{
  "detail": "Estoque insuficiente. Saldo atual: 0"
}
```

### Chamada 10

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/93326bc3-32e9-48ec-939b-a2c554b3a045/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "estoque_id": "91589033-94c2-4d25-8285-efbcc640a7b7",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 1,
  "custo_unitario": 1,
  "venda_unitario": 2
}
```

**Response:** `400`

```json
{
  "detail": "Estoque insuficiente. Saldo atual: 0"
}
```

---

## 70. `tests/test_fase4_estoque.py::test_excluir_os_estorna_e_audita`

- **Cenário:** F4-E2 — Excluir OS com itens: estoque volta, itens e OS somem e o audit_logs guarda o motivo — tudo junto
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/f718f167-8d78-4453-bb3a-63f1152183c4/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "estoque_id": "d70b51ef-85cf-4cd4-ac1a-3e4c4464cd99",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 3,
  "custo_unitario": 1,
  "venda_unitario": 2
}
```

**Response:** `200`

```json
{
  "id": "4f5e1e80-459a-4d2c-ae71-dab79346b659",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "os_id": "f718f167-8d78-4453-bb3a-63f1152183c4",
  "estoque_id": "d70b51ef-85cf-4cd4-ac1a-3e4c4464cd99",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 3,
  "custo_unitario": 1.0,
  "venda_unitario": 2.0,
  "criado_em": "2026-11-26T00:58:01.855425+00:00"
}
```

### Chamada 2

**Request:** `DELETE http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/f718f167-8d78-4453-bb3a-63f1152183c4?motivo_exclusao=teste%20F4-E2`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "status": "sucesso",
  "detail": "OS cancelada, estoque restaurado e log gerado."
}
```

---

## 71. `tests/test_fase4_estoque.py::test_lote_tudo_ou_nada`

- **Cenário:** F4-E3 — Lote em que o 2º item não tem saldo: 400 e o 1º item NÃO fica baixado nem gravado (tudo ou nada)
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/206c8cb6-d10b-4c2a-89d9-1f4be72ea627/itens/lote`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
[
  {
    "estoque_id": "811e9e68-b39c-4444-9719-c9e192cc2f1d",
    "tipo": "PECA",
    "nome_item": "ok",
    "quantidade": 2,
    "custo_unitario": 1,
    "venda_unitario": 2
  },
  {
    "estoque_id": "6466cd9a-a144-41fb-938c-a587cbe8cc2a",
    "tipo": "PECA",
    "nome_item": "sem saldo",
    "quantidade": 9,
    "custo_unitario": 1,
    "venda_unitario": 2
  }
]
```

**Response:** `400`

```json
{
  "detail": "Estoque insuficiente para 'sem saldo'. Saldo atual: 1"
}
```

---

## 72. `tests/test_fase4_estoque.py::test_saldo_insuficiente_e_ajuste_de_item`

- **Cenário:** F4-E4 — Saída manual e aumento de item acima do saldo → 400 com saldo intacto; reduzir item devolve a diferença
- **Resultado:** PASSOU

### Chamada 1

**Request:** `PATCH http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/1c7b1a0d-cb5c-47f6-8481-46f8ea9d5b10/ajustar`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "tipo": "saida",
  "quantidade": 4
}
```

**Response:** `400`

```json
{
  "detail": "Estoque insuficiente. Saldo atual: 3"
}
```

### Chamada 2

**Request:** `POST http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/fc7c1256-1fab-48ae-84ae-2b847c317893/itens`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "estoque_id": "1c7b1a0d-cb5c-47f6-8481-46f8ea9d5b10",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 2,
  "custo_unitario": 1,
  "venda_unitario": 2
}
```

**Response:** `200`

```json
{
  "id": "72edff82-cbae-4ae1-912d-542450734b14",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "os_id": "fc7c1256-1fab-48ae-84ae-2b847c317893",
  "estoque_id": "1c7b1a0d-cb5c-47f6-8481-46f8ea9d5b10",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 2,
  "custo_unitario": 1.0,
  "venda_unitario": 2.0,
  "criado_em": "2026-11-26T00:58:09.301296+00:00"
}
```

### Chamada 3

**Request:** `PUT http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/fc7c1256-1fab-48ae-84ae-2b847c317893/itens/72edff82-cbae-4ae1-912d-542450734b14`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "quantidade": 9
}
```

**Response:** `400`

```json
{
  "detail": "Estoque insuficiente. Saldo atual: 1"
}
```

### Chamada 4

**Request:** `PUT http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/fc7c1256-1fab-48ae-84ae-2b847c317893/itens/72edff82-cbae-4ae1-912d-542450734b14`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "quantidade": 1
}
```

**Response:** `200`

```json
{
  "id": "72edff82-cbae-4ae1-912d-542450734b14",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "os_id": "fc7c1256-1fab-48ae-84ae-2b847c317893",
  "estoque_id": "1c7b1a0d-cb5c-47f6-8481-46f8ea9d5b10",
  "tipo": "PECA",
  "nome_item": "Peça F4",
  "quantidade": 1,
  "custo_unitario": 1.0,
  "venda_unitario": 2.0,
  "criado_em": "2026-11-26T00:58:09.301296+00:00"
}
```

### Chamada 5

**Request:** `DELETE http://testserver/api/v1/os/94334e9f-629c-4c65-92f8-e26274ba3973/fc7c1256-1fab-48ae-84ae-2b847c317893/itens/72edff82-cbae-4ae1-912d-542450734b14`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "status": "sucesso",
  "detail": "Item removido e estornado (se aplicável)."
}
```

---

## 73. `tests/test_fase4_estoque.py::test_rpc_fechada_para_logado`

- **Cenário:** F4-E5 — Usuário logado não consegue chamar as funções de estoque direto no Supabase (só o backend)
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/rpc/baixar_estoque`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "p_item": "b027071a-f177-4f1f-9a1f-da2f0cfe078b",
  "p_empresa": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "p_qtd": 1
}
```

**Response:** `403`

```json
{
  "code": "42501",
  "details": null,
  "hint": null,
  "message": "permission denied for function baixar_estoque"
}
```

---

## 74. `tests/test_fase5_avaliacao_ponto.py::test_token_assinado`

- **Cenário:** F5-T — Token de avaliação: assinatura válida volta o os_id; adulterado, de outra OS, truncado ou lixo → None
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 75. `tests/test_fase5_avaliacao_ponto.py::test_avaliar_uma_vez`

- **Cenário:** F7 — Link com token válido: avalia (empresa, mecânico, cliente e placa vêm da OS); segunda avaliação da mesma OS → 409; média do mecânico atualizada
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/equipe/avaliacoes/94334e9f-629c-4c65-92f8-e26274ba3973/link/e830feca-14bb-427b-8821-f22c07805fd6`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "token": "e830feca-14bb-427b-8821-f22c07805fd6.IVYYvNAhfOj3MfNXW_fUV4XNf1TZhi-Xtivg7hHiQ-8",
  "caminho": "/?modo=avaliar&token=e830feca-14bb-427b-8821-f22c07805fd6.IVYYvNAhfOj3MfNXW_fUV4XNf1TZhi-Xtivg7hHiQ-8"
}
```

### Chamada 2

**Request:** `GET http://testserver/api/v1/equipe/avaliar/e830feca-14bb-427b-8821-f22c07805fd6.IVYYvNAhfOj3MfNXW_fUV4XNf1TZhi-Xtivg7hHiQ-8`

Headers: `{}`

**Response:** `200`

```json
{
  "veiculo_modelo": "Gol 1.0",
  "veiculo_placa": "TSTA001",
  "ja_avaliada": false
}
```

### Chamada 3

**Request:** `POST http://testserver/api/v1/equipe/avaliar`

Headers: `{"content-type": "application/json"}`

```json
{
  "token": "e830feca-14bb-427b-8821-f22c07805fd6.IVYYvNAhfOj3MfNXW_fUV4XNf1TZhi-Xtivg7hHiQ-8",
  "nota": 4,
  "comentario": "Rápido e honesto",
  "empresa_id": "b763e7f1-e35b-4aa4-baa8-c8d586caf705",
  "mecanico_id": "7051b94a-aa8e-4e95-bd7e-13c77a83b782",
  "veiculo_placa": "FORJADA"
}
```

**Response:** `200`

```json
{
  "id": "e4b8d56d-74a2-43c4-a20f-91cbbfdf5692",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "os_id": "e830feca-14bb-427b-8821-f22c07805fd6",
  "mecanico_id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
  "mecanico_nome": "Mecanico Teste A",
  "cliente_nome": "Cliente Teste A",
  "veiculo_modelo": "Gol 1.0",
  "veiculo_placa": "TSTA001",
  "nota": 4,
  "comentario": "Rápido e honesto",
  "data": null,
  "created_at": "2026-11-26T00:58:17.743086Z"
}
```

### Chamada 4

**Request:** `POST http://testserver/api/v1/equipe/avaliar`

Headers: `{"content-type": "application/json"}`

```json
{
  "token": "e830feca-14bb-427b-8821-f22c07805fd6.IVYYvNAhfOj3MfNXW_fUV4XNf1TZhi-Xtivg7hHiQ-8",
  "nota": 1
}
```

**Response:** `409`

```json
{
  "detail": "Esta OS já foi avaliada. Obrigado!"
}
```

### Chamada 5

**Request:** `GET http://testserver/api/v1/equipe/avaliar/e830feca-14bb-427b-8821-f22c07805fd6.IVYYvNAhfOj3MfNXW_fUV4XNf1TZhi-Xtivg7hHiQ-8`

Headers: `{}`

**Response:** `200`

```json
{
  "veiculo_modelo": "Gol 1.0",
  "veiculo_placa": "TSTA001",
  "ja_avaliada": true
}
```

---

## 76. `tests/test_fase5_avaliacao_ponto.py::test_token_invalido_nao_grava`

- **Cenário:** F8 — Token adulterado, sem token ou de OS inexistente: erro e nada gravado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/equipe/avaliar`

Headers: `{"content-type": "application/json"}`

```json
{
  "token": "adulterado.123",
  "nota": 5
}
```

**Response:** `404`

```json
{
  "detail": "Link de avaliação inválido ou expirado."
}
```

### Chamada 2

**Request:** `POST http://testserver/api/v1/equipe/avaliar`

Headers: `{"content-type": "application/json"}`

```json
{
  "nota": 5
}
```

**Response:** `422`

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "token"
      ],
      "msg": "Link de avaliação: campo obrigatório.",
      "type": "missing"
    }
  ]
}
```

### Chamada 3

**Request:** `POST http://testserver/api/v1/equipe/avaliar`

Headers: `{"content-type": "application/json"}`

```json
{
  "token": "4c37e9e4-9bcd-4d89-bdec-2b8238fb8011.qpMs-CU-F4Gv7RcMMmcxoce-5cpE3wc_ua3xJjqjmTI",
  "nota": 5
}
```

**Response:** `404`

```json
{
  "detail": "Link de avaliação inválido ou expirado."
}
```

### Chamada 4

**Request:** `POST http://testserver/api/v1/equipe/avaliar`

Headers: `{"content-type": "application/json"}`

```json
{
  "token": "9b45576f-8687-41de-bfff-f42cde85254e.QHvbpDSpRHKkTOKsQzNwlLfXFmqVxYfQUsb8-FNnFrs",
  "nota": 9
}
```

**Response:** `422`

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "nota"
      ],
      "msg": "Nota: não pode ser maior que 5.",
      "type": "less_than_equal"
    }
  ]
}
```

### Chamada 5

**Request:** `GET http://testserver/api/v1/equipe/avaliar/adulterado.123`

Headers: `{}`

**Response:** `404`

```json
{
  "detail": "Link de avaliação inválido ou expirado."
}
```

---

## 77. `tests/test_fase5_avaliacao_ponto.py::test_gerar_link_regras`

- **Cenário:** F5-L — Gerar link: só OS finalizada/paga e só da própria empresa; mecânico não gera
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/equipe/avaliacoes/94334e9f-629c-4c65-92f8-e26274ba3973/link/da1e6390-fec1-46f9-99ce-bb35ea4abc4c`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `400`

```json
{
  "detail": "A avaliação só fica disponível depois que a OS é finalizada."
}
```

### Chamada 2

**Request:** `GET http://testserver/api/v1/equipe/avaliacoes/94334e9f-629c-4c65-92f8-e26274ba3973/link/792a4dbf-3a8d-4f06-a8cd-8cb50ca822a4`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "token": "792a4dbf-3a8d-4f06-a8cd-8cb50ca822a4.dy2GsPVHOa79-QMSLExOA6SsenSM3ogG-Drg5nxPDeo",
  "caminho": "/?modo=avaliar&token=792a4dbf-3a8d-4f06-a8cd-8cb50ca822a4.dy2GsPVHOa79-QMSLExOA6SsenSM3ogG-Drg5nxPDeo"
}
```

### Chamada 3

**Request:** `GET http://testserver/api/v1/equipe/avaliacoes/b763e7f1-e35b-4aa4-baa8-c8d586caf705/link/656cff42-7c05-47a9-ad3c-6f4ced527ccc`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado a dados de outra empresa."
}
```

### Chamada 4

**Request:** `GET http://testserver/api/v1/equipe/avaliacoes/94334e9f-629c-4c65-92f8-e26274ba3973/link/656cff42-7c05-47a9-ad3c-6f4ced527ccc`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `404`

```json
{
  "detail": "OS não encontrado nesta empresa."
}
```

### Chamada 5

**Request:** `GET http://testserver/api/v1/equipe/avaliacoes/94334e9f-629c-4c65-92f8-e26274ba3973/link/792a4dbf-3a8d-4f06-a8cd-8cb50ca822a4`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado para o seu perfil."
}
```

---

## 78. `tests/test_fase5_avaliacao_ponto.py::test_anon_nao_insere_avaliacao`

- **Cenário:** F5-R — Chave anon não insere em avaliacoes_os direto pelo Supabase (policy pública removida)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 79. `tests/test_fase5_avaliacao_ponto.py::test_ponto_so_do_servidor`

- **Cenário:** F5-P — Ponto ignora usuario_id/data/hora enviados: grava o usuário do token, a data e a hora do servidor (America/Sao_Paulo)
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/equipe/pontos/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "tipo": "ENTRADA",
  "usuario_id": "f3b95dfc-237c-49b1-adf1-c1b1d048140f",
  "data": "2020-01-01",
  "hora": "03:00:00"
}
```

**Response:** `200`

```json
{
  "id": "e0a1abce-a46e-49e5-a4df-70eb89def5ab",
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "usuario_id": "df201096-62a8-49e8-b9bb-bb000244d4e8",
  "usuario_nome": "Mecanico Teste A",
  "data": "2026-11-25",
  "hora": "21:55:41",
  "tipo": "ENTRADA",
  "latitude": null,
  "longitude": null,
  "dentro_raio": true,
  "distancia_metros": 0.0,
  "created_at": "2026-11-26T00:58:27.658326Z"
}
```

---

## 80. `tests/test_fase6_1_categorias.py::test_item_com_categoria_nova`

- **Cenário:** F61-1 — Item com categoria nova ('  freios  e pastilhas ') grava, normalizada em maiúsculas; editar para outra nova também (antes: 400 do CHECK)
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/estoque/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "nome": "Item F61",
  "categoria": "  freios  e pastilhas ",
  "quantidade": 1,
  "minimo_alerta": 0,
  "custo": 1,
  "venda": 2
}
```

**Response:** `200`

```json
{
  "nome": "Item F61",
  "categoria": "FREIOS E PASTILHAS",
  "quantidade": 1,
  "custo": 1.0,
  "venda": 2.0,
  "minimo_alerta": 0,
  "codigo": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "822f1313-d26a-48e2-94ed-76775c20c1b0"
}
```

### Chamada 2

**Request:** `PUT http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/822f1313-d26a-48e2-94ed-76775c20c1b0`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "categoria": "acessórios de luxo"
}
```

**Response:** `200`

```json
{
  "nome": "Item F61",
  "categoria": "ACESSÓRIOS DE LUXO",
  "quantidade": 1,
  "custo": 1.0,
  "venda": 2.0,
  "minimo_alerta": 0,
  "codigo": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "822f1313-d26a-48e2-94ed-76775c20c1b0"
}
```

### Chamada 3

**Request:** `POST http://testserver/api/v1/estoque/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "nome": "Item F61",
  "categoria": "FERRAMENTAS",
  "quantidade": 1,
  "minimo_alerta": 0,
  "custo": 1,
  "venda": 2
}
```

**Response:** `200`

```json
{
  "nome": "Item F61",
  "categoria": "FERRAMENTAS",
  "quantidade": 1,
  "custo": 1.0,
  "venda": 2.0,
  "minimo_alerta": 0,
  "codigo": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "901ca3b5-19f1-424b-9872-c352d1668884"
}
```

---

## 81. `tests/test_fase6_1_categorias.py::test_categoria_invalida`

- **Cenário:** F61-2 — Categoria vazia ou com mais de 30 caracteres (limite da coluna) → 422 e nada gravado
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/estoque/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "nome": "Item F61",
  "categoria": "",
  "quantidade": 1,
  "minimo_alerta": 0,
  "custo": 1,
  "venda": 2
}
```

**Response:** `422`

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "categoria"
      ],
      "msg": "A categoria precisa ter de 1 a 30 caracteres.",
      "type": "value_error"
    }
  ]
}
```

### Chamada 2

**Request:** `PUT http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/cc5b7212-c001-459d-bff3-f29c9fc82807`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "categoria": ""
}
```

**Response:** `422`

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "categoria"
      ],
      "msg": "A categoria precisa ter de 1 a 30 caracteres.",
      "type": "value_error"
    }
  ]
}
```

### Chamada 3

**Request:** `POST http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/categorias`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "nome": ""
}
```

**Response:** `422`

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "nome"
      ],
      "msg": "A categoria precisa ter de 1 a 30 caracteres.",
      "type": "value_error"
    }
  ]
}
```

### Chamada 4

**Request:** `POST http://testserver/api/v1/estoque/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "nome": "Item F61",
  "categoria": "   ",
  "quantidade": 1,
  "minimo_alerta": 0,
  "custo": 1,
  "venda": 2
}
```

**Response:** `422`

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "categoria"
      ],
      "msg": "A categoria precisa ter de 1 a 30 caracteres.",
      "type": "value_error"
    }
  ]
}
```

### Chamada 5

**Request:** `PUT http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/cc5b7212-c001-459d-bff3-f29c9fc82807`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "categoria": "   "
}
```

**Response:** `422`

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "categoria"
      ],
      "msg": "A categoria precisa ter de 1 a 30 caracteres.",
      "type": "value_error"
    }
  ]
}
```

### Chamada 6

**Request:** `POST http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/categorias`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "nome": "   "
}
```

**Response:** `422`

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "nome"
      ],
      "msg": "A categoria precisa ter de 1 a 30 caracteres.",
      "type": "value_error"
    }
  ]
}
```

### Chamada 7

**Request:** `POST http://testserver/api/v1/estoque/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "nome": "Item F61",
  "categoria": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "quantidade": 1,
  "minimo_alerta": 0,
  "custo": 1,
  "venda": 2
}
```

**Response:** `422`

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "categoria"
      ],
      "msg": "A categoria precisa ter de 1 a 30 caracteres.",
      "type": "value_error"
    }
  ]
}
```

### Chamada 8

**Request:** `PUT http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/cc5b7212-c001-459d-bff3-f29c9fc82807`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "categoria": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
}
```

**Response:** `422`

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "categoria"
      ],
      "msg": "A categoria precisa ter de 1 a 30 caracteres.",
      "type": "value_error"
    }
  ]
}
```

### Chamada 9

**Request:** `POST http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/categorias`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "nome": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
}
```

**Response:** `422`

```json
{
  "detail": [
    {
      "loc": [
        "body",
        "nome"
      ],
      "msg": "A categoria precisa ter de 1 a 30 caracteres.",
      "type": "value_error"
    }
  ]
}
```

---

## 82. `tests/test_fase6_1_categorias.py::test_listar_e_criar_categoria`

- **Cenário:** F61-3 — Lista de categorias: padrão da oficina + criadas + as que itens já usam (MAO_OBRA); criar duplicada não duplica
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/categorias`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  "PECAS",
  "FLUIDOS",
  "PNEUS",
  "ELETRICA",
  "ACESSORIOS",
  "FERRAMENTAS",
  "DIVERSOS"
]
```

### Chamada 2

**Request:** `POST http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/categorias`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "nome": " lanternagem "
}
```

**Response:** `200`

```json
{
  "nome": "LANTERNAGEM"
}
```

### Chamada 3

**Request:** `POST http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/categorias`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "nome": " lanternagem "
}
```

**Response:** `200`

```json
{
  "nome": "LANTERNAGEM"
}
```

### Chamada 4

**Request:** `GET http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/categorias`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  "PECAS",
  "FLUIDOS",
  "PNEUS",
  "ELETRICA",
  "ACESSORIOS",
  "FERRAMENTAS",
  "DIVERSOS",
  "LANTERNAGEM"
]
```

---

## 83. `tests/test_fase6_1_categorias.py::test_excluir_categoria`

- **Cenário:** F61-4 — Excluir categoria com itens: itens vão para DIVERSOS, a categoria some; DIVERSOS e MAO_OBRA não saem
- **Resultado:** PASSOU

### Chamada 1

**Request:** `POST http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/categorias`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "nome": "Vidros"
}
```

**Response:** `200`

```json
{
  "nome": "VIDROS"
}
```

### Chamada 2

**Request:** `POST http://testserver/api/v1/estoque/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "nome": "Vidro F61-1",
  "categoria": "vidros",
  "quantidade": 1,
  "minimo_alerta": 0,
  "custo": 1,
  "venda": 2
}
```

**Response:** `200`

```json
{
  "nome": "Vidro F61-1",
  "categoria": "VIDROS",
  "quantidade": 1,
  "custo": 1.0,
  "venda": 2.0,
  "minimo_alerta": 0,
  "codigo": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "6d1cfbb2-73ab-422a-aa42-b15dc4f60d21"
}
```

### Chamada 3

**Request:** `POST http://testserver/api/v1/estoque/`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "nome": "Vidro F61-2",
  "categoria": "vidros",
  "quantidade": 1,
  "minimo_alerta": 0,
  "custo": 1,
  "venda": 2
}
```

**Response:** `200`

```json
{
  "nome": "Vidro F61-2",
  "categoria": "VIDROS",
  "quantidade": 1,
  "custo": 1.0,
  "venda": 2.0,
  "minimo_alerta": 0,
  "codigo": null,
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "id": "1792b950-27ba-4f1b-8250-7e350e662f29"
}
```

### Chamada 4

**Request:** `DELETE http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/categorias/vidros`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "status": "sucesso",
  "itens_reclassificados": 2
}
```

### Chamada 5

**Request:** `GET http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/categorias`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  "PECAS",
  "FLUIDOS",
  "PNEUS",
  "ELETRICA",
  "ACESSORIOS",
  "FERRAMENTAS",
  "DIVERSOS"
]
```

### Chamada 6

**Request:** `DELETE http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/categorias/DIVERSOS`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `400`

```json
{
  "detail": "Esta categoria é usada pelo sistema e não pode ser excluída."
}
```

### Chamada 7

**Request:** `DELETE http://testserver/api/v1/estoque/94334e9f-629c-4c65-92f8-e26274ba3973/categorias/MAO_OBRA`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `400`

```json
{
  "detail": "Esta categoria é usada pelo sistema e não pode ser excluída."
}
```

---

## 84. `tests/test_fase6_1_categorias.py::test_categorias_de_outra_empresa`

- **Cenário:** F61-5 — Isolamento: DONO da empresa A não lê, cria nem exclui categorias da empresa B
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/estoque/b763e7f1-e35b-4aa4-baa8-c8d586caf705/categorias`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado a dados de outra empresa."
}
```

### Chamada 2

**Request:** `POST http://testserver/api/v1/estoque/b763e7f1-e35b-4aa4-baa8-c8d586caf705/categorias`

Headers: `{"authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "nome": "INVASORA"
}
```

**Response:** `403`

```json
{
  "detail": "Acesso negado a dados de outra empresa."
}
```

### Chamada 3

**Request:** `DELETE http://testserver/api/v1/estoque/b763e7f1-e35b-4aa4-baa8-c8d586caf705/categorias/PECAS`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado a dados de outra empresa."
}
```

---

## 85. `tests/test_fase6_1_categorias.py::test_categorias_fechadas_no_rest`

- **Cenário:** F61-6 — Anon/usuário logado não lê nem grava categorias_estoque direto pelo REST (RLS fechado, só o backend)
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/categorias_estoque`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>"}`

**Response:** `401`

```json
{
  "code": "42501",
  "details": null,
  "hint": "Grant the required privileges to the current role with: GRANT SELECT ON public.categorias_estoque TO anon;",
  "message": "permission denied for table categorias_estoque"
}
```

### Chamada 2

**Request:** `POST https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/categorias_estoque`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "nome": "X"
}
```

**Response:** `401`

```json
{
  "code": "42501",
  "details": null,
  "hint": "Grant the required privileges to the current role with: GRANT INSERT ON public.categorias_estoque TO anon;",
  "message": "permission denied for table categorias_estoque"
}
```

### Chamada 3

**Request:** `GET https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/categorias_estoque`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "code": "42501",
  "details": null,
  "hint": "Grant the required privileges to the current role with: GRANT SELECT ON public.categorias_estoque TO authenticated;",
  "message": "permission denied for table categorias_estoque"
}
```

### Chamada 4

**Request:** `POST https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/categorias_estoque`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>", "content-type": "application/json"}`

```json
{
  "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
  "nome": "X"
}
```

**Response:** `403`

```json
{
  "code": "42501",
  "details": null,
  "hint": "Grant the required privileges to the current role with: GRANT INSERT ON public.categorias_estoque TO authenticated;",
  "message": "permission denied for table categorias_estoque"
}
```

---

## 86. `tests/test_fase6_2_escala.py::test_datas_invertidas`

- **Cenário:** R9-1 — Escala com data_fim antes de data_inicio → 422 em português e nada gravado
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 87. `tests/test_fase6_2_escala.py::test_datas_validas[2026-12-24-2026-12-24]`

- **Cenário:** R9-2 — Mesmo dia e período normal continuam aceitos
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 88. `tests/test_fase6_2_escala.py::test_datas_validas[2026-12-24-2026-12-30]`

- **Cenário:** R9-2 — Mesmo dia e período normal continuam aceitos
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 89. `tests/test_fase6_datas.py::test_para_br`

- **Cenário:** F6-T1 — para_br: 23:30 BRT (02:30Z do dia seguinte) continua no dia certo; sem fuso é tratado como UTC
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 90. `tests/test_fase6_datas.py::test_vencimento_folha[hoje0-31-2027-02-28]`

- **Cenário:** F6-T2 — Folha: dia de pagamento 31 vira o último dia do mês (fev, abril, dezembro); depois do dia, vai para o mês seguinte
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 91. `tests/test_fase6_datas.py::test_vencimento_folha[hoje1-31-2028-02-29]`

- **Cenário:** F6-T2 — Folha: dia de pagamento 31 vira o último dia do mês (fev, abril, dezembro); depois do dia, vai para o mês seguinte
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 92. `tests/test_fase6_datas.py::test_vencimento_folha[hoje2-31-2026-04-30]`

- **Cenário:** F6-T2 — Folha: dia de pagamento 31 vira o último dia do mês (fev, abril, dezembro); depois do dia, vai para o mês seguinte
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 93. `tests/test_fase6_datas.py::test_vencimento_folha[hoje3-5-2026-12-05]`

- **Cenário:** F6-T2 — Folha: dia de pagamento 31 vira o último dia do mês (fev, abril, dezembro); depois do dia, vai para o mês seguinte
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 94. `tests/test_fase6_datas.py::test_vencimento_folha[hoje4-5-2027-01-05]`

- **Cenário:** F6-T2 — Folha: dia de pagamento 31 vira o último dia do mês (fev, abril, dezembro); depois do dia, vai para o mês seguinte
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 95. `tests/test_fase6_datas.py::test_vencimento_folha[hoje5-31-2026-01-31]`

- **Cenário:** F6-T2 — Folha: dia de pagamento 31 vira o último dia do mês (fev, abril, dezembro); depois do dia, vai para o mês seguinte
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 96. `tests/test_fase6_datas.py::test_vencimento_folha[hoje6-30-2026-02-28]`

- **Cenário:** F6-T2 — Folha: dia de pagamento 31 vira o último dia do mês (fev, abril, dezembro); depois do dia, vai para o mês seguinte
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 97. `tests/test_fase7_busca.py::test_busca_os_no_banco`

- **Cenário:** F7-1 — Unitário: busca de OS vai para a view os_busca com ilike e janela no banco (sem limit(5000))
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 98. `tests/test_fase7_busca.py::test_listagem_sem_busca`

- **Cenário:** F7-2 — Unitário: sem busca a listagem segue na tabela, paginada
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 99. `tests/test_fase7_busca.py::test_termo_hostil`

- **Cenário:** F7-3 — Unitário: termo com vírgula, parênteses, aspas e % não quebra o filtro
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 100. `tests/test_fase7_busca.py::test_rotas_paginado[clientes]`

- **Cenário:** F7-4 — Unitário: /paginado de clientes, veículos e estoque devolve {items,total,skip,limit}; não é lido como id
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 101. `tests/test_fase7_busca.py::test_rotas_paginado[veiculos]`

- **Cenário:** F7-4 — Unitário: /paginado de clientes, veículos e estoque devolve {items,total,skip,limit}; não é lido como id
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 102. `tests/test_fase7_busca.py::test_rotas_paginado[estoque]`

- **Cenário:** F7-4 — Unitário: /paginado de clientes, veículos e estoque devolve {items,total,skip,limit}; não é lido como id
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 103. `tests/test_fase7_busca.py::test_limites_e_tenant`

- **Cenário:** F7-5 — Unitário: limit acima de 200 ou skip negativo → 422; empresa de outro tenant → 403
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 104. `tests/test_fase7_busca.py::test_rotas_antigas`

- **Cenário:** F7-6 — Unitário: rotas antigas (lista completa) continuam iguais
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 105. `tests/test_fase7_busca.py::test_busca_acha_os_5999`

- **Cenário:** F7-7 — Integração: 6000 OS na Oficina do tião; busca acha a OS nº 5999 e a OS de 6000 itens pagina com total correto
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/os/?empresa_id=94334e9f-629c-4c65-92f8-e26274ba3973&search=T002-bc76b0+OS+5999&limit=10`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "items": [
    {
      "id": "af61907a-e1c7-4dfd-a00c-f08ad9a2894e",
      "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
      "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
      "km_atual": null,
      "status": "ORCAMENTO",
      "data_abertura": "2026-11-26T00:59:07.265313+00:00",
      "total_geral": 0.0,
      "descricao_problema": "T002-bc76b0 OS 5999",
      "clientes": {
        "nome": "Cliente Teste A",
        "telefone": "11999990001"
      },
      "veiculos": {
        "placa": "TSTA001",
        "modelo": "Gol 1.0"
      }
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

### Chamada 2

**Request:** `GET http://testserver/api/v1/os/?empresa_id=94334e9f-629c-4c65-92f8-e26274ba3973&search=T002-bc76b0&skip=5990&limit=50`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
{
  "items": [
    {
      "id": "fd11837d-de0b-422f-bb28-7fb0c4c24bc2",
      "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
      "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
      "km_atual": null,
      "status": "ORCAMENTO",
      "data_abertura": "2026-11-26T00:59:00.22223+00:00",
      "total_geral": 0.0,
      "descricao_problema": "T002-bc76b0 OS 839",
      "clientes": {
        "nome": "Cliente Teste A",
        "telefone": "11999990001"
      },
      "veiculos": {
        "placa": "TSTA001",
        "modelo": "Gol 1.0"
      }
    },
    {
      "id": "fd13b278-aa8a-4ad1-8495-876812c59c40",
      "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
      "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
      "km_atual": null,
      "status": "ORCAMENTO",
      "data_abertura": "2026-11-26T00:59:00.22223+00:00",
      "total_geral": 0.0,
      "descricao_problema": "T002-bc76b0 OS 780",
      "clientes": {
        "nome": "Cliente Teste A",
        "telefone": "11999990001"
      },
      "veiculos": {
        "placa": "TSTA001",
        "modelo": "Gol 1.0"
      }
    },
    {
      "id": "fd3e8a8d-aa0c-4d4b-84eb-d841bc3bfd66",
      "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
      "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
      "km_atual": null,
      "status": "ORCAMENTO",
      "data_abertura": "2026-11-26T00:59:00.22223+00:00",
      "total_geral": 0.0,
      "descricao_problema": "T002-bc76b0 OS 646",
      "clientes": {
        "nome": "Cliente Teste A",
        "telefone": "11999990001"
      },
      "veiculos": {
        "placa": "TSTA001",
        "modelo": "Gol 1.0"
      }
    },
    {
      "id": "fd59c0af-0467-42a2-972e-d77794ab607e",
      "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
      "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
      "km_atual": null,
      "status": "ORCAMENTO",
      "data_abertura": "2026-11-26T00:59:00.22223+00:00",
      "total_geral": 0.0,
      "descricao_problema": "T002-bc76b0 OS 226",
      "clientes": {
        "nome": "Cliente Teste A",
        "telefone": "11999990001"
      },
      "veiculos": {
        "placa": "TSTA001",
        "modelo": "Gol 1.0"
      }
    },
    {
      "id": "fdb8a92a-fffe-4a6a-af3e-3a6a94f7e6e3",
      "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
      "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
      "km_atual": null,
      "status": "ORCAMENTO",
      "data_abertura": "2026-11-26T00:59:00.22223+00:00",
      "total_geral": 0.0,
      "descricao_problema": "T002-bc76b0 OS 297",
      "clientes": {
        "nome": "Cliente Teste A",
        "telefone": "11999990001"
      },
      "veiculos": {
        "placa": "TSTA001",
        "modelo": "Gol 1.0"
      }
    },
    {
      "id": "fe320be2-86ed-4442-b3ef-0205a16f4d6e",
      "cliente_id": "44e46577-443d-4c98-90d2-cd79e0123492",
      "veiculo_id": "522784a7-2f0f-492a-9cdd-ffa17f71cf53",
      "km_atual": null,
      "status
... (truncado)
```

---

## 106. `tests/test_fase7_financeiro_bot.py::test_periodo_na_query`

- **Cenário:** F7-F1 — Período do Financeiro vai na query com o dia de Brasília: 12/11 = 03:00Z a 02:59:59Z do dia seguinte
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 107. `tests/test_fase7_financeiro_bot.py::test_totais_iguais[None-None-esperado0]`

- **Cenário:** F7-F2 — Mesmos totais de antes (valores conferidos contra o código antigo num Postgres real): 23:30 BRT fica no dia 11, 00:00 e 23:59:59 no 12
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 108. `tests/test_fase7_financeiro_bot.py::test_totais_iguais[2026-11-12-2026-11-12-esperado1]`

- **Cenário:** F7-F2 — Mesmos totais de antes (valores conferidos contra o código antigo num Postgres real): 23:30 BRT fica no dia 11, 00:00 e 23:59:59 no 12
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 109. `tests/test_fase7_financeiro_bot.py::test_totais_iguais[2026-11-01-2026-11-30-esperado2]`

- **Cenário:** F7-F2 — Mesmos totais de antes (valores conferidos contra o código antigo num Postgres real): 23:30 BRT fica no dia 11, 00:00 e 23:59:59 no 12
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 110. `tests/test_fase7_financeiro_bot.py::test_totais_iguais[2026-09-01-2026-09-30-esperado3]`

- **Cenário:** F7-F2 — Mesmos totais de antes (valores conferidos contra o código antigo num Postgres real): 23:30 BRT fica no dia 11, 00:00 e 23:59:59 no 12
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 111. `tests/test_fase7_financeiro_bot.py::test_totais_iguais[2026-11-13-2026-11-13-esperado4]`

- **Cenário:** F7-F2 — Mesmos totais de antes (valores conferidos contra o código antigo num Postgres real): 23:30 BRT fica no dia 11, 00:00 e 23:59:59 no 12
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 112. `tests/test_fase7_financeiro_bot.py::test_totais_iguais[2026-11-12-None-esperado5]`

- **Cenário:** F7-F2 — Mesmos totais de antes (valores conferidos contra o código antigo num Postgres real): 23:30 BRT fica no dia 11, 00:00 e 23:59:59 no 12
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 113. `tests/test_fase7_financeiro_bot.py::test_historico_independe_do_periodo`

- **Cenário:** F7-F3 — Histórico de 6 meses não depende do período filtrado
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 114. `tests/test_fase7_financeiro_bot.py::test_inteligencia_periodo`

- **Cenário:** F7-F4 — Inteligência financeira filtra no banco e ignora OS de outra empresa
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 115. `tests/test_fase7_financeiro_bot.py::test_resumo_estoque`

- **Cenário:** F7-E1 — Resumo do estoque = stats da listagem completa (mesmos valores)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 116. `tests/test_fase7_financeiro_bot.py::test_dominios`

- **Cenário:** F7-B1 — url_audio: só https de domínio da lista (ou subdomínio); fora da lista ou lista vazia → erro antes de baixar
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 117. `tests/test_fase7_financeiro_bot.py::test_normalizar`

- **Cenário:** F7-B2 — Normalização de nome de peça
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 118. `tests/test_fase7_financeiro_bot.py::test_processar_audio`

- **Cenário:** F7-B3 — processar-audio: domínio fora → 400 sem baixar; Gemini chamado com await no cliente async; match exato, sem match vai sem estoque_id
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 119. `tests/test_fase8_422_pt.py::test_422_em_portugues[post-0]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 120. `tests/test_fase8_422_pt.py::test_422_em_portugues[post-1]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 121. `tests/test_fase8_422_pt.py::test_422_em_portugues[post-2]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 122. `tests/test_fase8_422_pt.py::test_422_em_portugues[post-3]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 123. `tests/test_fase8_422_pt.py::test_422_em_portugues[post-4]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 124. `tests/test_fase8_422_pt.py::test_422_em_portugues[post-5]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 125. `tests/test_fase8_422_pt.py::test_422_em_portugues[post-6]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 126. `tests/test_fase8_422_pt.py::test_422_em_portugues[put-7]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 127. `tests/test_fase8_422_pt.py::test_422_em_portugues[put-8]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 128. `tests/test_fase8_422_pt.py::test_422_em_portugues[put-9]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 129. `tests/test_fase8_422_pt.py::test_422_em_portugues[post-10]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 130. `tests/test_fase8_422_pt.py::test_422_em_portugues[post-11]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 131. `tests/test_fase8_422_pt.py::test_422_em_portugues[post-12]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 132. `tests/test_fase8_422_pt.py::test_422_em_portugues[post-13]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 133. `tests/test_fase8_422_pt.py::test_422_em_portugues[get-14]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 134. `tests/test_fase8_422_pt.py::test_422_em_portugues[post-15]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 135. `tests/test_fase8_422_pt.py::test_422_em_portugues[post-16]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 136. `tests/test_fase8_422_pt.py::test_422_em_portugues[post-17]`

- **Cenário:** F8-12 — 422 em português com o campo legível, um caso por tipo de erro (missing, tamanho, limites, parsing, literal, regra, JSON)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 137. `tests/test_fase8_422_pt.py::test_formato_e_sem_eco`

- **Cenário:** F8-13 — detail continua lista de {loc,msg,type}; input e senha digitada não são devolvidos
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 138. `tests/test_fase8_422_pt.py::test_varios_erros`

- **Cenário:** F8-14 — Vários erros no mesmo envio vêm todos, cada um com o seu campo
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 139. `tests/test_fase8_empresas.py::test_criar_ok`

- **Cenário:** T14-1 — criar_empresa feliz: empresa, configuração, login do Auth e perfil DONO criados
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 140. `tests/test_fase8_empresas.py::test_criar_desfaz[insert:empresas-500]`

- **Cenário:** T14-2 — Falha em QUALQUER passo desfaz os anteriores (empresa, configuração, login, perfil) e responde em português
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 141. `tests/test_fase8_empresas.py::test_criar_desfaz[insert:configuracoes_empresa-500]`

- **Cenário:** T14-2 — Falha em QUALQUER passo desfaz os anteriores (empresa, configuração, login, perfil) e responde em português
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 142. `tests/test_fase8_empresas.py::test_criar_desfaz[auth:create-400]`

- **Cenário:** T14-2 — Falha em QUALQUER passo desfaz os anteriores (empresa, configuração, login, perfil) e responde em português
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 143. `tests/test_fase8_empresas.py::test_criar_desfaz[insert:usuarios-500]`

- **Cenário:** T14-2 — Falha em QUALQUER passo desfaz os anteriores (empresa, configuração, login, perfil) e responde em português
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 144. `tests/test_fase8_empresas.py::test_criar_email_existente`

- **Cenário:** T14-3 — E-mail do dono já existente no Auth: 400 'Já existe um usuário com este e-mail.' e nada fica
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 145. `tests/test_fase8_empresas.py::test_criar_desfazer_falha`

- **Cenário:** T14-4 — Se o desfazer também falhar, o erro avisa que ficou pela metade (e vai para o log)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 146. `tests/test_fase8_empresas.py::test_criar_apierror`

- **Cenário:** T14-5 — APIError do banco no passo 1 continua indo para o handler global (mensagem mapeada)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 147. `tests/test_fase8_empresas.py::test_deletar_ok`

- **Cenário:** T14-6 — deletar_empresa remove os logins do Auth dos usuários DELA e só deles; solta o vínculo da auditoria
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 148. `tests/test_fase8_empresas.py::test_deletar_com_historico[clientes]`

- **Cenário:** T14-7 — Empresa com histórico (clientes, OS, lançamentos...) → 400 explicando e NADA é apagado (nem logins)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 149. `tests/test_fase8_empresas.py::test_deletar_com_historico[veiculos]`

- **Cenário:** T14-7 — Empresa com histórico (clientes, OS, lançamentos...) → 400 explicando e NADA é apagado (nem logins)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 150. `tests/test_fase8_empresas.py::test_deletar_com_historico[ordens_servico]`

- **Cenário:** T14-7 — Empresa com histórico (clientes, OS, lançamentos...) → 400 explicando e NADA é apagado (nem logins)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 151. `tests/test_fase8_empresas.py::test_deletar_com_historico[estoque]`

- **Cenário:** T14-7 — Empresa com histórico (clientes, OS, lançamentos...) → 400 explicando e NADA é apagado (nem logins)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 152. `tests/test_fase8_empresas.py::test_deletar_com_historico[transacoes_financeiras]`

- **Cenário:** T14-7 — Empresa com histórico (clientes, OS, lançamentos...) → 400 explicando e NADA é apagado (nem logins)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 153. `tests/test_fase8_empresas.py::test_deletar_404_e_master`

- **Cenário:** T14-8 — Empresa inexistente → 404; empresa com usuário master → 400; nada apagado
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 154. `tests/test_fase8_empresas.py::test_deletar_falha_no_auth_e_repete`

- **Cenário:** T14-9 — Falha ao remover um login: 502 em português, nada do banco apagado; repetir funciona (login já removido conta como feito)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 155. `tests/test_fase8_empresas.py::test_achar_auth_por_email`

- **Cenário:** T14-10 — Busca de login por e-mail lê página a página (page/per_page) e PARA ao achar; nunca list_users() solto
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 156. `tests/test_fase8_empresas.py::test_trocar_senha_usa_busca`

- **Cenário:** T14-11 — atualizar_usuario: senha de usuário sem login com este id usa a busca por e-mail (sem list_users solto)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 157. `tests/test_fase8_empresas.py::test_limites_empresa[EmpresaCreate-nome_fantasia-150]`

- **Cenário:** T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 158. `tests/test_fase8_empresas.py::test_limites_empresa[EmpresaCreate-razao_social-150]`

- **Cenário:** T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 159. `tests/test_fase8_empresas.py::test_limites_empresa[EmpresaCreate-cnpj-20]`

- **Cenário:** T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 160. `tests/test_fase8_empresas.py::test_limites_empresa[EmpresaCreate-telefone-30]`

- **Cenário:** T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 161. `tests/test_fase8_empresas.py::test_limites_empresa[EmpresaCreate-endereco-300]`

- **Cenário:** T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 162. `tests/test_fase8_empresas.py::test_limites_empresa[EmpresaCreate-nome_dono-100]`

- **Cenário:** T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 163. `tests/test_fase8_empresas.py::test_limites_empresa[EmpresaCreate-senha_dono-72]`

- **Cenário:** T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 164. `tests/test_fase8_empresas.py::test_limites_empresa[EmpresaUpdate-nome_fantasia-150]`

- **Cenário:** T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 165. `tests/test_fase8_empresas.py::test_limites_empresa[EmpresaUpdate-cnpj-20]`

- **Cenário:** T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 166. `tests/test_fase8_empresas.py::test_limites_empresa[EmpresaUpdate-telefone-30]`

- **Cenário:** T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 167. `tests/test_fase8_empresas.py::test_limites_empresa[EmpresaUpdate-endereco-300]`

- **Cenário:** T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 168. `tests/test_fase8_empresas.py::test_limites_empresa[ConfigUpdate-nome_exibicao-150]`

- **Cenário:** T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 169. `tests/test_fase8_empresas.py::test_limites_empresa[ConfigUpdate-cor_primaria-20]`

- **Cenário:** T14-12 — Schemas de empresa: limites no create, update e config; senha do dono 6..72
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 170. `tests/test_fase8_empresas.py::test_integracao_criar_e_apagar`

- **Cenário:** T14-13 — Integração: cria empresa de verdade, confere os 4 registros, apaga: tudo some (inclusive o login) e a auditoria fica sem vínculo
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 171. `tests/test_fase8_empresas.py::test_integracao_email_existente`

- **Cenário:** T14-14 — Integração: e-mail do dono que já existe no Auth → 400 em português e nenhuma empresa nem login sobra
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 172. `tests/test_fase8_empresas.py::test_retry_timeout`

- **Cenário:** T14-15 — Statement timeout (57014) ao desfazer/apagar: tenta de novo e conclui; outro erro não é repetido
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 173. `tests/test_fase8_erros_limites.py::test_erro_nao_mapeado`

- **Cenário:** F8-1 — Erro de banco desconhecido: mensagem genérica em português para o cliente, texto cru só no log
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 174. `tests/test_fase8_erros_limites.py::test_22001`

- **Cenário:** F8-2 — 22001 (texto grande demais) → 422 em português com o limite
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 175. `tests/test_fase8_erros_limites.py::test_mapeados_continuam`

- **Cenário:** F8-3 — Erros já mapeados continuam iguais (duplicado 409, obrigatório 422)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 176. `tests/test_fase8_erros_limites.py::test_limite[ClienteCreate.nome]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 177. `tests/test_fase8_erros_limites.py::test_limite[ClienteCreate.telefone]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 178. `tests/test_fase8_erros_limites.py::test_limite[ClienteCreate.cpf_cnpj]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 179. `tests/test_fase8_erros_limites.py::test_limite[ClienteUpdate.nome]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 180. `tests/test_fase8_erros_limites.py::test_limite[ClienteUpdate.telefone]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 181. `tests/test_fase8_erros_limites.py::test_limite[ClienteUpdate.cpf_cnpj]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 182. `tests/test_fase8_erros_limites.py::test_limite[VeiculoCreate.placa]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 183. `tests/test_fase8_erros_limites.py::test_limite[VeiculoCreate.modelo]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 184. `tests/test_fase8_erros_limites.py::test_limite[VeiculoCreate.marca]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 185. `tests/test_fase8_erros_limites.py::test_limite[VeiculoCreate.cor]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 186. `tests/test_fase8_erros_limites.py::test_limite[VeiculoUpdate.placa]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 187. `tests/test_fase8_erros_limites.py::test_limite[VeiculoUpdate.modelo]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 188. `tests/test_fase8_erros_limites.py::test_limite[VeiculoUpdate.marca]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 189. `tests/test_fase8_erros_limites.py::test_limite[VeiculoUpdate.cor]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 190. `tests/test_fase8_erros_limites.py::test_limite[EstoqueCreate.nome]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 191. `tests/test_fase8_erros_limites.py::test_limite[EstoqueCreate.codigo]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 192. `tests/test_fase8_erros_limites.py::test_limite[EstoqueCreate.categoria]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 193. `tests/test_fase8_erros_limites.py::test_limite[EstoqueUpdate.nome]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 194. `tests/test_fase8_erros_limites.py::test_limite[EstoqueUpdate.codigo]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 195. `tests/test_fase8_erros_limites.py::test_limite[EstoqueUpdate.categoria]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 196. `tests/test_fase8_erros_limites.py::test_limite[UsuarioCreate.nome]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 197. `tests/test_fase8_erros_limites.py::test_limite[UsuarioUpdate.nome]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 198. `tests/test_fase8_erros_limites.py::test_limite[OSItemCreate.nome_item]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 199. `tests/test_fase8_erros_limites.py::test_limite[OSItemUpdate.nome_item]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 200. `tests/test_fase8_erros_limites.py::test_limite[ConfigUpdate.whatsapp]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 201. `tests/test_fase8_erros_limites.py::test_limite[ConfigUpdate.chave_pix]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 202. `tests/test_fase8_erros_limites.py::test_limite[ConfigUpdate.inscricao_estadual]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 203. `tests/test_fase8_erros_limites.py::test_limite[CadastroRapidoRequest.nome_cliente]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 204. `tests/test_fase8_erros_limites.py::test_limite[CadastroRapidoRequest.telefone_cliente]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 205. `tests/test_fase8_erros_limites.py::test_limite[CadastroRapidoRequest.placa]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 206. `tests/test_fase8_erros_limites.py::test_limite[EscalaFolgaCreate.observacoes]`

- **Cenário:** F8-4 — Cada coluna varchar: no limite passa, 1 caractere acima → 422 (ValidationError) em create e update
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 207. `tests/test_fase8_erros_limites.py::test_email_limite`

- **Cenário:** F8-5 — E-mail de usuário acima de 255 → 422
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 208. `tests/test_fase8_erros_limites.py::test_ponto[-90--180-True]`

- **Cenário:** F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 209. `tests/test_fase8_erros_limites.py::test_ponto[90-180-True]`

- **Cenário:** F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 210. `tests/test_fase8_erros_limites.py::test_ponto[-23.5--46.6-True]`

- **Cenário:** F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 211. `tests/test_fase8_erros_limites.py::test_ponto[None-None-True]`

- **Cenário:** F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 212. `tests/test_fase8_erros_limites.py::test_ponto[90.1-0-False]`

- **Cenário:** F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 213. `tests/test_fase8_erros_limites.py::test_ponto[-90.1-0-False]`

- **Cenário:** F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 214. `tests/test_fase8_erros_limites.py::test_ponto[0-180.1-False]`

- **Cenário:** F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 215. `tests/test_fase8_erros_limites.py::test_ponto[0--180.1-False]`

- **Cenário:** F8-6 — Ponto: latitude -90..90 e longitude -180..180; fora → 422
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 216. `tests/test_fase8_erros_limites.py::test_folha[01/2026-True]`

- **Cenário:** F8-7 — Folha: mes_referencia só MM/AAAA válido
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 217. `tests/test_fase8_erros_limites.py::test_folha[12/2026-True]`

- **Cenário:** F8-7 — Folha: mes_referencia só MM/AAAA válido
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 218. `tests/test_fase8_erros_limites.py::test_folha[10/2099-True]`

- **Cenário:** F8-7 — Folha: mes_referencia só MM/AAAA válido
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 219. `tests/test_fase8_erros_limites.py::test_folha[13/2026-False]`

- **Cenário:** F8-7 — Folha: mes_referencia só MM/AAAA válido
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 220. `tests/test_fase8_erros_limites.py::test_folha[00/2026-False]`

- **Cenário:** F8-7 — Folha: mes_referencia só MM/AAAA válido
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 221. `tests/test_fase8_erros_limites.py::test_folha[1/2026-False]`

- **Cenário:** F8-7 — Folha: mes_referencia só MM/AAAA válido
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 222. `tests/test_fase8_erros_limites.py::test_folha[2026-10-False]`

- **Cenário:** F8-7 — Folha: mes_referencia só MM/AAAA válido
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 223. `tests/test_fase8_erros_limites.py::test_folha[10/26-False]`

- **Cenário:** F8-7 — Folha: mes_referencia só MM/AAAA válido
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 224. `tests/test_fase8_erros_limites.py::test_folha[outubro-False]`

- **Cenário:** F8-7 — Folha: mes_referencia só MM/AAAA válido
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 225. `tests/test_fase8_erros_limites.py::test_folha[-False]`

- **Cenário:** F8-7 — Folha: mes_referencia só MM/AAAA válido
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 226. `tests/test_fase8_erros_limites.py::test_folha[10/2026 -False]`

- **Cenário:** F8-7 — Folha: mes_referencia só MM/AAAA válido
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 227. `tests/test_fase8_erros_limites.py::test_folha[10/1999-False]`

- **Cenário:** F8-7 — Folha: mes_referencia só MM/AAAA válido
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 228. `tests/test_fase8_erros_limites.py::test_formas_pagamento`

- **Cenário:** F8-8 — Formas de pagamento: lista única (inclui TED e as do front); fora da lista → 422 em OS, lançamento, edição e baixa
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 229. `tests/test_fase8_erros_limites.py::test_leitura_de_dado_antigo`

- **Cenário:** F8-9 — Dado antigo com forma fora da lista continua sendo lido sem erro
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 230. `tests/test_fase8_erros_limites.py::test_rota_formas`

- **Cenário:** F8-10 — GET /api/v1/formas-pagamento devolve a lista (qualquer perfil logado)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 231. `tests/test_fase8_erros_limites.py::test_http_422`

- **Cenário:** F8-11 — HTTP: texto acima do limite e forma inválida chegam como 422 com mensagem
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 232. `tests/test_integracao_homologacao.py::test_guarda_recusa_empresa_de_producao`

- **Cenário:** F0-G — Guarda: testes recusam empresa de produção (Autotec Racing)
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 233. `tests/test_integracao_homologacao.py::test_dono_ve_a_propria_empresa`

- **Cenário:** T1+ — DONO da Oficina A acessa a própria empresa (controle positivo)
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/clientes/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `200`

```json
[
  {
    "nome": "Cliente Teste A",
    "telefone": "11999990001",
    "cpf_cnpj": null,
    "endereco": null,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "44e46577-443d-4c98-90d2-cd79e0123492"
  },
  {
    "nome": "Julya Lima Moreira",
    "telefone": "11978879957",
    "cpf_cnpj": null,
    "endereco": "Rua João de Sá, 240",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "a26df8a8-d7a6-4f81-a902-c26186ed18c2"
  },
  {
    "nome": "Marli",
    "telefone": "21323123123",
    "cpf_cnpj": "",
    "endereco": null,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "c94fb84a-fa0f-479d-adb2-5a617ed793e4"
  },
  {
    "nome": "TUNICO CARA DE PITO",
    "telefone": "string",
    "cpf_cnpj": "string",
    "endereco": "string",
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "3d577831-3c9d-4cfd-8b80-e028387d1fe8"
  },
  {
    "nome": "Vinicius",
    "telefone": "7181818",
    "cpf_cnpj": null,
    "endereco": null,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "514b854e-52c0-41ba-aabb-3cd6ffff27ef"
  },
  {
    "nome": "Zezinho esquilo",
    "telefone": "11976605555",
    "cpf_cnpj": "",
    "endereco": null,
    "empresa_id": "94334e9f-629c-4c65-92f8-e26274ba3973",
    "id": "7009affd-f0db-435e-bce7-39bdfb9f0a90"
  }
]
```

---

## 234. `tests/test_integracao_homologacao.py::test_dono_nao_ve_outra_empresa[clientes]`

- **Cenário:** T1 — DONO da Oficina A chamando rota com empresa_id da Oficina B → 403
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/clientes/b763e7f1-e35b-4aa4-baa8-c8d586caf705`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado a dados de outra empresa."
}
```

---

## 235. `tests/test_integracao_homologacao.py::test_dono_nao_ve_outra_empresa[veiculos]`

- **Cenário:** T1 — DONO da Oficina A chamando rota com empresa_id da Oficina B → 403
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/veiculos/b763e7f1-e35b-4aa4-baa8-c8d586caf705`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado a dados de outra empresa."
}
```

---

## 236. `tests/test_integracao_homologacao.py::test_dono_nao_ve_outra_empresa[estoque]`

- **Cenário:** T1 — DONO da Oficina A chamando rota com empresa_id da Oficina B → 403
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/estoque/b763e7f1-e35b-4aa4-baa8-c8d586caf705`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado a dados de outra empresa."
}
```

---

## 237. `tests/test_integracao_homologacao.py::test_dono_nao_ve_outra_empresa[dashboards]`

- **Cenário:** T1 — DONO da Oficina A chamando rota com empresa_id da Oficina B → 403
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/dashboards/b763e7f1-e35b-4aa4-baa8-c8d586caf705`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado a dados de outra empresa."
}
```

---

## 238. `tests/test_integracao_homologacao.py::test_mecanico_sem_financeiro`

- **Cenário:** F1 — MECÂNICO não acessa o financeiro (lado backend)
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET http://testserver/api/v1/transacoes-financeiras/94334e9f-629c-4c65-92f8-e26274ba3973`

Headers: `{"authorization": "<mascarado>"}`

**Response:** `403`

```json
{
  "detail": "Acesso negado para o seu perfil."
}
```

---

## 239. `tests/test_integracao_homologacao.py::test_anon_nao_le_nada_pela_api_rest`

- **Cenário:** F-1 — Chave anon (pública) não lê nada pela API REST do Supabase
- **Resultado:** PASSOU

### Chamada 1

**Request:** `GET https://uyoiauhiorvwwdkjyofs.supabase.co/rest/v1/clientes?select=id&limit=1`

Headers: `{"apikey": "<mascarado>", "authorization": "<mascarado>"}`

**Response:** `401`

```json
{
  "code": "42501",
  "details": null,
  "hint": "Grant the required privileges to the current role with: GRANT SELECT ON public.clientes TO anon;",
  "message": "permission denied for table clientes"
}
```

---

## 240. `tests/test_paralelismo.py::test_requisicoes_paralelas`

- **Cenário:** F3-P1 — 60 requisições simultâneas (8 rotas) com token válido: todas 200, nenhum 401/500
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 241. `tests/test_paralelismo.py::test_erro_de_infra_nao_vira_token_invalido`

- **Cenário:** F3-P2 — Falha de infraestrutura na checagem do token → 503 (a tela repete); token inválido → 401
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 242. `tests/test_tenant.py::test_bloqueia_outra_empresa`

- **Cenário:** T1 — Unitário: perfil da empresa A em rota da empresa B → 403
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 243. `tests/test_tenant.py::test_permite_propria_empresa`

- **Cenário:** T1+ — Unitário: MECÂNICO na própria empresa → 200
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 244. `tests/test_tenant.py::test_bloqueia_query_param_de_outra_empresa`

- **Cenário:** T1 — Unitário: empresa_id de outra empresa na query string → 403
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 245. `tests/test_tenant.py::test_master_acessa_qualquer_empresa`

- **Cenário:** T1-M — Unitário: master acessa qualquer empresa → 200
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._

---

## 246. `tests/test_tenant.py::test_post_usa_empresa_do_token`

- **Cenário:** F1.2 — POST grava na empresa do token, não na do body
- **Resultado:** PASSOU

_Sem chamadas HTTP (teste de função/banco)._
