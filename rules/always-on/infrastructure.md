---
description: "Regra de Rastreabilidade e Log (P4)"
trigger: always_on
---
<!-- infrastructure.md | Atualizado em: 26-06-2026 12:08:28(GMT-04:00) -->

# Infrastructure Rule (P4)

## P4: Rastreabilidade e Carimbo de Tempo

- Toda interação gerada pelo assistente DEVE iniciar com um cabeçalho técnico oculto ou visível (conforme spec) contendo:
  - Timestamp: `[DD-MM-YYYY HH:MM:SS(GMT-04:00)]`
  - Version: `Vitalia 2.0-SpecKit`
- O fuso horário `(GMT-04:00)` (America/Cuiaba) é obrigatório e imutável.
- Em arquivos de documentação markdown editados (ex: CONTEXT.md), você deve atualizar o cabeçalho no topo na primeira linha de comentário. Ex: `<!-- nome_arquivo.md | Atualizado em: 10-05-2026 14:30:00(GMT-04:00) -->`
