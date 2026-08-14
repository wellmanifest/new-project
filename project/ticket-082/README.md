# Ticket 082: Point governance identifiers at the live host

- **ID**: ticket-082
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-14

## Cel i Zakres

Standard publikuje dziesięć identyfikatorów wskazujących na `wellmanifest.dev`,
który nie jest już żywym hostem. Dziewięć repozytoriów w organizacji zaczęło
naprawiać to u siebie: tam, gdzie nie ma locka adopcji, zmiana weszła prosto na
`main`; w repozytoriach adoptowanych stoi zaparkowana na gałęzi
`chore/wellmanifest-com-host` bez PR-a, bo dotyka plików, których digesty
trzyma `manifest.lock.json`.

Ten ticket przenosi zmianę tam, gdzie jest jej miejsce — do pakietu, z którego
te pliki pochodzą. Repozytoria adoptujące przejmą ją przez ponowną adopcję
generatorem, a nie przez ręczną edycję plików zarządzanych.

Zakres obejmuje dwa `$id` schematów oraz `signedAttestationPredicateType` w
pięciu miejscach. Rozdzielenie ich jest niemożliwe: `manifest.schema.json`
pinuje predykat jako `const`, więc częściowa zmiana unieważniłaby każdy manifest
adoptującego repozytorium.

Poza zakresem: wydanie nowej rewizji do adopcji (decyzja właściciela) oraz
jakakolwiek edycja wewnątrz repozytoriów adoptujących.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Żaden identyfikator governance nie wskazuje już wycofanego hosta.
- [x] AC-02: Zestaw testów walidatora governance przechodzi z nową nazwą
  predykatu.
- [x] AC-03: Bramka hub przechodzi, a zmiana rozwiązuje się do dokładnie
  jednego ticketu workstreamu `governance`.

## Ryzyka i Uwagi
- Atestacje podpisane starym predykatem przestaną być uznawane po podniesieniu
  adopcji. Są związane z konkretnym HEAD-em i krótkożyciowe, więc mitygacją jest
  ponowne wystawienie atestacji po upgradzie, a nie akceptowanie dwóch wartości
  naraz — dwa dopuszczalne predykaty osłabiłyby granicę zaufania.
- `subactor/validator-agent` nie zawiera tej stałej na sztywno; czyta ją z
  manifestu repozytorium docelowego, więc weryfikator nie wymaga zmiany
  równoległej.
- Repozytoria adoptowane pozostają nienaruszone do momentu, w którym same
  wykonają `goal governance adopt --upgrade`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-082/`.
