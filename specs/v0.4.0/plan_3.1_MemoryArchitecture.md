# Plano Técnico: Spec 3.1 (Context Engine)

## 1. Módulos Core (`scripts/vitalia_context_engine.py`)

O script receberá o parâmetro `--session-dir` e `--machine-id`.
Usaremos a biblioteca `argparse` e `json` nativas para dependência zero de pacotes externos no core do kit.

### Comandos:
- `init`: Cria a pasta `.vitalia/memory/session/` (se não existir) e injeta os templates de `SESSION_STATE.md`, `LEARNINGS.md` e `DECISIONS.md`.
- `update-shard`: Grava o progresso no arquivo local do shard.
- `consolidate`: Lê todos os shards, mescla no `SESSION_HISTORY.md` e renderiza o `README.md`.

## 2. Refatoração dos TOML

**`extensions/session-start.toml`:**
- Remove o `.specify` e o `~/.vitalia-spec`.
- Aponta para `python3 scripts/vitalia_context_engine.py --action init` para forçar o setup no boot de projetos crus.

**`extensions/session-end.toml`:**
- Remove chamadas de scripts bash que não existem.
- Inclui a fase de Reflexão (gerar JSON de aprendizado que o LLM pede para o script consolidar).

**`extensions/session-consolidate.toml`:**
- Usa o `vitalia_context_engine.py --action consolidate` para gerar o `README.md`.

## 3. Correções Extras
- O bug do `install-project.sh` na sintaxe `sed` (s|{{NAME}}|${ext_name}|g).
