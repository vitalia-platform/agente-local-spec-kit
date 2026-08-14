# Implementation Plan: Kit SDD Enforcement (Symlinks & Kill Switch)

**Branch**: `main` | **Date**: 2026-07-27 | **Spec**: [spec.md](./spec.md)

## Summary
Implementar o loop de criação de symlinks estruturais no `install-project.sh`, ajustar arquivos `.toml` para utilizarem os novos caminhos encapsulados, e adicionar uma regra de "Kill Switch" na constituição do kit bloqueando o planejamento nativo das IDEs em favor do pipeline SDD.

## Technical Context

**Language/Version**: Bash, TOML, Markdown
**Primary Dependencies**: N/A
**Storage**: N/A
**Testing**: N/A
**Target Platform**: Vitalia Kit (Orquestradores de IA)
**Project Type**: CLI / Agentes Config
**Performance Goals**: N/A
**Constraints**: As mudanças no TOML devem usar expressões relativas `.vitalia/` sem quebrar compatibilidade reversa.

## Constitution Check

| Princípio | Status | Observação |
|-----------|--------|------------|
| Art. XII (Desacoplamento Limpo) | ✅ PASS | O uso de symlinks reforça que as extensões apontam para um contrato esperado, desacoplando o comando da pasta global direta. |
| Art. XXIII (Manutenção Agnóstica) | ✅ PASS | As alterações tornam o kit auto-contido. |

**Resultado**: APROVADO — prosseguir com planejamento

## Technical Decisions
- **Symlinks dinâmicos**: Optou-se por um `for loop` no bash sobre um array de diretórios conhecidos (`docs extensions integrations presets rules scripts specs`).
- **Kill Switch na constituição vs AGENTS.md**: Decidiu-se colocar a regra estritamente no `architect-constitution.md` para evitar duplicidade e garantir que seja lida globalmente.

## Project Structure

### Documentation (this feature)
- `~/.vitalia/kit/specs/002-kit-sdd-enforcement/spec.md`
- `~/.vitalia/kit/specs/002-kit-sdd-enforcement/checklists/requirements.md`
- `~/.vitalia/kit/specs/002-kit-sdd-enforcement/plan.md`

### Source Code
- `~/.vitalia/kit/scripts/install-project.sh`
- `~/.vitalia/kit/extensions/session-consolidate.toml`
- `~/.vitalia/kit/extensions/session-start.toml`
- `~/.vitalia/kit/extensions/release.toml`
- `~/.vitalia/kit/rules/always-on/architect-constitution.md`

## Phase Overview

### Phase 2: Foundational
- Modificar `install-project.sh` para adicionar o loop de symlinks.
### Phase 3: User Story 1 — Path Refactoring
- Substituir caminhos nos TOMLs de `scripts/` para `.vitalia/scripts/`.
### Phase 4: Polish & Cross-Cutting — Security Gate
- Inserir a regra do "Kill Switch" no `architect-constitution.md`.
