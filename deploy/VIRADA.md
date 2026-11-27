# Roteiro da virada — AutotecDB → `mecanify` (São Paulo)

Janela: **30/11/2026, 03:00**. Quem dispara e troca os segredos: o dono. Desenho e decisões: `PLANO_CORRECAO.md`, fase 4.2.
Regra da noite: **nada na Autotec Racing se escreve na AutotecDB** (o script só lê dela); só se escreve no `mecanify`.

## Antes (até 29/11)

- [ ] T-014 e #16 (plano em `assinaturas`) na `main` com QA PASSOU; imagens da API e do front construídas. Anotar o `sha` de cada uma.
- [ ] Backup diário rodando e **restauração testada** (RUNBOOK, seção 6): `restaurar-teste.sh` termina com código 0.
- [ ] Projeto `mecanify` (Auth): *Site URL* = `https://app.mecanify.com.br`, redirects e templates de e-mail iguais aos da AutotecDB.
  O e-mail embutido do Supabase gratuito manda poucos e-mails por hora; se a recuperação de senha for usada no dia, configurar SMTP.
- [ ] Ensaio geral: repetir a cópia com `--substituir` para ver o tempo total e as contagens (leva minutos; pode ser feito em qualquer dia).
- [ ] Preparar, sem aplicar, os valores novos: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` (do `mecanify`), `API_TAG`/`WEB_TAG`.
- [ ] Front: as chaves entram **na hora do build** (`VITE_SUPABASE_URL` e `VITE_SUPABASE_ANON_KEY`, em GitHub → frontend → Settings → Variables).
  Trocar as variáveis e rodar o CI na `main` gera a imagem nova; **não dá para trocar só no Vault**.
- [ ] Combinar com o tio: sistema fora do ar ~1 hora a partir das 03:00.

## Na noite

1. **Flask fora do ar** (onde estiver hospedado). A partir daqui ninguém grava na AutotecDB.
2. **Cópia de segurança da AutotecDB** (rollback): `docker run --rm -e PGURL="$ORIGEM_DB_URL" postgres:17-alpine sh -c 'pg_dump "$PGURL" -Fc --no-owner' > autotecdb-virada.dump`
   e guardar o arquivo fora da VM.
3. **Cópia final** (no PowerShell do dono, com `ORIGEM_DB_URL` e `DESTINO_DB_URL` preenchidos como nos ensaios):
   ```powershell
   python scripts\migrar_base.py --empresa caabdcdd-f537-42a6-8db1-35cb02257284 --so-conferir
   python scripts\migrar_base.py --empresa caabdcdd-f537-42a6-8db1-35cb02257284 --substituir
   ```
   Com a auditoria inteira (sem `--sem-auditoria`). As contagens do fim têm que bater com as do `--so-conferir`.
4. **Trocar os segredos**: no Vault, `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `BACKUP_DB_URL` (se ainda não estiver) e fixar `API_TAG`/`WEB_TAG`
   nos `sha` anotados. As VMs pegam sozinhas em até ~3 min. Conferir:
   ```bash
   curl -fsS https://app.mecanify.com.br/api/v1/health
   ```
5. **Fumaça** (só leitura na Autotec Racing; escrita só em empresa de teste):
   - entrar com o dono da Autotec Racing e com um mecânico; ver clientes, veículos, uma OS antiga e o estoque;
   - `pytest tests/test_integracao_homologacao.py -q` com `TESTES_BASE=mecanify`;
   - conferir os totais na tela contra o `--so-conferir` do passo 3.
6. **Liberar**: avisar o tio. Todos precisam entrar de novo (a chave de sessão é outra; as senhas continuam as mesmas).

## Voltar atrás

- **Antes do passo 6** (ninguém gravou no `mecanify`): no Vault, devolver `SUPABASE_URL` e a chave de serviço da AutotecDB e apagar `API_TAG`/`WEB_TAG`;
  religar o Flask. A AutotecDB não foi alterada.
- **Depois do passo 6** voltar custa dados: o que foi lançado no `mecanify` não existe na AutotecDB. Decidir com o dono antes; a saída normal é
  corrigir para frente, não voltar.

## Depois

- [ ] Flask desligado de vez; AutotecDB sem gravação de ninguém.
- [ ] Ligar a restauração noturna `mecanify` → AutotecDB (só agora; antes apagaria dados do Flask). Tarefa própria, ainda não escrita.
- [ ] Rotacionar as chaves e a senha do banco da AutotecDB; guardar as novas no gerenciador de senhas.
- [ ] 03:00 do dia seguinte: conferir que o backup do `mecanify` foi para o bucket; rodar o `restaurar-teste.sh`.
- [ ] Redefinir a senha dos 2 usuários que não tinham senha no Flask (o mestre da plataforma e o dono da TETECA).
