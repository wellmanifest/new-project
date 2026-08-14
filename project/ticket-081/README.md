# Ticket 081: Adopt Policy DSL v1 for CONTRIBUTING

- **ID**: ticket-081
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-14

## Cel i Zakres

Adoptować `wellmanifest.policy/v1` jako jawny standard języka bloków
normatywnych w `CONTRIBUTING.md`, zachowując `VERSION 13` jako wersję profilu
dokumentu i `policy-sh@1` wyłącznie jako alias runtime. Dodać manifest profilu,
naprawić dwa policy-shaped bloki błędnie oznaczone jako Bash, udokumentować
granice Env DSL/LLM/MCP/POA i zabezpieczyć selektory testem regresji.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: Ticket wiąże jawne polecenie wykonania z dokładnym base SHA,
  czterema plikami implementacyjnymi i zerem zależności runtime.
- [ ] AC-02: `CONTRIBUTING VERSION 13` odróżnia wersję profilu dokumentu od
  Policy DSL v1 i aliasu `policy-sh@1`.
- [ ] AC-03: Wszystkie normatywne reguły Policy DSL używają selektora `dsl`;
  zwykłe przykłady Bash nie są interpretowane jako polityka.
- [ ] AC-04: `dsl-manifest.json` wiąże źródło, dokumentację i parser-contract
  dokładnymi SHA-256 oraz mapuje Policy DSL, Env DSL, DSL Standard i POA.
- [ ] AC-05: Manifest nie fabrykuje immutable locka do lokalnego,
  nieopublikowanego `policy-dsl`; opublikowane DSL i POA są przypięte dokładnie.
- [ ] AC-06: Test regresji wykrywa policy-shaped reguły poza kanonicznymi
  fence'ami i nadal przechodzi pełny audyt reguł.
- [ ] AC-07: Governance, wszystkie suite'y shell, Ruff, JSON i manifest
  conformance przechodzą; Docker jest jawnie niewymagany.

## Ryzyka i Uwagi

- `policy-dsl` pozostaje lokalnym standardem eksperymentalnym do chwili
  chronionej publikacji; manifest używa mappingu, nie fałszywego locka.
- Zmiana etykiety fence'a nie zmienia semantyki dwóch reguł, lecz usuwa
  ostrzeżenie kompatybilności i domyka deterministyczny selektor Markdown.
- Dokument ani wynik parsera nie stanowi zgody na wykonanie; efekty pozostają
  za chronioną granicą POA i governance.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-081/`.
