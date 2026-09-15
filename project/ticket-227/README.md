# Ticket 227: Derive release fixture versions from canonical sources

- **ID**: ticket-227
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-14

## Cel i Zakres
Usunąć literały bieżącej wersji z testów adopcji i governance, zachowując
wykrywanie prawdziwej niezgodności wersji. Wydać poprawkę wraz ze spójnymi
projekcjami 0.20.28 i dokumentacją kontrolowanego streamowania.

Użytkownik autoryzował wykonanie i chronioną publikację standardu oraz jego
późniejszą adopcję w Taskand. Agent `codex` wykonuje ten bounded zakres;
autoryzacja sesji nie zastępuje niezależnego zatwierdzenia exact-head.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Testy adopcji i governance działają przy nowej wersji bez zmiany literałów testowych i nadal weryfikują zgodność źródła, manifestu i locka.
- [x] AC-02: Niezgodna wersja jest zawsze rzeczywiście różna, także dla źródła 9.9.9, i blokuje adopcję przed zapisem zarządzanych plików.
- [ ] AC-03: VERSION, oba manifesty, changelog i dokumentacja są spójne; publikacja zachowuje Goal, wymagane checki i niezależne review.

Oba zestawy PASS w izolowanym obrazie
`sha256:b856811ab56d71a80744e11e5204809fbdec50de1ba9d4b7d27d2ae98d0a3a0d`.
Kontrola zakresu: 0 błędów; dokumentacja: 6 dokumentów, 0 findings.
Przed poprawką nowa wersja powodowała AssertionError w teście starego literału.
Opcjonalny test integracji z prywatnym Registry pominięty zgodnie z jego
warunkiem: brak `TEST_REGISTRY_TICKET_RUNTIME`; nie jest dowodem integracji.
Publikacja i późniejszy release wymagają osobnych receiptów exact-head.

Surowe wyniki: prywatny receipt store `release-fixtures-20260914.ItCdfK`.
Adoption: `sha256:a1a8e083626115100c05f934c7f772c60dee21b18b3170a3dabb2c9b0c8039f5`.
Governance tests: `sha256:82061e4b36228bdb1e51e6ee4f3e9e3f1a088fc1f72de31f7d4af65e983f0777`.
Rejestr: https://github.com/wellmanifest/new-project/issues/346, Planfile PLF-008
(projekcja obserwacji, nie źródło autoryzacji).

## Ryzyka i Uwagi
- Ryzyko testu tautologicznego: podstawowy assertion porównuje wynik adopcji
  z VERSION źródła, nie tylko dwa wygenerowane pola między sobą.
- Ryzyko fałszywego testu negatywnego: JSON zmienia dokładnie standard.version
  i jawnie potwierdza różnicę; odmowa nadal musi poprzedzać zapis targetu.
- Historyczne tagi, cudze niezapisane zmiany i kopie adopterów pozostają nietknięte.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-227/`.
