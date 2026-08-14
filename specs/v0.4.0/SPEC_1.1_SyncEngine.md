# Spec 1.1: Sync Engine

> **Épico**: Kit v0.4.0 — Integração SDD Completa  
> **Sprint**: 1  
> **Status**: 🟡 Pronto para Implementação  
> **Data**: 2026-07-24

---

## Propósito

Criar um arquivo YAML centralizado (`smart-router.yaml`) que funcione como fonte de verdade para a tabela de roteamento de domínios → skills, e estender o script de sincronização (`sync-constitution.py`) para gerar automaticamente `smart-router.md` a partir deste YAML, com opção de sincronização seletiva via flags `--constitution` e `--router`.

---

## User Stories

### User Story 1 — Manutenção Centralizada do Smart Router (Priority: P1)

Como **mantenedor do kit**, preciso ter **um arquivo YAML centralizado** que defina a tabela completa de roteamento (domínio/intenção → skill/especialista) para que possa atualizar a tabela sem tocar em templates de markdown ou código espalhado.

**Why this priority**: Fonte única reduz risco de divergência entre código que faz routing e documentação; torna fácil atualizar regras sem quebrar implementação.

**Independent Test**: Posso criar uma nova regra de roteamento (ex: "novo domínio X → skill Y") **apenas** editando `smart-router.yaml`, rodar `sync-constitution.py --router`, e a mudança aparecer em `smart-router.md`.

**Acceptance Scenarios**:
1. **Given** que `smart-router.yaml` existe e contém uma entrada `"domínio: desenvolvimento" → "agente: coder"`, **When** eu executo `sync-constitution.py --router`, **Then** o arquivo `smart-router.md` é gerado/atualizado com uma tabela que inclui essa entrada, legível para o agente.
2. **Given** que eu edito `smart-router.yaml` e adiciono uma nova regra, **When** eu executo `sync-constitution.py --router`, **Then** `smart-router.md` reflete a mudança sem erros de parsing.
3. **Given** que `smart-router.yaml` está malformado (ex: YAML inválido), **When** eu executo `sync-constitution.py --router`, **Then** o script exibe erro claro indicando linha e tipo de problema.

---

### User Story 2 — Sincronização Seletiva (Priority: P1)

Como **desenvolvedor do kit**, preciso poder sincronizar **apenas** a Constituição OU **apenas** o Smart Router, sem atualizar o outro, para evitar rebuild desnecessário e permitir workflows independentes de CI/CD.

**Why this priority**: Dois artefatos evoluem em ritmos diferentes. Seleção granular economiza tempo de build e permite paralelização.

**Independent Test**: Consigo executar `sync-constitution.py --constitution` sem tocar em `smart-router.md`, e vice-versa com `--router`.

**Acceptance Scenarios**:
1. **Given** que tanto `architect-constitution.md` quanto `smart-router.md` existem, **When** eu executo `sync-constitution.py --constitution`, **Then** apenas `architect-constitution.md` é modificado; `smart-router.md` mantém timestamp anterior.
2. **Given** que ambos os arquivos existem, **When** eu executo `sync-constitution.py --router`, **Then** apenas `smart-router.md` é modificado; `architect-constitution.md` mantém timestamp anterior.
3. **Given** que eu executo `sync-constitution.py` sem flags, **When** o script termina, **Then** ambos `architect-constitution.md` e `smart-router.md` foram atualizados.

---

### User Story 3 — Versionamento e Rastreabilidade (Priority: P2)

Como **auditor**, preciso que ambos os arquivos gerados (`architect-constitution.md` e `smart-router.md`) incluam timestamp de geração e referência ao script/versão que os criou, para que eu possa rastrear quando cada mudança foi feita.

**Why this priority**: Compliance. Artefatos formais precisam de auditoria.

**Independent Test**: Ambos os arquivos gerados incluem: timestamp, versão script, commit hash (se em git).

**Acceptance Scenarios**:
1. **Given** que `sync-constitution.py` é executado, **When** arquivos são gerados, **Then** cada um inclui cabeçalho com timestamp ISO-8601 e versão do script.
2. **Given** que estou em repositório git, **When** script é executado, **Then** commit hash é incluído no cabeçalho.
3. **Given** que consulto arquivo gerado, **When** leio comentário de geração, **Then** posso rastrear exatamente quando foi gerado e por qual versão do script.

---

## Requisitos Funcionais

- **FR-001**: Arquivo `smart-router.yaml` criado em `rules/` com schema bem-definido.
- **FR-002**: Estrutura do YAML: `[domain]` → `[intenção/keywords]` → `[skill/agente]` + `[prioridade/weight]`.
- **FR-003**: Script `sync-constitution.py` estendido para ler `smart-router.yaml`.
- **FR-004**: Gerar `smart-router.md` (tabela legível + fluxo de roteamento).
- **FR-005**: Flags `--constitution`, `--router`, ambas (default).
- **FR-006**: Erro humanizado se YAML inválido (linha, esperado, recebido).
- **FR-007**: Cabeçalho em ambos .md: timestamp, versão script, commit hash.
- **FR-008**: Script exit code 0 = sucesso, 1 = erro (para CI/CD).

---

## Critérios de Sucesso

- **SC-001**: `smart-router.yaml` é fonte única de verdade (sem duplicação).
- **SC-002**: Mudança em YAML → `smart-router.md` refletida em < 5 segundos.
- **SC-003**: Sincronização seletiva funciona: `--constitution` não toca .router, vice-versa.
- **SC-004**: 100% das entradas YAML aparecem em .md (zero perda).
- **SC-005**: YAML malformado é detectado, erro humanizado.
- **SC-006**: Timestamp/versão aparecem em ambos .md.

---

## Arquitetura Técnica

### Estrutura smart-router.yaml

```yaml
# rules/smart-router.yaml
# Schema: Domain → Intent Patterns → Skill Selection
# Generated .md: rules/smart-router.md (via sync-constitution.py)

metadata:
  version: "0.4.0"
  generated: false  # Hand-maintained
  last_updated: "2026-07-24"

domains:
  - name: "development"
    priority: 10
    intents:
      - pattern: "continue"
        keywords: ["continue", "próximo passo", "next step"]
        skill: "coder"
        
      - pattern: "pair programming"
        keywords: ["pair", "juntos", "together"]
        skill: "coder"
        mode: "pair"
        
  - name: "healthcare"
    priority: 15
    intents:
      - pattern: "exercise planning"
        keywords: ["exercício", "VO₂max", "zona de treino"]
        skill: "exercise-physiologist"
        gate: "medical-gate"
```

### Fluxo sync-constitution.py

```
1. Parse command-line flags: --constitution, --router, ambos?
2. Se --constitution ou ambos:
   a. Ler architect-constitution.md
   b. Validar seções (Art. I-V)
   c. Gravar cabeçalho (timestamp, versão)
3. Se --router ou ambos:
   a. Ler smart-router.yaml
   b. Validar schema (domain, intents, skill)
   c. Gerar tabela markdown em smart-router.md
   d. Gravar cabeçalho (timestamp, versão)
4. Se erro: exibir mensagem + exit(1)
5. Senão: exit(0)
```

---

## Tasks

| ID | Prioridade | User Story | Descrição | Ficheiros |
|---|---|---|---|---|
| T01.1.1 | P | US1 | Criar schema de `smart-router.yaml` | `rules/smart-router.yaml` |
| T01.1.2 | P | US1 | Preencher 15-20 regras de roteamento (todas as domains) | `rules/smart-router.yaml` |
| T01.1.3 | P | US1 | Estender `sync-constitution.py` para ler YAML | `scripts/sync-constitution.py` |
| T01.1.4 | P | US1 | Gerar tabela markdown de `smart-router.yaml` | `scripts/sync-constitution.py` |
| T01.1.5 | P | US2 | Implementar flag `--constitution` | `scripts/sync-constitution.py` |
| T01.1.6 | P | US2 | Implementar flag `--router` | `scripts/sync-constitution.py` |
| T01.1.7 | P | US2 | Lógica: flags controlam qual arquivo é gerado | `scripts/sync-constitution.py` |
| T01.1.8 | S | US3 | Adicionar cabeçalho com timestamp ISO-8601 | `scripts/sync-constitution.py` |
| T01.1.9 | S | US3 | Adicionar versão script no cabeçalho | `scripts/sync-constitution.py` |
| T01.1.10 | S | US3 | Integrar commit hash (se git) no cabeçalho | `scripts/sync-constitution.py` |
| T01.1.11 | S | — | Validação: YAML malformado → erro humanizado | `scripts/sync-constitution.py` |
| T01.1.12 | S | — | Testes: parsing YAML válido/inválido | `tests/v0.4.0/test_sync_engine.py` |
| T01.1.13 | S | — | Testes: geração de smart-router.md | `tests/v0.4.0/test_sync_engine.py` |
| T01.1.14 | S | — | Testes: flags funcionam isoladamente | `tests/v0.4.0/test_sync_engine.py` |

---

## Definition of Done

- ✅ `smart-router.yaml` criado com schema + 15-20 regras
- ✅ `sync-constitution.py` estendido (YAML parsing)
- ✅ `smart-router.md` gerado corretamente de YAML
- ✅ Flags `--constitution`, `--router` funcionam isoladamente
- ✅ Cabeçalho com timestamp + versão + hash
- ✅ Erro humanizado para YAML malformado
- ✅ Exit codes corretos (0/1)
- ✅ Testes: parsing, geração, flags, errors
- ✅ Documentado em README (como usar sync-constitution.py)

