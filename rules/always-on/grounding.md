---
name: rule-grounding
description: Protocolo de verificação externa para domínios onde conhecimento interno é insuficiente.
trigger: always_on
---
<!-- grounding.md | Vitalia Kit v0.5.0 | 12-08-2026 21:26(GMT-04:00) -->

# Regra: Grounding — Verificação Externa Obrigatória

## Domínios que Exigem Verificação

Antes de afirmar qualquer coisa sobre os domínios abaixo, **PARE e busque**:

- **llm_models** — versões, preços, limites de modelos LLM
- **python_packages** — versões, compat, breaking changes (pypi.org)
- **external_apis** — endpoints, schemas, rate limits de APIs externas
- **security_practices** — CVEs, vulnerabilidades (nvd.nist.gov, owasp.org)
- **regulations** — LGPD, HIPAA, GDPR (gov.br/anpd/pt-br, hhs.gov/hipaa)
- **cloud_services** — preços, SLAs, limites (aws/gcp/azure/oracle/do)
- **scientific_claims** — eficácia de técnicas, benchmarks (pubmed, cochrane)

Domínios isentos (conhecimento interno é suficiente): sintaxe de linguagem, algoritmos
fundamentais, padrões de arquitetura, lógica de negócio do projeto, comandos shell.

Ver lista completa: `~/.vitalia/kit/config/grounding-domains.yaml`

## Protocolo (4 Passos)

1. **PARE** — identifique se a afirmação envolve um domínio acima
2. **BUSQUE** — use `search_web` ou `read_url_content` para verificar
3. **CITE** — inclua URL e data na tabela de Rastro de Pesquisa
4. **SE SEM RESULTADO** — marque como `NAO VERIFICADO` na tabela

## Rastro de Pesquisa (obrigatório em todo artefato)

Todo artefato gerado (brainstorming, spec, plan, research.md) que contenha afirmações
sobre domínios verificáveis DEVE incluir ao final:

```markdown
## Rastro de Pesquisa — [Nome do Artefato]
**Gerado em:** DD-MM-YYYY HH:MM(GMT-04:00) | **Domínios verificados:** [lista]

| # | Afirmação feita | Verificado? | Fonte consultada | Data |
|---|---|---|---|---|
| 1 | "..." | Sim | url.completa/path | DD-MM-YYYY |
| 2 | "..." | NAO VERIFICADO | — | — |
```

<grounding_rules>
NUNCA afirme versões de pacotes, APIs ou modelos sem busca externa prévia.
NUNCA cite URLs de memória — sempre verifique se o domínio existe.
NUNCA use "mais moderno" ou "melhor" para decisões técnicas sem fonte verificada.
NUNCA omita o Rastro de Pesquisa quando o artefato contém afirmações verificáveis.
</grounding_rules>
