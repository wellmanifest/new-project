# Ticket 109: Publish adopter governance enforcement as new-project 0.18.5

- **ID**: ticket-109
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-22

## Cel i Zakres

Opublikować zintegrowane tickety 106–108 jako niezmienny
`wellmanifest/new-project 0.18.5`, aby repozytoria adoptujące mogły przypiąć
pełny kontrakt host-agnostyczny i job `governance / enforce` do dokładnego SHA.
Zmiana jest mechanicznym patch release: aktualizuje nośniki wersji, aktywne
asercje wersji i changelog; nie zmienia zachowania zintegrowanej bramki.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: `VERSION`, oba manifesty i aktywne asercje testowe wskazują
      `0.18.5`.
- [x] AC-02: changelog opisuje host contract, dystrybucję i egzekucję CI jako
      kompatybilny patch.
- [x] AC-03: wszystkie zestawy `tests/*.test.sh`, Ruff, diff hygiene i
      exact-base governance przechodzą przed merge.
- [x] AC-04: Validator zatwierdza i scala dokładny head przygotowania release.
- [x] AC-05: po ponownym teście czystego merge SHA Goal tworzy wcześniej
      nieistniejące tag i GitHub Release `v0.18.5`, bez przesuwania starego taga.

## Ryzyka i Uwagi
- Tag i GitHub Release są nieodwracalne operacyjnie. Publikacja nastąpi dopiero
  po exact-head trusted merge i ponownym pełnym teście czystego `main`.
- Ten ticket nie adoptuje wydania w żadnym target repo i nie zmienia rulesetów.

## Pre-publication evidence

- 10/10 zestawów `tests/*.test.sh`: PASS.
- Ruff: `All checks passed!`.
- Diff hygiene: PASS.
- Exact-base governance od `a3945be`: `GOV-PASS`.
- Tag i GitHub Release `v0.18.5` pozostają nieobecne przed publikacją.

## Final evidence

- Pull request: `wellmanifest/new-project#180`.
- Frozen implementation head: `0f1ba61a6d91e742988af5bcda07650b991359d4`.
- Validator approval: review `5001265454`, run `32605154146`.
- Merge commit: `5cc475f6200df9f8c1d045240277c6eaa2f9a642`.
- Clean-main 10/10 suites, Ruff, diff hygiene and governance: PASS.
- Goal `2.1.300` published `v0.18.5`; its peeled tag equals the merge commit.
- GitHub Release is published, non-draft and not a prerelease.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-109/`.
