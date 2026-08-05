# Ticket 024: Strategia package-manifest dla pliku ktory target musi rozszerzyc

- **ID**: ticket-024
- **Owner**: unresolved:human
- **Status**: PLAN
- **Workflow state**: WAIT_FOR_APPROVAL
- **Utworzono**: 2026-08-05

## Cel i zakres

`governance/package-manifest.json` zna dwie strategie: `managed`, którą
`--upgrade` nadpisuje, i `seed`, którą standard zapisuje raz. **Nie ma nic
pomiędzy** dla pliku, który target musi rozszerzyć o własne polecenia, zachowując
bramę standardu.

`project.sh` i `project.bat` są zadeklarowane jako `managed`, a standardowy
`project.sh` jest wyłącznie bramą governance: przekazuje wszystkie argumenty do
`project/governance-check.sh` i nie ma punktu rozszerzenia.

## Dowód z realnej adopcji

`create_adoption_lock.py --check` przeciw `subactor/intent-contract-dsl-runtime`
planuje **17 zmian: 15 CREATE i 2 UPDATE**. Oba UPDATE to `project.sh` i
`project.bat`.

W tamtym repozytorium `project.sh` (5454 B wobec 1551 B w standardzie) jest
punktem wejścia dla:

- `Dockerfile:33` → `CMD ["bash", "project.sh", "verify"]`
- `compose.yml:13` → `command: ["bash", "project.sh", "verify"]`
- `.github/workflows/verify.yml` → `project.sh install`, `project.sh makedocs`

Adopcja zatrzymałaby weryfikację Dockerową, którą to repozytorium dokumentuje
jako źródło prawdy wykonania, oraz CI. Target ma dziś trzy wyjścia i każde płaci
za problem, którego źródło jest tutaj:

1. przemianować własne polecenia — kaskada przez Dockerfile, compose, CI oraz
   dokumenty generowane, które emitują `project.bat`;
2. zostawić skrypty niezarządzane — `--check` raportuje drift bezterminowo,
   a `--upgrade` kasuje je przy pierwszym nieuważnym użyciu;
3. wstawić bramę na początek własnego skryptu — plik na trwałe różni się od
   locka, czyli punkt 2 w innej formie.

Właściciel tamtego repozytorium **odłożył adopcję** zamiast wybierać którekolwiek
(`subactor/intent-contract-dsl-runtime`, `project/ticket-014`). To jest koszt
mierzalny: standard nie został przyjęty w działającym systemie, bo nie ma
sposobu, by przyjąć go bez zepsucia tego systemu.

## Proponowany kierunek

Trzecia strategia, roboczo `extendable`: standard jest właścicielem **bramy**,
target **reszty**, a lock hashuje wyłącznie część zarządzaną. Dwa kształty do
rozważenia:

- **Sekcja pilnowana znacznikami** w jednym pliku, jak `AUTO:TICKET_INDEX`
  w `project/TICKETS.md` — mechanizm jest w tym repozytorium już używany
  i sprawdzony.
- **Rozdzielenie plików**: standard dostarcza `project/governance-entry.sh`,
  a `project.sh` targetu staje się `seed`, który wywołuje bramę pierwszą linią.
  Prostsze do zhashowania, ale zmienia obecny kontrakt `managed`.

Wybór kształtu należy do przeglądu; ten ticket rejestruje problem i koszt, nie
przesądza implementacji.

## Kryteria odbioru

- [ ] AC-01: `package-manifest.json` wyraża trzecią strategię, a schemat ją waliduje.
- [ ] AC-02: `--upgrade` aktualizuje część zarządzaną, nie kasując części targetu.
- [ ] AC-03: `--check` nie raportuje driftu dla nietkniętej części targetu.
- [ ] AC-04: Lock wiąże wyłącznie treść zarządzaną; zmiana części targetu nie unieważnia adopcji.
- [ ] AC-05: Przypadek negatywny: uszkodzona lub usunięta brama zatrzymuje walidację.
- [ ] AC-06: Dokumentacja adopcji opisuje wybór strategii i ścieżkę migracji dla targetów już zaadoptowanych.

## Ryzyka i uwagi

- Zmiana dotyka kontraktu adopcji, więc każdy zaadoptowany target musi przejść
  jawny, przejrzany `--upgrade`. Migracja nie może być cicha.
- Strategia rozszerzalna osłabia gwarancję „plik zarządzany jest identyczny
  z opublikowanym". Lock musi więc wiązać część zarządzaną **osobnym** hashem,
  inaczej zyskujemy elastyczność kosztem proweniencji.

## Poza zakresem

- Zmiana zachowania samej bramy governance.
- Migracja istniejących targetów; ta odbywa się jawnym `--upgrade` po przeglądzie.
