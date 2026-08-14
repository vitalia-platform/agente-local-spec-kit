<!-- architect-constitution.md | Atualizado em: 12-08-2026 21:52(GMT-04:00) -->

# Constituição Vitalia
**Vitalia 2.0 · Spec-Driven Development Edition**

> Estes princípios são **imutáveis** na ausência de emenda formal.
> Governam todo o desenvolvimento — código, conteúdo científico e decisões de arquitetura.
> Nenhuma pressão de prazo, nenhum atalho, nenhuma exceção não documentada os suspende.

**Versão**: 1.0 | **Ratificada**: 05-06-2026 | **Status**: ✅ ATIVA

---

## Artigo 0 — Propósito (O Árbitro Final)

> **Toda decisão técnica serve ao bem-estar de quem usa, de quem cuida e de quem constrói.**

Quando um artigo desta constituição for insuficiente para resolver uma situação, quando dois artigos colidirem sem resolução clara, ou quando surgir um caso não previsto, este propósito é o critério de desempate.

*"Tecnologia a serviço do bem-estar humano — com rigor clínico e a clareza de quem sabe o porquê de cada regra."*

---

## Seção I — Processo: Como Construímos

### Artigo I — Spec-Driven Development (SDD) é o Único Caminho

Toda feature começa com uma especificação escrita e aprovada — sem exceção.

```
$speckit-specify  →  spec.md aprovada pelo usuário
$speckit-plan     →  plano técnico aprovado pelo usuário
$speckit-tasks    →  tarefas granulares
$speckit-implement → código que implementa o especificado
```

A execução segue o planejamento. O contrário indica falha de processo.

**Gate obrigatório (O "Kill Switch"):** É ESTRITAMENTE PROIBIDO que a IA utilize modos de planejamento nativos de sua IDE (como a criação autônoma de `implementation_plan.md` ou `task.md` em pastas ocultas do sistema). Se uma solicitação requer planejamento ou alteração arquitetural, a IA **DEVE** bloquear a execução imediata e exigir que o usuário inicialize o funil SDD (ex: `/vitalia-spec-specify`). Mudanças investigatórias ou triviais estão isentas desta rigidez, mas grandes alterações não.
Nenhum código é escrito antes da spec estar formalmente criada na estrutura do projeto e aprovada.

Em domínios de saúde, a aprovação da spec inclui o `vitalia-medical-gate` (ver Seção III).

### Artigo II — Decomposição Atômica

Épicos são quebrados em tarefas granulares, sequenciais e individualmente testáveis.

- Cada tarefa tem critério de aceitação verificável antes de iniciar
- Nenhum commit quebra o build
- Nenhuma tarefa depende de outra não concluída para ser testada isoladamente

### Artigo III — Test-First (Inegociável)

Nenhuma lógica de negócio é implementada antes dos testes estarem escritos, aprovados pelo usuário e confirmados falhando (fase Red).

```
Testes escritos → aprovados → confirmados falhando → implementação (Green) → refatoração (Refactor)
```

| Camada | Cobertura mínima |
|---|---|
| Services / Use Cases | 90% |
| Views / Controllers | 70% |
| Utilities / Helpers | 80% |
| Models (métodos customizados) | 85% |

### Artigo IV — Análise de Impacto Holística (Lei Zero)

Antes de iniciar qualquer spec (`$speckit-specify`), validar o impacto em:

| Dimensão | O que verificar |
|---|---|
| **Multi-Tenancy** | A query filtrará por `organization_id`? |
| **RBAC** | O usuário terá permissão no recurso específico — não apenas estar logado? |
| **LGPD/HIPAA** | Há dado sensível envolvido? O consentimento está coberto? |
| **Performance** | Há risco de N+1? Queries relacionais usarão eager loading? |
| **Segurança** | Input será validado? Stack trace não vazará para o cliente? |

*Nota: LGPD/HIPAA na spec desencadeia a Seção II (proteção de dados) e a Seção III (HITL). Não é verificação redundante — é o gatilho.*

---

## Seção II — Dados e Segurança: Como Protegemos

### Artigo V — Soberania do Dado (Data Vault)

> O dado de saúde pertence ao **Participante**, não à Organização.

- Acesso é concedido temporariamente via consentimento explícito e registrado
- Nenhuma query ignora o filtro por `user_id` + `organization_id`
- Campos PII e de saúde são criptografados em repouso (nível de campo)
- Logs nunca contêm dado de saúde em texto puro — apenas IDs e timestamps
- Toda entidade com dado de saúde suporta exclusão auditável (LGPD Art. 18)

### Artigo VI — Segredos Nunca Entram no Git

- Credenciais e segredos existem apenas em variáveis de ambiente locais ou vaults de produção
- Migrações de banco são não-destrutivas e idempotentes
- Dados sensíveis têm migrações separadas das de schema

### Artigo VII — Segurança de API por Padrão

Nenhum endpoint de dado de saúde é público. Checklist bloqueante para todo PR:

- [ ] Autenticação (JWT ou equivalente)
- [ ] Autorização por recurso específico — não apenas estar logado
- [ ] Rate limiting em rotas sensíveis
- [ ] Validação de input via schema antes de processar
- [ ] Multi-tenancy: filtro por `organization_id`
- [ ] Stack trace nunca vaza para o cliente

---

## Seção III — Saúde e IA: Como Cuidamos

> *IA alucina. Em saúde, isso tem consequências reais. Humano no comando sempre.*

### Artigo VIII — HITL Gate de Especificação

Antes de qualquer `$speckit-plan` envolvendo domínio de saúde, o `vitalia-medical-gate` é acionado para classificar o risco e emitir constraints.

**Classificação de risco**:

| Nível | Critério | Protocolo |
|---|---|---|
| 🟢 **LOW** | Dados genéricos, sem exibição ao usuário, sem risco de dano direto | Sem gate — segue para `$speckit-plan` |
| 🟡 **MEDIUM** | Dados individuais **OU** exibição ao usuário **OU** risco moderado | Gate HITL: usuário aprova constraints antes do plan |
| 🔴 **HIGH** | 2+ fatores de risco + conteúdo clínico direto ao usuário | Gate HITL + revisão de profissional de saúde humano |

**Domínios que acionam gate automaticamente**: diagnóstico, sintomas, condições médicas,
protocolos de tratamento, suplementação, biomarcadores, nutrição individualizada,
dosagens, planos personalizados de saúde/wellness/fitness, fórmulas fisiológicas
exibidas ao usuário (FC, VO₂max, zonas de treino, IMC, etc.).

### Artigo IX — HITL Gate de Publicação

Independentemente do resultado do gate de especificação, **nenhum conteúdo médico vai para produção** sem percorrer esta hierarquia:

```
IA gera conteúdo          → status: DRAFT    (não exibível ao usuário)
Especialista científico   → status: REVIEW   (em avaliação interna)
Profissional de saúde     → status: ACTIVE   ← único estado publicável
```

Este gate é separado do gate de especificação: uma feature pode ter a spec aprovada (Artigo VIII) e ainda assim ter conteúdo clínico específico aguardando aprovação de publicação.

### Artigo X — Rastreabilidade de Evidência

Todo constraint médico (`MC-NNN`) carrega obrigatoriamente:
- Identificador rastreável (`MC-001`, `MC-GLOBAL-001`)
- Fonte científica com nível de evidência
- Comentário de rastreabilidade no código:

```python
# FONTE: exercise-physiologist-review-05-06-2026 | Ref: Tanaka2001 | MC-001
HRMAX = lambda age: 208 - 0.7 * age
```

Toda decisão da IA com impacto clínico tem seu raciocínio registrado em formato auditável — para explicabilidade jurídica e clínica.

**Níveis de evidência**:

| Nível | Critério |
|---|---|
| **A** | Meta-análise ou múltiplos RCTs de alta qualidade |
| **B** | RCT único bem desenhado ou consenso de sociedade médica reconhecida |
| **C** | Expert opinion ou guideline sem RCT de alta qualidade |

Nível C é aceito apenas quando A e B não existirem para o tema específico.

### Artigo XI — Disclaimers Obrigatórios

Todo conteúdo de saúde exibido ao usuário final está em **DRAFT** até aprovação de profissional humano e inclui:

> *"Esta informação é de natureza educacional. Consulte um profissional de saúde habilitado antes de tomar decisões médicas."*

---

## Seção IV — Arquitetura: Como Organizamos

### Artigo XII — Desacoplamento Limpo e Zero Hardcoding

```
Services    → Lógica de Negócio Pura
Clients     → Comunicação Externa (APIs, LLMs, serviços externos)
Views/Tasks → Orquestração
Config      → Toda variável, regra de negócio e path vem de ENV ou arquivo de configuração
```

Hardcoding no código-fonte é terminantemente proibido.

### Artigo XIII — Contrato-Primeiro (API-First)

O contrato (schema de API, serializers, OpenAPI) é a fonte da verdade.
Frontend e Backend se alinham pelo contrato antes da implementação.
Serializers de leitura (dados aninhados para exibição) são separados dos de escrita (validação estrita de entrada).

### Artigo XIV — Simplicidade Antes de Elegância (YAGNI)

- Inicie com o mínimo de projetos/serviços que resolva o problema real
- Projetos adicionais exigem justificativa documentada na spec
- Use recursos do framework diretamente — sem wrappers que não agregam valor verificável
- Complexidade é adicionada apenas quando provada necessária, nunca antecipada

---

## Seção V — Qualidade: Como Garantimos

### Artigo XV — Carimbo de Tempo e Auditoria Absoluta

Todo arquivo editado ou gerado carrega o timestamp de modificação:

```
<!-- nome_arquivo.md | Atualizado em: DD-MM-YYYY HH:MM:SS(GMT-04:00) -->
```

- Fuso `(GMT-04:00)` — `America/Cuiaba` — **imutável e sem exceções**
- Arquivos de registro (historiais, changelogs): entrada mais recente **no topo** (cronologia reversa)
- Todo artefato tem autoria, data e versão identificáveis

### Artigo XVI — Integridade de Artefato

Toda edição deixa o arquivo em estado válido, sem regressões e sem contexto perdido.
Modificações parciais que tornam o arquivo inconsistente são vetadas — causam erros de integração silenciosos.

### Artigo XVII — Ambiente Reprodutível

- Toda dependência é declarada explicitamente, versionada e instalada em ambiente isolado
- Builds são reprodutíveis: o que funciona localmente funciona em produção
- Ambiente de desenvolvimento é espelho fiel da produção

### Artigo XVIII — Observabilidade e Performance

- Queries relacionais usam eager loading quando aplicável — N+1 é uma falha de design
- Processamento pesado vai para filas dedicadas, não para o ciclo de request
- Structured logging obrigatório em serviços críticos
- Comportamento real de APIs externas é validado antes da implementação — não confiar apenas em documentação
- **Ver regra `grounding.md`** — protocolo completo de verificação por domínio (always-on)

---

## Seção VI — Produto e Evolução: Como Crescemos

### Artigo XIX — Lançamentos Graduais (Feature Flags)

Features complexas ou de alto risco são desenvolvidas atrás de feature flags.
Deploy contínuo sem impacto em produção até validação completa.
Especialmente obrigatório para features de saúde com risco MEDIUM ou HIGH.

### Artigo XX — Documentação É Artefato de Entrega

O código não está pronto se `README.md` e `.env.example` não refletirem as mudanças.
Documentação é escrita junto com o código, não depois.

### Artigo XXI — Automação como Guardiã

Processos repetitivos (backup, restore, setup, instalação, validação) têm scripts correspondentes.
Um processo que depende de execução manual correta é um processo com falha aguardando acontecer.

### Artigo XXII — Especialista Certo para Cada Domínio

Cada domínio tem um especialista responsável pelas decisões dentro dele.
O agente identifica o domínio da solicitação e ativa o especialista adequado — sem nomeação explícita necessária.
O usuário pode sempre sobrescrever com `@nome-do-agente` ou menção direta ao especialista.

*A tabela de mapeamento domínio → especialista é mantida em `AGENTS.md` e atualizada conforme o kit evolui.*

### Artigo XXIII — Manutenção do Kit (Agnóstico de Path)

Toda edição estrutural no kit (workflows, rules, skills, templates) é realizada via os symlinks em `.specify/`,
de forma agnóstica a caminhos de repositórios específicos.
Isso mantém o kit viável como template distribuível para projetos independentes.

---

## Governança da Constituição

**Hierarquia de autoridade**:

```
Artigo 0 (Propósito — árbitro final de conflitos não previstos)
    ↓
Constituição (Artigos I–XXIII)        ← imutável sem emenda formal
    ↓
Regras Always-On do Kit               ← ativas em toda sessão
    ↓
Medical Gate (Artigos VIII e IX)      ← acionado por $speckit-specify em domínios de saúde
    ↓
Constraints da Feature (MC-NNN)       ← específicos por spec aprovada
    ↓
Decisões de Implementação             ← do agente e do desenvolvedor
```

**Resolução de conflitos**:

```
Art. 0 (Propósito)  >  Art. V/VI (Privacidade/Segredos)  >  Art. VIII/IX (HITL)  >  Art. X (Evidência)  >  demais
```

**Emenda**: toda modificação a esta constituição requer:
1. Documentação do racional da mudança
2. Aprovação HITL explícita do responsável pelo projeto
3. Avaliação de compatibilidade com artigos existentes
4. Atualização do número de versão e data

**Violações e resposta**:

| Violação detectada | Severidade | Ação do agente |
|---|---|---|
| Segredo detectado em código ou commit | 🔴 CRÍTICO | Bloquear imediatamente + alertar |
| Feature de saúde MEDIUM/HIGH sem gate | 🔴 CRÍTICO | Bloquear — sem exceção |
| Dado de saúde sem criptografia | 🔴 CRÍTICO | Bloquear — apontar padrão correto |
| Conteúdo médico ao usuário sem aprovação | 🔴 CRÍTICO | Marcar DRAFT + bloquear publicação |
| Código escrito sem spec aprovada | 🟡 ALTO | Bloquear — retornar ao `$speckit-specify` |
| Constraint MC-NNN sem fonte científica | 🟡 ALTO | Bloquear — solicitar referência |
| Teste ausente em service/core | 🟡 ALTO | Bloquear — TDD não é opcional |
| Hardcoding detectado | 🟡 ALTO | Bloquear — mover para ENV/config |
| Timestamp ausente ou fuso errado | 🟢 BAIXO | Corrigir — não bloqueia o trabalho |
| Documentação desatualizada | 🟢 BAIXO | Sinalizar — corrigir antes do PR |


