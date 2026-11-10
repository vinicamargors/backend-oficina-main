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

## 5. Verificação rápida

```bash
curl -fsS https://app.mecanify.com.br/api/v1/health      # {"status":"ok"}
curl -fsSI https://app.mecanify.com.br/ | grep -i -E "x-frame|strict-transport|cache-control"
```
