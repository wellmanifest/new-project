<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# wygeneruj

Pewnie — poniżej masz **propozycję lepszego formatu DSL v1**, zaprojektowanego pod **czytelność dla człowieka i LLM** oraz pod **runtime w TypeScript** zgodny z celem z README: `NL -> LLM ts -> DSL -> ts-runtime -> js/nodejs code`.[^1]

## Proponowany format: `workflow.dsl.yaml`

Najlepszy kompromis to **YAML-like DSL z jawnymi blokami `when/then/else`**. Jest czytelny, łatwy do edycji ręcznej, a jednocześnie prosty do walidacji i parsowania w TS.[^1]

```yaml
version: 1
kind: workflow
id: office-command-router
title: "Routing poleceń biurowych"
description: "Konwertuje polecenie człowieka na decyzję, pytanie doprecyzowujące albo wykonanie akcji."

metadata:
  owner: perplexity
  audience: human+ai
  domain: office-automation

inputs:
  user_request:
    type: natural_language
    required: true
  context:
    type: object
    required: true
  sources:
    type: list
    items:
      type: string
    required: false

facts:
  access_to_logs:
    type: boolean
    default: false
  access_to_db:
    type: boolean
    default: false
  user_approval:
    type: boolean
    default: false
  command_is_safe:
    type: boolean
    default: true

steps:
  - id: analyze_request
    action: llm.analyze
    input: user_request
    output: analysis

  - id: detect_missing_data
    action: rule.evaluate
    output: decision

rules:
  - id: ask_for_clarification
    priority: 10
    when:
      any:
        - fact: access_to_logs
          equals: false
        - fact: access_to_db
          equals: false
    then:
      emit:
        type: question
        text: "Brakuje dostępu do logów lub bazy danych. Co mam użyć jako źródło prawdy?"

  - id: request_confirmation
    priority: 20
    when:
      all:
        - fact: user_approval
          equals: false
        - fact: command_is_safe
          equals: false
    then:
      emit:
        type: confirmation
        text: "Polecenie wymaga potwierdzenia. Czy mam kontynuować?"

  - id: generate_dsl_request
    priority: 30
    when:
      all:
        - fact: access_to_logs
          equals: true
        - fact: access_to_db
          equals: true
        - fact: user_approval
          equals: true
    then:
      emit:
        type: dsl_request
        template: request.v1
        set:
          source: user_request
          context: context
          evidence:
            - logs
            - db

outputs:
  decision:
    type: enum
    values: [question, confirmation, dsl_request, reject]

  request.v1:
    type: object
    fields:
      source: string
      context: object
      evidence:
        type: list
        items:
          type: string
```


## Co jest lepsze od obecnych wersji

Ten format jest lepszy niż to, co widać w obecnych plikach, bo:

- rozdziela **metadane, wejścia, fakty, reguły i wyjścia**,
- ma **jawny priorytet** reguł,
- nie miesza opisu z wykonaniem,
- daje jednoznaczny model dla parsera,
- jest przyjazny do ręcznej edycji przez człowieka.[^2][^3][^4][^1]


## Minimalny grammar dla runtime

Dla runtime w TypeScript warto przyjąć taki model semantyczny:

```ts
type Workflow = {
  version: number;
  kind: "workflow";
  id: string;
  title: string;
  description?: string;
  metadata?: Record<string, unknown>;
  inputs: Record<string, InputDef>;
  facts?: Record<string, FactDef>;
  steps?: StepDef[];
  rules: RuleDef[];
  outputs?: Record<string, OutputDef>;
};
```

I reguły w stylu:

```ts
type RuleDef = {
  id: string;
  priority?: number;
  when: Condition;
  then: Action;
};
```

To umożliwia:

- walidację schematu,
- kompilację do AST,
- testowanie reguł,
- generowanie kodu frontend/backend,
- łatwe wersjonowanie.[^1]


## Jak bym zrobił runtime

Polecam taki układ repo:

```text
dsl/
  workflow.dsl.yaml
  examples/
    office-router.dsl.yaml
    approval-flow.dsl.yaml
runtime/
  src/
    parser.ts
    schema.ts
    evaluator.ts
    compiler.ts
    ast.ts
    types.ts
  tests/
    parser.test.ts
    evaluator.test.ts
    compiler.test.ts
frontend/
backend/
tools/
  python/
    nl_to_dsl_checker.py
```

To dobrze odpowiada temu, co opisujesz w README: osobny DSL, osobny runtime TS, przykłady, testy i integracje dla frontend/backend.[^1]

## Co powinno być w DSL v1

W pierwszej wersji dodałbym tylko:

- `metadata`
- `inputs`
- `facts`
- `rules`
- `outputs`
- `priority`
- `when/then`
- `emit`
- `set`

Nie dodawałbym jeszcze za dużo feature’ów, bo przy Twoim celu najważniejsze jest, żeby:

- LLM generował poprawny plik,
- człowiek mógł go czytać,
- runtime mógł go deterministycznie wykonać.[^1]


## Co dalej

Najlepszy następny krok to stworzyć:

1. **`workflow.dsl.yaml` jako spec v1**,
2. **JSON Schema** do walidacji,
3. **TypeScript parser/evaluator**,
4. **przykłady w `examples/`**,
5. **python checker** porównujący semantykę NL → DSL → JS.[^1]

Mogę w kolejnym kroku od razu wygenerować Ci:

- pełny **JSON Schema**,
- pełny **parser TypeScript**,
- albo **pierwszy zestaw 3 przykładowych plików DSL**.

<div align="center">⁂</div>

[^1]: README.md

[^2]: CONTRIBUTING.md

[^3]: CONTRIBUTING-2.md

[^4]: CONTRIBUTING-3.md

