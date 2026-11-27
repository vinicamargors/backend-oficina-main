#!/usr/bin/env bash
# Backup diario do banco (Fase 4.2): pg_dump -> Object Storage da Oracle. Roda pelo autotec-backup.timer (03:00 de Brasilia).
# Precisa no segredo do Vault: BACKUP_DB_URL (postgresql://... da conexao Session pooler do projeto) e BACKUP_BUCKET.
# Os 30 dias de retencao sao uma regra do proprio bucket (RUNBOOK, secao 6), nao deste script.
set -euo pipefail

source /etc/autotec/vm.conf
set -a; source /etc/autotec/api.env; set +a
: "${BACKUP_DB_URL:?falta BACKUP_DB_URL no segredo do Vault}"
: "${BACKUP_BUCKET:?falta BACKUP_BUCKET no segredo do Vault}"

umask 077
dia="$(date -u +%F)"
dir="$(mktemp -d /var/tmp/backup.XXXXXX)"
trap 'rm -rf "$dir"' EXIT
arq="$dir/mecanify-$dia.dump"
PG=(docker run --rm -i -e "PGURL=$BACKUP_DB_URL" postgres:17-alpine)   # pg_dump precisa ser >= a versao do servidor (17)

# public = os dados; auth = logins e senhas. Formato custom (-Fc): comprimido e restauravel por tabela.
"${PG[@]}" sh -c 'pg_dump "$PGURL" -Fc --no-owner --no-privileges -n public -n auth' > "$arq"

# Conferencia: um dump vazio ou cortado nao pode subir como se fosse backup bom.
"${PG[@]}" pg_restore --list < "$arq" > "$dir/lista.txt"
grep -q "TABLE DATA public empresas" "$dir/lista.txt" || { echo "dump sem a tabela empresas: abortado" >&2; exit 1; }
grep -q "TABLE DATA auth users" "$dir/lista.txt" || { echo "dump sem auth.users: abortado" >&2; exit 1; }

ns="$(/opt/oci/bin/oci os ns get --auth instance_principal --query data --raw-output)"
/opt/oci/bin/oci os object put --auth instance_principal --namespace-name "$ns" --bucket-name "$BACKUP_BUCKET" \
  --name "mecanify/mecanify-$dia.dump" --file "$arq" --force >/dev/null
echo "backup ok: mecanify/mecanify-$dia.dump ($(stat -c %s "$arq") bytes)"
