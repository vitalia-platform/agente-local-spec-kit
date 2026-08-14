<!-- tasks_1.1_SyncEngine.md | Atualizado em: 24-07-2026 10:50:00(GMT-04:00) -->
# Tasks: Spec 1.1 — Sync Engine

**Spec**: [SPEC_1.1_SyncEngine.md](file:///home/andre/projetos/assistidos/test-spec-agents/specs/v0.4.0/SPEC_1.1_SyncEngine.md) | **Plan**: [plan_1.1_SyncEngine.md](file:///home/andre/projetos/assistidos/test-spec-agents/specs/v0.4.0/plan_1.1_SyncEngine.md)
**Gerado em**: 2026-07-24

---

## MVP Scope

> Implementar **Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2)** entrega o motor principal do Sync Engine funcionando.
> A fase de rastreabilidade (US3) e polimento final são incrementos que podem ser feitos após a entrega do motor core.

---

## Phase 1: Setup

*Inicialização do ambiente. Sem label de US.*

- [X] T001 Inicializar e validar a estrutura base de `scripts/v0.4.0/sync-constitution.py` para as novas funções.
- [X] T002 Inicializar a suite de testes no arquivo `tests/v0.4.0/test_sync_engine.py`.

---

## Phase 2: Foundational

*Dependências bloqueantes. Sem label de US.*

- [X] T003 Validar/Criar schema do `rules/smart-router.yaml` para assegurar que está no formato correto para parsing.
- [X] T004 Garantir preenchimento das 15-20 regras de roteamento (todas as domains) em `rules/smart-router.yaml`.

---

## Phase 3: User Story 1 — Manutenção Centralizada do Smart Router

**Story Goal**: Centralizar as regras no YAML e gerar `smart-router.md` a partir do `sync-constitution.py`.
**Independent Test**: Posso criar uma nova regra em `smart-router.yaml`, executar o script e a regra aparece no arquivo `smart-router.md`.
**Referência**: FR-001, FR-002, FR-003, FR-004, FR-006

- [X] T005 [US1] Estender funcionalidade de parse de YAML usando PyYAML em `scripts/v0.4.0/sync-constitution.py`.
- [X] T006 [US1] Adicionar tratamento de YAML malformado e reportar erro humanizado (linha e razão) em `scripts/v0.4.0/sync-constitution.py`.
- [X] T007 [US1] Implementar gerador de tabela Markdown (`rules/smart-router.md`) a partir das chaves YAML extraídas em `scripts/v0.4.0/sync-constitution.py`.

---

## Phase 4: User Story 2 — Sincronização Seletiva

**Story Goal**: Sincronizar apenas o artefato escolhido via flags CLI para economia de processamento em pipelines.
**Independent Test**: Consigo executar `sync-constitution.py --constitution` e `smart-router.md` fica inalterado.
**Referência**: FR-005

- [X] T008 [P] [US2] Implementar flag `--constitution` no CLI parser de `scripts/v0.4.0/sync-constitution.py`.
- [X] T009 [P] [US2] Implementar flag `--router` no CLI parser de `scripts/v0.4.0/sync-constitution.py`.
- [X] T010 [US2] Implementar lógica de controle: processar as flags e acionar somente o gerador e arquivo respectivo em `scripts/v0.4.0/sync-constitution.py`.

---

## Phase 5: User Story 3 — Versionamento e Rastreabilidade

**Story Goal**: Incluir cabeçalhos informativos em todos os `.md` gerados, contendo metadados de execução.
**Independent Test**: Arquivos gerados incluem cabeçalho com timestamp, versão e commit hash.
**Referência**: FR-007

- [X] T011 [P] [US3] Incorporar timestamp ISO-8601 no cabeçalho dos artefatos em `scripts/v0.4.0/sync-constitution.py`.
- [X] T012 [P] [US3] Incorporar a versão do script no cabeçalho dos artefatos em `scripts/v0.4.0/sync-constitution.py`.
- [X] T013 [P] [US3] Recuperar o short hash do git commit mais recente e adicionar ao cabeçalho em `scripts/v0.4.0/sync-constitution.py`.

---

## Phase 6: Polish & Cross-Cutting

*Qualidade, performance e automação de testes. Sem label de US.*
**Referência**: FR-008

- [X] T014 [P] Criar testes unitários para o parsing de YAML válido e malformado em `tests/v0.4.0/test_sync_engine.py`.
- [X] T015 [P] Criar testes unitários validando a string final gerada para o Markdown em `tests/v0.4.0/test_sync_engine.py`.
- [X] T016 [P] Criar testes garantindo que as flags de CLI acionam somente os arquivos esperados em `tests/v0.4.0/test_sync_engine.py`.
- [X] T017 [P] Assegurar e testar que o script retorna exit code 0 em sucesso e exit code 1 ou 2 em falhas em `scripts/v0.4.0/sync-constitution.py`.

---

## Dependency Graph

```
Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3)
                                  ↘ Phase 6 (Tests) ↗
```

## Parallel Execution

Tasks marcadas `[P]` dentro da mesma fase podem ser executadas simultaneamente sem conflitos.
