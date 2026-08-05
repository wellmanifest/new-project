# Ticket 021: Poprawność scaffoldera ticketów

- **ID**: ticket-021
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-05

## Cel i zakres

Jeden wynik: **scaffolder nie może wyprodukować ticketu nieważnego lub kolidującego
z cudzą pracą.** Trzy niezależne sposoby, na jakie to dziś robi, mają wspólną
przyczynę — narzędzie patrzy na węższy stan niż ten, który je obowiązuje.

### 1. Nieważna intencja

Ticket 016 uczynił `intent/v3` z obiektem `classification` obowiązkowym dla
aktywnych ticketów. `project/new-ticket.sh` nadal generował `intent/v2` bez
klasyfikacji, więc zescaffoldowany ticket przechodził walidację dopóki był
nieaktywny i **stawał się nieważny w momencie przejścia na `IN_PROGRESS`** —
`scripts/governance_check.py` zgłasza wtedy `GOV-INTENT-002`: „Active ticket
{name} lacks deterministic intent/v3 classification".

Egzekwowanie przesunęło się w ticketcie 016; generator nie. To ta sama klasa
rozjazdu co ticket 017, tylko po stronie narzędzia zamiast manifestu.

## Wdrożone

`project/new-ticket.sh`:

- generuje `new-project.intent/v3` z obiektem `classification`;
- przyjmuje `--kind`, `--priority` i `--origin`;
- **waliduje je wobec kontraktu, nie wobec listy w skrypcie** — dopuszczalne
  wartości czyta z `dimensions` w `work-classification.dsl.json`, szukając go
  najpierw w `.governance/` (target), potem w `governance/` (hub). Nieznana
  wartość kończy się `GOV-CLASS-001` i wypisuje listę dopuszczalnych; brak
  kontraktu to `GOV-CLASS-000` z instrukcją naprawy.
- Walidacja biegnie **przed** `mkdir`, więc odrzucone wywołanie nie zostawia
  pustego katalogu ticketu.

`template/files/intent.template.json` — ta sama zmiana; szablon ma pierwszeństwo
przed heredocem w skrypcie, więc obie ścieżki musiały ruszyć razem.

Domyślne wartości to odpowiedź samego kontraktu na nieklasyfikowany nowy ticket:
reguła `W-CLASS-006` (`work-request` / `maintenance`) przypisuje `SERVICE` i
`health`, a `priorityDerivation.serviceDefault` daje `P2`. Nie są wymyślone.

### 2. Kolizja numerów

`highest` wyliczany był wyłącznie z katalogów na dysku. Numer zajęty na
**wypchniętej, niescalonej gałęzi** jest niewidoczny, więc dwie równoległe sesje
dostają ten sam id, a przegrywający dowiaduje się o tym dopiero przy review.

To nie jest teoria. W trakcie tego ticketu numer 017 został zajęty przez inną
pracę, przez co PR #19 został zamknięty; potem PR #22 wymagał przebudowy; a numer
018 — pod którym ten ticket pierwotnie powstał — okazał się zajęty przez
`origin/ticket/018-branch-lifecycle-runtime`. Ten ticket nosi numer 021, bo
poprawiona alokacja sama go wskazała.

### 3. Indeks z martwymi linkami

`readme.sh` indeksował każdy katalog `project/ticket-*`, także nieśledzony przez
git. Regeneracja indeksu przy cudzej pracy w toku wpisuje wiersze, których linki
nie rozwiązują się w żadnym commicie poza working tree autora. W tej sesji
zdarzyło się dwa razy i wymagało ręcznego przycinania staged indeksu.

## Kryteria odbioru

- [x] AC-01: Scaffolder generuje `intent/v3` z kompletnym obiektem `classification`.
- [x] AC-02: Wygenerowana intencja spełnia `governance/intent.schema.json` (dziesięć pól wymaganych, trzy wymiary z enumów).
- [x] AC-03: Wartość spoza kontraktu jest odrzucana z listą dopuszczalnych.
- [x] AC-04: Odrzucone wywołanie nie tworzy katalogu ticketu.
- [x] AC-05: Szablon i fallback w skrypcie emitują ten sam kształt.
- [x] AC-06: Numer ticketu pomija id zajęte na dowolnej znanej klonowi zdalnej gałęzi.
- [x] AC-07: `readme.sh` pomija nieśledzone katalogi ticketów i mówi o tym wprost.
- [x] AC-08: Trzy zestawy regresyjne przechodzą.
- [x] AC-09: Linked worktree korzystają ze wspólnej blokady i trwałego high-water mark.
- [x] AC-10: Governance zabrania wielu writerów w jednym worktree i automatycznego przejmowania obcych zmian.

## Dowód wykonania

Ten ticket został utworzony poprawionym scaffolderem, z jawną klasyfikacją
`BUG / P1 / regression`, i jego `intent.json` jest zwalidowany wobec schematu.

- `./project/new-ticket.sh ... --priority P9` → `GOV-CLASS-001`, exit 1, brak `project/ticket-021/`.
- `bash tests/governance-scripts.test.sh` — PASS
- `bash tests/governance-validator.test.sh` — PASS
- `bash tests/adoption-lock.test.sh` — PASS

## Ograniczenie przyjęte świadomie

Alokacja czyta lokalne i zdalne refy, a linked worktree tego samego klona dzielą
blokadę oraz high-water mark w `git-common-dir`. Dwa niezależne klony nadal
wymagają świeżego `fetch` i publikacji brancha, ponieważ nie współdzielą lokalnego
stanu rezerwacji.

Świeżość zależy od `git fetch`. Nieaktualne referencje zdalne dają nieaktualną
odpowiedź, dlatego warto pobrać przed założeniem ticketu.

## Poza zakresem

- Zmiana samego kontraktu klasyfikacji ani reguł `W-CLASS-*`.
- Migracja istniejących ticketów v1/v2; historyczne nieaktywne pozostają czytelne.
