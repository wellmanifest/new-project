# Ticket 038: Provenance-bound atomic standard adoption transaction

- **ID**: ticket-038
- **Owner**: agent:codex
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-08-08

## Cel i zakres

Immutable upgrade standardu zastępuje jeden hash-locked zestaw plików
`managed`. Taki zestaw może przekroczyć zwykły limit liczby plików i przeciąć
normalne granice workstreamów, mimo że jest jedną niepodzielną operacją.
Dzielenie zmiany pozostawia target z lockiem niezgodnym z plikami; poszerzanie
globalnego budżetu lub własności osłabia wszystkie przyszłe tickety.

Ticket doda jawny kontrakt `delivery.standardAdoption` do intentu oraz
deterministyczne rozpoznawanie jednej atomowej transakcji. Z rozliczenia
zwykłego diffu można wyłączyć wyłącznie zmienione targety o strategii
`managed`, gdy:

- bazowy i docelowy lock są poprawne, a ich `sourceRevision` odpowiadają
  zatwierdzonym `fromRevision` i `toRevision`;
- dla aktualizowanej ścieżki bazowy i docelowy package manifest identyfikują
  ją jako `managed`, a zawartość z obu stron odpowiada właściwym lockom;
- dla nowej ścieżki plik nie istnieje w bazie, docelowy package manifest
  identyfikuje go jako `managed`, a head zawartość odpowiada head lockowi;
- repozytorium źródłowe jest dokładnie `wellmanifest/new-project`;
- pozostały target-local diff nadal rozwiązuje się do jednego aktywnego
  ticketu i przechodzi zwykły budżet, ownership, scope oraz approval.

Target-local seed manifest, `.governance/manifest.lock.json`, changelog oraz
każdy plik spoza zweryfikowanego zbioru `managed` nie otrzymują wyjątku.
Lock i intent są dowodem strukturalnym, nie zaufaną autoryzacją merge;
protected exact-head review lub zweryfikowana atestacja pozostają wymagane.

## Kryteria odbioru

- [x] AC-01: Intent v3 opcjonalnie i ściśle deklaruje
  `delivery.standardAdoption` z repozytorium oraz pełnymi, różnymi SHA
  `fromRevision` i `toRevision`.
- [x] AC-02: Poprawna zmiana pełnego zbioru `managed` jest rozliczana jako
  jedna atomowa adopcja i nie zużywa zwykłego budżetu plików ani nie przejmuje
  normalnej własności workstreamów.
- [x] AC-03: Lock, seed manifest i wszystkie target-local pliki pozostają w
  zwykłym diffie, muszą należeć do ticketu/workstreamu i mieszczą się w jego
  budżecie.
- [x] AC-04: Brak deklaracji, błędne SHA/repozytorium, niezgodny hash, ścieżka
  `seed`, arbitralna ścieżka nieujęta jako head `managed` lub niezgodne package
  manifesty fail-closed bez wyjątku budżetowego/własnościowego.
- [x] AC-05: Transakcja nie omija aktywnego ticketu, stanu EDIT, allowedPaths
  dla target-local diffu ani chronionej aprobaty current-head.
- [x] AC-06: Dokumentacja wyjaśnia granicę zaufania, wymagany upgrade przez
  Goal i zakaz używania transakcji jako ogólnego mechanizmu powiększania PR.

Niespójność adopcji używa istniejącego `GOV-SYNC-001`. Osobny kod wymagałby
zmiany szóstego pliku traceability bez nowej semantyki naprawczej; ponowne
użycie kodu synchronizacji utrzymuje zatwierdzony limit pięciu plików.

## Ryzyka i uwagi

- Head lock i intent są zawartością PR, dlatego same nie dowodzą publikacji
  upstream. Mitygacja: kontrakt jedynie klasyfikuje ograniczony zbiór diffu;
  merge nadal wymaga chronionego evidence związanego z current HEAD, a Goal
  `--check` weryfikuje wskazane źródło przed zatwierdzeniem.
- Nowy plik `managed` nie ma bazowego hasha. Granica deterministyczna wymaga
  jego nieobecności w bazie, deklaracji `managed` i zgodności z head lockiem;
  jego pochodzenie upstream potwierdza obowiązkowy protected exact-head review
  oraz Goal `--check`, a nie repozytorium-kontrolowany lock samodzielnie.
- Ticket nie implementuje strategii `extendable`; pozostaje ona niezależnym
  zakresem ticketu 024.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Poza zakresem

- Zwiększanie domyślnego `maxImplementationFiles`.
- Przenoszenie zwykłej własności ścieżek między workstreamami.
- Uznawanie repozytorium-kontrolowanego Markdown/locka za merge approval.
- Publikacja wersji, tagu lub GitHub Release; wykona ją osobny ticket po merge.

## Decyzja wykonawcza

Użytkownik zatwierdził kompletny plan ticketu 038 dnia 2026-08-08. Ticket
przeszedł do `IN_PROGRESS / EDIT`; implementacja pozostaje ograniczona przez
`intent.json` do pięciu zadeklarowanych ścieżek standardu.

Implementacja wykorzystała cztery ścieżki standardu i przeszła pełny kontrakt
Linux huba. Ticket jest w `VALIDATION`; merge nadal wymaga Linux, Windows oraz
chronionej aprobaty exact-head.

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-038/`.
