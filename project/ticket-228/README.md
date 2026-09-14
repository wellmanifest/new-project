# Ticket 228: Standardize audit evidence storage and managed lifecycle routing

- **ID**: ticket-228
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-09-14

## Cel i Zakres
Ustandaryzować przechowywanie audytów, dowodów i raportów oraz wybór
istniejących procedur zamiast doraźnych skryptów. Profil należy do new-project;
nie tworzy nowego repozytorium, magazynu ani obowiązkowej zależności runtime.
Autoryzacja sesji: bieżące zlecenie użytkownika obejmuje tę zmianę dokumentacji
i jej walidację; wcześniejsze zlecenie publikacji wellmanifest obejmuje Goal
i chroniony PR. Nie jest to approval exact-head ani zgoda na usuwanie lub
migrację historycznych audytów.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: Rozdzielone lokalizacje logów, receiptów, raportów, zadań i kodu;
  XDG oraz opcjonalny indeks w primary checkout bez migracji legacy.
- [ ] AC-02: Planfile, alokator i publikator mają odrębne role; brak adaptera,
  zły projekt i niepewny wynik zdalny prowadzą do jawnej, bezpiecznej procedury.
- [ ] AC-03: Dokumenty są zgodne z aktualnym alokatorem, polityką i bramą hubu;
  ograniczenia egzekwowania i adopcji pozostają jawne.

## Ryzyka i Uwagi
- Ryzyka: błędny projekt Planfile, utrata audytów przy usunięciu worktree,
  skrypt w katalogu logów uznany za autoryzowany runtime. Mitygacja: readback
  tożsamości, zachowanie istniejących danych i referencje do wersjonowanego kodu.
- Poza zakresem: zmiany taskand-gpt6, cleanup, instalacja nowego kontrolera,
  fleet rollout oraz modyfikacja istniejących reguł approval/merge.

## Rejestracja i dowody

- Projektowy pilot Planfile: `PLF-009`, magazyn primary checkout
  `.subactor/recovery/planfile`, runtime `31aaab644486400237ce8ffbfe6a01a9b02fb095`.
  Rejestracja przez DSL; nie jest to automatyczna synchronizacja GitHub ani authority.
- Lokalne testy: work-registration 41/41, work-start 48/48,
  rule-enforcement PASS oraz walidator docs PASS. Surowe wyniki w prywatnym
  audycie `audit-evidence-228-20260914.Ft5tRK`; nie jest to zdalny trwały receipt.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-228/`.
