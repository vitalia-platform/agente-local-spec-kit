# Spec 5.2: Unificação de Presets (5.2a, 5.2b, 5.2c)

> **Épico**: Kit v0.4.0 — Integração SDD Completa  
> **Sprint**: 5  
> **Status**: 🟢 Em Execução  
> **Data**: 2026-07-24

---

## Propósito

Eliminar a redundância metodológica e a sobreposição de regras de formatação (ex: 6 arquivos tentando definir como um Spec deve parecer).
- Todos os "formatos de Spec" migram para o diretório `presets/`.
- O comando `spec-specify` é o único portão de entrada, recebendo o argumento `--preset=nome`.
- Os comandos satélites (`blueprint-specify`) tornam-se Shims de aviso (compatibilidade reversa, Decisão 2B).

---

## Engenharia

### 1. Sistema de Presets
- Diretório: `presets/` na raiz do kit.
- Templates consolidados:
  - `software.md` (o padrão).
  - `clinical.md` (antigo medical-gate.spec.md).
  - `blueprint.md` (antigo blueprint.spec.md fundido com spec-quality-blueprint.md).

### 2. O Motor (`spec-specify.toml`)
- A skill lerá a flag `--preset` dos `{{args}}`.
- Instruirá o LLM a carregar o conteúdo de `{{VITALIA_KIT_DIR}}/presets/[preset_escolhido].md` e aplicá-lo ao gerar o `spec.md`. Se nenhum for passado, usa `software.md`.

### 3. Remoção de Ruído Global
- O arquivo `rules/always-on/spec-quality-blueprint.md` impunha regras rigorosas de UI para QUALQUER projeto (até backend/data science). Ele será deletado e seu conteúdo mesclado dentro de `presets/blueprint.md`.

### 4. Shims (Decisão 2B)
- `blueprint-specify.toml` e `blueprint-plan.toml` terão seus prompts totalmente removidos e substituídos por uma mensagem:
> "⚠️ Este comando foi descontinuado na v0.4.0. Redirecionando seu pedido para /vitalia-spec-specify --preset=blueprint..."
