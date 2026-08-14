# Spec 3.1: Arquitetura de Memória 3-Tier e Context Engine

> **Épico**: Kit v0.4.0 — Integração SDD Completa (Área 3)
> **Status**: 🟢 Em Execução
> **Data**: 2026-07-24

---

## Propósito

Reestruturar a gestão de contexto do Kit Vitalia, abandonando a dependência de scripts frágeis e caminhos hardcoded (`.specify`). Consolidar o motor de memória em um sistema de 3-Tiers que isola estado, decisões e aprendizados, operando perfeitamente num ambiente Dual-Git (código vs contexto) e gerando um Dashboard visual (README.md) impecável para o repositório de contexto na nuvem.

---

## Arquitetura de Dados (3-Tier)

O repositório de contexto (`{{VITALIA_MEMORY_DIR}}`) armazenará o seguinte:

- **Tier 1 (Working State):** `SESSION_STATE.md`. Registra a feature ativa, P0 (próximo passo), e métricas de sessões.
- **Tier 2 (Decisions):** `DECISIONS.md`. Append-only de ADRs e decisões arquiteturais.
- **Tier 2 (Learnings):** `LEARNINGS.md`. Append-only com classificação `[KIT]` e `[PROJETO]`.
- **Shards Locais:** `shards/[MACHINE_ID].md`. Arquivo exclusivo de cada máquina operante.
- **Dashboard Global:** `README.md`. Vitrine do repositório de contexto.

---

## Requisitos Visuais (O Dashboard)

O `README.md` injetado na raiz do repositório de contexto deverá:
1. Parametrizar o nome do projeto (extraído do `SESSION_STATE.md`).
2. Extrair e exibir o P0 de cada shard.
3. Exibir Badge de staleness (⚠️) para shards sem sincronização há mais de 24h.
4. Possuir uma seção de "📝 Aprendizados Pendentes" extraída de `LEARNINGS.md`.
5. Renderizar gráficos Mermaid robustos (limpando parênteses nos IDs).

---

## Engenharia do Motor (`vitalia_context_engine.py`)

Em vez de resgatar 5 scripts Python/Bash fragmentados da v0.3.0, a Spec 3.1 define a criação do `scripts/vitalia_context_engine.py`. Ele atuará como CLI único para todas as operações de sessão:
- `--action init`: Inicializa a estrutura de pastas e arquivos base (SESSION_STATE, LEARNINGS, DECISIONS).
- `--action start`: Resolve os arquivos da sessão atual para o `session-start.toml`.
- `--action end`: Captura reflexões, atualiza o shard e o estado local.
- `--action consolidate`: Reconstroi o `README.md` (Dashboard visual), consolida o `SESSION_HISTORY.md` e aplica locks.

## Atualização dos Extensors (.toml)

Os prompts de `session-start.toml`, `session-end.toml` e `session-consolidate.toml` delegarão a execução complexa ao `vitalia_context_engine.py`, mantendo a filosofia do "Thin Client" para o LLM. Caminhos fixos como `.specify/memory` e `~/.vitalia-spec/` serão banidos.
