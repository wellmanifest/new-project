# Ticket 348: Isolate governance preflight cache test checkout

- **ID**: ticket-348
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT

## Cel i zakres

Izolować testy cache od rzeczywistego checkoutu. Chroniony publisher ustawia TMPDIR wewnątrz repozytorium, podczas gdy wynik selektora musi pozostać poza badanym checkoutem. Prywatny klon testowy i jego katalog nadrzędny mieszczą się w kanonicznym cache właściciela. Testy wywołują bieżące implementacje CLI; konfiguracja źródła pozostaje bez zmian.

## Kryteria odbioru

- AC-01: Wszystkie pięć istniejących testów i negatywne asercje przechodzą z chronionym środowiskiem, źródłem tylko do odczytu i własnym zapisywalnym cache.
- AC-02: Jeden plik implementacji testu, schemat i bramka zgodne z intencją; niezależne wymagane CI i recenzja oraz scalenie przez chroniony Validator.

## Granica wykonania

Natywna rezerwacja nie daje prawa do edycji testu. Najpierw dokładna rejestracja operatora i autentyczne acquire/check kontrolera z nowym fencingiem. Produkcyjne ograniczenia ścieżek, zgód i snapshotów pozostają bez zmian. Źródło testu jest niezmienione; proponowany diff znajduje się wyłącznie w ignorowanym receipcie.
