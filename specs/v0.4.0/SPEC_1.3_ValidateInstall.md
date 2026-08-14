# Spec 1.3: Validação de Install

> **Épico**: Kit v0.4.0 — Integração SDD Completa  
> **Sprint**: 1  
> **Status**: 🟡 Pronto para Implementação  
> **Data**: 2026-07-24

---

## Propósito

Criar um script de validação (`validate-kit-install.sh`) que verifica se a instalação do kit foi bem-sucedida, detectando problemas comuns como placeholders não-resolvidos (`{{...}}`), paths inválidos, hooks faltando, permissões incorretas. Script funciona como primeira linha de defesa contra erros silenciosos pós-instalação.

---

## User Stories

### User Story 1 — Detectar Placeholders Não-Resolvidos (Priority: P1)

Como **usuário pós-instalação**, preciso de um script que me avise **imediatamente** se há placeholders tipo `{{VITALIA_DIR}}` que não foram resolvidos, para que eu saiba que algo deu errado na instalação antes de tentar usar o kit.

**Why this priority**: Placeholders não-resolvidos causam falhas silenciosas (paths inválidos, skills não-encontradas). Detecção rápida economiza debug.

**Independent Test**: Deixar um `{{...}}` em um arquivo `.toml` ou `.md`, rodar `validate-kit-install.sh`, e script reporta: "❌ Unresolved placeholder {{VITALIA_DIR}} in extensions/continue.toml:42".

**Acceptance Scenarios**:
1. **Given** que um arquivo tem `{{VITALIA_DIR}}` não-resolvido, **When** `validate-kit-install.sh` roda, **Then** detecta e lista: arquivo, linha, placeholder.
2. **Given** que múltiplos arquivos têm placeholders, **When** script roda, **Then** lista todos (não para no primeiro erro).
3. **Given** que não há placeholders, **When** script roda, **Then** seção de placeholders mostra "✅ OK: No unresolved placeholders".

---

### User Story 2 — Validar Paths e Estrutura de Diretórios (Priority: P1)

Como **sysadmin**, preciso que o script verifique se **todos os diretórios esperados existem** (rules/, extensions/, scripts/, specs/) e se **paths em `.toml` apontam para arquivos reais**, para que eu saiba que estrutura está íntegra.

**Why this priority**: Estrutura corrupta causa erros de runtime. Validação estrutural antecipa problemas.

**Independent Test**: Remover um diretório (ex: specs/), rodar `validate-kit-install.sh`, e script reporta: "❌ Missing directory: ~/specs/".

**Acceptance Scenarios**:
1. **Given** que diretório `rules/` não existe, **When** script roda, **Then** reporta: "❌ Missing required directory: ./rules/".
2. **Given** que `.toml` referencia arquivo que não existe, **When** script roda, **Then** reporta: "❌ Path not found in extensions/continue.toml: ./rules/architect-constitution.md".
3. **Given** que estrutura está completa, **When** script roda, **Then** "✅ All required directories present and valid".

---

### User Story 3 — Validar Hooks e Permissões (Priority: P2)

Como **desenvolvedor**, preciso que o script verifique se **scripts executáveis têm permissão** (`+x`), e se **hooks definidos em `.toml` existem e são válidos**, para que Skills não falhem por falta de permissão ou hooks órfãos.

**Why this priority**: Permissões esquecidas causam "command not found" misterioso.

**Independent Test**: Remover permissão +x de um script (`chmod -x scripts/sync-constitution.py`), rodar `validate-kit-install.sh`, e script reporta: "❌ Permission denied: ./scripts/sync-constitution.py (expected +x)".

**Acceptance Scenarios**:
1. **Given** que script não tem permissão +x, **When** script roda, **Then** reporta com sugestão: "❌ ./scripts/sync-constitution.py não é executável. Use: chmod +x ...".
2. **Given** que `.toml` define hook que não existe, **When** script valida, **Then** reporta: "⚠️  Hook reference not found: before_specify (defined in spec-specify.toml, file not found)".
3. **Given** que tudo está correto, **When** script roda, **Then** "✅ All scripts have correct permissions (+x)".

---

## Requisitos Funcionais

- **FR-001**: Detectar placeholders `{{...}}` em arquivos (recursive search).
- **FR-002**: Validar existência de diretórios core (rules/, extensions/, scripts/, specs/).
- **FR-003**: Validar paths referenciados em `.toml` (apontam para arquivos reais).
- **FR-004**: Verificar permissões +x em scripts Python/Bash.
- **FR-005**: Validar sintaxe TOML (usando `toml` parser ou similar).
- **FR-006**: Detectar hooks órfãos (definidos mas não implementados).
- **FR-007**: Gerar relatório estruturado (seções: Placeholders, Paths, Permissions, Hooks).
- **FR-008**: Exit code 0 = OK, 1 = problemas encontrados, 2 = erro crítico.

---

## Critérios de Sucesso

- **SC-001**: 100% dos placeholders detectados (zero falsos negativos).
- **SC-002**: 100% dos paths inválidos encontrados.
- **SC-003**: Permissões verificadas em todos scripts.
- **SC-004**: Hooks órfãos detectados.
- **SC-005**: Relatório é claro e acionável (qual arquivo, qual linha, como corrigir).
- **SC-006**: Script executa em < 5 segundos (performance).

---

## Arquitetura Técnica

### Estrutura de Output

```
🔍 VALIDAÇÃO DE INSTALAÇÃO DO KIT v0.4.0
═════════════════════════════════════════

📋 PLACEHOLDERS NÃO-RESOLVIDOS
✅ OK: No unresolved placeholders

📁 ESTRUTURA DE DIRETÓRIOS
✅ ./rules/ exists
✅ ./extensions/ exists
✅ ./scripts/ exists
✅ ./specs/ exists

📄 VALIDAÇÃO DE PATHS
✅ extensions/continue.toml references valid paths
✅ rules/architect-constitution.md exists

🔐 PERMISSÕES
❌ ./scripts/sync-constitution.py is not executable (expected +x)
   Fix: chmod +x ./scripts/sync-constitution.py

🪝 HOOKS
✅ All hooks defined and implemented

═════════════════════════════════════════
STATUS: 1 issue found (see above)
EXIT CODE: 1
```

### Pseudo-código

```bash
#!/bin/bash

validate_placeholders() {
  echo "📋 PLACEHOLDERS..."
  found=0
  for file in $(find . -type f -name "*.toml" -o -name "*.md"); do
    if grep -q "{{.*}}" "$file"; then
      grep -n "{{.*}}" "$file" | while read line; do
        echo "❌ Unresolved: $file:$line"
        found=$((found+1))
      done
    fi
  done
  if [ $found -eq 0 ]; then echo "✅ OK"; fi
}

validate_permissions() {
  echo "🔐 PERMISSIONS..."
  for script in scripts/*.py scripts/*.sh; do
    if [ ! -x "$script" ]; then
      echo "❌ Not executable: $script"
      echo "   Fix: chmod +x $script"
    fi
  done
}

# ... etc
```

---

## Tasks

| ID | Prioridade | User Story | Descrição | Ficheiros |
|---|---|---|---|---|
| T01.3.1 | P | US1 | Escrever função `validate_placeholders()` | `scripts/validate-kit-install.sh` |
| T01.3.2 | P | US1 | Detectar `{{...}}` com grep/regex | `scripts/validate-kit-install.sh` |
| T01.3.3 | P | US1 | Reportar filename:line:placeholder | `scripts/validate-kit-install.sh` |
| T01.3.4 | P | US2 | Escrever função `validate_directories()` | `scripts/validate-kit-install.sh` |
| T01.3.5 | P | US2 | Verificar existência de dirs core | `scripts/validate-kit-install.sh` |
| T01.3.6 | P | US2 | Validar paths em `.toml` | `scripts/validate-kit-install.sh` |
| T01.3.7 | P | US3 | Escrever função `validate_permissions()` | `scripts/validate-kit-install.sh` |
| T01.3.8 | P | US3 | Verificar +x em scripts | `scripts/validate-kit-install.sh` |
| T01.3.9 | S | US3 | Detectar hooks órfãos | `scripts/validate-kit-install.sh` |
| T01.3.10 | S | — | Gerar relatório estruturado (sections) | `scripts/validate-kit-install.sh` |
| T01.3.11 | S | — | Exit codes: 0=OK, 1=issues, 2=critical | `scripts/validate-kit-install.sh` |
| T01.3.12 | S | — | Testes: todos os checks (placeholder, path, perm, hook) | `tests/v0.4.0/test_validate_install.py` |

---

## Definition of Done

- ✅ `validate-kit-install.sh` criado
- ✅ Detecção de placeholders 100% (recursive)
- ✅ Validação de diretórios core
- ✅ Validação de paths referenciados
- ✅ Verificação de permissões +x
- ✅ Detecção de hooks órfãos
- ✅ Relatório claro e acionável
- ✅ Exit codes corretos
- ✅ Executa em < 5s
- ✅ Testes cobrindo todos os casos
- ✅ Documentado em README (como rodar)

