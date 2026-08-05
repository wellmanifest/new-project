# Ticket 015: Publikacja immutable 0.11.0

- **ID**: ticket-015
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-05

## Cel i zakres

Wydać kontrakt klasyfikacji pracy i manifest pakietu jako immutable `v0.11.0`,
zamiast przypisywać nowe semantyki do istniejącego tagu `v0.10.0`.

## Kryteria odbioru

- [x] AC-01: `VERSION`, manifest domyślny, changelog i testy wskazują 0.11.0.
- [ ] AC-02: Trzy zestawy regresyjne przechodzą przed merge; walidacja po
  merge pozostaje wymagana.
- [ ] AC-03: Annotowany tag `v0.11.0` i GitHub Release wskazują ten sam pełny
  SHA z chronionego `main`.
- [ ] AC-04: Czysty detached checkout release SHA przechodzi pełny kontrakt CI.
- [ ] AC-05: Istniejące tagi nie są przesuwane ani nadpisywane.

## Ryzyka i mitygacje

- Jeśli tag lub Release już istnieje, publikacja zatrzymuje się bez overwrite.
- Jeśli `main` zmieni się po walidacji, test czystego checkoutu jest powtarzany
  dla nowego SHA.
- Adopterzy przypinają pełny release SHA, nie nazwę brancha ani sam numer wersji.

## Uczestnicy

- Human participant: unresolved; plik `user-*` nie został utworzony.
- Agent participant: [`ai-codex.md`](ai-codex.md)

## Autoryzacja sesji

Użytkownik poleceniem „kontynuuj” 2026-08-05 zatwierdził wcześniej
przedstawiony plan ticketu 015. Jest to zgoda na implementację w bieżącej
sesji, a nie zaufany dowód merge.

## Dowody przed merge

- `governance scripts: PASS`
- `governance validator: PASS`
- `adoption lock: PASS`
- `v0.11.0`: brak istniejącego taga i GitHub Release w chwili kontroli.
