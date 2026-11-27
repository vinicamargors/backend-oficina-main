#!/usr/bin/env bash
# Teste de restauracao: baixa o backup mais recente (ou usa o arquivo dado), restaura num Postgres descartavel
# e compara as contagens com o banco vivo. Rodar na VM, a mao, pelo menos uma vez por mes.
# Uso: sudo /opt/autotec/deploy/restaurar-teste.sh [arquivo.dump]
set -euo pipefail

source /etc/autotec/vm.conf
set -a; source /etc/autotec/api.env; set +a
: "${BACKUP_DB_URL:?falta BACKUP_DB_URL no segredo do Vault}"

umask 077
dir="$(mktemp -d /var/tmp/restaura.XXXXXX)"
nome="restaura-teste-$$"
trap 'docker rm -f "$nome" >/dev/null 2>&1 || true; rm -rf "$dir"' EXIT

arq="${1:-}"
if [ -z "$arq" ]; then
  : "${BACKUP_BUCKET:?falta BACKUP_BUCKET no segredo do Vault}"
  ns="$(/opt/oci/bin/oci os ns get --auth instance_principal --query data --raw-output)"
  ultimo="$(/opt/oci/bin/oci os object list --auth instance_principal --namespace-name "$ns" --bucket-name "$BACKUP_BUCKET" \
    --prefix mecanify/ --all --query 'max(data[*].name)' --raw-output)"
  [ -n "$ultimo" ] || { echo "nenhum backup no bucket" >&2; exit 1; }
  arq="$dir/ultimo.dump"
  /opt/oci/bin/oci os object get --auth instance_principal --namespace-name "$ns" --bucket-name "$BACKUP_BUCKET" \
    --name "$ultimo" --file "$arq" >/dev/null
  echo "restaurando $ultimo"
fi

docker run -d --name "$nome" -e POSTGRES_PASSWORD=teste postgres:17-alpine >/dev/null
for _ in $(seq 1 30); do docker exec "$nome" pg_isready -U postgres >/dev/null 2>&1 && break; sleep 1; done
sql() { docker exec -i "$nome" psql -U postgres -v ON_ERROR_STOP=1 "$@"; }
# O Supabase guarda as extensoes no schema "extensions"; as tabelas podem referenciar isso.
sql -c 'create schema extensions; create extension "uuid-ossp" schema extensions; create extension pgcrypto schema extensions;' >/dev/null

docker exec -i "$nome" pg_restore -U postgres -d postgres --no-owner --no-privileges < "$arq" 2> "$dir/erros.txt" || true
echo "erros do pg_restore: $(grep -c . "$dir/erros.txt" || true)"; head -n 10 "$dir/erros.txt"

tabelas="public.empresas public.usuarios public.clientes public.veiculos public.ordens_servico public.os_itens public.audit_logs auth.users"
ruim=0
for t in $tabelas; do
  restaurado="$(sql -Atc "select count(*) from $t")"
  vivo="$(docker run --rm -e "PGURL=$BACKUP_DB_URL" postgres:17-alpine sh -c "psql \"\$PGURL\" -Atc 'select count(*) from $t'")"
  [ "$restaurado" = "$vivo" ] && marca=ok || { marca="DIFERENTE"; ruim=1; }
  printf '%-28s backup=%-8s vivo=%-8s %s\n' "$t" "$restaurado" "$vivo" "$marca"
done
# Diferenca pequena e normal se alguem gravou depois do backup; diferenca grande ou tabela vazia nao.
exit "$ruim"
