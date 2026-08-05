# Ticket 018: Scaffolder emituje intent v3 z klasyfikacja

- **ID**: ticket-018
- **Owner**: unresolved:human
- **Status**: PLAN
- **Workflow state**: WAIT_FOR_APPROVAL
- **Utworzono**: 2026-08-05

## Cel i zakres

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

## Kryteria odbioru

- [x] AC-01: Scaffolder generuje `intent/v3` z kompletnym obiektem `classification`.
- [x] AC-02: Wygenerowana intencja spełnia `governance/intent.schema.json` (dziesięć pól wymaganych, trzy wymiary z enumów).
- [x] AC-03: Wartość spoza kontraktu jest odrzucana z listą dopuszczalnych.
- [x] AC-04: Odrzucone wywołanie nie tworzy katalogu ticketu.
- [x] AC-05: Szablon i fallback w skrypcie emitują ten sam kształt.
- [x] AC-06: Trzy zestawy regresyjne przechodzą.

## Dowód wykonania

Ten ticket został utworzony poprawionym scaffolderem, z jawną klasyfikacją
`BUG / P1 / regression`, i jego `intent.json` jest zwalidowany wobec schematu.

- `./project/new-ticket.sh ... --priority P9` → `GOV-CLASS-001`, exit 1, brak `project/ticket-018/`.
- `bash tests/governance-scripts.test.sh` — PASS
- `bash tests/governance-validator.test.sh` — PASS
- `bash tests/adoption-lock.test.sh` — PASS

## Poza zakresem

- Zmiana samego kontraktu klasyfikacji ani reguł `W-CLASS-*`.
- Migracja istniejących ticketów v1/v2; historyczne nieaktywne pozostają czytelne.
