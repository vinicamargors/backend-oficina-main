# Fase 4.2 — ensaio local do esquema novo e do script de migração (2026-11-16)

**Onde rodou:** Postgres embutido e descartável na máquina de desenvolvimento (pacote `pgserver`), com dois bancos:
`origem` (esquema antigo reduzido, com os defeitos reais da AutotecDB) e `destino` (`migrations/100_esquema_sp.sql`).
**Nenhum banco real foi tocado.** O Supabase foi simulado só com os papéis `anon`/`authenticated`/`service_role` e as tabelas
`auth.users`/`auth.identities` (com as colunas geradas). O que isso **não** prova está no fim.

Dados da origem: 1 oficina de teste (3 usuários: um com login, um só do Flask com senha bcrypt, um sem senha), 1 oficina real
(não deve ser copiada com `--teste`), 1 master, 2 itens de OS (um sem empresa, um com a empresa errada), 3 linhas de auditoria
(uma com empresa, uma recuperável pelo conteúdo, uma irrecuperável).

| # | Cenário | Comando / ação | Esperado | Resultado |
|---|---|---|---|---|
| E42-1 | Esquema aplica do zero | `psql -v ON_ERROR_STOP=1 -f 100_esquema_sp.sql` | sem erro | ✅ |
| E42-2 | Conferir sem gravar | `migrar_base --teste --so-conferir` | avisa os 2 usuários só do legado; mostra contagens; exit 0 | ✅ |
| E42-3 | Copiar oficinas de teste | `migrar_base --teste` | só "Teste A" + master; contagens conferidas; exit 0 | ✅ `usuarios 3, auth.users 2, os_itens 2, audit_logs 2` |
| E42-4 | Rodar de novo sem `--substituir` | `migrar_base --teste` | recusa, exit 1, nada muda | ✅ "já existe no destino" |
| E42-5 | Rodar de novo com `--substituir` | `migrar_base --teste --substituir` | apaga e copia; mesmas contagens (sem lixo da cópia anterior) | ✅ |
| E42-6 | Origem intacta | `select count(*) from audit_logs` na origem | 3 (igual a antes) | ✅ |
| E42-7 | Usuário só do Flask | `auth.users` no destino | login criado com o mesmo hash `$2b$`, e-mail em minúsculas | ✅ `flask@t.local` |
| E42-8 | Itens de OS herdam a empresa da OS | `os_itens where empresa_id = A` | 2 | ✅ |
| E42-9 | Auditoria: recuperável entra, irrecuperável fica | `audit_logs` no destino | 2 de 3 | ✅ |
| E42-10 | Plano vira assinatura | `assinaturas` | `profissional/TESTE` | ✅ |
| E42-11 | Empresa nova ganha assinatura sozinha | `insert into empresas` | 1 assinatura | ✅ |
| E42-12 | Auditoria com empresa, 1 linha por operação | insert + update de cliente | 2 linhas, todas com `empresa_id` | ✅ |
| E42-13 | Excluir OS: estorno + 1 linha de DELETE | `baixar_estoque(2)` → 3; `deletar_os_com_estorno` | estoque 4 (devolve o item da OS); 1 DELETE de OS, 2 de itens | ✅ |
| E42-14 | Estoque negativo | `update estoque set quantidade = -1` | recusado | ✅ `estoque_quantidade_check` |
| E42-15 | Cliente sem empresa | `insert into clientes` sem `empresa_id` | recusado | ✅ not-null |
| E42-16 | Escala invertida | `data_fim < data_inicio` | recusado | ✅ `escalas_periodo_valido` |
| E42-17 | Transação com tipo inválido | `tipo = 'OUTRO'` | recusado | ✅ `transacoes_financeiras_tipo_check` |
| E42-18 | Placa repetida na oficina | mesma placa, mesma empresa | recusado | ✅ `veiculos_placa_empresa_unique` |
| E42-19 | Usuário sem empresa que não é master | `cargo = 'DONO'`, sem empresa | recusado | ✅ `usuarios_empresa_ou_master` |
| E42-20 | anon não lê tabela | `set role anon; select from clientes` | permission denied | ✅ |
| E42-21 | Usuário logado não chama RPC | `set role authenticated; select baixar_estoque(...)` | permission denied | ✅ |

Testes automáticos no repositório: `tests/test_fase4_2_migracao.py` (F42-1..3, sem banco) — 3/3. Suíte completa contra a base atual: 99/99
(`testes-backend-20261116-145315.md`).

## Não verificado (fica para o ensaio no projeto novo)

- Se o papel `postgres` do Supabase aceita `SET session_replication_role = replica` e gravar em `auth.users`/`auth.identities`.
- Se o GoTrue de verdade aceita o login criado a partir do hash do Flask (aqui só conferi que a linha é gravada).
- `service_role` lendo com RLS ligado (no Supabase ele ignora RLS; no ensaio local o papel simulado não ignora).
- O backend rodando contra o esquema novo (falta o PR que troca `empresas.plano` por `assinaturas`).
- Volume real: 1.223 OS e 30 mil linhas de auditoria (aqui foram poucas linhas).
