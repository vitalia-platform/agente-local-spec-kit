# Tasks: Kit SDD Enforcement

## Phase 2: Foundational
- [x] T001 [P] [FR-001] Modificar `install-project.sh` para incluir o loop iterativo de symlinks das pastas estruturais do kit dentro do `.vitalia/` recém-criado.

## Phase 3: Path Refactoring
- [x] T002 [P] [FR-002] Atualizar o script call em `session-consolidate.toml` para `.vitalia/scripts/vitalia_context_engine.py`.
- [x] T003 [P] [FR-002] Atualizar o script call em `session-start.toml` para `.vitalia/scripts/vitalia_context_engine.py`.
- [x] T004 [P] [FR-002] Atualizar o script call em `release.toml` para `.vitalia/scripts/validate-kit.py`.

## Phase 4: Polish & Security Gate
- [x] T005 [P] [FR-003] Inserir a cláusula rigorosa de "Kill Switch" na seção de Spec-Driven Development do arquivo `architect-constitution.md`.
