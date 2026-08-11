# Ticket 056: Report missing target prerequisites during adoption

- **ID**: ticket-056
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-11

## Cel i Zakres

Rozszerzyć przypięty generator adopcji uruchamiany przez
`goal governance adopt`, aby w `--check` i po zapisie raportował wymagane
pliki target-owned, których nadal zabraknie po zastosowaniu kompletnego planu
pakietu. Raport ma pomóc przygotować repo do pierwszego `GOV-PASS`, ale nie
może tworzyć tych plików, uznawać zarządzanych plików za brakujące ani zmieniać
dotychczasowych kodów wyjścia dla driftu pakietu.

Zmiana obejmuje generator, regresję adopcji i dokumentację Goal. Nie obejmuje
ogólnej walidacji stacków, automatycznego scaffoldingu targetu, zmian manifestu,
wersji, zależności ani publikacji.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: Polecenie użytkownika stanowi bounded
  `SESSION_EXECUTION_AUTHORIZATION` dla lokalnej implementacji i testów.
- [ ] AC-02: Preflight pustego targetu raportuje w stabilnej kolejności tylko
  te `requiredFiles`, których nie utworzy plan adopcji, i niczego nie zapisuje.
- [ ] AC-03: Pliki zarządzane obecne w payloadzie nie są raportowane jako
  brakujące, a utworzenie pliku target-owned usuwa jego ostrzeżenie.
- [ ] AC-04: Brak prerequisite pozostaje informacyjny: `--check` nadal zwraca
  `0` dla pakietu up-to-date i `1` dla driftu, a adopcja nadal może zakończyć
  instalację bez przejmowania zawartości targetu.
- [ ] AC-05: Focused adoption test, pełny Linux contract, Ruff i ponowny pilot
  Goal na repo bez `TODO.md` przechodzą z oczekiwanym raportem.

## Ryzyka i Uwagi

- Raport musi liczyć stan po planowanej instalacji, inaczej fałszywie oznaczy
  `AGENTS.md` i zarządzane skrypty jako brakujące.
- Nie wolno zmieniać kodu wyjścia wyłącznie z powodu target-owned prerequisite;
  ten interfejs opisuje drift pakietu i jest używany do idempotence check.
- Lista z manifestu musi być walidowana jako bezpieczne, względne ścieżki i
  emitowana deterministycznie.
- Nie wykonujemy push, PR, merge, tagowania ani publikacji.

## Autoryzacja

Bieżące polecenie użytkownika zleca lokalne poprawianie standardu na podstawie
kolejnych pilotów. Operacje zewnętrzne wymagają osobnej dyspozycji.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-056/`.
