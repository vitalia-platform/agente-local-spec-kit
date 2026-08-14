# Spec 2.2: Converge — Dogfooding Tool

> **Épico**: Kit v0.4.0 — Integração SDD Completa  
> **Sprint**: 1  
> **Status**: 🟡 Pronto para Implementação  
> **Data**: 2026-07-24

---

## Propósito

Criar `/vitalia-converge` skill que serve como **dogfooding do próprio kit**: reconcilia `spec.md` ↔ `plan.md` ↔ `tasks.md` do kit, detecta inconsistências (FRs sem tasks, tasks completadas mas não marcadas, nomenclatura divergente), valida terminologia (FR-xxx vs FC-xxx), e sugere correções. Resultado: primeiro teste real do kit — ele prova que funciona em si mesmo.

---

## User Stories

### User Story 1 — Reconciliação Spec ↔ Plan ↔ Tasks (Priority: P1)

Como **auditor do kit**, preciso de um comando que **automaticamente verifique coerência entre spec, plan e tasks**, mostrando (1) FRs com/sem tasks, (2) tasks completadas/não-marcadas, (3) inconsistências, para que eu saiba se os artefatos estão em sincronia.

**Why this priority**: Spec drift é problema silencioso. O kit deve dogfood-se.

**Independent Test**: Executar `/vitalia-converge` e obter relatório:
- "3 FRs em spec.md"
- "3 FRs referenciados em tasks.md"
- "✅ Cobertura 100%"

**Acceptance Scenarios**:
1. **Given** que spec tem FR-001, FR-002, FR-003, **When** `/vitalia-converge` roda, **Then** detecta e lista: "3 FRs found in spec.md".
2. **Given** que FR-001 tem task T01.1 e T01.2 mas plan.md não lista T01.2, **When** converge roda, **Then** detecta: "⚠️  Task T01.2 referenced in spec but not in plan".
3. **Given** que task está marked `[x]` (completo) mas não há evidência (arquivo/função/teste), **When** converge roda, **Then** detecta: "❓  Task T01.1 marked done but no evidence found (expected file, function, test)".

---

### User Story 2 — Detecção de Código Não-Rastreado (Priority: P1)

Como **desenvolvedor**, quando implemenro um recurso, preciso que `/vitalia-converge` **automatically detecte se há código novo que não está rastreado em tasks.md**, para que não haja implementação "orphan".

**Why this priority**: Desvio de escopo é silencioso sem tracking explícito.

**Independent Test**: Criar novo arquivo `extensions/novo-skill.toml` sem adicionar à `tasks.md`, rodar `/vitalia-converge`, e detecta: "❌ Untracked code found: extensions/novo-skill.toml (not mentioned in any task)".

**Acceptance Scenarios**:
1. **Given** que arquivo novo existe (extensions/novo-skill.toml), **When** converge roda, **Then** detecta: "⚠️  Untracked file: extensions/novo-skill.toml".
2. **Given** que função nova está definida, **When** converge procura referência em tasks.md, **Then** se não encontra: "❌ Function novo_skill() found in code but not referenced in tasks".
3. **Given** que todo código tem task referência, **When** converge roda, **Then** "✅ All code is traceable to task".

---

### User Story 3 — Terminologia Consistency (Priority: P2)

Como **stylekeeper**, preciso que `/vitalia-converge` **verifique se nomenclatura é consistente** (FR vs FC, T01.1 vs TASK-001, ...), para que o kit mantenha padrão unificado.

**Why this priority**: Inconsistência confunde leitura.

**Independent Test**: Encontrar "FC-001" quando spec usa "FR-xxx", rodar converge, e detecta: "⚠️  Nomenclature inconsistency: found 'FC-001' but spec uses 'FR-xxx'".

**Acceptance Scenarios**:
1. **Given** que spec usa "FR-xxx" (Functional Requirements), **When** converge valida, **Then** nenhum "FC-xxx" ou "SR-xxx" aparece em tasks.
2. **Given** que tasks usam "T01.1" mas plan usa "TASK-001", **When** converge roda, **Then** alerta: "⚠️  Mixed task IDs: both 'T01.1' and 'TASK-001' found".
3. **Given** que nomenclatura é consistente, **When** converge roda, **Then** "✅ Nomenclature is consistent across artifacts".

---

## Requisitos Funcionais

- **FR-001**: Ler `spec.md`, extrair FRs (regex: FR-\d{3}).
- **FR-002**: Ler `plan.md`, extrair tarefas/objetivos.
- **FR-003**: Ler `tasks.md`, extrair tasks (T01.1, status, referências).
- **FR-004**: Mapear FR → Tasks (bidirecional).
- **FR-005**: Detectar orphan FRs (sem task), orphan Tasks (sem FR).
- **FR-006**: Detectar tasks marcadas done mas sem evidência (arquivo, função, teste).
- **FR-007**: Escanear codebase (extensions/, scripts/, rules/) detectar untracked code.
- **FR-008**: Validar nomenclatura (FR vs FC, T01.1 consistency).
- **FR-009**: Gerar relatório estruturado (Coverage %, Gaps, Untracked, Consistency).
- **FR-010**: Sugerir correções (ex: "Add T04.5 to tasks.md").

---

## Critérios de Sucesso

- **SC-001**: Coverage ≥ 95% (FR vs Task mapping).
- **SC-002**: Untracked code detectado 100%.
- **SC-003**: Nomenclature inconsistencies detectadas 95%+.
- **SC-004**: Relatório é acionável (qual arquivo, qual linha, como corrigir).
- **SC-005**: Executa em < 10 segundos (performance).
- **SC-006**: Zero false positives (não marca falso orphan).

---

## Arquitetura Técnica

### Estrutura de Output

```
🔍 CONVERGE ANALYSIS: specs/v0.4.0/
═════════════════════════════════════

📋 COVERAGE ANALYSIS
Spec FRs:        11 (FR-001 to FR-011)
Tasks mapping:   11
Coverage:        100% ✅

📝 SPEC → PLAN → TASKS RECONCILIATION
✅ FR-001 → plan.md section "Sync Engine"
✅ FR-001 → tasks T01.1, T01.2, T01.3
❌ FR-012 → no tasks found (ORPHAN)
⚠️  Task T03.5 → no FR reference

📁 UNTRACKED CODE DETECTION
Scanning: extensions/, scripts/, rules/, specs/
❌ extensions/novo-skill.toml (not mentioned in tasks)
✅ extensions/converge.toml (referenced in T02.2.1)

📐 NOMENCLATURE CONSISTENCY
Task IDs:   T01.1, T01.2, ... (consistent ✅)
FR IDs:     FR-001, FR-002, ... (consistent ✅)
SC IDs:     SC-001, SC-002, ... (consistent ✅)

═════════════════════════════════════
ISSUES: 2 gaps, 1 orphan FR, 1 untracked file
EXIT CODE: 0 (warnings only, not critical)
```

### Pseudo-código

```python
def converge_analysis(spec_path: str):
    spec = read_markdown(spec_path + "/spec.md")
    plan = read_markdown(spec_path + "/plan.md")
    tasks = read_markdown(spec_path + "/tasks.md")
    
    frs = extract_ids(spec, r"FR-\d{3}")
    task_refs = extract_ids(tasks, r"T\d{2}\.\d")
    code_files = scan_codebase(spec_path)
    
    # Map FR → Tasks
    for fr in frs:
        if fr not in task_refs:
            report.add_gap(f"ORPHAN FR: {fr}")
    
    # Detect untracked code
    for file in code_files:
        if not is_referenced_in_tasks(file, tasks):
            report.add_gap(f"UNTRACKED: {file}")
    
    # Nomenclature check
    if not is_consistent_nomenclature(tasks):
        report.add_warning("Nomenclature inconsistent")
    
    return report
```

---

## Tasks

| ID | Prioridade | User Story | Descrição | Ficheiros |
|---|---|---|---|---|
| T02.2.1 | P | US1 | Ler spec.md, extrair FRs | `extensions/converge.toml` |
| T02.2.2 | P | US1 | Ler plan.md, extrair objectives | `extensions/converge.toml` |
| T02.2.3 | P | US1 | Ler tasks.md, extrair tasks | `extensions/converge.toml` |
| T02.2.4 | P | US1 | Mapear FR → Tasks (bidirecional) | `extensions/converge.toml` |
| T02.2.5 | P | US1 | Detectar orphan FRs e tasks | `extensions/converge.toml` |
| T02.2.6 | P | US2 | Escanear codebase (extensions/, scripts/, rules/) | `extensions/converge.toml` |
| T02.2.7 | P | US2 | Detectar untracked files | `extensions/converge.toml` |
| T02.2.8 | P | US2 | Detectar untracked functions/classes | `extensions/converge.toml` |
| T02.2.9 | S | US3 | Validar nomenclature (FR, T, SC consistency) | `extensions/converge.toml` |
| T02.2.10 | S | — | Gerar relatório estruturado | `extensions/converge.toml` |
| T02.2.11 | S | — | Sugerir correções (text suggestions) | `extensions/converge.toml` |
| T02.2.12 | S | — | Testes: FR/Task mapping 95%+ accuracy | `tests/v0.4.0/test_converge.py` |
| T02.2.13 | S | — | Testes: untracked detection 100% | `tests/v0.4.0/test_converge.py` |
| T02.2.14 | S | — | Testes: nomenclature check | `tests/v0.4.0/test_converge.py` |

---

## Definition of Done

- ✅ `/vitalia-converge` skill criado (extension em converge.toml)
- ✅ Leitura de spec/plan/tasks funcionando
- ✅ Mapping FR ↔ Tasks bidirecional
- ✅ Detecção de orphans (FR sem task, task sem FR)
- ✅ Scan de codebase detecta untracked
- ✅ Nomenclature validation 95%+ acurácia
- ✅ Relatório estruturado e acionável
- ✅ Executa em < 10s
- ✅ Testes cobrindo: mapping, untracked, nomenclature
- ✅ Documentado (como rodar, interpretar relatório)

