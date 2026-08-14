---
name: rule-session-context
description: Concentra as obrigações estritas e as regras de tratamento do repositório de contexto de sessão (.vitalia/memory/session).
trigger: always_on
---
<!-- session-context.md | Atualizado pela Spec 3.1 -->

# Regra: Tratamento do Contexto de Sessão

Esta regra é a fonte da verdade para o manuseio dos arquivos dentro de `.vitalia/memory/session/` e do controle de fluxo de contexto das máquinas. 

**ANTES de responder qualquer solicitação de trabalho em código:**
1. Sempre verifique o estado do repositório executando o motor de contexto. Se a pasta `data/` não existir, rode `python3 ~/.vitalia/kit/scripts/vitalia_context_engine.py --action init`. Se existir, rode com `--action consolidate`.
2. Se o contexto não foi lido nesta sessão, leia imediatamente o `SESSION_STATE.md` para carregar o próximo passo (P0) e os constraints ativos.
3. Se houver divergências ou se você se sentir perdido, recomende o uso de `/vitalia-session-start`.

---

## 📂 Obrigações de Arquivos do Contexto

Todo arquivo dentro do diretório de contexto obedece a regras rígidas de atualização:

| Arquivo/Pasta | Responsabilidade de Escrita | Propósito |
| :--- | :--- | :--- |
| `SESSION_STATE.md` | Context Engine (`consolidate`) | Estado ativo e P0. Sobrescrito a cada consolidação. |
| `LEARNINGS.md` | Context Engine (`consolidate`) | Aprendizados renderizados a partir do JSONL. Sobrescrito. |
| `DECISIONS.md` | Context Engine (`consolidate`) | Decisões renderizadas a partir do JSONL. Sobrescrito. |
| `SESSION_HISTORY.md` | Context Engine (`consolidate`) | Histórico visual de sessões. Sobrescrito. |
| `DASHBOARD.md` / `README.md` | Context Engine (`consolidate`) | Visão estática do estado multi-máquina, bloqueio e semáforos. |
| `data/*.jsonl` | Agente BASH (`append`) / Script | Logs **IMUTÁVEIS** (append-only). Nunca apague ou reescreva linhas antigas. |
| `shards/*.yaml` | Agente BASH (overwrite) / Script | Arquivos de sincronização locais. O agente apenas escreve no `<machine_id>.yaml` da máquina atual. |

**Regra de Imutabilidade JSONL**:
Os arquivos em `data/` são registros transacionais apend-only. Para adicionar um aprendizado ou decisão nova, gere um ID único e faça um append no final do respectivo arquivo JSONL. NUNCA sobrescreva ou edite linhas passadas.

---

## 🛡️ Geração de Diagramas Mermaid (Defensive Programming)

Sempre que o contexto gerar um diagrama Mermaid, você **DEVE OBRIGATORIAMENTE**:

1. **Envelopar todos os rótulos de nós (nodes) com aspas duplas (`""`).**
   - *Correto:* `A["Status Concluído"]`
2. **Envelopar todos os rótulos de arestas (edges) com aspas duplas (`""`), especialmente dados dinâmicos.**
   - *Correto:* `A -->|"26-06-2026 (GMT-04:00)"| B`

Isso previne que caracteres especiais `() [] {} |` quebrem silenciosamente o renderizador do GitHub.
