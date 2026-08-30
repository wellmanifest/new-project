# Ticket 161: Atomowa alokacja ticketów dla rozproszonych workerów

- **ID**: ticket-161
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-30

## Cel i Zakres

Usunąć okno wyścigu pomiędzy niezależnymi klonami i hostami. Standard ma
rozróżniać lokalną alokację jednego klonu od trybu rozproszonego, w którym
numer ticketu pochodzi wyłącznie z atomowego, zarejestrowanego procesu i jest
związany z niezmiennym receiptem. Lokalny high-water pozostaje bezpiecznym
fallbackiem tylko dla profilu `local-single-clone`.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: Kontrakt rozróżnia `local-single-clone` i `registered`, a tryb
      rozproszony wymaga capability URI, zaufanego issuera oraz receipt.
- [ ] AC-02: `new-ticket.sh` odmawia lokalnego numerowania w trybie
      `registered`, emituje kanoniczny request i akceptuje tylko receipt
      związany z tym repozytorium, korelacją, klasyfikacją i niewygasłym lease.
- [ ] AC-03: Receipt nie może wskazać numeru istniejącego w katalogu ani w
      znanych refach; lokalna blokada nadal serializuje worktree jednego klonu.
- [ ] AC-04: Stabilny `ERROR` i runbook opisują zachowanie bez ręcznego rename,
      nadpisania historii, usunięcia obcej pracy lub przedwczesnego zamknięcia.
- [ ] AC-05: Testy regresyjne obejmują brak receipt, zły digest, wygaśnięcie,
      obcego issuera, poprawną alokację oraz zachowanie profilu lokalnego.
- [ ] AC-06: Standard 0.19.15 jest opublikowany przez chroniony Validator.

## Ryzyka i Uwagi

- Ryzyko: strukturalnie poprawny plik udający receipt. Mitygacja: policy wymaga
  pozyskania go z zarejestrowanego URI przez kontroler; plik nie jest merge ani
  execution authority, a runtime musi zweryfikować issuera i fencing token.
- Ryzyko: regresja adopterów bez Registry. Mitygacja: brak konfiguracji i
  profil bazowy zachowują dotychczasowy `local-single-clone`; tylko świadomie
  skonfigurowany profil rozproszony przechodzi fail-closed.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-161/`.
