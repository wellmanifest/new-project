# Ticket 172: Make agent work resumable without conversation memory

- **ID**: ticket-172
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-01

## Cel i Zakres

Zdefiniować i egzekwować mały kontrakt ciągłości pracy, dzięki któremu agent
po utracie kontekstu rozmowy, restarcie albo handoffie odtwarza stan z
bieżącego repozytorium i monotonicznego receiptu, a nie z pamięci modelu.
Checkpoint ma przechowywać tylko ograniczone, bezsekretowe referencje i nie
może udzielać autoryzacji ani zastępować ponownej obserwacji Git/PR/lease.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Zamknięty schemat odrzuca checkpoint bez dokładnego ticketu,
  intentu, HEAD-u, fazy, monotonicznego poprzednika albo bezpiecznego stanu
  workspace.
- [x] AC-02: Deterministyczny runtime zapisuje i rozwiązuje append-only chain,
  wykrywa rozjazd z bieżącym repozytorium oraz nie uznaje checkpointu za
  authority.
- [x] AC-03: `POLICY.md`, `CONTRIBUTING.md`, instrukcje hostów i dokumentacja
  opisują obowiązkowe momenty checkpointu, procedurę wznowienia oraz podział
  odpowiedzialności między `new-project`, ticket/git lifecycle, logs i runtime.
- [x] AC-04: Pakiet adopcyjny dostarcza schema, runtime i runbook, a pełna
  deterministyczna bramka standardu przechodzi na Linuxie.

## Ryzyka i Uwagi

- Risk 1: Checkpoint mógłby stać się drugim SSOT albo ukrytą zgodą. Mitygacja:
  pozostaje nieautorytatywną projekcją, a resume ponownie weryfikuje intent,
  Git, lease i zewnętrzne efekty.
- Risk 2: Snapshot brudnego workspace może ujawnić sekret. Mitygacja: standard
  przyjmuje wyłącznie zewnętrzną, przeskanowaną referencję i digest; bez niej
  checkpoint fail-closes zamiast kopiować deltę lub surowy log.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-172/`.
