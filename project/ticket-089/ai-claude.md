# ai-claude.md — ticket-089

## Rozumienie intencji

`.governance/required-checks.json` jest w standardzie ogłoszony źródłem prawdy
dla `requiredCheckNames` i zobowiązuje zewnętrznych konsumentów (validator-agent,
ruleset GitHuba) do czytania właśnie jego. Ta deklaracja jest dziś nieprawdziwa
w 21 z 23 adoptujących repozytoriów, a mechanizm, który miał tego pilnować, nie
wykonuje się u nikogo poza hubem.

Celem ticketu nie jest zmiana czyichkolwiek checków. Celem jest doprowadzenie do
stanu, w którym zdanie „ten plik jest źródłem prawdy" da się spełnić — dziś
adoptujący nie może tego zrobić nawet chcąc.

## Zakres prac

Wyłącznie hub. Pięć plików implementacji:

| Plik | Zmiana |
| --- | --- |
| `governance/package-manifest.json` | `required-checks.json`: `managed` → `extendable` |
| `governance/required-checks.schema.json` | nowy, `managed` — ogranicza instancję |
| `scripts/check_required_checks.py` | rozwiązywanie ścieżki + parsowanie `name:` joba |
| `scripts/governance_check.py` | wywołanie bramki |
| `tests/required-checks.test.sh` | trzy nowe przypadki w syntetycznym adoptującym |

Poza zakresem: nazwy checków w jakimkolwiek repozytorium, podbicie wersji
standardu u adoptujących, mechanika dispatchu validator-agenta, edycja
`governance/required-checks.json` (instancja hubu zostaje bez zmian).

## Koncepcja

### 1. Strategia dystrybucji

Manifest zna trzy strategie: `managed` (34 pliki, przypięte bajt-w-bajt),
`seed` (2, tworzone raz i oddane celowi) oraz `extendable` (1). `extendable`
jest już użyte dokładnie do tego wzorca:

    governance/manifest.default.json  ->  .governance/manifest.json

cel wpisuje własne wartości, a przypięty `manifest.schema.json` je ogranicza.
Plik z danymi per-repozytorium nie może być `managed`; to jest cała przyczyna
defektu i jej usunięcie jest zmianą jednego pola plus nowy schemat.

### 2. Rozwiązywanie ścieżki

`package-manifest.json:20` przenosi skrypt ze `scripts/` do `.governance/`, nie
korygując zaszytej w nim stałej. `repo_root()` liczy `parents[1]`, co w obu
układach daje korzeń repo, ale `SOURCE_REL = governance/required-checks.json`
istnieje tylko w hubie.

Rozwiązanie: szukać pliku najpierw obok skryptu, potem w układzie hubu. Brak
pliku ma dawać komunikat bramki z listą sprawdzonych ścieżek, nie traceback.

### 3. Nazwa checka

Ruleset wymaga nazwy wyświetlanej (pole `name:` joba), bramka porównuje z
kluczem joba. Pokrywają się tylko w hubie, gdzie żaden job nie nadpisuje `name:`.

    .github/workflows/new-project-governance.yml
      15:  remote-lifecycle:                       <- to widzi bramka
      16:    name: governance / remote lifecycle   <- tego wymaga ruleset

Bez tej poprawki adoptujący nie napisze pliku, który jest jednocześnie prawdziwy
i przechodzi bramkę — więc sama zmiana strategii by nie wystarczyła.

### 4. Dlaczego test tego nie złapał

`tests/required-checks.test.sh` uruchamia bramkę wyłącznie z układu hubu i
używa `--source` / `--workflow` do mutacji. Nigdy nie kopiuje skryptu do
`.governance/` i nigdy nie testuje joba z nadpisanym `name:`. Oba nowe
przypadki muszą wejść do tego pliku, inaczej regresja wróci.

### 5. Kontrakt jest za wąski

`required-checks.json` deklaruje **jeden** `workflowFile`. W dziesięciu
repozytoriach egzekwowane konteksty pochodzą z **dwóch** plików:

    autonomy
      new-project-governance.yml  ->  governance / remote lifecycle
      standard-conformance.yml    ->  standards / autonomy conformance

    dotyczy: authority-lifecycle, autonomy, git-lifecycle, legal-lifecycle,
             product-lifecycle, repair-lifecycle, saas-lifecycle,
             ticket-lifecycle, twin-lifecycle, validation-attestation

Instancje dają się wygenerować czysto tylko dla siedmiu repozytoriów o jednym
workflow (`account-runtime`, `code-dsl`, `dsl`, `merge`, `performance`, `poa`,
`policy-dsl`). Pozostałe nie zapiszą prawdy, dopóki kontrakt nie zmieni kształtu
na `requiredChecks: [{name, workflowFile}]`.

Ta zmiana musi wejść razem ze zmianą strategii — inaczej instancje trzeba by
migrować dwa razy.

## Kryteria Odbioru

- **AC-01** `strategy` dla `.governance/required-checks.json` to `extendable`.
- **AC-02** `python3 scripts/check_required_checks.py` nadal przechodzi w hubie.
- **AC-03** Test kopiuje bramkę do układu `.governance/` — dziś czerwony, po
  poprawce zielony.
- **AC-04** `governance_check.py` wywołuje bramkę.
- **AC-05** Job z `name: governance / remote lifecycle` jest publikowany pod tą
  nazwą, więc deklaracja może się zgadzać z rulesetem.
- **AC-06** bramka hubu przypisuje diff do ticket-089. Uwaga: w hubie należy
  użyć wywołania z `.github/workflows/ci.yml`, bo dystrybuowany
  `./project/governance-check.sh` ma zaszyte `.governance/` i w hubie nie działa
  (osobny defekt, ustalenie 05).

## Praca następcza (nie w tym tickecie)

Uzupełnienie instancji w 21 repozytoriach faktycznymi nazwami checków
odczytanymi z rulesetów. Wykonalne dopiero po tej zmianie: dziś takie
repozytorium musiałoby wybierać między zgodnością z lockiem a prawdziwością
pliku.

## Stan

`BLOCKED`. Cała implementacja jest gotowa i zweryfikowana w
piaskownicy (hub bez regresji, adoptujący przechodzi, trzy mutacje odrzucane).
Nie zapisano jej do repozytorium, bo ticket nie jest aktywny.
