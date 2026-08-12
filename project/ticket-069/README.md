# Ticket 069: Extract Git and ticket lifecycle subprojects

- **ID**: ticket-069
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-12

## Cel i zakres

Wydzielić z głównych dokumentów `new-project` dwa komponowalne standardy:
`git-lifecycle` oraz `ticket-lifecycle`. Moduły mają opisywać osobne maszyny
stanów, zamknięte kontrakty JSON Schema i ograniczone request DSL w GBNF,
pozostawiając `POLICY.md` i `CONTRIBUTING.md` jako nadrzędną, egzekwowalną
projekcję zgodności.

W `git-lifecycle` należy rozwiązać impas nowego repozytorium bez `HEAD`:
jawne zlecenie utworzenia repozytorium w trybie autonomicznym może autoryzować
dokładnie jeden lokalny commit seed baseline, zanim powstanie implementacja.
Wyjątek nie może autoryzować remote, push, PR, merge, tagu ani release.

## Kryteria odbioru

- [x] AC-01: Dokumenty podprojektów wyjaśniają kompozycję, precedencję,
  wersjonowanie i granice odpowiedzialności modułów.
- [x] AC-02: `git-lifecycle` definiuje pełną maszynę stanów Git oraz atomową,
  fail-closed transakcję autonomicznego seed baseline dla unborn `HEAD`.
- [x] AC-03: Zamknięte Git JSON Schema i request-only GBNF nie przyjmują
  poleceń shell, URL-i remote, sekretów ani dowolnych ścieżek z modelu.
- [x] AC-04: `ticket-lifecycle` definiuje alokację, plan, bounded intent,
  autoryzację sesji, walidację, publikację, zamknięcie i wznowienie.
- [x] AC-05: Zamknięte ticket JSON Schema i request-only GBNF wiążą operację z
  repozytorium, ticketem, stanem oczekiwanym oraz referencjami dowodów.
- [x] AC-06: `POLICY.md`, `CONTRIBUTING.md` i instrukcje agentów dopuszczają
  seed baseline tylko w wąskiej granicy, bez osłabienia `C-PUBLISH-001`.
- [x] AC-07: Governance, Draft 2020-12 metaschema, pozytywne i negatywne
  kontrakty, audyt rule-enforcement oraz pełne testy Linux przechodzą.

## Ryzyka i uwagi

- Autonomia nie jest ogólną zgodą na commit. Seed baseline działa wyłącznie
  dla tworzonego repozytorium z unborn `HEAD`, przed implementacją i na
  jawnie wyliczonym allowliście plików nośnych.
- Model wybiera wyłącznie typowaną akcję i opaque references. Kontroler
  rozwiązuje ścieżki, nazwy branchy i skutki Git poza wyjściem modelu.
- Ticket 069 został początkowo lokalnie ułożony na governance-only zamknięciu
  ticketu 068 (`fef7434`), aby nie nadpisać równoległego writer'a. Po scaleniu
  PR #101 został bez utraty zmian przeniesiony na zintegrowany `origin/main`
  `e0314db86e9f2a78a0512605c27c855ce72ad267`.
- Po scaleniu niezależnej poprawki ticketu 070 przez PR #102 branch został
  ponownie przeniesiony bez utraty zmian na `origin/main`
  `4e6ba5ec15873346446d67d8787f17f68f57f81e` (`v0.16.1`).
- Metaschema, kontrakty i pełny Linux contract przechodzą na `v0.16.1`.
  Dawny konflikt workstreamu z ticketem 070 zniknął po jego governance-only
  closure na `main`. Ticket 069 został wznowiony do walidacji względem
  aktualnej bazy `452d4008a71d67ad1965f6042faa217978a82b42`.
- Po rebase na bieżący `main` (`new-project 0.16.2`) audyt 171 reguł, wszystkie
  dziewięć testów Linux, dwa identyczne kontrakty standalone/subproject oraz
  `git diff --check` przechodzą. Ticket pozostaje `IN_PROGRESS / PUBLICATION`
  do czasu niezależnego exact-head review i trusted merge.

## Publication authorization

The user's explicit request to push the changes authorizes committing this
bounded diff, pushing its ticket branch and opening a pull request. It does not
authorize direct push to `main`, trusted merge, tag or release creation.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Implementacja
standardów należy do `subprojects/` oraz nadrzędnych projekcji polityki.

## Standalone extraction

The two modules have also been extracted into independent local repositories:

- `wellmanifest/git-lifecycle`, governed seed baseline
  `c142c3b3c8a2eda3a3bf3a8e7cb711cf4bdc8629`;
- `wellmanifest/ticket-lifecycle`, governed seed baseline
  `dd80fc8e2b33ef0133e104a4b97329d69a64c3a9`.

Each standalone repository owns its ticket, Docker conformance and subsequent
contract development. The `subprojects/` copies in `new-project` remain the
composition/incubation projection required by this ticket until an immutable
standalone release can replace source duplication with versioned references.
No remote repository, push or release was created during extraction.

## Dowody dostawy

- PR #108 przeszedł oba wymagane checki Linux i Windows dla exact HEAD
  `16618957355bdeeedd751ab8dc5a964e204b560f`.
- `ifuri-validator-agent[bot]` zatwierdził dokładnie ten HEAD w review
  `4919433080`.
- PR #108 został scalony do `main` jako
  `5484605930c6235bed7ad9e2e462281e619654ac`, a tymczasowy zdalny branch
  `goal/ticket-069` został usunięty przez politykę repozytorium.
