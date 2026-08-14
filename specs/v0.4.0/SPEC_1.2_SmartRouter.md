# Spec 1.2: Smart Router + Path Resolution

> **Épico**: Kit v0.4.0 — Integração SDD Completa  
> **Sprint**: 2  
> **Status**: 🟢 Em Execução  
> **Data**: 2026-07-24

---

## Propósito

Resolver o problema da "Troca de Modelo" que causa amnésia comportamental. O Antigravity não deve depender de um `AGENTS.md` gigante.
1. O `AGENTS.md` vira um *Thin Client* que aponta para as regras globais e proíbe hardcoding.
2. A intenção livre (linguagem natural) invoca o `vitalia-route.toml`, que carrega o `smart-router.md` gerado pela Spec 1.1 e roteia a conversa para a skill correta.
3. Garantir agnosticismo de *path*: o `install-project.sh` injeta a variável `{{VITALIA_KIT_DIR}}` em todos os shims e prompts no ato da instalação.

---

## Engenharia

### 1. `AGENTS.md` (O Thin Client)
O `AGENTS.md` que vai para o projeto será drástico e conciso (menos de 30 linhas).
Ele instruirá o agente a:
- Seguir o `architect-constitution.yaml`.
- Executar `/vitalia-route` quando o usuário fizer um pedido genérico, delegando a decisão arquitetural à tabela.

### 2. `vitalia-route.toml` (O Roteador)
Uma skill enxuta que:
- Lê o `smart-router.md`.
- Classifica a intenção do usuário (ex: "vamos depurar" -> debug).
- Sugere a chamada correta do comando (ex: `/debug`).

### 3. Agnosticismo em `install-project.sh`
O instalador deve substituir placeholders como `{{VITALIA_KIT_DIR}}` e `{{VERSION}}` nos `.toml` durante a instalação:
- No template Antigravity (`SKILL.md.template`), corrige o Bug 10 ("Vitalia Kit 0.3").
- Nos comandos `.gemini/commands/`, assegura que scripts globais possam ser acionados de qualquer lugar.
