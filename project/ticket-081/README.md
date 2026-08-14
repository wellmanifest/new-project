# Ticket 081: Adopt Policy DSL v1 for CONTRIBUTING

- **ID**: ticket-081
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-14

## Cel i Zakres

Adoptować `wellmanifest.policy/v1` jako jawny standard języka bloków
normatywnych w `CONTRIBUTING.md`, zachowując `VERSION 13` jako wersję profilu
dokumentu i `policy-sh@1` wyłącznie jako alias runtime. Dodać manifest profilu,
naprawić dwa policy-shaped bloki błędnie oznaczone jako Bash, udokumentować
granice Env DSL/LLM/MCP/POA i zabezpieczyć selektory testem regresji.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Ticket wiąże jawne polecenie wykonania z aktualnym dokładnym base SHA,
  czterema plikami implementacyjnymi i zerem zależności runtime.
- [x] AC-02: `CONTRIBUTING VERSION 13` odróżnia wersję profilu dokumentu od
  Policy DSL v1 i aliasu `policy-sh@1`.
- [x] AC-03: Wszystkie normatywne reguły Policy DSL używają selektora `dsl`;
  zwykłe przykłady Bash nie są interpretowane jako polityka.
- [x] AC-04: `dsl-manifest.json` wiąże źródło, dokumentację i parser-contract
  dokładnymi SHA-256 oraz mapuje Policy DSL, Env DSL, DSL Standard i POA.
- [x] AC-05: Manifest przypina opublikowany kontrakt `policy-dsl` do dokładnej,
  chronionej rewizji i digestów; DSL Standard oraz POA pozostają przypięte.
- [x] AC-06: Test regresji wykrywa policy-shaped reguły poza kanonicznymi
  fence'ami i nadal przechodzi pełny audyt reguł.
- [x] AC-07: Governance, wszystkie suite'y shell, Ruff, JSON i manifest
  conformance przechodzą; Docker jest jawnie niewymagany.

## Ryzyka i Uwagi

- `policy-dsl` pozostaje standardem eksperymentalnym, lecz jego kontrakt v1 ma
  chronioną publikację; profil nie śledzi mutowalnej gałęzi ani taga.
- Zmiana etykiety fence'a nie zmienia semantyki dwóch reguł, lecz usuwa
  ostrzeżenie kompatybilności i domyka deterministyczny selektor Markdown.
- Dokument ani wynik parsera nie stanowi zgody na wykonanie; efekty pozostają
  za chronioną granicą POA i governance.

## Dowody walidacji

- Manifest i standards lock: `DSL-PASS` bez błędów.
- Pełny carrier `CONTRIBUTING.md`: `POLICY-MARKDOWN-PASS`.
- Dziewięć suite'ów `tests/*.test.sh`: PASS; Ruff dla `scripts`: PASS.
- Cztery pliki implementacyjne i ich SHA-256 mieszczą się dokładnie w intencie;
  brama Hub raportuje `GOV-PASS` bez błędów i ostrzeżeń.
- Docker: niewymagany przez `governance/manifest.hub.json`.
- Po integracji ticketu 080 profil został ponownie oparty na `main` i związał
  kontrakty z reviewed revision
  `daaf7b7b96312a2469de1b4799f2f81c7396de4e`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-081/`.
