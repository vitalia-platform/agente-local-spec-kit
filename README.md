<!-- README.md | Vitalia Kit v0.5.0 | 12-08-2026 22:17(GMT-04:00) -->

# Vitalia Kit — Spec-Driven Development para Agentes de IA

> **O problema que este kit resolve:** LLMs alucinam. Em desenvolvimento de software, isso significa código gerado com versões erradas de libs, arquitetura inventada sem pesquisa, e decisões técnicas baseadas em conhecimento de treinamento desatualizado. O Vitalia Kit é um conjunto de guardrails, workflows e scripts que tornam o agente **verificável, auditável e reprodutível**.

---

## 📖 Índice

1. [Por que SDD?](#por-que-sdd)
2. [Conceitos Fundamentais](#conceitos-fundamentais)
3. [Arquitetura do Kit](#arquitetura-do-kit)
4. [Guard Rails de Grounding](#guard-rails-de-grounding)
5. [Instalação](#instalação)
6. [Uso — Commands Disponíveis](#uso--commands-disponíveis)
7. [O Pipeline SDD na Prática](#o-pipeline-sdd-na-prática)
8. [Estrutura de Arquivos](#estrutura-de-arquivos)

---

## Por que SDD?

**Spec-Driven Development (SDD)** é a prática de forçar o agente de IA a passar por fases explícitas e verificáveis antes de escrever qualquer linha de código:

```
Brainstorming → Spec → Plan → Tasks → Implement → Review → Release
```

Cada fase produz um artefato (`.md`) que pode ser lido, auditado e corrigido por um humano antes de avançar. Isso elimina o "Vibe Coding" — o hábito destrutivo de aceitar código gerado sem entender as decisões por trás dele.

### O problema do Vibe Coding

Quando você pede a um LLM "crie um sistema de autenticação com JWT", ele vai criar — e vai usar a versão de biblioteca que estava no seu treinamento, não a atual. Vai escolher um padrão arquitetural sem justificativa. Vai assumir que seu ambiente é igual ao dele. Meses depois, você descobre que a lib tem uma CVE crítica, que a arquitetura não escala, e que o código não roda no ambiente de produção.

O SDD força o agente a:

1. **Pesquisar antes de afirmar** (Guard Rails de Grounding)
2. **Documentar antes de codar** (spec.md, plan.md, tasks.md)
3. **Verificar o ambiente antes de executar** (Phase 0 automática)
4. **Deixar rastro auditável** (Rastro de Pesquisa obrigatório)

---

## Conceitos Fundamentais

### 1. Constituição do Agente

O arquivo `rules/always-on/architect-constitution.md` define as **leis imutáveis** que o agente deve seguir em toda interação — do Art. I (SDD Pipeline obrigatório) ao Art. XXIII (agnóstico de paths hardcoded). É o contrato entre você e o agente.

### 2. Always-On Rules

Arquivos em `rules/always-on/` são carregados automaticamente pelo IDE do agente em **toda sessão** via `.agents/rules/` (symlinks criados pelo instalador). Eles não precisam ser mencionados explicitamente — são o equivalente a regras de negócio injetadas no sistema prompt.

### 3. Guard Rails de Grounding

LLMs "blefam" sobre fatos externos porque foram treinados para dar respostas confiantes. O grounding é o antídoto: uma lista de domínios (versões de libs, APIs, regulações, etc.) onde o agente é **proibido** de usar conhecimento interno — ele deve buscar a fonte antes de afirmar qualquer coisa.

### 4. HITL (Human-in-the-Loop)

Decisões críticas nunca são automáticas. O kit define pontos de parada explícitos onde um humano deve aprovar antes de o agente prosseguir: aprovação de specs, promoção de domínios de grounding para o kit global, publicação de conteúdo clínico.

### 5. Context Engine

O `vitalia_context_engine.py` é o script central que gerencia o estado de sessão de desenvolvimento: consolida shards de contexto de múltiplas máquinas, gera o `DASHBOARD.md`, mantém o JSONL append-only de aprendizados/decisões e gera o `grounding-domains-local.yaml`.

---

## Arquitetura do Kit

```
~/.vitalia/kit/
├── rules/
│   └── always-on/              ← Injetadas automaticamente em toda sessão
│       ├── architect-constitution.md
│       ├── grounding.md         ← Guard Rails de Grounding (v0.5.0)
│       ├── hitl-medical.md
│       ├── infrastructure.md
│       ├── session-context.md
│       ├── smart-routing.md
│       └── vitalia-core.md
│
├── extensions/                 ← Workflows dos commands (/vitalia-*)
│   ├── brainstorming.toml
│   ├── spec-specify.toml
│   ├── spec-plan.toml
│   ├── spec-tasks.toml
│   ├── spec-implement.toml
│   ├── session-start.toml
│   ├── session-end.toml
│   └── session-consolidate.toml
│
├── config/
│   └── grounding-domains.yaml  ← Domínios que exigem verificação externa
│
├── scripts/
│   └── vitalia_context_engine.py  ← Motor de contexto multi-máquina
│
├── integrations/
│   └── antigravity/
│       └── SKILL.md.template   ← Template para geração dos skills no projeto
│
├── install-project.sh          ← Instalador interativo
└── AGENTS.md                   ← Ponteiro central para o agente
```

---

## Guard Rails de Grounding

> Introduzido na v0.5.0 — Feature 006

O sistema de grounding opera em 4 camadas independentes e complementares:

### Camada 1 — Domínios Configuráveis

`config/grounding-domains.yaml` define 7 domínios onde o agente é proibido de usar conhecimento interno:

| Domínio | O que cobre | Fontes Autoritativas |
|---|---|---|
| `llm_models` | Versões, limites de contexto, benchmarks de modelos | ai.google.dev, platform.openai.com, docs.anthropic.com |
| `python_packages` | Versões, breaking changes, compatibilidade | pypi.org |
| `external_apis` | Endpoints, schemas, rate limits, autenticação | Documentação oficial da API |
| `security_practices` | CVEs, OWASP, vulnerabilidades conhecidas | nvd.nist.gov, owasp.org |
| `regulations` | LGPD, HIPAA, GDPR, normas de compliance | gov.br/anpd, hhs.gov/hipaa |
| `cloud_services` | Preços, SLAs, limites de serviços em nuvem | aws/gcp/azure/oracle pricing |
| `scientific_claims` | Eficácia de técnicas, benchmarks de pesquisa | pubmed.ncbi.nlm.nih.gov, cochranelibrary.com |

### Camada 2 — Regra Always-On

`rules/always-on/grounding.md` (≤ 60 linhas) é injetada em toda sessão. Define o **protocolo de 4 passos**:

1. **PARE** — identifique se a afirmação envolve um domínio verificável
2. **BUSQUE** — use `search_web` ou `read_url_content`
3. **CITE** — inclua URL e data na tabela de Rastro de Pesquisa
4. **SE SEM RESULTADO** — marque como `NAO VERIFICADO`

### Camada 3 — Rastreamento por Projeto (JSONL)

Cada projeto mantém `data/grounding-domains.jsonl` (append-only). Durante `session-end`, o agente detecta novos domínios e os registra com `scope: null` para curadoria posterior.

### Camada 4 — Curadoria HITL no Consolidate

O `session-consolidate` exibe os domínios pendentes em uma tabela interativa e permite ao desenvolvedor:
- **Promover para global** → edita `config/grounding-domains.yaml` do kit (com confirmação HITL)
- **Manter local** → fica apenas no projeto atual
- **Rejeitar** → descartado

---

## Instalação

### Pré-requisitos

- Git (qualquer versão moderna)
- Python 3.10 ou superior
- PyYAML: `pip install pyyaml`
- Antigravity IDE (ou qualquer agente com suporte a `.agents/rules/` e `AGENTS.md`)

### Passo 1 — Clonar o Kit Global

```bash
git clone git@github.com:vitalia-platform/agente-local-spec-kit.git ~/.vitalia/kit
```

### Passo 2 — Ativar em um Projeto

```bash
# Na raiz do seu projeto:
bash ~/.vitalia/kit/scripts/install-project.sh
```

O instalador criará interativamente:
- `.vitalia/` com symlinks para extensions, rules, scripts
- `.agents/skills/` com SKILL.md por command
- **`.agents/rules/` com symlinks para todas as always-on rules** ← enforcement real
- `.vitalia/memory/session/` como repositório Git de contexto

### Passo 3 — Inicializar o Contexto

```bash
python3 ~/.vitalia/kit/scripts/vitalia_context_engine.py \
  --action init \
  --session-dir .vitalia/memory/session
```

Isso cria:
- `data/grounding-domains.jsonl` (vazio)
- `grounding-domains-local.yaml` (baseado no yaml global)
- `DASHBOARD.md` com a seção Guard Rails

### Passo 4 (Opcional) — Sincronização Multi-máquina

```bash
# Criar repo privado no GitHub para contexto compartilhado:
git -C .vitalia/memory/session remote add origin git@github.com:seu-usuario/seu-projeto-context.git
git -C .vitalia/memory/session push -u origin main
```

---

## Uso — Commands Disponíveis

Ative digitando `/vitalia-[nome]` no chat do agente:

### Pipeline SDD Principal

| Command | Descrição | Artefato Produzido |
|---|---|---|
| `/vitalia-brainstorming [tema]` | Reflexão socrática antes de codar — identifica pontos cegos e trade-offs | Análise estruturada |
| `/vitalia-spec-specify [feature]` | Especificação formal com FRs, SCs, User Stories e Given/When/Then | `specs/NNN/spec.md` |
| `/vitalia-spec-plan` | Arquitetura técnica com decisões documentadas e fontes verificadas | `specs/NNN/plan.md` + `research.md` |
| `/vitalia-spec-tasks` | Tarefas atômicas com **Phase 0 automática** (venv + pip check + compat) | `specs/NNN/tasks.md` |
| `/vitalia-analyze` | Consistência spec ↔ plan ↔ tasks — bloqueia implement se CRITICAL | Relatório de findings |
| `/vitalia-spec-implement` | Execução sistemática do tasks.md, marcando [X] a cada task | Código + tasks atualizadas |

### Gestão de Sessão

| Command | Descrição |
|---|---|
| `/vitalia-session-start` | Recupera contexto completo, apresenta DASHBOARD e P0 (próximo passo) |
| `/vitalia-session-end` | Reflexão, detecção de novos domínios de grounding, commit e shard |
| `/vitalia-session-consolidate` | Sincroniza shards, **curação interativa de grounding**, push para nuvem |

### Qualidade e Governança

| Command | Descrição |
|---|---|
| `/vitalia-review [arquivo]` | Auditoria de qualidade, arquitetura e segurança |
| `/vitalia-debug` | Fluxo sistemático de depuração (isolamento → hipótese → teste) |
| `/vitalia-adr` | Architecture Decision Record interativo |
| `/vitalia-release` | Checklist de qualidade + changelog + tag semântica |
| `/vitalia-converge` | Reconcilia código real vs spec/plan/tasks (dogfooding do pipeline) |
| `/vitalia-pair` | Ativa modo pair programming estruturado |

---

## O Pipeline SDD na Prática

### Exemplo: Feature de Autenticação

```
# 1. Recuperar contexto da sessão anterior
/vitalia-session-start

# 2. Estruturar o problema ANTES de codar
/vitalia-brainstorming Autenticação JWT com refresh tokens e revogação

# 3. Especificar formalmente
/vitalia-spec-specify Autenticação JWT para a API REST

# 4. Planejar a arquitetura (o agente PESQUISA as libs antes de escolher)
/vitalia-spec-plan

# 5. Gerar tasks com Phase 0 automática
/vitalia-spec-tasks

# 6. Implementar task por task, com marcação [X]
/vitalia-spec-implement

# 7. Encerrar e registrar aprendizados
/vitalia-session-end
```

### Exemplo de Rastro de Pesquisa (obrigatório em todo artefato)

```markdown
## Rastro de Pesquisa — Plan: Autenticação JWT

**Gerado em:** 12-08-2026 22:00(GMT-04:00) | **Domínios verificados:** python_packages

| # | Afirmação feita | Verificado? | Fonte consultada | Data |
|---|---|---|---|---|
| 1 | "PyJWT 2.8.0 é a versão atual" | Sim | pypi.org/project/PyJWT | 12-08-2026 |
| 2 | "Compatível com Python 3.10+" | Sim | pypi.org/project/PyJWT#history | 12-08-2026 |
| 3 | "RS256 é recomendado pelo OWASP" | NAO VERIFICADO | — | — |
```

### Phase 0 — Verificação de Ambiente (gerada automaticamente)

Todo `tasks.md` gerado pelo kit começa com:

```markdown
## Phase 0: Grounding & Environment

- [ ] T000-A Ativar venv: `source .venv/bin/activate`
- [ ] T000-B Verificar Python do venv (não do sistema): `python --version`
- [ ] T000-C Verificar deps: `pip list --outdated`
- [ ] T000-D [Cada lib na spec] Verificar versão atual em pypi.org
- [ ] T000-E Verificar conflitos: `pip check`
```

---

## Estrutura de Arquivos Gerada no Projeto

```
seu-projeto/
├── .vitalia/
│   ├── extensions/  → ~/.vitalia/kit/extensions/   (symlink)
│   ├── rules/       → ~/.vitalia/kit/rules/         (symlink)
│   ├── scripts/     → ~/.vitalia/kit/scripts/       (symlink)
│   ├── config/      → ~/.vitalia/kit/config/        (symlink)
│   ├── feature.json                                 ← Feature ativa
│   └── memory/
│       └── session/                                 ← Repo Git separado
│           ├── DASHBOARD.md                         ← Estado visual
│           ├── SESSION_STATE.md                     ← P0 e constraints
│           ├── LEARNINGS.md                         ← View gerada
│           ├── DECISIONS.md                         ← View gerada
│           ├── grounding-domains-local.yaml         ← VIEW (não editar)
│           └── data/
│               ├── learnings.jsonl                  ← Append-only
│               ├── decisions.jsonl                  ← Append-only
│               └── grounding-domains.jsonl          ← Append-only
│
├── .agents/
│   ├── AGENTS.md                                    ← Ponteiro (thin client)
│   ├── rules/                                       ← Symlinks always-on rules
│   │   ├── grounding.md          → kit/rules/always-on/grounding.md
│   │   ├── architect-constitution.md → ...
│   │   └── ...
│   └── skills/                                      ← Um SKILL.md por command
│       ├── vitalia-session-start/SKILL.md
│       ├── vitalia-spec-specify/SKILL.md
│       └── ...
│
└── specs/
    └── NNN-nome-da-feature/
        ├── spec.md
        ├── plan.md
        ├── research.md
        ├── tasks.md
        └── checklists/
            └── requirements.md
```

---

## Rastro de Pesquisa — Este README

**Gerado em:** 12-08-2026 22:17(GMT-04:00) | **Domínios verificados:** python_packages

| # | Afirmação feita | Verificado? | Fonte consultada | Data |
|---|---|---|---|---|
| 1 | PyYAML é dependência do context engine | Sim | grep "import yaml" vitalia_context_engine.py:9 | 12-08-2026 |
| 2 | Python 3.10+ como requisito mínimo | Sim | pypi.org/project/PyYAML — requires Python >=3.6 (permissivo) | 12-08-2026 |
| 3 | "PyJWT 2.8.0 é a versão atual" no exemplo | NAO VERIFICADO | Exemplo didático — não use em produção sem verificar | — |
