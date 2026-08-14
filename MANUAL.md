# Manual do Vitalia Kit 0.3

> **Versão**: 0.3.0 — Série: "Spec Kit Convergence"
> **Repositório**: `git@github.com:vitalia-platform/spec-agents.git`
>
> Este manual é a referência técnica completa do kit. Leia o [README.md](./README.md)
> para a visão geral e instruções de instalação.

---

## Índice

1. [Fundamentos: O que é SDD?](#1-fundamentos)
2. [Formato .toml — A Linguagem do Kit](#2-formato-toml)
3. [A Linguagem das Especificações](#3-a-linguagem-das-especificações)
4. [Pipeline Principal (Opção A)](#4-pipeline-principal)
5. [Ciclo Principal — Referência dos Comandos](#5-ciclo-principal)
6. [Suporte Transversal](#6-suporte-transversal)
7. [Sessão e Contexto](#7-sessão-e-contexto)
8. [Segurança e Qualidade](#8-segurança-e-qualidade)
9. [Domínio Educacional](#9-domínio-educacional)
10. [Sistema de Hooks](#10-sistema-de-hooks)
11. [Redis e Transporte de Dados](#11-redis-e-transporte-de-dados)
12. [Memória do Projeto](#12-memória-do-projeto)
13. [Integrações por Ferramenta](#13-integrações-por-ferramenta)
14. [Templates de Artefatos](#14-templates-de-artefatos)
15. [Dicionário Completo de Termos](#15-dicionário-completo-de-termos)
16. [Comparativo: Vitalia Kit 0.3 vs Spec Kit](#16-comparativo)
17. [Guia de Atualização e Migração](#17-atualização-e-migração)

---

## 1. Fundamentos

**Spec-Driven Development (SDD)** é uma metodologia onde a especificação vem
antes do código. Cada feature parte de uma necessidade do usuário e o agente
de IA nunca escreve código sem artefatos aprovados.

### O ciclo de artefatos

```
Ideia → spec.md → plan.md → tasks.md → Código → Release
          ↑           ↑          ↑
      O QUÊ/       COMO       CHECKLIST
      POR QUÊ     técnico     atômico
```

### Os três artefatos fundamentais

| Artefato | Pergunta | Audiência | Contém |
|---|---|---|---|
| `spec.md` | O QUÊ e POR QUÊ | Stakeholders, PO, devs | FR-xxx, SC-xxx, User Stories, Gherkin |
| `plan.md` | COMO | Engenheiros | Stack, arquitetura, estrutura de arquivos, fases |
| `tasks.md` | QUANDO e QUEM | Engenheiros, CI | T001 [P] [US1] com caminhos de arquivo |

### O princípio HITL (Human in the Loop)

```
spec.md gerado → [HITL 1: aprovação] → plan.md + tasks.md → [HITL 2: aprovação] → código
```

Nenhum artefato avança para a fase seguinte sem aprovação explícita do desenvolvedor.

---

## 2. Formato .toml

Cada extensão do kit é um arquivo `.toml` em `extensions/`. O formato tem
**campos obrigatórios** (lidos por qualquer IDE) e **seções opcionais**
(para AG2 e orquestradores Python):

```toml
# ── Obrigatório: qualquer IDE lê ─────────────────────────────
description = "Texto curto para discovery e autocomplete"

# ── Opcional: IDEs ignoram; AG2 e orquestradores usam ────────

[meta]
version          = "0.3.0"
hardware_profile = "lightweight"  # lightweight | heavy | any
domain_gates     = []             # ["health"] aciona medical-gate auto

[hooks]
before = []           # ex: ["brainstorming"]
after  = ["analyze"]  # ex: ["medical-gate", "clarify"]

[tools]
# Tools que o AG2 precisa registrar ANTES de iniciar o agente
required = ["write_file", "read_file"]
optional = ["web_search", "semantic_search"]

[context]
# Arquivos lidos como contexto antes de executar
reads  = [".vitalia/feature.json"]
# Arquivos escritos/persistidos ao final
writes = [".vitalia/feature.json", "specs/*/spec.md"]

[variables]
# Mapeamento de variáveis de entrada e saída entre workflows
input  = ["args", "feature_directory"]     # {{args}} no prompt
output = ["feature_directory", "spec_file"] # disponíveis pro próximo workflow

[transport]
preferred     = "redis"   # redis | file
redis_key     = "vitalia:workflow:specify"
file_path     = ".vitalia/pipeline.json"  # fallback
session_shard = true      # incluir no shard do /session-end

# ── O corpo da instrução ──────────────────────────────────────
prompt = """
## User Input
\`\`\`text
{{args}}
\`\`\`
... instrução completa em Markdown ...
"""
```

### Por que .toml e não .md?

| Capacidade | .md | .toml |
|---|---|---|
| Gemini CLI slash command | ❌ | ✅ `description` + `prompt` |
| Discovery automático por IDEs | ❌ apenas AGY | ✅ qualquer ferramenta |
| `{{args}}` como variável portável | ❌ | ✅ padrão universal |
| Metadados estruturados (hooks, tools) | ❌ | ✅ campos tipados |
| Parser Python para AG2 | ❌ código específico | ✅ `tomllib` padrão |

### A variável `{{args}}`

`{{args}}` é o conteúdo que o usuário digitou após o comando.
Exemplos de interpolação por ferramenta:

```
Usuário digita: /vitalia-spec-specify criar sistema de login

AGY       → {{args}} = "criar sistema de login"
Gemini    → {{args}} = "criar sistema de login"
AG2       → tool recebe: skill("spec-specify", args="criar sistema de login")
```

---

## 3. A Linguagem das Especificações

### 3.1 User Stories com Prioridade

```markdown
### User Story 1 - [Título] (Priority: P1)

[Jornada em linguagem simples]

**Why this priority**: [Valor e justificativa de ser P1]

**Independent Test**: [Como testar ISOLADAMENTE, sem depender de outras histórias]

**Acceptance Scenarios**:
1. **Given** [pré-condição], **When** [ação], **Then** [resultado verificável]
2. **Given** [...], **When** [...], **Then** [...]
```

**Por que `**Why this priority**`?** — Marcador semântico. O agente sabe que
deve preencher com justificativa de valor, não texto livre.

**Por que `**Independent Test**`?** — Garante que cada história pode ser
entregue e testada sozinha (MVP incremental).

### 3.2 Cenários Given/When/Then (Gherkin)

```
Given [pré-condição: estado inicial do sistema]
When  [evento: ação do usuário ou chamada ao sistema]
Then  [pós-condição: resultado verificável]
```

**Ruim**: "O usuário consegue ver suas figurinhas."
**Bom**: "Given que a página 2 está aberta e a API respondeu, When a
renderização ocorre, Then cada slot preenchido exibe foto, nome e cargo visíveis."

> **Regra de ouro**: se você não consegue escrever um `Then` testável, o
> requisito está mal definido.

### 3.3 Requisitos Funcionais FR-xxx

```markdown
- **FR-001**: O sistema **MUST** [capacidade testável obrigatória]
- **FR-002**: O sistema **SHOULD** [capacidade recomendada]
- **FR-003**: Usuários **MAY** [capacidade opcional]
```

**Vocabulário normativo** (RFC 2119):
- `MUST` — obrigatório, não-negociável
- `SHOULD` — fortemente recomendado, exceções precisam ser justificadas
- `MAY` — opcional, adiciona valor

### 3.4 Critérios de Sucesso SC-xxx

```markdown
- **SC-001**: [Métrica mensurável e tecnologia-agnóstica]
```

| ❌ Errado (técnico) | ✅ Correto (outcome do usuário) |
|---|---|
| "API responde em 200ms" | "Usuários veem resultados em < 1.5s" |
| "Redis cache > 80% hit rate" | "Sistema suporta 1000 usuários simultâneos" |
| "React renderiza eficientemente" | "Usuário completa fluxo em < 2 minutos" |

### 3.5 Checklists de Qualidade

Os checklists em `checklists/` validam a **qualidade da escrita dos requisitos**,
não o comportamento do sistema:

```markdown
# ❌ ERRADO (testa implementação)
- [ ] Verificar que o botão exibe 3 cards

# ✅ CORRETO (testa qualidade do requisito)
- [ ] O número e layout dos cards estão explicitamente especificados? [Completeness]
- [ ] "Exibição proeminente" está quantificada com posicionamento específico? [Clarity]
```

**Marcadores de qualidade**: `[Completeness]`, `[Clarity]`, `[Consistency]`,
`[Measurability]`, `[Coverage]`, `[Gap]`, `[Ambiguity]`, `[Conflict]`, `[Assumption]`

---

## 4. Pipeline Principal

```
ENTRADA: Ideia ou problema

/vitalia-brainstorming      ← Opcional. Socrático. Revela pontos cegos.
         ↓
/vitalia-spec-specify       ← Gera specs/NNN-feature/spec.md
   • FR-xxx, SC-xxx, P1/P2, Given/When/Then
   • [NEEDS CLARIFICATION] máx. 3 → todos de uma vez
   • Valida com checklists/requirements.md
   • Grava .vitalia/feature.json
         ↓
    ┌──────────────┐
    │   HITL 1     │  Aprovação do spec.md
    └──────────────┘
         ↓
/vitalia-clarify            ← Opcional. ≤5 perguntas, uma de cada vez.
         ↓
/vitalia-spec-plan          ← Gera plan.md + research.md + constitution check
         ↓
/vitalia-spec-tasks         ← Gera tasks.md (T001 [P] [US1] path/to/file)
         ↓
/vitalia-spec-analyze       ← Automático (hook after_tasks)
   • CRITICAL = bloqueia implement
         ↓
    ┌──────────────┐
    │   HITL 2     │  Aprovação do tasks.md + relatório do analyze
    └──────────────┘
         ↓
[medical-gate / science-review se domain_gates=["health"]]
         ↓
/vitalia-spec-implement     ← Executa T001→TN marcando [X]
   • Verifica checklists antes
   • Valida Acceptance Scenarios ao final
         ↓
/vitalia-release            ← CHANGELOG + SemVer + tag git
```

---

## 5. Ciclo Principal

### `/vitalia-spec-specify`

**Arquivo**: [extensions/spec-specify.toml](./extensions/spec-specify.toml)
**Hardware**: lightweight

**Propósito**: Traduzir ideia em `spec.md` formal.

**Saída**:
- `specs/NNN-feature/spec.md`
- `specs/NNN-feature/checklists/requirements.md`
- `.vitalia/feature.json`

**Protocolo de qualidade**:
- Máx. 3 `[NEEDS CLARIFICATION]` — resto usa default documentado em Assumptions
- Todos apresentados de uma vez, não em cascata
- Validação automática com checklist (máx. 3 iterações)

---

### `/vitalia-clarify`

**Arquivo**: [extensions/clarify.toml](./extensions/clarify.toml)
**Hardware**: lightweight

**Propósito**: Detectar e resolver ambiguidades cirurgicamente após a spec.

**Protocolo**:
1. Scan de ambiguidades por taxonomia (escopo, dados, UX, performance, segurança, terminologia)
2. Fila de até 5 perguntas priorizadas por `Impacto × Incerteza`
3. **Uma pergunta por vez**, com recomendação explícita
4. Integração **imediata** na spec.md após cada resposta
5. Re-validação automática do checklist

---

### `/vitalia-spec-plan`

**Arquivo**: [extensions/spec-plan.toml](./extensions/spec-plan.toml)
**Hardware**: lightweight

**Fase 0 — Pesquisa** → `research.md`:

```markdown
## Decisão: [Nome]
- **Escolhido**: X
- **Justificativa**: por que X serve melhor aqui
- **Alternativas**: Y rejeitado porque...; Z rejeitado porque...
```

**Fase 1 — Design** → `plan.md` + (quando aplicável):
- `data-model.md` — entidades com atributos e relacionamentos técnicos
- `contracts/` — contratos de API, CLI, ou biblioteca
- `quickstart.md` — cenários executáveis end-to-end

**Constitution Check** é gate obrigatório — bloqueia se MUST falhar.

**Regra de escala**:
- < 5 arquivos → decision na seção `## Technical Decisions` do plan.md
- 5+ arquivos, API pública, libs externas → `research.md` separado

---

### `/vitalia-spec-tasks`

**Arquivo**: [extensions/spec-tasks.toml](./extensions/spec-tasks.toml)
**Hardware**: lightweight

**Formato obrigatório**:

```
- [ ] T### [P] [USN] Descrição com caminho/de/arquivo/exato
```

| Componente | Obrigatoriedade |
|---|---|
| `- [ ]` | SEMPRE |
| `T###` | SEMPRE — ID sequencial 3 dígitos |
| `[P]` | Quando paralelizável (sem deps) |
| `[USN]` | Apenas nas fases de User Story |
| Caminho de arquivo | SEMPRE |

**Estrutura de fases**:

```
Phase 1: Setup         (sem label US — ambiente)
Phase 2: Foundational  (sem label US — deps bloqueantes)
Phase 3: User Story 1  ([US1] obrigatório)
Phase 4: User Story 2  ([US2] obrigatório)
Phase N: Polish        (sem label US — qualidade)
```

**MVP explícito**: Phase 1 + 2 + 3 = produto funcionando.

---

### `/vitalia-spec-analyze`

**Arquivo**: [extensions/analyze.toml](./extensions/analyze.toml)
**Hardware**: lightweight | **Modo**: read-only

**Detecta** (com severidade CRITICAL/HIGH/MEDIUM/LOW):
- **A. Duplicações**: FRs semanticamente equivalentes, US duplicadas
- **B. Ambiguidades**: SCs sem métrica, FRs sem objeto mensurável
- **C. Subespecificação**: FRs sem task, US sem phase, tasks com arquivos não em plan
- **D. Violações da constituição**: contradições com MUST, medical gate ausente
- **E. Gaps de cobertura**: FRs com zero tasks, tasks órfãs
- **F. Drift de terminologia**: mesmo conceito com nomes diferentes entre artefatos

**Gate**: CRITICAL bloqueia `/vitalia-spec-implement`.

---

### `/vitalia-spec-implement`

**Arquivo**: [extensions/spec-implement.toml](./extensions/spec-implement.toml)
**Hardware**: heavy

**Antes de começar**:
- Verifica todos os `checklists/*.md` — para se houver incompletos
- Cria/verifica `.gitignore`, `.dockerignore`

**Durante**:
- Marca `[/]` (em andamento) → `[X]` (concluída)
- Para em erros sequenciais; continua em `[P]`
- Sugere commits atômicos após cada fase

**Ao final**: valida cada `Then` dos Acceptance Scenarios.

---

## 6. Suporte Transversal

### `/vitalia-brainstorming`

Protocolo socrático que **nunca gera código no primeiro passo**.
O agente analisa, identifica pontos cegos, apresenta opções com Prós e Contras,
e aguarda a decisão do usuário.

### `/vitalia-debug`

Debugging em 4 fases:
1. **Reproduce** — isolar o ambiente mínimo para reproduzir
2. **Isolate** — identificar o componente responsável
3. **Understand** — entender a causa raiz
4. **Fix** — corrigir com teste que previne regressão

### `/vitalia-review`

Revisão de código contra a Constituição do Arquiteto (21 princípios):
- Isolamento de dados, secrets via .env, timestamps em artefatos, etc.
- Produz lista de violações com severidade e sugestão de correção

### `/vitalia-pair`

Modo pair programming: cada bloco de código é proposto e aprovado pelo
desenvolvedor antes de ser escrito. Útil para features críticas ou
quando o desenvolvedor quer aprender o que está sendo feito.

### `/vitalia-continue`

Retoma implementação entre sessões:
1. Lê o código existente
2. Entende o estado atual
3. Propõe o próximo passo
4. Aguarda aprovação antes de escrever qualquer linha

### `/vitalia-adr`

Cria Architecture Decision Records rastreáveis por feature:
- Contexto e problema
- Opções consideradas (prós/contras)
- Decisão tomada e justificativa
- Consequências conhecidas

### `/vitalia-release`

Checklist de qualidade + CHANGELOG + SemVer + tag git:
1. Verifica que todos os Acceptance Scenarios passam
2. Gera CHANGELOG entry
3. Propõe versão SemVer
4. Cria tag git assinada

---

## 7. Sessão e Contexto

### `/vitalia-session-start`

Elimina o cold start do agente:
1. Lê `memory/session/CONTEXT.md`
2. Apresenta o estado atual do projeto
3. Identifica a feature ativa (via `.vitalia/feature.json`)
4. Propõe o próximo passo prioritário

### `/vitalia-session-end`

Encerra a sessão em 4 fases estanques:
1. **Avaliação proativa** — identifica melhorias possíveis
2. **Reflexão HITL** — apresenta a reflexão para o desenvolvedor validar
3. **Commit** — commita o repositório do projeto
4. **Shard local** — grava o shard em `memory/session/shards/`

> **Nota**: NÃO sincroniza com a nuvem. Use `/session-consolidate` para isso.

### `/vitalia-session-consolidate`

Sincroniza shards de múltiplas máquinas e reconstrói o `DASHBOARD.md`.
Gerencia concorrência estrita para evitar conflitos entre sessões paralelas.

---

## 8. Segurança e Qualidade

### `/vitalia-medical-gate`

**Gate I — Antes do plano** (domain_gates = ["health"]):
- Avalia o risco clínico do spec.md
- Classifica: sem risco / informativo / diagnóstico / terapêutico
- Bloqueia implementação se risco não justificado

**Gate II — Antes de publicar**:
- Verifica pré-condições de publicação de conteúdo médico
- Exige: revisão por profissional de saúde, disclaimers, data de validade

### `/vitalia-science-review`

1. Identifica o domínio científico relevante (nutrição, exercício, oncologia, etc.)
2. Aciona persona(s) especializada(s)
3. Cada persona produz um parecer com **constraints para implementação**
4. Parecer consolidado com severidade de cada constraint

### `/vitalia-skill-evaluation`

Analisa o histórico da sessão (transcript) para identificar:
- Gargalos recorrentes
- Erros e repetições
- Oportunidades de nova skill ou regra

Propõe novo SKILL.md ou AGENTS.md rule para aprovação HITL.

---

## 9. Domínio Educacional

### `/vitalia-blueprint-specify`

Transposição pedagógica — fase de especificação:
- Coleta tema, contexto e objetivo pedagógico
- Gera especificação pedagógica (análoga ao spec.md para software)

### `/vitalia-blueprint-plan`

Transposição pedagógica — fase de planejamento:
- Lê a especificação pedagógica
- Detalha estrutura da aula, metodologias ativas e materiais necessários

---

## 10. Sistema de Hooks

O arquivo `.vitalia/extensions.yml` de cada projeto define hooks por fase do pipeline:

```yaml
# .vitalia/extensions.yml
hooks:

  before_specify:
    - extension: brainstorming
      command: vitalia-brainstorming
      optional: true          # anunciado, não executado automaticamente
      prompt: "Deseja fazer um brainstorming antes de criar a spec?"

  after_specify:
    - extension: medical-gate
      command: vitalia-medical-gate
      optional: false         # EXECUTADO automaticamente
      condition: "domain == 'health'"

  after_tasks:
    - extension: analyze
      command: vitalia-spec-analyze
      optional: false         # sempre executa após /spec-tasks

  before_implement:
    - extension: pair
      command: vitalia-pair
      optional: true
```

**`optional: false`** → agente DEVE executar antes de prosseguir.
**`optional: true`** → agente anuncia ao usuário que está disponível.
**`condition:`** → expressão avaliada pelo agente (não automática).

---

## 11. Redis e Transporte de Dados

O `install-project.sh` detecta se o agente-local está ativo (Redis disponível).
Se sim, o kit opera em **modo Redis-first**:

### O que vai para Redis

| Dado | Redis Key | Quando |
|---|---|---|
| Estado do workflow ativo | `vitalia:workflow:STATE` | Durante execução |
| Feature ativa (cache) | `vitalia:feature:active` | Após `/spec-specify` |
| Cache semântico de specs | `vitalia:semantic:specs:{hash}` | Busca de specs similares |
| Sprint state | `vitalia:sprint_state` | Via `update_sprint_state()` |
| Tool requests/results | `vitalia:tool_requests:*` | Tool Bridge (agente-local) |
| Audit log | `vitalia:events` | Todas as execuções |

### O que SEMPRE vai para arquivo

| Dado | Arquivo | Por quê |
|---|---|---|
| Feature ativa (persistente) | `.vitalia/feature.json` | Sobrevive a restart do Redis |
| Contexto de sessão | `memory/session/DASHBOARD.md` | Versionado por git |
| Dados gerados (reviews, etc.) | `memory/data_storage/` | Persistência de longo prazo |
| Fallback de transporte (Convenção B) | `.vitalia/pipeline.json` | Alternativa estática ao Redis para orquestração |

> **Regra**: Redis = memória de curto prazo (sessão).
> `memory/` = memória de longo prazo (permanente, multi-máquina).

---

## 12. Memória do Projeto

```
[projeto]/.vitalia/memory/
├── constitution.md        ← Princípios MUST do projeto (commitar no projeto)
├── session/               ← GIT REPO SEPARADO
│   ├── CONTEXT.md         ← Estado da sessão atual
│   ├── DASHBOARD.md       ← Visão global multi-máquina
│   └── shards/
│       └── machine-timestamp.json
└── data_storage/          ← GIT REPO SEPARADO
    ├── reviews/           ← Outputs de /review, /science-review
    ├── research/          ← Conteúdo de research.md das features
    └── specs/             ← Snapshots de specs aprovadas (auditoria)
```

**Por que repositórios separados?**
- Controle de acesso diferente (session é privado, data pode ser compartilhado)
- Histórico limpo por domínio
- Sincronização independente por máquina
- Segue o padrão do "Dual-Git" do agente-local

---

## 13. Integrações por Ferramenta

### Antigravity IDE (AGY)

**Como funciona**: `install-project.sh` usa o template
[`integrations/antigravity/SKILL.md.template`](./integrations/antigravity/SKILL.md.template)
para gerar um `SKILL.md` em `.agents/skills/vitalia-NAME/` para cada extensão:

```markdown
---
name: vitalia-NAME
description: [campo description do .toml]
---
# Vitalia: NAME
1. Leia `~/.vitalia/kit/extensions/NAME.toml`
2. Extraia o campo `prompt`
3. Execute rigorosamente as instruções do `prompt`
```

### AG2 (agente-local)

**Como funciona**: `load_dynamic_skill()` em `tools.py` carrega o campo `prompt`
do `.toml` e injeta no contexto do agente.

**Atualização necessária em `tools.py`**:

```python
def load_dynamic_skill(skill_name: str) -> str:
    """Carrega um workflow Vitalia Kit (.toml) para o contexto do agente."""
    import tomllib  # Python 3.11+
    kit_dir = os.path.expanduser("~/.vitalia/kit/extensions")
    skill_path = os.path.join(kit_dir, f"{skill_name}.toml")
    try:
        with open(skill_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("prompt", f"Erro: 'prompt' ausente em {skill_name}.toml")
    except FileNotFoundError:
        return f"Erro: {skill_name} não encontrado em {kit_dir}."
    except Exception as e:
        return f"Erro ao carregar {skill_name}: {str(e)}"
```

Ver guia completo: [`integrations/ag2/kit.md`](./integrations/ag2/kit.md)

### Gemini CLI

```bash
# Instalado por install-project.sh se selecionado
# Copia cada .toml para .gemini/commands/vitalia.NAME.toml
/vitalia-spec-specify criar sistema de login
```

---

## 14. Templates de Artefatos

### spec.md

```markdown
# Feature Specification: [NOME]
**Feature**: `NNN-nome` | **Created**: [DATA] | **Status**: Draft

## User Scenarios & Testing

### User Story 1 - [Título] (Priority: P1)
[Jornada]
**Why this priority**: [Valor]
**Independent Test**: [Como testar isoladamente]
**Acceptance Scenarios**:
1. **Given** [...], **When** [...], **Then** [...]

### Edge Cases
- O que acontece quando [condição de borda]?

## Requirements

### Functional Requirements
- **FR-001**: O sistema **MUST** [...]
- **FR-002**: O sistema **SHOULD** [...]

## Success Criteria
### Measurable Outcomes
- **SC-001**: [Métrica mensurável e agnóstica de tecnologia]

## Assumptions
- [Suposição documentada]

## Out of Scope
- [O que explicitamente não faz parte desta feature]
```

### tasks.md

```markdown
# Tasks: [FEATURE]
**Spec**: [link] | **Plan**: [link] | **Gerado em**: [DATA]

## MVP Scope
> Phase 1 + Phase 2 + Phase 3 = produto funcionando.

## Phase 1: Setup
- [ ] T001 Criar estrutura de diretórios conforme plan.md

## Phase 3: User Story 1 — [Título]
**Story Goal**: [entrega para o usuário]
**Independent Test**: [validação isolada]
**Referência**: FR-001, FR-002

- [ ] T005 [P] [US1] Implementar X em src/models/x.py
- [ ] T006 [P] [US1] Escrever testes em tests/test_x.py
- [ ] T007 [US1] Integrar X em src/main.py

## Dependency Graph
\`\`\`
Phase 1 → Phase 2 → Phase 3 → Phase N
\`\`\`
```

---

## 15. Dicionário Completo de Termos

### Artefatos

| Termo | Arquivo | Descrição |
|---|---|---|
| `spec.md` | `specs/NNN/spec.md` | Especificação agnóstica (O QUÊ/POR QUÊ) |
| `plan.md` | `specs/NNN/plan.md` | Plano técnico (COMO) |
| `tasks.md` | `specs/NNN/tasks.md` | Checklist atômico de execução |
| `research.md` | `specs/NNN/research.md` | Decisões técnicas: Decision/Rationale/Alternatives |
| `data-model.md` | `specs/NNN/data-model.md` | Entidades, atributos, relações (técnico) |
| `quickstart.md` | `specs/NNN/quickstart.md` | Guia de validação end-to-end executável |
| `constitution.md` | `.vitalia/memory/constitution.md` | Princípios MUST do projeto |
| `feature.json` | `.vitalia/feature.json` | Ponteiro para feature ativa |
| `contracts/` | `specs/NNN/contracts/` | Contratos de interface pública |
| `checklists/` | `specs/NNN/checklists/` | Validação de qualidade dos requisitos |

### Marcadores de conteúdo da spec

| Padrão | Significado |
|---|---|
| `Priority: P1` | MVP mínimo — entregável sozinho |
| `**Why this priority**` | Marcador: justificativa de valor obrigatória |
| `**Independent Test**` | Marcador: como testar a US isoladamente |
| `**Acceptance Scenarios**` | Lista de cenários Gherkin |
| `**Given / When / Then**` | Estado / ação / resultado verificável |
| `**FR-001**` | Functional Requirement numerado |
| `MUST / SHOULD / MAY` | Vocabulário normativo RFC 2119 |
| `**SC-001**` | Success Criterion mensurável |
| `[NEEDS CLARIFICATION: ...]` | Ambiguidade (máx. 3 por spec) |

### Formato de tasks

| Componente | Exemplo | Obrigatório |
|---|---|---|
| Checkbox | `- [ ]` | SEMPRE |
| Task ID | `T001` | SEMPRE |
| Parallelizable | `[P]` | Quando sem deps pendentes |
| User Story | `[US1]` | Nas fases de US |
| Caminho de arquivo | `src/models/user.py` | SEMPRE |

### Checklists de qualidade

| Marcador | O que valida |
|---|---|
| `[Completeness]` | Requisito está presente? |
| `[Clarity]` | Requisito é específico e não-ambíguo? |
| `[Consistency]` | Requisitos se alinham sem conflito? |
| `[Measurability]` | Critério pode ser verificado objetivamente? |
| `[Coverage]` | Todos os cenários estão cobertos? |
| `[Gap]` | Requisito ausente detectado |
| `[Ambiguity]` | Termo vago que precisa ser quantificado |
| `[Conflict]` | Dois requisitos contraditórios |
| `[Assumption]` | Suposição implícita a validar |

---

## 16. Comparativo

### O que foi absorvido do Spec Kit

| Conceito Spec Kit | Vitalia 0.3 |
|---|---|
| Prioridades P1/P2 em User Stories | ✅ Adotado |
| `**Why this priority**` + `**Independent Test**` | ✅ Adotado |
| `Given / When / Then` (Gherkin) | ✅ Adotado |
| `FR-xxx` / `SC-xxx` com vocabulário normativo | ✅ Adotado |
| `[NEEDS CLARIFICATION]` máx. 3 | ✅ Adotado |
| Auto-geração de `specs/NNN-feature/` | ✅ Adotado |
| `feature.json` para feature ativa | ✅ Adotado |
| Validação com checklist de qualidade | ✅ Adotado |
| `research.md` com Decision/Rationale/Alternatives | ✅ Adotado |
| `data-model.md`, `contracts/`, `quickstart.md` | ✅ Adotado (condicional) |
| Constitution Check como gate no plan | ✅ Adotado |
| Formato `T001 [P] [US1] path/` | ✅ Adotado |
| MVP scope explícito no tasks.md | ✅ Adotado |
| Verificação de checklists antes de implement | ✅ Adotado |
| Validação de Acceptance Scenarios ao final | ✅ Adotado |
| Hook system (`before_`/`after_`) | ✅ Adotado |
| `/speckit.clarify` → `/vitalia-clarify` | ✅ Adotado |
| `/speckit.analyze` → `/vitalia-spec-analyze` | ✅ Adotado (com gates Vitalia) |
| Formato `.toml` com `description` + `prompt` | ✅ Adotado e expandido |

### O que o Vitalia Kit mantém exclusivamente

| Recurso | Valor |
|---|---|
| `/vitalia-brainstorming` socrático | Exploração mais profunda que `/clarify` do Spec Kit |
| Session management completo | start, end, consolidate com shards |
| Medical Gate (Artigos VIII/IX) | Safety automático para conteúdo clínico |
| Science Review com personas | Revisão especializada com constraints |
| Blueprint pedagógico | Transposição didática — sem equivalente no Spec Kit |
| ADR integrado | Decisões arquiteturais rastreadas por feature |
| Skill Evaluation | Auto-melhoria do kit pelo histórico da sessão |
| Pair mode | Aprovação chunk-a-chunk |
| Suporte a AG2 (agente-local) | `load_dynamic_skill` via `.toml` |
| Redis-first transport | Estado via Redis quando agente-local ativo |
| Memória dual-repo | session/ e data_storage/ em repos separados |

---

## 17. Atualização e Migração

### Atualizar o kit

```bash
# Verificar versão atual
cat ~/.vitalia/kit/VERSION

# Atualizar
git -C ~/.vitalia/kit pull --ff-only origin main

# Se novas extensões foram adicionadas, re-gerar shims
cd /seu/projeto && bash ~/.vitalia/kit/scripts/install-project.sh
```

### Migrar de vitalia-spec (versão anterior) para spec-agents 0.3

```bash
# 1. Confirmar que 0.3 está instalado
cat ~/.vitalia/kit/VERSION   # deve mostrar 0.3.0

# 2. Remover o plugin AGY antigo
rm -rf ~/.gemini/config/plugins/vitalia/

# 3. Remover o kit antigo
rm -rf ~/.vitalia-spec/

# 4. Para cada projeto que usava o kit antigo:
cd /seu/projeto
rm -rf .agents/skills/     # remover shims antigos
rm -rf .specify/           # remover symlinks antigos
bash ~/.vitalia/kit/scripts/install-project.sh
```

### Adicionar uma nova extensão ao kit

1. Criar `extensions/NOME.toml` seguindo o formato padrão
2. Documentar no `MANUAL.md` (seção apropriada)
3. Atualizar o `README.md` (tabela de extensões)
4. Commitar e fazer push para `spec-agents`
5. Em cada projeto: `bash ~/.vitalia/kit/scripts/install-project.sh` (re-gera shims)

---

*Vitalia Kit 0.3 — Manual de Referência*
*Última atualização: Julho 2026*
