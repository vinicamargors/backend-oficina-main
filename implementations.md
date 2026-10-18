# 🛠️ Plano de Implementação — Auditoria Ponytail & Revisão Crítica de Segurança

> **Documento Atualizado:** 14/10/2026  
> **Escopo:** Backend Oficina (`c:\Projects\backend-oficina-main`)  
> **Filosofia:** *Lazy Senior Dev Mode* — O melhor código é aquele que não precisa ser escrito. Redução de diff, eliminação de código morto, uso de stdlib e recursos nativos da plataforma (Supabase/PostgreSQL/FastAPI). Segurança e integridade de dados são inegociáveis.  
> **Status:** Consolidado com Auditoria Ponytail, Revisão de Segurança (Argon) e 5 Guardas de Produção.

---

## ⚠️ 5 ARMADILHAS SILENCIOSAS DE PRODUÇÃO (LEITURA OBRIGATÓRIA ANTES DE CODIFICAR)

Para não quebrar o sistema que já está rodando, as seguintes regras são **mandatórias**:

1. **A rota `GET /api/v1/usuarios/me` e a chave `"sub"`:**
   - *Risco:* No código original, `/me` fazia `user_id = usuario_logado.get("sub")`. O novo `validar_passaporte` busca o perfil em `usuarios`. Se retornar um dict sem `"sub"` e `/me` continuar buscando `"sub"`, `/me` quebra.
   - *Solução Ponytail:* `validar_passaporte` faz `.select("*")` na tabela `usuarios` e devolve o perfil completo. Na rota `/me`, **retornamos o próprio `usuario_logado` diretamente**, eliminando a query duplicada `obter_perfil_logado` e preenchendo perfeitamente o schema `UsuarioResponse`!

2. **`db_data` montado à mão em `criar_usuario` (`modules/usuarios/service.py`):**
   - *Risco:* `criar_usuario` não usa `dados.model_dump()`, mas monta o dict chave a chave. Colocar `telefone` apenas em `schemas.py` não salva o telefone no banco.
   - *Solução:* Adicionar explicitamente `"telefone": limpar_telefone(dados.telefone) if dados.telefone else None` dentro do `db_data` no `service.py`, e também sanitizar no `atualizar_usuario`.

3. **O Trigger de Auditoria no Postgres perde o `motivo_exclusao` da OS:**
   - *Risco:* No `deletar_os`, o `motivo_exclusao` é injetado em memória em Python (`os_atual["motivo_exclusao"] = motivo_exclusao`) para o log de auditoria. O trigger do Postgres em `DELETE` só lê `to_jsonb(OLD)`, que não tem essa coluna. A exportação de logs (`modules/logs/service.py`) ficaria sem o motivo.
   - *Solução:* Manter a inserção explícita em `audit_logs` **especificamente na função `deletar_os`**, garantindo que o motivo seja registrado no histórico sem depender de trigger para esse caso específico.

4. **Busca com Join em `listar_os` (Cuidado com `.or_()` do PostgREST):**
   - *Risco:* PostgREST **não aceita** `.or_()` global envolvendo colunas de tabelas filhas do join (`clientes.nome`, `veiculos.placa`), e dá erro ao rodar `.ilike()` em UUID.
   - *Solução:* **Manter a busca em memória** atual para o modo `if search:`, garantindo que o cruzamento por placa, cliente e descrição continue funcionando perfeitamente sem quebrar a API.

5. **Upsert em `configuracoes_empresa` (`modules/empresas/service.py`):**
   - *Risco:* A tabela tem `id` como PK, mas `atualizar_configuracoes` só tem `empresa_id`. Um `.upsert(campos)` sem parâmetro tenta bater no `id`.
   - *Solução:* Usar `.upsert(campos, on_conflict="empresa_id")` (se houver UNIQUE constraint) ou manter o pattern enxuto `select id -> update/insert` seguro.

---

## 🚨 FASE 0: Segurança Crítica & Correção de Bugs (Prioridade Zero)

### 0.1 Blindagem de Autenticação & Autorização (Fim do `x_cargo` via Header)
- **Problema:** Rotas decidem privilégios lendo `x_cargo: str = Header(...)`. Qualquer usuário enviando `x-cargo: master` acessa o caixa, logs e outras oficinas. Além disso, `modules/usuarios/router.py` foi declarado sem `Depends(validar_passaporte)`, deixando criação de usuários (com `supabase_admin`) aberta ao público.
- **Solução Ponytail:**
  1. `core/security.py`: `validar_passaporte` valida o JWT no Supabase e busca o perfil completo (`*`) em `usuarios` (`id`, `empresa_id`, `cargo`, `ativo`, `nome`, `email`, `telefone`).
  2. `exigir_cargos(*cargos)`: dependência que valida `usuario["cargo"] in cargos`. NUNCA lê header.
  3. Proteger `modules/usuarios/router.py` com `dependencies=[Depends(validar_passaporte)]`.
  4. Na rota `GET /me`, devolver direto o `usuario_logado` retornado pelo `validar_passaporte`.
  5. Criar `validar_chave_bot` exigindo header `X-Bot-Key == os.getenv("BOT_API_KEY")` em `modules/bot/router.py`.

```python
# core/security.py
import os
import re
from fastapi import HTTPException, Security, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.database import supabase

seguranca_armada = HTTPBearer()

def limpar_telefone(tel: str) -> str:
    """Remove caracteres não numéricos do telefone"""
    return re.sub(r"\D", "", tel) if tel else ""

def validar_passaporte(credentials: HTTPAuthorizationCredentials = Security(seguranca_armada)):
    token = credentials.credentials
    try:
        auth_response = supabase.auth.get_user(token)
        user_id = auth_response.user.id
        
        perfil = supabase.table("usuarios").select("*").eq("id", user_id).execute().data
        if not perfil or not perfil[0].get("ativo"):
            raise HTTPException(status_code=403, detail="Usuário inativo ou sem perfil vinculado.")
            
        return perfil[0] # Retorna o perfil completo direto do banco
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Passaporte rejeitado. Token inválido ou expirado.")

def exigir_cargos(*cargos_permitidos: str):
    def dependency(usuario: dict = Depends(validar_passaporte)):
        if usuario.get("cargo") not in cargos_permitidos:
            raise HTTPException(status_code=403, detail="Acesso negado para o seu perfil.")
        return usuario
    return dependency

def validar_chave_bot(x_bot_key: str = Header(...)):
    bot_key = os.getenv("BOT_API_KEY")
    if not bot_key or x_bot_key != bot_key:
        raise HTTPException(status_code=403, detail="Acesso não autorizado ao módulo do Bot.")
```

---

### 0.2 Blindagem Multi-Tenant (Combate a IDOR)
- **Problema:** `modules/os/service.py` atualiza e deleta OS e itens sem amarrar `empresa_id` (`.update().eq("id", os_id)`). Usuários de uma oficina podem alterar registros de outra.
- **Solução:** Adicionar `.eq("empresa_id", empresa_id)` obrigatoriamente em todos os `update` e `delete` de `ordens_servico` e `os_itens`.
- **Validação de Inquilino:** Se `usuario["cargo"] != "master"`, validar `str(empresa_id) == str(usuario["empresa_id"])`.

---

### 0.3 Eliminação de `IndexError` (Crash 500)
- **Problema:** O código acessa `.data[0]` diretamente sem verificar se a lista está vazia em `usuarios/service.py:34`, `os/service.py:88, 98, 107, 124, 146, 160`, e `empresas/service.py:80`. Se o registro não existir, estoura `IndexError` (HTTP 500).
- **Solução:** Guard pattern limpo de 1 linha:
  ```python
  res = supabase.table("...").select("*").eq("id", id).execute()
  if not res.data:
      raise HTTPException(status_code=404, detail="Registro não encontrado.")
  registro = res.data[0]
  ```

---

### 0.4 Correções Críticas no Chatbot (`modules/bot`)
1. **Nome da coluna do problema:**
   - Em `bot/service.py:157`, trocar `campos["problema_relatado"]` por `campos["descricao_problema"]` para bater com o schema e banco de `ordens_servico`.
2. **Nome da coluna do mecânico:**
   - Em `bot/service.py:117, 148`, trocar `"usuario_id": req.mecanico_id` por `"mecanico_responsavel_id": req.mecanico_id`.
3. **Telefone em `modules/usuarios/schemas.py` & `service.py`:**
   - Adicionar `telefone: Optional[str] = None` em `UsuarioBase`, `UsuarioCreate` e `UsuarioUpdate`.
   - Em `criar_usuario`, incluir `"telefone": limpar_telefone(dados.telefone)` no dicionário `db_data`.
4. **Idempotência no `/cadastro-rapido`:**
   - Se a placa já existir na empresa, reaproveitar o veículo e cliente existentes em vez de estourar 409 Conflict.
5. **Sanitização de telefone:**
   - Higienizar o telefone (`limpar_telefone`) tanto no cadastro de usuário quanto na consulta do bot `identificar_mecanico`.

---

## 📊 Scorecard da Otimização Ponytail

| Métrica | Situação Atual | Pós-Implementação | Redução Estimada |
| :--- | :--- | :--- | :--- |
| **Linhas de Código** | ~1.650 linhas | ~1.300 linhas | **-350 linhas (-21%)** |
| **Roundtrips de Banco por Operação** | 2 a 3 por CRUD | 1 por CRUD | **-50% a -66% de I/O** |
| **Tabelas / Middlewares Manuais** | APM próprio em Postgres | Métricas Nativas / Logs | **1 middleware e 1 tabela a menos** |
| **Complexidade Algorítmica (Financeiro)** | $O(6 \times N)$ com re-parse de data | $O(N)$ passo único | **Economia de CPU e latência** |
| **Vulnerabilidades Críticas (x_cargo / IDOR)** | 5 routers vulneráveis | 0 (blindado no banco/token) | **100% resolvido** |

---

## 🎯 Lista Ranqueada de Achados Ponytail

1. `native` **Auditoria manual via queries Python e pre-fetch `estado_anterior`.**  
   *O que cortar:* `core/audit.py`, função `salvar_audit_log` e todas as chamadas `estado_anterior = obter_*(...)` espalhadas pelos services (`clientes`, `veiculos`, `estoque`, `usuarios`, `os`), mantendo insert explícito apenas em `deletar_os` para salvar o `motivo_exclusao`.  
   *Substituto:* Trigger nativo em PostgreSQL no Supabase gravando `to_jsonb(OLD)` e `to_jsonb(NEW)` automaticamente.  
   *Local:* `[core/audit.py, modules/clientes/service.py, modules/veiculos/service.py, modules/estoque/service.py, modules/usuarios/service.py, modules/os/service.py]`  
   *Economia:* **-85 linhas**

2. `yagni` **Middleware de APM caseiro gravando latência de requisições no Supabase via HTTP síncrono.**  
   *O que cortar:* `core/apm.py` (executa `.insert().execute()` bloqueante a cada request HTTP) e `modules/monitoramento/router.py`.  
   *Substituto:* Dashboard nativo de métricas do Supabase / métricas padrão do Uvicorn e FastAPI.  
   *Local:* `[core/apm.py, modules/monitoramento/router.py, main.py:7,37,51]`  
   *Economia:* **-86 linhas**

3. `native` **Download de áudio, escrita temporária em disco e ciclo de upload/delete na API de arquivos do Gemini.**  
   *O que cortar:* `tempfile.mkstemp()`, `os.fdopen()`, `gemini_client.files.upload()`, `os.remove()`, e `gemini_client.files.delete()`.  
   *Substituto:* `types.Part.from_bytes(data=resp.content, mime_type="audio/ogg")` direto no `generate_content`.  
   *Local:* `[modules/bot/service.py:182-189, 234-241]`  
   *Economia:* **-25 linhas**

4. `shrink` **6 varreduras repetidas em memória com múltiplos `datetime.fromisoformat` no histórico financeiro.**  
   *O que cortar:* Loop aninhado `for i in range(5, -1, -1): for os in os_data:` reprocessando strings ISO.  
   *Substituto:* Agrupamento em um único loop usando `collections.defaultdict`.  
   *Local:* `[modules/financeiro/service.py:49-83]`  
   *Economia:* **-30 linhas**

5. `yagni` **Funções de verificação de permissão e leitura de header duplicadas em 5 routers.**  
   *O que cortar:* `check_master` e `verificar_permissao` declarados localmente em `empresas`, `usuarios`, `logs`, `financeiro` e `monitoramento`.  
   *Substituto:* Dependência `exigir_cargos("master", "DONO")` em `core/security.py`.  
   *Local:* `[modules/empresas/router.py, modules/usuarios/router.py, modules/logs/router.py, modules/financeiro/router.py, modules/monitoramento/router.py]`  
   *Economia:* **-25 linhas**

6. `delete` **Recálculo financeiro inútil de OS durante remoção de itens em cascata.**  
   *O que cortar:* `recalcular_totais_os(os_id)` chamado a cada item deletado dentro de `deletar_os()`, logo antes de apagar a própria OS do banco.  
   *Substituto:* Deletar os itens diretamente sem disparar recálculos matemáticos descartáveis.  
   *Local:* `[modules/os/service.py:150, 157]`  
   *Economia:* **-15 linhas**

7. `native` **Queries manuais de verificação de duplicidade antes do INSERT.**  
   *O que cortar:* `duplicado = supabase.table(...).select("id")...` em veículos e estoque.  
   *Substituto:* Deixar a constraint UNIQUE do Postgres agir; o `core/errors.py` já captura o erro `23505` e devolve 409 formatado.  
   *Local:* `[modules/veiculos/service.py:48-51, modules/estoque/service.py:38-41]`  
   *Economia:* **-14 linhas**

8. `yagni` **Lógica de sincronização de KM do veículo duplicada no serviço do bot.**  
   *O que cortar:* `select` e `update` manual de KM em `veiculos` dentro de `bot/service.py`.  
   *Substituto:* Chamar `modules.os.service.atualizar_os` já existente.  
   *Local:* `[modules/bot/service.py:162-167]`  
   *Economia:* **-8 linhas**

9. `shrink` **Download de todos os IDs apenas para calcular `len()` em estatísticas.**  
   *O que cortar:* `len(supabase.table(...).select("id")...data)` para clientes, veículos e ordens.  
   *Substituto:* Parâmetro nativo `count="exact", head=True` do PostgREST (`response.count`).  
   *Local:* `[modules/empresas/service.py:85-89]`  
   *Economia:* **-6 linhas**

10. `shrink` **Escada de 35 linhas de `if/elif` em `core/errors.py`.**  
    *O que cortar:* Checagem sequencial de strings de erro.  
    *Substituto:* Dicionário de mapeamento `{ "código_pg": (status_code, "mensagem") }`.  
    *Local:* `[core/errors.py:12-46]`  
    *Economia:* **-20 linhas**

11. `stdlib` **Contador manual de status de OS com loop e dicionário.**  
    *O que cortar:* Dicionário pré-alocado e laço de incremento para status de OS.  
    *Substituto:* `collections.Counter(os.get("status") for os in os_data)`.  
    *Local:* `[modules/dashboards/service.py:7-13]`  
    *Economia:* **-6 linhas**

12. `shrink` **Instanciação avulsa de `httpx.AsyncClient` a cada requisição externa.**  
    *O que cortar:* Blocos `async with httpx.AsyncClient() as client:` repetidos.  
    *Substituto:* Instância compartilhada em nível de módulo ou dependência reutilizável.  
    *Local:* `[modules/veiculos/service.py:14, modules/bot/service.py:178]`  
    *Economia:* **-4 linhas**

13. `delete` **Chamada redundante de `load_dotenv()` no módulo de bot.**  
    *O que cortar:* `from dotenv import load_dotenv; load_dotenv()` dentro de `bot/service.py`.  
    *Substituto:* Centralizado no `core/database.py` ou `main.py`.  
    *Local:* `[modules/bot/service.py:8, 16]`  
    *Economia:* **-2 linhas**

14. `delete` **Arquivo binário de áudio de teste na raiz do projeto.**  
    *O que cortar:* Arquivo `audio_teste.ogg` (45 KB) deixado na raiz.  
    *Substituto:* Nada (remover do repositório).  
    *Local:* `[audio_teste.ogg]`  
    *Economia:* **-45 KB**

---

## 📋 Detalhamento das Fases de Execução

### FASE 1: Triggers de Auditoria no PostgreSQL (Eliminação de `core/audit.py`)
Executar no SQL Editor do Supabase:

```sql
CREATE OR REPLACE FUNCTION process_audit_log()
RETURNS TRIGGER AS $$
DECLARE
    v_empresa_id UUID;
BEGIN
    IF (TG_OP = 'DELETE') THEN
        v_empresa_id := OLD.empresa_id;
        INSERT INTO audit_logs (tabela, operacao, registro_id, empresa_id, dados_antes, dados_depois)
        VALUES (TG_TABLE_NAME, TG_OP, OLD.id::text, v_empresa_id, to_jsonb(OLD), NULL);
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        v_empresa_id := NEW.empresa_id;
        INSERT INTO audit_logs (tabela, operacao, registro_id, empresa_id, dados_antes, dados_depois)
        VALUES (TG_TABLE_NAME, TG_OP, NEW.id::text, v_empresa_id, to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        v_empresa_id := NEW.empresa_id;
        INSERT INTO audit_logs (tabela, operacao, registro_id, empresa_id, dados_antes, dados_depois)
        VALUES (TG_TABLE_NAME, TG_OP, NEW.id::text, v_empresa_id, NULL, to_jsonb(NEW));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS trg_audit_clientes ON public.clientes;
DROP TRIGGER IF EXISTS trg_audit_veiculos ON public.veiculos;
DROP TRIGGER IF EXISTS trg_audit_estoque ON public.estoque;
DROP TRIGGER IF EXISTS trg_audit_usuarios ON public.usuarios;
DROP TRIGGER IF EXISTS trg_audit_os ON public.ordens_servico;

CREATE TRIGGER trg_audit_clientes AFTER INSERT OR UPDATE OR DELETE ON public.clientes FOR EACH ROW EXECUTE FUNCTION process_audit_log();
CREATE TRIGGER trg_audit_veiculos AFTER INSERT OR UPDATE OR DELETE ON public.veiculos FOR EACH ROW EXECUTE FUNCTION process_audit_log();
CREATE TRIGGER trg_audit_estoque AFTER INSERT OR UPDATE OR DELETE ON public.estoque FOR EACH ROW EXECUTE FUNCTION process_audit_log();
CREATE TRIGGER trg_audit_usuarios AFTER INSERT OR UPDATE OR DELETE ON public.usuarios FOR EACH ROW EXECUTE FUNCTION process_audit_log();
-- Em ordens_servico, o DELETE já faz o insert explícito com motivo_exclusao via Python:
CREATE TRIGGER trg_audit_os AFTER INSERT OR UPDATE ON public.ordens_servico FOR EACH ROW EXECUTE FUNCTION process_audit_log();
```

---

### FASE 2: Remoção do APM Bloqueante
1. Deletar `core/apm.py`.
2. Em `main.py`, remover `MonitoramentoAPMMiddleware` e a rota `monitoramento_router`.
3. Remover a pasta `modules/monitoramento/`.

---

### FASE 3: Refatoração do Chatbot (`modules/bot/service.py`)
1. **Áudio Multimodal In-Memory (Zero Disco):**
   ```python
   audio_part = types.Part.from_bytes(data=resp.content, mime_type="audio/ogg")
   response = gemini_client.models.generate_content(
       model='gemini-2.5-flash',
       contents=[audio_part, prompt],
       config=types.GenerateContentConfig(
           response_mime_type="application/json",
           response_schema=schemas.ExtracaoOS,
           temperature=0.1
       )
   )
   ```
2. **Correção de Colunas:**
   - `descricao_problema` na atualização de OS.
   - `mecanico_responsavel_id` na abertura de OS.
3. **Idempotência no Cadastro Rápido:**
   - Consultar se veículo já existe antes de duplicar.
4. **Vínculo com Estoque e Custo:**
   - Buscar itens no estoque da empresa pelo nome para preencher `estoque_id` e `custo_unitario`, evitando distorção no faturamento e lucro.

---

### FASE 4: Refatoração Algorítmica do Financeiro & Dashboards
1. `modules/financeiro/service.py`: varredura única com `defaultdict` para histórico de 6 meses.
2. `modules/dashboards/service.py`: `collections.Counter` para status de OS.

---

### FASE 5: Tratamento de Erros no Core (`core/errors.py`)
Substituir o bloco sequencial por tabela `dict`:

```python
ERROS_POSTGRES = {
    "23505": (409, "Conflito: Já existe um registro ativo com estes dados únicos (Placa, CPF/CNPJ, Email)."),
    "23503": (400, "Operação inválida: Registro possui dependências ativas ou vincula-se a registro inexistente."),
    "23502": (422, "Dados incompletos: Um campo obrigatório não foi preenchido."),
    "23514": (400, "Regra de negócio violada pelo banco de dados."),
    "22P02": (422, "Formato de dado inválido (ex: UUID inválido).")
}

async def supabase_exception_handler(request: Request, exc: APIError):
    erro_str = str(exc)
    for code, (status, msg) in ERROS_POSTGRES.items():
        if code in erro_str:
            return JSONResponse(status_code=status, content={"detail": msg})
    return JSONResponse(status_code=400, content={"detail": f"Erro de transação: {erro_str}"})
```

---

## 🚀 Roteiro de Execução Passo a Passo (Mapeamento Completo dos 14 Achados)

Sim! Os 14 achados do Ponytail (mais as correções críticas de segurança) estão distribuídos e são eliminados nos seguintes passos de execução:

### 🔹 Passo 1: Segurança Central & Tratamento de Erros
*Arquivos:* `core/security.py`, `core/errors.py`
- ✅ **Mata o Achado #5 (`yagni`):** Cria a dependência central `exigir_cargos` e elimina o header inseguro `x_cargo` e as funções locais duplicadas.
- ✅ **Mata o Achado #10 (`shrink`):** Reduz a escada de 35 linhas de `if/elif` em `core/errors.py` para um mapeamento limpo de dicionário (`dict`).
- 🛡️ **Segurança (Fase 0):** `validar_passaporte` busca o perfil real no banco (`id`, `empresa_id`, `cargo`, `ativo`), eliminando falsificação de privilégios. Adiciona `limpar_telefone` e `validar_chave_bot`.

---

### 🔹 Passo 2: Módulo Usuários & Blindagem de Acesso
*Arquivos:* `modules/usuarios/router.py`, `modules/usuarios/schemas.py`, `modules/usuarios/service.py`
- ✅ **Mata o Achado #5 (continuação):** Remove `verificar_permissao` duplicado e tranca todo o router com `validar_passaporte`.
- 🛡️ **Armadilha #1:** A rota `/me` retorna direto o `usuario_logado` sem fazer uma segunda query inútil.
- 🛡️ **Armadilha #2 & Bug Chatbot:** Adiciona `telefone` no `schemas.py` e inclui `"telefone": limpar_telefone(dados.telefone)` no `db_data` manual de `criar_usuario`. Elimina risco de `IndexError` em `atualizar_usuario`.

---

### 🔹 Passo 3: Módulo Bot de Atendimento & IA Multimodal
*Arquivos:* `modules/bot/router.py`, `modules/bot/service.py`
- ✅ **Mata o Achado #3 (`native`):** Elimina criação de arquivo em disco (`tempfile.mkstemp`), upload remoto e delete no Gemini; envia áudio 100% em memória via `types.Part.from_bytes`.
- ✅ **Mata o Achado #8 (`yagni`):** Remove código duplicado de sincronização de KM do veículo em `atualizar_dados_os`.
- ✅ **Mata o Achado #12 (`shrink`):** Elimina instâncias descartáveis de `httpx.AsyncClient` criadas a cada request.
- ✅ **Mata o Achado #13 (`delete`):** Remove chamada redundante de `load_dotenv()` no service.
- 🛡️ **Bugs Críticos do Bot:** Corrige colunas `descricao_problema` (estava `problema_relatado`) e `mecanico_responsavel_id` (estava `usuario_id`). Sanitiza telefone com `limpar_telefone` e adiciona idempotência no cadastro rápido. Tranca o router com `validar_chave_bot`.

---

### 🔹 Passo 4: Ordens de Serviço, Veículos e Estoque
*Arquivos:* `modules/os/service.py`, `modules/veiculos/service.py`, `modules/estoque/service.py`
- ✅ **Mata o Achado #6 (`delete`):** Elimina o recálculo inútil de totais (`recalcular_totais_os`) durante a deleção de itens em cascata dentro de `deletar_os`.
- ✅ **Mata o Achado #7 (`native`):** Remove queries manuais redundantes de pre-check de duplicidade (`select id... if duplicado: raise 409`) em `veiculos` e `estoque`, deixando o Postgres e o `core/errors.py` barrarem naturalmente.
- ✅ **Mata o Achado #12 (continuação):** Remove instanciação avulsa de `httpx.AsyncClient` em `veiculos/service.py`.
- 🛡️ **Armadilha #3 & Multi-tenant:** Amarra `.eq("empresa_id", empresa_id)` contra IDOR e mantém o insert explícito em `audit_logs` no `deletar_os` para salvar o `motivo_exclusao`.
- 🛡️ **Armadilha #4:** Mantém a busca em memória para `if search:`, evitando o erro 400 do PostgREST em joins.

---

### 🔹 Passo 5: Módulos Estratégico, Operacional & SaaS
*Arquivos:* `modules/financeiro/service.py`, `modules/dashboards/service.py`, `modules/empresas/service.py`
- ✅ **Mata o Achado #4 (`shrink`):** Reduz o loop $O(6 \times N)$ de histórico financeiro para uma única varredura agregando em `collections.defaultdict`.
- ✅ **Mata o Achado #9 (`shrink`):** Substitui `len(supabase.table(...).select("id")...)` por `count='exact', head=True` nativo do PostgREST.
- ✅ **Mata o Achado #11 (`stdlib`):** Substitui o loop e dict manual de contagem de status de OS por `collections.Counter`.
- 🛡️ **Armadilha #5:** Preserva integridade de `atualizar_configuracoes` sem quebrar no upsert.

---

### 🔹 Passo 6: Limpeza de Código Morto & Migração de Auditoria
*Arquivos:* `core/apm.py`, `modules/monitoramento/`, `audio_teste.ogg`, `core/audit.py`, `main.py`
- ✅ **Mata o Achado #1 (`native`):** Remove chamadas manuais de `salvar_audit_log` e pre-fetch de estado anterior após aplicar as triggers SQL no Supabase. Remove `core/audit.py`.
- ✅ **Mata o Achado #2 (`yagni`):** Deleta `core/apm.py` (middleware bloqueante) e a pasta `modules/monitoramento/`. Limpa os registros em `main.py`.
- ✅ **Mata o Achado #14 (`delete`):** Remove o arquivo residual `audio_teste.ogg` (45 KB) da raiz do projeto.

