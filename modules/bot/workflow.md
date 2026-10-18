# 🤖 AutoTecPRO - Workflow da Máquina de Estados (Chatbot)

Este documento mapeia o fluxo de navegação contínua do assistente de oficina pelo WhatsApp. A arquitetura baseia-se numa Máquina de Estados Finita guardada na tabela `bot_sessoes`.

## 🛑 Regra de Ouro Universal
Qualquer mensagem recebida com os termos: `OI, OLÁ, MENU, SAIR, CANCELAR`, reseta imediatamente o `estado_atual` para `MENU` e limpa os `dados_temporarios`.

---

## 🗺️ Mapeamento de Estados e Transições

### 🔹 Estado Zero: `MENU`
* **Descrição:** Ponto de partida. Exibe as 6 opções principais.
* **Transições:**
  * Digita `1` -> Vai para `AGUARDANDO_OS_CONSULTA`
  * Digita `3` -> Vai para `ABRIR_OS_BUSCA`
  * Digita `5` -> Vai para `ADD_ITENS_BUSCA_OS`

---

### 🔹 Fluxo 1: Consulta de Histórico de OS
* **Estado:** `AGUARDANDO_OS_CONSULTA`
  * **Ação:** Recebe Placa/Nome. Cruza dados e traz o ranking de carros encontrados.
  * **Saída:** Vai para `CONSULTA_SELECAO_VEICULO`.
* **Estado:** `CONSULTA_SELECAO_VEICULO`
  * **Ação:** Recebe o número da opção (ex: `1`). Puxa o histórico de OS do veículo e exibe listagem curta (UUID cortado) enumerada de 1 a 5.
  * **Saída:** Vai para `CONSULTA_LISTAGEM_OS`.
* **Estado:** `CONSULTA_LISTAGEM_OS`
  * **Ação Dupla:** * Se receber `0`: Avança a página das OSs (offset de +5).
    * Se receber `1` a `5`: Faz o query completo com JOIN em `os_itens` e exibe o dossiê detalhado (status, KM, relato, peças e total).
  * **Saída:** Após exibir o dossiê, regressa automaticamente ao `MENU`.

---

### 🔹 Fluxo 3: Abertura Fluida de OS (Foco em Produtividade)
Fluxo contínuo sem UUIDs. O sistema já identifica o mecânico pelo telefone.

* **Estado:** `ABRIR_OS_BUSCA`
  * **Ação:** Recebe termo (ex: "Marcio Parati"). Faz query %LIKE% cruzada em Cliente + Veículo.
  * **Saída:** Exibe ranking numerado e vai para `ABRIR_OS_SELECAO`.
* **Estado:** `ABRIR_OS_SELECAO`
  * **Ação:** Recebe o número da opção (ex: `1`). Cria a OS no banco atrelando o `usuario_id` do mecânico.
  * **Saída:** Vai para `ABRIR_OS_KM`.
* **Estado:** `ABRIR_OS_KM`
  * **Ação:** Recebe números puros. Atualiza `km_atual` da OS criada.
  * **Saída:** Vai para `ABRIR_OS_PROBLEMA`.
* **Estado:** `ABRIR_OS_PROBLEMA`
  * **Ação:** Recebe o texto livre do relato do cliente. Atualiza `problema_relatado`.
  * **Saída:** Vai direto para a cabine da IA em `ADD_ITENS_AGUARDANDO_AUDIO`.

---

### 🔹 Fluxo 5: Adição de Itens via IA Generativa
Módulo de alta tecnologia usando Whisper (Transcrição) + Gemini (JSON Estruturado) para capturar o suor do mecânico e converter em faturamento.

* **Estado:** `ADD_ITENS_BUSCA_OS`
  * **Ação:** Recebe Placa/Nome. Busca apenas OS em andamento (status abertos).
  * **Saída:** Se achar uma, vai direto para `ADD_ITENS_AGUARDANDO_AUDIO`. Se achar várias, vai para `ADD_ITENS_SELECAO_OS`.
* **Estado:** `ADD_ITENS_SELECAO_OS`
  * **Ação:** Recebe o número da OS desejada no menu de empate.
  * **Saída:** Vai para `ADD_ITENS_AGUARDANDO_AUDIO`.
* **Estado:** `ADD_ITENS_AGUARDANDO_AUDIO` (🎯 O Ponto de Integração da IA)
  * **Ação Pendente:** Este estado aguarda a rota `/webhook/audio` (ou texto) acionar o pipeline do LLM.
  * **Objetivo Final:** Injetar os itens estruturados na `os_itens` e recalcular o faturamento da OS.