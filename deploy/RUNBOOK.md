# Runbook — AutoTec na Oracle Cloud (São Paulo)

Desenho e decisões: `PLANO_CORRECAO.md`, fase 4.1. Este arquivo é o passo a passo operacional.

```
Navegador → Cloudflare (app.mecanify.com.br) ⇢ túnel ⇢ [VM1 | VM2]: cloudflared → web (Caddy :8080) → api (:8000) → Supabase
```

Nenhuma porta aberta na VM. O container `web` (imagem do front) serve o site em `/` e repassa `/api` para a `api`.

## 1. Segredo no Vault (uma vez)

Crie **um** segredo `autotec-env` no OCI Vault (chave de software, grátis). Conteúdo, uma variável por linha:

```
SUPABASE_URL=https://<projeto>.supabase.co
SUPABASE_SERVICE_KEY=...
GEMINI_API_KEY=...
BOT_API_KEY=...
ALLOWED_ORIGINS=https://app.mecanify.com.br
# AVALIACAO_SECRET=...      # opcional: chave dos links de avaliação; sem ela deriva da SUPABASE_SERVICE_KEY (rotacionar essa chave invalida links já enviados)
TUNNEL_TOKEN=...            # token do túnel da Cloudflare
GHCR_USER=vinicamargors
GHCR_READ_TOKEN=...         # PAT clássico só com read:packages
GIT_READ_TOKEN=...          # PAT fine-grained: só o repo backend-oficina-main, Contents: read
# API_TAG=<sha>             # opcional: fixa a versão da API (rollback)
# WEB_TAG=<sha>             # opcional: fixa a versão do front
```

Rotacionar um segredo = editar a versão no Vault. As VMs pegam sozinhas em até ~3 min.
Copie o OCID do segredo para `SECRET_OCID` em `deploy/cloud-init.yaml`.

## 2. Cloudflare (uma vez)

1. Zero Trust → Networks → Tunnels → criar `autotec`; copie o token para `TUNNEL_TOKEN`.
2. Public hostname: `app.mecanify.com.br` → serviço `http://web:8080`.
3. O DNS do `mecanify.com.br` precisa estar na Cloudflare. O registro do app é criado pelo túnel.

## 3. Oracle (uma vez)

- Compartment `autotec`; Budget de US$ 1 com alerta; quotas (só `VM.Standard.A1.Flex` ≤ 2 OCPU / 12 GB, 0 LB).
- VCN com subnet pública e security list **sem ingress** da internet; Bastion para acesso.
- Dynamic group das VMs (`instance.compartment.id = '<ocid>'`) + política:
  `Allow dynamic-group autotec-vms to read secret-bundles in compartment autotec where target.secret.id = '<ocid do segredo>'`
- 2 VMs `VM.Standard.A1.Flex`, 1 OCPU / 6 GB, Ubuntu 24.04 aarch64, boot 50 GB, user-data = `deploy/cloud-init.yaml`,
  em fault domains diferentes. *Out of host capacity*: esperar e tentar de novo (São Paulo tem 1 AD só).

## 4. Dia a dia

- **Deploy:** merge na `main` dos repos back/front → CI publica a imagem → cada VM atualiza em ≤ ~5 min.
- **Rollback:** no segredo do Vault, `API_TAG=<sha anterior>` (e/ou `WEB_TAG`). Para voltar a seguir a `main`, apague a linha.
- **Logs:** `sudo docker compose -f /opt/autotec/deploy/docker-compose.yml logs -f api` (via Bastion).
- **Status do deploy:** `systemctl status autotec-deploy.service` e `journalctl -u autotec-deploy -n 50`.
- **VM quebrada:** não conserte, recrie com o mesmo `cloud-init.yaml` (~10 min).

## 6. Backup diário do banco (Fase 4.2)

`deploy/backup.sh` roda todo dia às 03:00 (Brasília) pelo `autotec-backup.timer`, instalado pelo próprio `atualizar.sh`. Faz `pg_dump` dos
schemas `public` e `auth` (dados + logins), confere o arquivo e sobe para o bucket. As duas VMs rodam; o nome do arquivo é o dia, então a
segunda só sobrescreve a primeira.

Configuração (uma vez, antes do corte):

1. Bucket privado `autotec-backups` no compartment `autotec` (Standard, sem acesso público).
2. Regra de ciclo de vida do bucket: apagar objetos com prefixo `mecanify/` após **30 dias**.
3. Política: `Allow dynamic-group autotec-vms to manage objects in compartment autotec where target.bucket.name = 'autotec-backups'`
   (e `read buckets` para o `os ns get`/listagem).
4. No segredo do Vault, duas linhas novas (o valor da primeira é a conexão **Session pooler** do projeto, com a senha do banco; fica só no Vault):
   ```
   BACKUP_DB_URL=postgresql://postgres.<ref>:<senha>@aws-1-sa-east-1.pooler.supabase.com:5432/postgres
   BACKUP_BUCKET=autotec-backups
   ```
   Atenção: o `api.env` inteiro vai para o container da API; ele passa a enxergar `BACKUP_DB_URL`. Trocar a senha do banco = editar o Vault.
5. Conferir: `sudo systemctl start autotec-backup.service && journalctl -u autotec-backup -n 20` deve terminar com `backup ok: ...`.

**Teste de restauração** (uma vez antes do corte e uma vez por mês): `sudo /opt/autotec/deploy/restaurar-teste.sh`. Restaura o último backup num
Postgres descartável e compara as contagens com o banco vivo. Termina com código 0 só se todas baterem; diferença pequena logo depois de alguém
gravar é normal, tabela vazia ou muito menor não é.

Backup falhou: `journalctl -u autotec-backup -n 50`. Sem alarme ainda (item da 4.1: alarme por e-mail quando o arquivo do dia não existir).

## 5. Verificação rápida

```bash
curl -fsS https://app.mecanify.com.br/api/v1/health      # {"status":"ok"}
curl -fsSI https://app.mecanify.com.br/ | grep -i -E "x-frame|strict-transport|cache-control"
```
