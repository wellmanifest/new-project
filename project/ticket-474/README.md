# Ticket 474: Align protected delivery guidance with human manual-owner-override

- **ID**: ticket-474
- **Owner**: agent:antigravity
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-11-24

## Cel i Zakres
Align the `wellmanifest:protected-delivery` instruction block (`AGENTS.md` and `template/files/AGENTS.template.md`), host policy block (`scripts/host_publication_policy.py`), and their deterministic test assertions with `wellmanifest/merge@95f3cd62` and `wellmanifest/autonomy@22a04550`: allow authenticated human-owner `manual-owner-override` merges when CI, OneDev, Validator, or controllers fail or stall, forbid auto-reverting them, and keep AI agents strictly prohibited from self-approval or direct merges.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Update `AGENTS.md`, `template/files/AGENTS.template.md` (keeping `wellmanifest:protected-delivery` byte-identical), and `scripts/host_publication_policy.py` with the `manual-owner-override` exception (`wellmanifest/merge@95f3cd62`, `wellmanifest/autonomy@22a04550`) without granting AI agent merge authority.
- [x] AC-02: Update `tests/host_publication_policy_test.py` and `tests/agent-hosts.test.sh` assertions and pass all host/publication test suites and `./project/governance-check.sh`.

## Ryzyka i Uwagi
- Risk 1: Diverging `wellmanifest:protected-delivery` bytes between `AGENTS.md` and `template/files/AGENTS.template.md` or breaking pinned `LOCAL_CI_PUBLICATION.template.md` SHA-256 — mitigated by leaving `LOCAL_CI_PUBLICATION.template.md` untouched and verifying both `agent-hosts.test.sh` and `local-ci-publication.test.sh`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt i opcjonalne decyzje. Surowe logi
pozostają poza śledzonym repozytorium; Git zapisuje tylko skrót wyniku i
referencję do receiptu. Kod wykonywalny, skrypty badawcze i testy należą do
zwykłych katalogów źródłowych, nie do `project/ticket-474/`.

<!-- ticket-radar:start -->
## Ticket Radar

Initial planned-scope estimate; advisory only, not execution or merge approval.

| Measure | Initial assessment |
| --- | --- |
| Impact score | 60/100 |
| Complexity | L |
| Estimated effort | 64 min |
| Planning budget | 30 min |
| Split recommended | yes |

Diagnostics: RADAR-ACCEPTANCE-MISSING, RADAR-BUDGET-EXCEEDED.
<!-- ticket-radar:end -->
