# Ticket 044: Publish extendable target manifest contract

- **ID**: ticket-044
- **Owner**: agent:codex
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-08

## Cel i Zakres

Opublikować scalony kontrakt `extendable` z ticketu 024 jako nowe, immutable
wydanie `v0.14.0`. Jest to minor release, ponieważ
`new-project.package-manifest/v1` otrzymał nową publiczną strategię, adopcja
materializuje nowy zarządzany artefakt `.governance/manifest.base.json`, a
semantyka locka rozdziela pliki `managed` od targetowego manifestu.

Wydanie musi związać `VERSION`, domyślny manifest, changelog oraz aktywne
asercje wersji, przejść pełny Linux i Windows contract na dokładnym HEAD,
zostać niezależnie zatwierdzone, a następnie otrzymać nowy annotowany tag i
opublikowany GitHub Release wskazujące dokładny, ponownie przetestowany merge
commit. Ticket nie migruje todo2code; jego pełny release SHA stanie się wejściem
dla osobnego downstream ticketu 062.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `VERSION`, `manifest.default.json`, bieżące asercje testowe i
  `CHANGELOG.md` jednoznacznie wskazują `0.14.0`; historyczne fixture’y
  wcześniejszych wydań pozostają przypięte.
- [x] AC-02: Pełny kontrakt Linux, chroniony `windows-governance` i niezależny
  exact-head Validator przechodzą przed merge.
- [x] AC-03: Pełny kontrakt Linux przechodzi ponownie w czystym detached
  checkout merge/release SHA.
- [x] AC-04: Nowy annotowany tag `v0.14.0` i opublikowany, nie-draftowy,
  nie-prerelease GitHub Release wskazują dokładnie zwalidowany merge SHA.
- [x] AC-05: Nie istnieje force-update ani przesunięcie wcześniejszego taga;
  downstream otrzymuje pełny SHA, nie branch lub ruchomą nazwę.

## Ryzyka i Uwagi

- Tag i release są nieodwracalne operacyjnie: przed publikacją muszą przejść
  chronione checki, exact-head review i czysty checkout merge SHA.
- `0.14.0` jest wymagane przez zmianę publicznego kontraktu adopcji; patch
  `0.13.3` zaniżyłby kompatybilnościowy zakres zmiany.
- Nigdy nie przesuwać, nie nadpisywać ani nie usuwać opublikowanego taga.
- Brak zmian implementacji `extendable`, authority, approval, AQL, sekretów,
  zależności, Dockera i mechanizmu runtime evolution.
- Brak migracji repozytoriów downstream w tym ticketcie.

## Zatwierdzenie

Użytkownik zatwierdził ten bezpośrednio poprzedzający plan poleceniem
`kontynuuj` 2026-08-09. Ticket przeszedł do `IN_PROGRESS / EDIT` przed zmianą
pięciu plików wydania. Publikacja pozostaje związana z pełną walidacją i
dokładnym merge SHA opisanymi w kryteriach odbioru.

## Dowody walidacji

- `VERSION`, domyślny manifest i aktywne asercje wskazują `0.14.0`;
  syntetyczny następny upgrade używa `0.14.1`, a historyczne fixture'y
  zachowują własne wersje.
- Pełny lokalny kontrakt Linux przeszedł 2026-08-09: osiem zestawów testów,
  kontrola required checks, kompletność suite'ów w CI oraz `git diff --check`.
- Przed publikacją ticket pozostawał otwarty do czasu chronionego
  Linux/Windows, niezależnego exact-head review i czystego testu merge SHA.
- PR #69 przeszedł oba wymagane checki (`test`, `windows-governance`) i został
  zatwierdzony dla dokładnego HEAD
  `fe2882aae7fc466f04683ad27f8e127330039749` przez deterministyczny Validator
  (`D-044-1933`, run `31282846839`).
- PR #69 został scalony jako
  `a22eb47ca0e7c06ac927d1c0d843eabb798bfadd`; pełny kontrakt Linux przeszedł
  ponownie w czystym detached checkout tego SHA.
- Nowy annotowany tag `v0.14.0` peeluje dokładnie do `a22eb47`; opublikowany
  GitHub Release jest nie-draftowy i nie jest prerelease'em. Nie wykonano
  force-update, przesunięcia ani usunięcia żadnego taga.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-044/`.
