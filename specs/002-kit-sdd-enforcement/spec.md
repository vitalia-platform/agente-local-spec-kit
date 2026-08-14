# Specification: Kit SDD Enforcement (Symlinks & Kill Switch)

## Background & Context
O Vitalia Kit exige um fluxo rígido de Spec-Driven Development (SDD). No entanto, foi detectado que os Agentes (como Antigravity) continuam usando seus modos de planejamento nativos (`implementation_plan.md`), ignorando o pipeline SDD. Além disso, existe um débito arquitetural no kit onde os arquivos TOML assumem a presença de scripts globais na raiz do projeto (`scripts/`), sem utilizar symlinks.

## Goals
- Garantir que todos os projetos instalados pelo kit possuam acesso aos artefatos globais do kit via symlinks em `.vitalia/`.
- Ajustar as extensões do kit para utilizarem esses symlinks, promovendo o encapsulamento do projeto.
- Impedir terminantemente (Kill Switch) que IAs pulem o pipeline SDD ao realizar tarefas complexas, blindando o RAG e a memória de contexto.

## Out of Scope
- Modificação de outros arquivos TOML que não sejam os afetados.
- Alterações no Antigravity core (apenas regras via constituição do Kit).

## Assumptions
- O `architect-constitution.md` é a fonte da verdade primária lida por todos os orquestradores.
- O `install-project.sh` é o único ponto de entrada para criação de novos projetos.

## User Scenarios & Testing
- **Scenario 1:** Um usuário roda `install-project.sh`.
  - **Given** um projeto vazio
  - **When** o script finaliza
  - **Then** a pasta `.vitalia/` possui symlinks para `docs`, `extensions`, `integrations`, `presets`, `rules`, `scripts`, `specs`.
- **Scenario 2:** Um agente IA recebe um pedido complexo de arquitetura.
  - **Given** que o agente carregou a constituição do projeto
  - **When** ele processa o pedido
  - **Then** ele recusa a criação de artefatos de planejamento nativos e orienta o usuário a acionar `/vitalia-spec-specify`.

## Functional Requirements
- **FR-001 [MUST]:** O `install-project.sh` deve criar symlinks para todas as pastas estruturais do kit dentro da pasta `.vitalia/` do projeto destino.
- **FR-002 [MUST]:** As extensões `session-consolidate.toml`, `session-start.toml` e `release.toml` devem chamar os scripts python prefixados por `.vitalia/scripts/`.
- **FR-003 [MUST]:** A constituição `architect-constitution.md` deve conter um "Kill Switch" explícito na seção do SDD proibindo artefatos nativos (`implementation_plan.md`, `task.md`) para forçar o pipeline SDD.

## Success Criteria
- Instalação limpa via script gera a estrutura de symlinks correta.
- IAs que leem a constituição recusam a criação de planejamentos fora do SDD.
