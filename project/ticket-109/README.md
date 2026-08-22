# Ticket 109: Publish adopter governance enforcement as new-project 0.18.5

- **ID**: ticket-109
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-22

## Cel i Zakres

Opublikować zintegrowane tickety 106–108 jako niezmienny
`wellmanifest/new-project 0.18.5`, aby repozytoria adoptujące mogły przypiąć
pełny kontrakt host-agnostyczny i job `governance / enforce` do dokładnego SHA.
Zmiana jest mechanicznym patch release: aktualizuje nośniki wersji, aktywne
asercje wersji i changelog; nie zmienia zachowania zintegrowanej bramki.

## Kryteria Odbioru (Acceptance Criteria)
- [ ] AC-01: `VERSION`, oba manifesty i aktywne asercje testowe wskazują
      `0.18.5`.
- [ ] AC-02: changelog opisuje host contract, dystrybucję i egzekucję CI jako
      kompatybilny patch.
- [ ] AC-03: wszystkie zestawy `tests/*.test.sh`, Ruff, diff hygiene i
      exact-base governance przechodzą przed merge.
- [ ] AC-04: Validator zatwierdza i scala dokładny head przygotowania release.
- [ ] AC-05: po ponownym teście czystego merge SHA Goal tworzy wcześniej
      nieistniejące tag i GitHub Release `v0.18.5`, bez przesuwania starego taga.

## Ryzyka i Uwagi
- Tag i GitHub Release są nieodwracalne operacyjnie. Publikacja nastąpi dopiero
  po exact-head trusted merge i ponownym pełnym teście czystego `main`.
- Ten ticket nie adoptuje wydania w żadnym target repo i nie zmienia rulesetów.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-109/`.
