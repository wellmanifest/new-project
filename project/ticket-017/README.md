# Ticket 017: Strategia dla pliku zarządzanego, który target musi rozszerzyć

- **ID**: ticket-017
- **Owner**: unresolved:human
- **Status**: PLAN
- **Workflow state**: WAIT_FOR_APPROVAL
- **Utworzono**: 2026-08-05

## Problem

`governance/package-manifest.json` zna dwie strategie: `managed` (standard
nadpisuje plik przy `--upgrade`) i `seed` (standard wpisuje raz, target edytuje
dalej). Nie ma strategii pośredniej dla pliku, który **target musi rozszerzyć o
własne polecenia, zachowując bramę standardu**.

`project.sh` i `project.bat` są zadeklarowane jako `managed`, a standardowy
`project.sh` jest wyłącznie bramą governance: przekazuje wszystkie argumenty do
`project/governance-check.sh` i nie ma punktu rozszerzenia.

## Dowód z realnej adopcji

`subactor/intent-contract-dsl-runtime`, `create_adoption_lock.py --check` przeciw
0.10.0 — plan to 17 zmian, **15 × CREATE i 2 × UPDATE**. Oba UPDATE to
`project.sh` i `project.bat`.

W tym repozytorium `project.sh` (5454 B, wobec 1551 B w standardzie) jest punktem
wejścia dla:

- `Dockerfile:33` → `CMD ["bash", "project.sh", "verify"]`
- `compose.yml:13` → `command: ["bash", "project.sh", "verify"]`
- `.github/workflows/verify.yml` → `project.sh install`, `project.sh makedocs`

Adopcja zatrzymałaby weryfikację Dockerową, którą to repozytorium dokumentuje
jako źródło prawdy wykonania, oraz CI. Target ma dziś trzy wyjścia i każde jest złe:

1. przemianować własne polecenia — kaskada przez Dockerfile, compose, CI i
   dokumenty generowane, które emitują `project.bat`;
2. zostawić skrypty niezarządzane — `--check` raportuje drift bezterminowo,
   a `--upgrade` kasuje je przy pierwszym nieuważnym użyciu;
3. wstawić bramę na początek własnego skryptu — plik na trwałe różni się od
   locka, czyli punkt 2 w innej formie.

Żadne z nich nie jest tym, co standard chce osiągnąć: brama ma działać, a target
ma zachować swoje polecenia.

## Proponowany kierunek

Strategia `extendable` (nazwa do rozstrzygnięcia): standard jest właścicielem
**bramy**, target jest właścicielem **reszty**, a lock hashuje wyłącznie część
zarządzaną. Do rozważenia dwa kształty:

- **Sekcja pilnowana znacznikami** w jednym pliku, jak `AUTO:TICKET_INDEX` w
  `project/TICKETS.md` — mechanizm jest w repozytorium już używany i sprawdzony.
- **Rozdzielenie plików**: standard dostarcza `project/governance-entry.sh`,
  a `project.sh` targetu staje się `seed`, który wywołuje bramę pierwszą linią.
  Prostsze do zhashowania, ale zmienia obecny kontrakt `managed`.

## Kryteria odbioru

- [ ] AC-01: `package-manifest.json` wyraża trzecią strategię, a schemat ją waliduje.
- [ ] AC-02: `--upgrade` aktualizuje część zarządzaną, nie kasując części targetu.
- [ ] AC-03: `--check` nie raportuje driftu dla nietkniętej części targetu.
- [ ] AC-04: Lock wiąże wyłącznie treść zarządzaną; zmiana części targetu nie unieważnia adopcji.
- [ ] AC-05: Przypadek negatywny: uszkodzona lub usunięta brama zatrzymuje walidację.
- [ ] AC-06: `docs/GOVERNANCE_RECONCILIATION_*.md` lub następca opisuje wybór strategii przy adopcji.

## Poza zakresem

- Zmiana zachowania samej bramy governance.
- Migracja istniejących targetów; ta odbywa się jawnym `--upgrade` po przeglądzie.

## Obserwacja poboczna — scaffolder emituje `intent/v2`

Zauważone przy tworzeniu tego ticketu, **nie w jego zakresie**, zgłaszane osobno.

`project/new-ticket.sh` generuje `intent.json` ze `schema:
"new-project.intent/v2"` i bez obiektu `classification`. Ticket-016 wprowadził
wymóg, by aktywny ticket miał `intent/v3` z klasyfikacją —
`scripts/governance_check.py:1055` zgłasza wtedy `GOV-INTENT-002`: „Active ticket
{name} lacks deterministic intent/v3 classification".

Ticket zescaffoldowany domyślnie przechodzi walidację dopóki jest w stanie
nieaktywnym, ale **staje się nieważny w momencie przejścia na `IN_PROGRESS`**,
dopóki ktoś ręcznie nie zmigruje intencji. Egzekwowanie przesunęło się, generator
nie. To ta sama klasa rozjazdu co problem opisany wyżej, tylko w innym miejscu.

Ten ticket ma `intent/v3` wpisane ręcznie.
