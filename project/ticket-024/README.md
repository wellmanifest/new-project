# Ticket 024: Rozszerzalny target manifest z zarządzaną bazą standardu

- **ID**: ticket-024
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-08-05

## Cel i zakres

`governance/package-manifest.json` zna dwie strategie: `managed`, którą
`--upgrade` nadpisuje, i `seed`, którą standard zapisuje raz. Lock adopcji
hashuje jednak również zasiany `.governance/manifest.json`. Target nie może
więc dopisać właściciela własnej ścieżki bez ręcznej zmiany chronionego locka.
**Nie ma kontraktu pomiędzy pełnym nadpisaniem a niekontrolowanym lokalnym
forkiem.**

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

Po audycie działającej adopcji wybieramy dla pierwszej implementacji
**rozdzielenie zarządzanej bazy od targetowego dokumentu**:

```text
.governance/manifest.base.json  managed, hash-bound
              +
.governance/manifest.json       extendable, target-owned additions
              ↓
      deterministic validation
```

`manifest.base.json` zawiera kanoniczną, deterministyczną projekcję wartości
należących do standardu. Pola opisujące konkretny projekt — przede wszystkim
mapa workstreamów, targetowe ścieżki integracji i publicznych interfejsów — nie
są fałszywie uznawane za uniwersalną politykę standardu. `manifest.json` musi
rekursywnie zachować projekcję bazy, ale może dodawać własne klucze i elementy
tablic, w tym targetowe workstreamy i `ownedPaths`. Upgrade wykonuje
deterministyczny merge względem poprzedniej bazy: aktualizuje część standardu i
zachowuje wyłącznie legalne dodatki targetu.

Lock wiąże bazę, a nie cały dokument rozszerzalny. Usunięcie albo podmiana
wymagania standardu nadal generuje `GOV-SYNC-001`. Targetowa zmiana nadal
podlega zwykłemu ticketowi, ownership, budżetowi oraz protected approval.

Pierwszy adapter jest celowo ograniczony do dokumentów JSON. Pierwotny problem
rozszerzalnych `project.sh`/`project.bat` pozostaje uzasadnieniem strategii, ale
adapter sekcji wykonywalnych wymaga osobnego, zależnego ticketu i modelu
bezpiecznych markerów.

## Potwierdzony przypadek downstream

W `semcod/todo2code` pełna walidacja poprawki wersji zatrzymuje się wyłącznie na
`test/python-runtime.test.ts`: plik nie pasuje do żadnego workstreamu w
targetowym manifeście. Próba dopisania własności powoduje `GOV-SYNC-001`, bo
`.governance/manifest.json` znajduje się w `managedFiles` locka. Ticket 024 ma
umożliwić wykonanie tej zmiany dopiero po opublikowaniu i jawnej adopcji nowej
wersji standardu; nie modyfikuje repozytorium downstream bezpośrednio.

## Kryteria odbioru

- [x] AC-01: `package-manifest.json` wyraża strategię `extendable` dla JSON i
  odrzuca nieobsługiwany lub niepoprawny wpis.
- [x] AC-02: `--upgrade` aktualizuje zarządzaną bazę i zachowuje targetowe
  workstreamy oraz `ownedPaths`.
- [x] AC-03: `--check` nie raportuje driftu dla legalnego dodatku targetu, a
  lock nie hashuje całego dokumentu rozszerzalnego.
- [x] AC-04: Zarządzana baza pozostaje dokładnie hash-bound i zgodna z
  opublikowanym source revision.
- [x] AC-05: Usunięta lub zmieniona wartość bazy w targetowym manifeście
  zatrzymuje walidację stabilnym `GOV-SYNC-001`.
- [x] AC-06: Fixture o kształcie todo2code może przypisać
  `test/python-runtime.test.ts` do workstreamu bez edycji locka i bez ominięcia
  zwykłych bramek ticketu, authority oraz approval.

## Ryzyka i uwagi

- Zmiana dotyka kontraktu adopcji, więc każdy zaadoptowany target musi przejść
  jawny, przejrzany `--upgrade`. Migracja nie może być cicha.
- Target nie może nadpisać scalaru ani usunąć elementu opublikowanego przez
  standard. Merge i walidacja muszą używać tego samego kanonicznego algorytmu.
- `manifest.base.json` jest kanonicznie wyliczany z opublikowanego źródła i
  objęty lockiem, więc tę samą projekcję można odtworzyć, a elastyczność targetu
  nie osłabia proweniencji standardu.

## Poza zakresem

- Zmiana zachowania samej bramy governance.
- Migracja istniejących targetów; ta odbywa się jawnym `--upgrade` po przeglądzie.
- Rozszerzalne skrypty wykonywalne i markery sekcji tekstowych.
- Zmiana AQL, authority, approval, sekretów, zależności lub mechanizmu ewolucji.
- Publikacja wersji, taga i GitHub Release.

## Uczestnicy

- Human participant: unresolved; `user-*` tworzy wyłącznie jego ludzki
  właściciel lub zaufana granica intake.
- Agent participants: istniejący `ai-claude.md` oraz `ai-codex.md`; każdy agent
  modyfikuje wyłącznie własny plik uczestnika.

## Decyzja wykonawcza

Rozszerzony plan powstał po wykryciu rzeczywistego blokera w
`semcod/todo2code`. Użytkownik zatwierdził dokładny plan ticketu 024 oraz
przejście do `EDIT` 2026-08-09. Zgoda obejmuje pięć ścieżek implementacyjnych
zadeklarowanych w `intent.json`; nie jest zaufanym dowodem merge ani zgodą na
wydanie, migrację downstream lub zmianę authority.

## Implementacja i walidacja

- `package-manifest/v1` akceptuje `extendable` wyłącznie dla targetowego
  manifestu JSON i wymaga odpowiadającej mu zarządzanej bazy z tego samego
  źródła.
- Adopcja rozpoznaje legacy lock z zasianym manifestem, odtwarza poprzednią
  bazę z przypiętej rewizji i wykonuje deterministyczny merge bez utraty
  targetowych workstreamów.
- Nowy lock zawiera wyłącznie pliki `managed`; rozszerzalny manifest przechodzi
  normalny scope, ownership, budżet i approval targetu.
- Runtime waliduje hash bazy oraz rekursywną zgodność targetu; naruszenie daje
  stabilny `GOV-SYNC-001`.
- Pełny kontrakt Linux CI: PASS — required checks, decision replay,
  governance scripts, validator, branch lifecycle, governance environment,
  adoption lock, rule-enforcement oraz kompletność listy suite’ów.
- Regresja na rzeczywistym manifeście todo2code zachowała osiem workstreamów,
  wyłączyła `manifest.json` z locka i zakończyła kolejny `--check` jako
  `up-to-date`.
- Windows i exact-head Validator pozostają wymaganymi chronionymi checkami PR;
  nie były wykonywane lokalnie.
