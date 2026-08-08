---
participant-id: agent:codex
participant: codex
role: agent
ticket: ticket-038
---
# Participant: codex (AI agent)

## Understanding

Problem nie wynika z rozmiaru funkcji aplikacyjnej, lecz z niepodzielności
opublikowanego pakietu. Obecny checker traktuje każdy zmieniony plik `managed`
jak zwykłą implementację. Upgrade `todo2code` z 0.11.0 do 0.12.0 zmienia 15
takich plików przy limicie pięciu i obejmuje zarówno ścieżki governance, jak
`scripts/runtime.sh` należący do integration. Lock wymaga ich jednoczesnej
zgodności.

Bezpieczna granica to jawna transakcja intentu, która odejmuje z normalnego
diffu tylko deterministycznie zweryfikowane targety `managed`. Nie zmienia ona
własności tych ścieżek poza transakcją. Seed manifest, lock, changelog i inne
lokalne zmiany pozostają zwykłą implementacją, dzięki czemu ticket nadal musi
mieć realny, ograniczony i jednoznacznie należący diff.

## Execution plan

1. Po osobnej aprobacie przejść do `IN_PROGRESS / EDIT`.
2. Dodać ściśle walidowaną, opcjonalną deklarację
   `delivery.standardAdoption` do intent/v3.
3. Wyliczać zweryfikowane ścieżki transakcji z bazowego i docelowego locka,
   package manifestów, strategii `managed` oraz hashy zawartości; dla nowego
   targetu wymagać nieobecności w bazie i pełnej zgodności head.
4. Usuwać wyłącznie ten zbiór z normalnego rozliczenia ticketu, budżetu i
   workstreamu; wszystkie pozostałe ścieżki sprawdzać bez zmian.
5. Dodać pozytywny upgrade wieloplikowy oraz negatywne regresje dla locka,
   hashy, SHA, repozytorium, `seed`, arbitralnych ścieżek, scope i approval.
6. Udokumentować granicę zaufania i wymagane użycie Goal `--check`.
7. Uruchomić pełny kontrakt Linux/Windows/Docker i wysłać jeden PR do
   exact-head Validator App.
8. W osobnym ticketcie opublikować nowe immutable wydanie; dopiero potem
   wznowić adopcję todo2code ticket-050.

## Actual changes

- Utworzono odrębny ticket 038 po jawnej zgodzie użytkownika; nie rozszerzono
  niezależnego ticketu 024.
- Przeanalizowano realny diff adopcji: 15 zmienionych plików `managed`, limit
  pięciu i przekroczenie granicy governance/integration; sześć targetów jest
  nowych względem package manifestu 0.11.0.
- Nie zmieniono kodu, schematów, testów ani dokumentacji standardu.
- Użytkownik zatwierdził kompletny plan 2026-08-08; ticket przeszedł do
  `IN_PROGRESS / EDIT` przed pierwszą zmianą implementacyjną.

## Blockers

- Docelowe `toRevision` dla todo2code będzie znane dopiero po osobnym,
  zatwierdzonym wydaniu; ticket 050 pozostaje w PLAN.
