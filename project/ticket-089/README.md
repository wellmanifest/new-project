# Ticket 089: Required-checks SSOT: per-repo instance and a gate that runs

- **ID**: ticket-089
- **Owner**: unresolved:human
- **Status**: BLOCKED
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-16

> **Blokada**: workstream `governance` dopuszcza jeden aktywny ticket
> (`maxActiveTicketsPerWorkstream: 1`), a `ticket-088` ma status `IN_PROGRESS`.
> Jego praca jest już scalona do `main` (PR #137, `31b3521`), brakuje wyłącznie
> ustawienia `DONE`. Ten ticket jest block-routowany zgodnie z remediacją
> `GOV-WORKSTREAM-002`; przechodzi do `IN_PROGRESS` po domknięciu 088. Zakresy
> nie kolidują: 088 dotyka `AGENTS.md`, `docs/`, `template/`, a 089
> `governance/`, `scripts/`, `tests/`.

## Cel i Zakres

`.governance/required-checks.json` jest ogłoszony źródłem prawdy dla
`requiredCheckNames`, ale dystrybuowany ze strategią `managed`, czyli przypięty
bajt-w-bajt. Plik z danymi per-repozytorium nie może być identyczny wszędzie —
deklaracja jest nieprawdziwa w 21 z 23 adoptujących repozytoriów. Bramka, która
miała tego pilnować, nie wykonuje się u żadnego z nich.

Zakres obejmuje wyłącznie hub: strategię dystrybucji, schemat instancji,
rozwiązywanie ścieżki i parsowanie nazwy checka w bramce oraz jej wpięcie do
`governance_check.py`. Pełna analiza w `ai-claude.md`.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: `strategy` dla `.governance/required-checks.json` to `extendable`.
- [ ] AC-02: `python3 scripts/check_required_checks.py` nadal przechodzi w hubie.
- [ ] AC-03: test pokrywa układ `.governance/` adoptującego.
- [ ] AC-04: `governance_check.py` wywołuje bramkę.
- [ ] AC-05: job z nadpisanym `name:` jest publikowany pod nazwą wyświetlaną.
- [ ] AC-06: bramka hubu przypisuje diff do ticket-089.

## Ryzyka i Uwagi
- Risk 1: {Opis ryzyka i mitygacja}

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-089/`.
