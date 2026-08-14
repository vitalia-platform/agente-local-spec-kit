<!-- quickstart_1.1_SyncEngine.md | Atualizado em: 24-07-2026 10:47:00(GMT-04:00) -->
# Quickstart: Spec 1.1 — Sync Engine

## Pré-requisitos

- Python 3.9+ instalado
- Dependências instaladas: `pip install -r requirements.txt`

---

## Cenário 1: Sincronização Completa (Padrão)

 Executar o script sem flags para sincronizar tanto a Constituição quanto o Smart Router:

```bash
python3 scripts/v0.4.0/sync-constitution.py -v
```

**Esperado**:
- Script retorna exit code `0`.
- Arquivo `rules/smart-router.md` é criado/atualizado a partir de `rules/smart-router.yaml`.
- Arquivo `rules/architect-constitution.md` possui cabeçalho de auditoria com timestamp ISO-8601 UTC.

---

## Cenário 2: Sincronização Seletiva (`--router` apenas)

Executar apenas a atualização do Smart Router:

```bash
python3 scripts/v0.4.0/sync-constitution.py --router -v
```

**Esperado**:
- Apenas `rules/smart-router.md` é atualizado.
- `rules/architect-constitution.md` não é modificado.

---

## Cenário 3: Validação de YAML Malformado

Testar a reação a um YAML com erro de sintaxe:

```bash
python3 scripts/v0.4.0/sync-constitution.py --router
```

**Esperado**:
- Exibe mensagem de erro clara indicando falha de parsing.
- Script encerra com exit code `1`.

---

## Cenário 4: Testes Automatizados

Executar a suíte de testes com PyTest:

```bash
pytest tests/v0.4.0/test_sync_engine.py -v
```

**Esperado**:
- Todos os testes passam (100% PASS).
