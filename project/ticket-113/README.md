# Ticket 113: Complete the host contract with the aider and Copilot hosts

- **ID**: ticket-113
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-23

## Cel i Zakres

`ticket-107` rozsyłał `CLAUDE.md`, `GEMINI.md`, regułę Cursora i hooka, ale
hosty `aider` i `copilot` wypadły z tamtego slice'u przy limicie dziewięciu
plików — naprawa fixture'u adopcyjnego była warunkiem weryfikowalności tamtej
zmiany i zajęła miejsce, które miały zająć te dwa hosty. To jest ich ticket.

`.aider.conf.yml` ładuje `AGENTS.md` i `CLAUDE.md` do każdej sesji przez klucz
`read:` i ustawia `auto-commits: false`, więc narzędzie nie utworzy commita,
którego hook nie widział. `.github/copilot-instructions.md` jest ładowany
automatycznie przez Copilot Chat i Copilot coding agent.

Po tej zmianie kontrakt obejmuje sześć hostów: `generic` (`AGENTS.md`),
`claude`, `gemini`, `cursor`, `aider`, `copilot`.

## Kryteria Odbioru (Acceptance Criteria)

- [x] AC-01: `python3 scripts/agent_host_check.py --root .` →
  `GOV-AGENT-HOST-PASS` przy sześciu zadeklarowanych hostach.
- [x] AC-02: `bash tests/agent-hosts.test.sh` — fixture wyprowadza pliki hostów
  z kontraktu, więc oba nowe hosty są sprawdzone bez edycji testu. To zwrot z
  decyzji podjętej w `ticket-107`.
- [x] AC-03: `bash tests/adoption-lock.test.sh` — oba nowe źródła pakietowe
  adoptują się i zapisują digest.
- [x] AC-04: `./project/governance-check.sh --actor agent` → `GOV-PASS`.

## Ryzyka i Uwagi

- Risk 1: `auto-commits: false` zmienia domyślne zachowanie aidera w każdym
  adopterze, który przyjmie ten plik. To jest zamierzone: commit ma przechodzić
  przez hooka, nie obok niego.
- Risk 2: `agent_host_check.py` wymaga odtąd obu plików. Adopter dostaje je tą
  samą transakcją adopcyjną co zaktualizowany kontrakt, więc jedno nie może
  wyprzedzić drugiego.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-113/`.
