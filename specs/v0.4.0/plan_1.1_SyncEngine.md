<!-- plan_1.1_SyncEngine.md | Atualizado em: 24-07-2026 10:47:00(GMT-04:00) -->
# Implementation Plan: Spec 1.1 — Sync Engine

**Branch**: `main` | **Date**: 2026-07-24 | **Spec**: [SPEC_1.1_SyncEngine.md](file:///home/andre/projetos/assistidos/test-spec-agents/specs/v0.4.0/SPEC_1.1_SyncEngine.md)

## Summary

O **Sync Engine** centraliza a tabela de roteamento de domínios → skills no arquivo `rules/smart-router.yaml` (fonte da verdade) e estende o script `scripts/v0.4.0/sync-constitution.py` para gerar automaticamente `rules/smart-router.md` em formato Markdown tabular legível para o agente. Além disso, introduz sincronização seletiva por flags CLI (`--constitution`, `--router`) e insere um cabeçalho de auditoria com timestamp ISO-8601 UTC, versão do script e commit hash Git.

---

## Technical Context

- **Language/Version**: Python 3.11+
- **Primary Dependencies**: `pyyaml>=6.0`, `argparse`, `pathlib`
- **Storage**: Arquivos locais no repositório (`.yaml`, `.md`)
- **Testing**: `pytest>=7.0` em `tests/v0.4.0/test_sync_engine.py`
- **Target Platform**: CLI / Automação Local & CI/CD
- **Project Type**: Tooling / CLI Utility
- **Performance Goals**: Geração e sincronização executadas em < 5 segundos (SC-002)
- **Constraints**: 
  - Exit code `0` em caso de sucesso, `1` para erros de validação/parsing, `2` para erros críticos de I/O.
  - Zero hardcoding de regras de roteamento dentro do código Python.

---

## Constitution Check

| Princípio | Status | Observação |
|-----------|--------|------------|
| **Artigo I — Spec-Driven Development** | ✅ PASS | Spec `SPEC_1.1_SyncEngine.md` aprovada e `plan` em construção. |
| **Artigo IV — Impacto Holístico** | ✅ PASS | Ferramenta interna de build/sync local sem PII, multi-tenancy ou RBAC runtime. |
| **Artigo VI — Segredos Fora do Git** | ✅ PASS | Nenhuma credencial ou segredo hardcoded. |
| **Artigo VIII/IX — Medical Gate** | ✅ PASS | Domínio exclusivo de tooling/infraestrutura (Risco LOW — sem gate clínico). |
| **Artigo XII — Desacoplamento & Zero Hardcoding** | ✅ PASS | Regras extraídas para `rules/smart-router.yaml`. Script Python é puro motor de transformação. |
| **Artigo XV — Timestamp & Auditoria** | ✅ PASS | Cabeçalho de auditoria gerado automaticamente com timestamp ISO-8601 UTC e commit Git. |
| **Artigo XVII — Ambiente Reprodutível** | ✅ PASS | Dependências declaradas em `requirements.txt`. |

**Resultado**: **APROVADO** — prosseguir com planejamento e implementação.

---

## Technical Decisions

### Decisão 1: Fonte Única de Verdade (`rules/smart-router.yaml`)
- **Escolhido**: Schema YAML estruturado por domínios (`domains`), prioridades (`priority`), intenções (`intents`), palavras-chave (`keywords`) e skills associadas (`skill`).
- **Justificativa**: Legível para humanos, facilmente versionável em Git e consumível por bibliotecas padrão como PyYAML.
- **Alternativas**:
  - Manter Markdown manual (`smart-router.md`): Rejeitado por falta de validação de schema e risco de erro de sintaxe.
  - JSON: Rejeitado por ser menos ergonômico para edição manual.

### Decisão 2: Motor de Sincronização Seletiva via CLI
- **Escolhido**: `argparse` em `scripts/v0.4.0/sync-constitution.py` com flags `--constitution` e `--router`.
- **Justificativa**: Permite pipelines de CI/CD ou comandos isolados atualizar apenas o artefato necessário sem reprocessar outros.
- **Comportamento por Padrão**: Executar sem flags sincroniza ambos os artefatos.

### Decisão 3: Tratamento de Erros e Exit Codes Humanizados
- **Escolhido**: Capturar `yaml.YAMLError` e erros de parsing, exibindo linha do erro, arquivo afetado e instrução clara no `sys.stderr`, retornando `exit code 1`.

---

## Project Structure

### Documentation (this feature)
```text
specs/v0.4.0/
├── SPEC_1.1_SyncEngine.md
├── plan_1.1_SyncEngine.md
└── quickstart_1.1_SyncEngine.md
```

### Source Code
```text
rules/
├── smart-router.yaml          # Fonte da verdade (Hand-maintained)
├── smart-router.md            # Gerado automaticamente
└── architect-constitution.md  # Gerado/atualizado com cabeçalho

scripts/v0.4.0/
└── sync-constitution.py       # Script principal do Sync Engine

tests/v0.4.0/
└── test_sync_engine.py        # Suíte de testes automatizados
```

---

## Phase Overview

### Phase 1: Validação do Schema e Arquivo YAML (`smart-router.yaml`)
- Confirmar integridade de `rules/smart-router.yaml` cobrindo todas as intenções e domínios.

### Phase 2: Refatoração e Expansão do `sync-constitution.py`
- Ajustar suporte a resolução de caminhos relativos ao `REPO_ROOT`.
- Implementar gerador de tabela Markdown para `smart-router.md` a partir do dict YAML.
- Implementar parsing de erros amigável para YAML sintaticamente incorreto.
- Implementar gerador de cabeçalho de auditoria com timestamp ISO-8601 UTC, versão (`0.4.0`) e git commit hash.

### Phase 3: Controle de Fluxo por Flags (`--constitution`, `--router`)
- Garantir comportamento estrito das flags CLI isoladamente e em conjunto (padrão).

### Phase 4: Testes Automatizados (`test_sync_engine.py`)
- Testar parsing de YAML válido e inválido.
- Testar saída das flags isoladas `--constitution` e `--router`.
- Testar inclusão do cabeçalho de auditoria e verificação de exit codes.
