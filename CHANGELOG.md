# Changelog

All notable changes to this project will be documented in this file.

## [0.6.0] — 2026-08-26

### ✨ Features
- **Context Engine:** Refatoração completa para Arquitetura Orientada a Objetos (OOP) no `vitalia_context_engine.py`, resolvendo deadlocks com timeout estrito de 15 segundos para operações remotas de Git.
- **Hook Runner:** Criação do `vitalia_hook_runner.py` nativo (Opção C), processando TOML puramente via `tomllib` e emitindo JSON unificado para o Antigravity IDE consumir de forma passiva.
- **Integração:** Novo `SKILL.md.template` atualizado para acionar o hook runner nativamente, reduzindo alucinações e consumo de tokens pelo agente.

### 🐛 Bug Fixes
- **Segurança (SSH):** Implementação de `GIT_TERMINAL_PROMPT=0` nas execuções de background do Git para prevenir deadlocks com solicitação de chaves SSH não destravadas.

## [0.5.0] — 2026-08-14

### ✨ Features
- **Task Verifier:** Criação do `verify_tasks.py` implementando o LLM-as-a-Judge local.
- **Memória 3-Tier:** Consolidação do padrão v0.5.0 e regras globais de grounding.

## [0.4.0] — 2026-07-24

### ✨ Features
- **Sync Engine:** Implementação completa da sincronização seletiva (`--constitution` e `--router`) via `sync-constitution.py`.
- **Smart Router:** Parse e geração otimizada do YAML de regras com tabela formatada em Markdown.
- **Rastreabilidade:** Adição de metadados de execução e _commit hash_ aos cabeçalhos dos arquivos gerados.
- **Testes:** Nova suíte de testes robusta em `test_sync_engine.py` cobrindo sucesso, falhas sintáticas e flags do CLI.

### 🐛 Bug Fixes
- **Erros de Parse:** Implementado retorno humanizado de erros para sintaxe YAML malformada, indicando linha e coluna exatas.
- **Imports no Teste:** Corrigida a lógica de _import_ no pytest para processar scripts que contêm hífens em seu nome.
