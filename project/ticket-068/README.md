# Ticket 068: Correct Goal release contract and publish remediation DSL

- **ID**: ticket-068
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-12

## Cel i Zakres

Usunąć wygenerowaną dla ticketu 065 konfigurację Goal, która omyłkowo
przedstawia Governance Hub jako pakiet publikowany do rejestrów. Dodać
źródłowy manifest huba i uruchamiać istniejący deterministyczny validator na
rzeczywistym diffie PR, aby zmiana spoza `intent.allowedPaths` nie mogła
ponownie przejść na samych testach fixture'ów. Następnie opublikować scalony
DSL remediacji jako immutable `v0.16.0`.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: CI huba deterministycznie wiąże diff PR z dokładnie jednym
  aktywnym ticketem i odrzuca ścieżkę spoza jego `allowedPaths`.
- [x] AC-02: `goal.yaml` ma tożsamość `new-project`, nie deklaruje żadnego
  registry ani strategii publikacji pakietów i dopuszcza wyłącznie zarządzany
  PR oraz immutable release z `main`.
- [ ] AC-03: wersje w `VERSION`, manifeście targetu i manifeście huba są
  spójne, a pełne Linux/Windows contract tests przechodzą na exact HEAD i po
  merge.
- [ ] AC-04: annotowany tag i finalny GitHub Release `v0.16.0` wskazują
  dokładny, czysty i ponownie przetestowany commit `origin/main`.

## Ryzyka i Uwagi

- Goal scala brakujące klucze z szerokimi defaultami. Konfiguracja jawnie
  klasyfikuje hub jako projekt `generic`, a test sprawdza surowy kontrakt bez
  rejestrów; filesystem nie zawiera manifestu pakietu, więc registry stage nie
  może się aktywować.
- Source Hub i repozytorium adoptujące mają inne granice własności. Osobny
  manifest huba nie jest częścią pakietu adopcyjnego i nie zastępuje
  `manifest.default.json`.
- Publikacja nastąpi dopiero po trusted exact-head review, merge i czystym
  powtórzeniu testów.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-068/`.
