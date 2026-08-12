# Ticket 060: Upgrade reusable workflows to Node 24 actions

- **ID**: ticket-060
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-12

## Cel i Zakres

Usunąć ostrzeżenia o wycofaniu Node.js 20 z własnych workflow standardu przez
aktualizację immutable pinów `actions/checkout`, `actions/setup-python` i
`actions/github-script` do wydań działających na Node.js 24. Zmiana obejmuje
lokalne CI huba i publikowany reusable workflow governance; nie zmienia jego
uprawnień, zdarzeń, skryptów ani kontraktu wejść.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Polecenie użytkownika stanowi bounded
  `SESSION_EXECUTION_AUTHORIZATION` dla implementacji, testów i publikacji PR.
- [ ] AC-02: Wszystkie własne użycia `checkout` i `setup-python` wskazują pełne
  SHA oficjalnych wydań z runtime Node.js 24.
- [ ] AC-03: Oba użycia `github-script` wskazują pełne SHA v8, a istniejące
  skrypty zachowują używany interfejs CommonJS i Octokit bez migracji do v9.
- [ ] AC-04: Pełny kontrakt Linux, Windows i reusable governance przechodzi, a
  Check Runs nie raportują adnotacji Node.js 20 pochodzących z tych workflow.
- [ ] AC-05: LLM-first `todo2code` ocenia exact-head bez deterministycznego
  substytutu, a niezależny Validator App zatwierdza dokładny HEAD PR.

## Ryzyka i Uwagi

- Nowe akcje wymagają runnera co najmniej `v2.327.1`; GitHub-hosted runners są
  sprawdzane przez rzeczywiste uruchomienia Linux i Windows.
- `github-script` v9 jest nowszy, ale wnosi breaking changes niezwiązane z
  usunięciem Node.js 20. Bounded naprawa używa v8, pierwszego wydania Node 24.
- Brak zmian wersji pakietu governance: workflow nie należy do payloadu
  adopcyjnego; downstream przypnie nowy commit standardu w osobnym ticketcie.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-060/`.
