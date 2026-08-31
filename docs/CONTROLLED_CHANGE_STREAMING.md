# Kontrolowane streamowanie zmian

## Cel

Standard ma umożliwiać szybki przepływ małych, niezależnych zmian, zachowując
fail-closed authority dla efektów zewnętrznych. Konflikt techniczny nie jest
automatycznie konfliktem semantycznym: dwa branche mogą dotykać tego samego
pliku, ale nadal dać się bezpiecznie zrebasować albo scalić w ustalonej
kolejności.

## Reguła deeskalacji

Kontroler klasyfikuje kolizję przed blokadą i zapisuje decyzję oraz receipt:

| Klasa | Warunek | Działanie |
| --- | --- | --- |
| `parallel` | rozłączne scope i brak zależności | niezależne worktree oraz PR |
| `rebase` | wspólna baza, konflikt Git rozwiązywalny bez zmiany kontraktu | rebase na aktualnym `main`, ponowne testy i exact-head validation |
| `split` | część scope jest niezależna | zachować wspólny ancestor, wydzielić następcę z nowym scope i ticketem |
| `serialize` | wspólny kontrakt lub ścieżka integracyjna | ustawić deterministyczną kolejność przez dependency, bez wzajemnego oczekiwania |
| `handoff` | writer utracił aktualność, lecz delta pozostaje użyteczna | fenced successor przejmuje scope; poprzednik dostaje receipt `superseded` |
| `block` | konflikt semantyczny, brak authority lub nieweryfikowalny stan | zatrzymać tylko dany scope i zwolnić niepowiązane rezerwacje |

Żaden wariant nie zezwala na bezpośredni merge, zmianę zamrożonego headu ani
nadpisanie cudzej pracy.

## Pozostałe implementacje

1. **`wellmanifest.change-flow/v1`** — dodać mały DSL procesu. Każdy flow ma
   identyfikator, repository scope, wejściowe lease URI, zależności, strategię
   deeskalacji, idempotency key i oczekiwany receipt. Walidator musi odrzucać
   cykle, niejednoznaczne scope i retry bez idempotency key.
2. **Atomowa alokacja workspace** — rozszerzyć registered allocator tak, aby
   jeden receipt zawierał ticket, branch, kanoniczny worktree path, lease URI i
   fencing token. CLI nie może samodzielnie zgadywać numeru lub tworzyć branch
   przed potwierdzoną alokacją.
3. **Handoff lease** — zmienić `supersede` na dwuetapowe `prepare-handoff` /
   `accept-handoff`. Następca jest najpierw fenced i otrzymuje identyczny
   `scopeHash`; dopiero potem poprzednik jest zwalniany. Terminalny receipt nie
   może być warunkiem utworzenia następcy.
4. **Kolejka integracyjna wielu repozytoriów** — manifestuje graph zależności
   PR/release między repozytoriami. Gotowe elementy wykonują się równolegle,
   a każdy shared contract ma jeden integration owner oraz określoną kolejność.
5. **Obserwowalność zgodna z `wellmanifest/logs`** — każdy transition i
   deeskalacja emituje ustrukturyzowany event z `correlationId`, `flowId`,
   `leaseId`, `fencingToken`, klasą decyzji, retry count i `ERROR` code. Logi
   nie zawierają sekretów, pełnych diffów ani ścieżek hosta.
6. **Kontrolowane wdrożenie** — najpierw dry-run i raport tylko dla jednej
   organizacji, potem canary repozytoriów z aktywną pracą, a dopiero później
   wymóg dla registered allocation. Każdy etap ma miernik: stale lease,
   collision rate, retry success i czas od merge do następnego gotowego PR.
7. **Release jako część flow** — release wymaga receiptu merge aktualnego
   `main`, dokładnego SHA, zielonych checków i nieistniejącego tagu. Nie wolno
   publikować tagu/release przed merge'em PR przygotowującego wersję.

## Kryterium gotowości

Nowy mechanizm jest gotowy do obowiązkowego użycia dopiero, gdy testy symulują
jednoczesny rebase, split i handoff w dwóch repozytoriach, a każde zakończenie
ma monotoniczny, weryfikowalny receipt chain.
