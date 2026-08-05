# Ticket 019: Deterministyczny audyt lifecycle branchy GitHub

- **ID**: ticket-019
- **Owner**: unresolved:human
- **Status**: CANCELLED
- **Workflow state**: CANCELLED
- **Utworzono**: 2026-08-05

## Cel i zakres

Ticket miał dodać deterministyczny audyt lifecycle branchy GitHub. Ten sam cel
został wcześniej ukończony przez `ticket-018`, zatwierdzony na exact head przez
Validator Agent i scalony w PR #24. Ticket-019 jest duplikatem i nie może
uruchamiać drugiej implementacji tego samego kontraktu.

## Kryteria odbioru

- [x] AC-01: Duplikat został powiązany z ukończonym ticket-018.
- [x] AC-02: Nie utworzono drugiego runtime ani konkurencyjnego źródła prawdy.
- [x] AC-03: Powód anulowania i dowód publikacji ticketu zastępującego są jawne.

## Dowód zastąpienia

- Ticket zastępujący: `ticket-018` (`DONE / DONE`).
- PR implementacyjny: `wellmanifest/new-project#24`.
- Approved head: `c57f203b8d2a4c4e25beefa0ccfebe215a3b45cd`.
- Merge commit: `89ddf4262291ad533eab2aa5513d33575925b972`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-019/`.
