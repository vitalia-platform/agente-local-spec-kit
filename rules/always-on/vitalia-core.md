---
description: "Vitalia Core Governance (P1, P2, P7, P9) - Governança base de saúde e privacidade."
trigger: always_on
---
<!-- vitalia-core.md | Atualizado em: 26-06-2026 12:08:28(GMT-04:00) -->

# Vitalia Core Governance

## P2: User-Centric Validation

- Todas as sugestões técnicas devem ser acompanhadas de um "Impacto ao Usuário Final".
- Se uma decisão de design for tomada, justifique-a com base na necessidade do usuário.

## P7: Privacy by Design (LGPD / Data Vault)

- O dado de saúde pertence ao Participante, não à Organização.
- Nunca solicite ou armazene PII (Personally Identifiable Information) sem flag de consentimento explícita.
- Respostas que envolvem dados de saúde simulados ou reais devem ser sanitizadas por padrão.

## P9: Human-in-the-Loop (HITL) - Friction for Safety

- Para decisões críticas de arquitetura e aprovações clínicas, a IA deve parar e solicitar: "Aguardando aprovação humana para prosseguir com [X]".
- Em fluxos de Alto Risco, a UX e a implementação do código devem refletir a impossibilidade de "aprovação cega".
