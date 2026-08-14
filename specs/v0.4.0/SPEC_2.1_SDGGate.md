# Spec 2.1: SDD Gate e Cleanup

> **Épico**: Kit v0.4.0 — Integração SDD Completa  
> **Sprint**: 3  
> **Status**: 🟢 Em Execução  
> **Data**: 2026-07-24

---

## Propósito

Impedir a "Ação Órfã" (desenvolvimento sem planejamento) forçando as skills executoras a verificarem o estado do planejamento antes de tocarem no código. Aproveitar a oportunidade para criar o especialista bibliográfico (separando ele do antigo `/session-start`).

---

## Engenharia

### 1. O Passo 0 Obrigatório
Nos arquivos `continue.toml`, `pair.toml` e `debug.toml`, a **Fase 1: Reconhecimento** passa a ter o **Passo 0**:
```markdown
### Passo 0: Validação SDD (Obrigatório)
1. Antes de ler qualquer código, verifique se existe um arquivo `tasks.md` pendente para a feature atual.
2. Se NÃO existir, acione a **Technical Stop Flag**: pare o processo imediatamente e instrua o usuário a rodar o comando `/vitalia-spec-specify`. Não gere nenhum código.
3. Se existir, verifique se a ação solicitada está mapeada neste documento.
```

### 2. O Especialista Bibliográfico (`vitalia-integrative-review.toml`)
Criação da skill dedicada ao fluxo PRISMA e revisão integrativa, permitindo a transição segura dos blocos de pesquisa sem poluir o início das sessões regulares de software.
