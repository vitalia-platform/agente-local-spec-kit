# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] — 2026-07-24

### ✨ Features
- **Sync Engine:** Implementação completa da sincronização seletiva (`--constitution` e `--router`) via `sync-constitution.py`.
- **Smart Router:** Parse e geração otimizada do YAML de regras com tabela formatada em Markdown.
- **Rastreabilidade:** Adição de metadados de execução e _commit hash_ aos cabeçalhos dos arquivos gerados.
- **Testes:** Nova suíte de testes robusta em `test_sync_engine.py` cobrindo sucesso, falhas sintáticas e flags do CLI.

### 🐛 Bug Fixes
- **Erros de Parse:** Implementado retorno humanizado de erros para sintaxe YAML malformada, indicando linha e coluna exatas.
- **Imports no Teste:** Corrigida a lógica de _import_ no pytest para processar scripts que contêm hífens em seu nome.
