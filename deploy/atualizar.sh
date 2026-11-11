#!/usr/bin/env bash
# Roda a cada ~2 min por autotec-deploy.timer (e uma vez no boot). Idempotente: sem versão nova, não reinicia nada.
# Passos: 1) lê o segredo do Vault  2) atualiza o repositório de deploy  3) puxa imagens  4) sobe o que mudou.
set -euo pipefail

source /etc/autotec/vm.conf      # SECRET_OCID, REPO_URL, GIT_BRANCH (escrito pelo cloud-init)
umask 077

# 1) Vault -> /etc/autotec/api.env (formato KEY=VALUE, um por linha). Rotacionar segredo = editar no Vault.
tmp="$(mktemp /etc/autotec/.api.env.XXXXXX)"
/opt/oci/bin/oci secrets secret-bundle get --secret-id "$SECRET_OCID" --auth instance_principal \
  --query 'data."secret-bundle-content".content' --raw-output | base64 -d > "$tmp"
mv "$tmp" /etc/autotec/api.env

# shellcheck disable=SC1091
set -a; source /etc/autotec/api.env; set +a

# 2) compose e este script vêm do repositório. GIT_READ_TOKEN (só leitura) é opcional: repositório público dispensa.
ORIGEM="https://${GIT_READ_TOKEN:+x-access-token:${GIT_READ_TOKEN}@}${REPO_URL}"
if [ ! -d /opt/autotec/.git ]; then
  git clone --branch "$GIT_BRANCH" "$ORIGEM" /opt/autotec
fi
git -C /opt/autotec remote set-url origin "$ORIGEM"
git -C /opt/autotec fetch --quiet origin "$GIT_BRANCH"
git -C /opt/autotec reset --quiet --hard "origin/$GIT_BRANCH"

# 3) e 4) imagens. API_TAG / WEB_TAG (no segredo) fixam uma versão para rollback; sem elas, segue a main.
# GHCR_READ_TOKEN também é opcional: imagens públicas no GHCR são baixadas sem login.
if [ -n "${GHCR_READ_TOKEN:-}" ]; then
  echo "$GHCR_READ_TOKEN" | docker login ghcr.io -u "$GHCR_USER" --password-stdin >/dev/null
fi
cd /opt/autotec/deploy
docker compose pull --quiet
docker compose up -d --remove-orphans
docker image prune -f >/dev/null
