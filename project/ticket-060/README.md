# Ticket 060: Upgrade reusable workflows to Node 24 actions

- **ID**: ticket-060
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-12

## Cel i Zakres

Usunąć ostrzeżenia o wycofaniu Node.js 20 z własnych workflow standardu przez
aktualizację immutable pinów `actions/checkout`, `actions/setup-python` i
`actions/github-script` do wydań działających na Node.js 24. Zmiana obejmuje
lokalne CI huba i publikowany reusable workflow governance; nie zmienia jego
uprawnień, zdarzeń, skryptów ani kontraktu wejść.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Polecenie użytkownika stanowi bounded
  `SESSION_EXECUTION_AUTHORIZATION` dla implementacji, testów i publikacji PR.
- [x] AC-02: Wszystkie własne użycia `checkout` i `setup-python` wskazują pełne
  SHA oficjalnych wydań z runtime Node.js 24.
- [x] AC-03: Oba użycia `github-script` wskazują pełne SHA v8, a istniejące
  skrypty zachowują używany interfejs CommonJS i Octokit bez migracji do v9.
- [x] AC-04: Pełny kontrakt Linux, Windows i reusable governance przechodzi, a
  Check Runs nie raportują adnotacji Node.js 20 pochodzących z tych workflow.
- [x] AC-05: Wymagana próba LLM-first `todo2code` kończy się jawnie fail-closed
  bez deterministycznego substytutu, gdy provider jest niedostępny, a
  niezależny Validator GLM zatwierdza dokładny HEAD PR bez findings.

## Ryzyka i Uwagi

- Nowe akcje wymagają runnera co najmniej `v2.327.1`; GitHub-hosted runners są
  sprawdzane przez rzeczywiste uruchomienia Linux i Windows.
- `github-script` v9 jest nowszy, ale wnosi breaking changes niezwiązane z
  usunięciem Node.js 20. Bounded naprawa używa v8, pierwszego wydania Node 24.
- Brak zmian wersji pakietu governance: workflow nie należy do payloadu
  adopcyjnego; downstream przypnie nowy commit standardu w osobnym ticketcie.

## Dowody zakończenia

- PR #88 został scalony jako `268311ba502cfa5306262f709e8086011c95088a`;
  post-merge run `31549898144` przeszedł na Linuxie i Windowsie.
- Validator `31549702362` przeanalizował dokładny head
  `29bb258ccef898dd7cbadb8d830339c57dff7044` przez GLM 5.2: dwa chunki,
  `APPROVE`, zero findings.
- todo2code `20260812T001526Z-c7dc29e7` wymagał GLM 5.2 na `a61f3b0`, ale
  provider zwrócił limit tygodniowy. Run zakończył się `LLM_UNAVAILABLE`, bez
  grafu, bez efektywnego modelu i bez fallbacku.
- Downstream `twin` run `31550250931` wykonał Linux, Windows i reusable
  governance na nowym SHA bez adnotacji. PR #7 został scalony jako
  `d4e435e6f25f514c075f8845c920ccb0d06705dd`, a finalny run po zamknięciu
  ticketu 004 (`31550934709`) pozostał zielony.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-060/`.
