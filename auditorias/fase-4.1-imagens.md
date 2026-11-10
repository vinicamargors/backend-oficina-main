# Fase 4.1 — verificação local das imagens (09/11/2026)

Docker Desktop local (x86_64). As imagens de produção são ARM64, construídas pelo GitHub Actions; aqui o objetivo foi validar
Dockerfiles, Caddyfile, healthchecks e o comportamento do proxy. Rede interna de teste, containers com as mesmas
restrições do compose (`--read-only`, `--cap-drop ALL`). `SUPABASE_*` falsos: nada tocou o banco real.

| Cenário do plano | Como | Resultado |
|---|---|---|
| Imagens constroem (`autotec-api` 269 MB, `autotec-web` 84 MB) | `docker build` de cada repo | passou |
| API roda como usuário não-root, FS somente leitura | `docker exec id -u` → `10001`; `--read-only --tmpfs /tmp` | passou |
| `GET /api/v1/health` pela API e pelo Caddy | `wget` de dentro do `web` → `{"status":"ok"}` | passou |
| SPA: rota desconhecida cai no `index.html` | `GET /oficina/ordens` → HTML do index | passou |
| Cache: `index.html` sem cache, `/assets/*` imutável + gzip | `no-cache`; `public, max-age=31536000, immutable`, `Content-Encoding: gzip` | passou |
| Cabeçalhos de segurança | `X-Frame-Options: DENY`, `Strict-Transport-Security`, `Referrer-Policy`; sem `Server` | passou |
| Proxy `/api` não abre rota protegida | `GET /api/v1/clientes/{empresa}` sem token → 403 | passou |
| CORS fechado por `ALLOWED_ORIGINS` | origem do app → permitida; `https://evil.example` → 400 | passou |
| Healthchecks do compose | comandos do compose rodados no container: `api hc 200`, `web hc ok` | passou |
| Troca de versão da API (restart com o web consultando a cada 0,5 s) | 30 consultas: 29 × 200 e **1 × 502** durante o restart | **ressalva** |

## Achados

1. **`cap_drop: ALL` impede o Caddy de iniciar** (`exec /usr/bin/caddy: operation not permitted`): o binário tem a
   capability `NET_BIND_SERVICE`. Corrigido no compose com `cap_add: [NET_BIND_SERVICE]` (o container de teste final subiu com isso).
2. **Um 502 durante o restart da API.** `lb_try_duration` não cobriu a janela de desligamento. O front repete GET em
   502, então a leitura se recupera; uma escrita (POST/PUT) exatamente nessa janela mostraria erro ao usuário. Mitigado
   por: deploy só quando há versão nova, as duas VMs defasadas (`RandomizedDelaySec`), e janela de ~1 s. Aceito; se incomodar,
   subir a nova API antes de derrubar a antiga (réplicas no compose).
3. **A porta publicada (`-p 18080:8080`) não respondeu do Windows host** (Docker Desktop/WSL), por isso as verificações
   foram feitas de dentro da rede do Docker. Não afeta a VM: o compose de produção não publica porta alguma.

## Não verificado aqui

- Build ARM64 (CI). `cloud-init.yaml`, `atualizar.sh` (OCI CLI/Vault, git, systemd) e o túnel da Cloudflare só
  podem ser exercitados com a conta Oracle/Cloudflare — passos B e C do plano.
- `docker compose up` completo com o `cloudflared` (precisa do token do túnel).

Testes automatizados novos: `tests/test_deploy.py` (F41-H, F41-C) → `testes-deploy-20261109-220949.md`.
