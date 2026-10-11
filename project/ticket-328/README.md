# Ticket 328: Include standard packaging and build ignores in adoption lock gitignore payload

- **ID**: ticket-328
- **Owner**: agent:gemini
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-10-11

## Cel i Zakres

Rozszerzenie `worktree_ignore_payload` w `scripts/create_adoption_lock.py` o automatyczne dołączanie standardowych reguł ignorowania artefaktów budowania i pakietów (dla Pythona: `*.egg-info/`, `*.egg`, `build/`, `dist/`; dla Node: `node_modules/`; dla Rusta: `/target/`), gdy w adoptowanym repozytorium wykryte zostaną odpowiednie manifesty (`pyproject.toml`, `setup.py`, `package.json`, `Cargo.toml`).
Zapobiega to blokowaniu operacji governance i alokacji ticketów przez błędy brudnego checkoutu przy standardowych instalacjach deweloperskich (`pip install -e`).

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `scripts/create_adoption_lock.py` dołącza reguły ignorowania artefaktów budowania bazując na wykrytych manifestach środowiskowych.
- [x] AC-02: Test `tests/worktrees-adoption.test.py` weryfikuje poprawne ignorowanie plików `*.egg-info`, `dist/`, `build/` i `node_modules/`.
- [x] AC-03: Governance checks pass cleanly with 0 errors and 0 warnings.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Kod wykonywalny, skrypty i testy należą do zwykłych katalogów źródłowych, nie do `project/ticket-328/`.
