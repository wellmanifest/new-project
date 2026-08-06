# Ticket 030: Derive required check names from one source

- **ID**: ticket-030
- **Owner**: unresolved:human
- **Status**: PLAN
- **Workflow state**: WAIT_FOR_APPROVAL
- **Utworzono**: 2026-08-06

## Cel i Zakres

Nazwy wymaganych checków dla `main` są dziś zapisane w co najmniej trzech
miejscach, które nikt nie porównuje ze sobą. Rozjazd już nastąpił:

| miejsce | wartość dla `wellmanifest/new-project` |
|---|---|
| ruleset `main-governance-protection` | `test`, `windows-governance` |
| `docs/GOVERNANCE_ENFORCEMENT.md` | `test`, `windows-governance` (+ `governance / enforce`) |
| `validator-agent`, `DIRECT_PR_REQUIRED_CHECKS` | **tylko `test`** |

Skutek nie jest kosmetyczny. Zewnętrzny walidator, który zna tylko `test`,
zatwierdzi pull requesta z czerwonym `windows-governance` — a więc wystawi
zaufane zatwierdzenie dla zestawu zmian, którego ruleset i tak nie wpuści.
Zatwierdzenie mówi wtedy coś, czego nie sprawdziło.

To ta sama klasa błędu co tickety 018, 021 i 025: ręcznie utrzymywana lista
zakresu, która przestała nadążać za rzeczywistością. Za każdym razem lekarstwem
było odczytanie listy zamiast trzymania jej drugiej kopii.

Zakres: jedno źródło prawdy dla nazw wymaganych checków i bramka wykrywająca
rozjazd. Poza zakresem pozostaje zmiana samego zestawu checków.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: Nazwy wymaganych checków mają jedno źródło w repozytorium,
  wskazane wprost w `docs/GOVERNANCE_ENFORCEMENT.md`.
- [ ] AC-02: Bramka porównuje to źródło z zestawem checków faktycznie
  publikowanych przez `.github/workflows/ci.yml` i failuje, nazywając check,
  którego brakuje po którejkolwiek stronie.
- [ ] AC-03: Test mutacyjny: usunięcie jednego joba z `ci.yml` jest wykrywane
  po nazwie; przywrócenie przywraca zielony wynik.
- [ ] AC-04: Dokumentacja mówi wprost, że konsument zewnętrzny — na przykład
  `validator-agent` — czyta ten sam zestaw, i wskazuje gdzie.

## Ryzyka i Uwagi

- Ryzyko: ruleset żyje w konfiguracji GitHuba, poza repozytorium, więc bramka
  nie może go odczytać w CI bez uprawnień administracyjnych. Mitygacja do
  rozważenia: źródło w repozytorium jest deklaracją, a zgodność rulesetu z nim
  weryfikuje osobny, ręcznie uruchamiany krok.
- Uwaga: `governance / enforce` jest celowo ignorowany przez walidator jako
  check cyrkularny; jedno źródło musi tę różnicę zapisać, a nie zatrzeć.
- Uwaga: `windows-governance` uruchamia `tests/windows-governance.test.ps1`,
  który jest świadomie poza strażnikiem kompletności z ticketu 025 — inny
  interpreter i osobny job.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-030/`.
