# Ticket 005: Harden external approval evidence validation

- **ID**: ticket-005
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-04

## Cel i zakres

Uszczelnić kanoniczny walidator dowodów aprobaty po niezależnym review
`todo2code`: dowód z nieprawidłowym authority albo bindingiem nie może zasilać
bramki jako zaufany, a plik dowodu ma być odczytany bez podążania za symlinkiem
w ostatnim komponencie ścieżki.

Zakres jest celowo mały (klasa złożoności `S`, limit 30 minut): jeden moduł
walidatora, jeden istniejący test kontraktowy, wersja/changelog i artefakty
ticketu. Bez zmian schematów, API publicznego ani zależności runtime.

## Architektura przed implementacją

```text
protected resolver -> external JSON file -> safe no-follow read
                                        -> schema + binding + authority
                                        -> trusted approval projection
```

Każdy błąd walidacji kończy projekcję wartością `None`; ogólna bramka nadal
emituje stabilne `GOV-APPROVAL-*` i działa fail-closed.

## Kryteria odbioru (Acceptance Criteria)

- [x] AC-01: Dowód z błędnym bindingiem lub authority emituje właściwy
  diagnostic i nie przekazuje `source`/`ticket` do trusted approval gate.
- [x] AC-02: Odczyt dowodu odrzuca symlink oraz plik inny niż regularny.
- [x] AC-03: Poprawny zewnętrzny dowód GitHub App i signed attestation nadal
  przechodzi bez regresji.
- [x] AC-04: Pełne testy governance, test adopcji i kontrola diffu przechodzą.
- [ ] AC-05: Poprawka zostaje opublikowana, a `todo2code` adoptuje dokładny
  opublikowany SHA i uzyskuje świeżą atestację dla nowego HEAD.

## Ryzyka i uwagi

- Ryzyko: fałszywe odrzucenie poprawnego dowodu. Mitygacja: zachować testy
  pozytywne dla GitHub App i signed attestation.
- Ryzyko: platforma bez `O_NOFOLLOW`. Mitygacja: fail-closed z czytelnym
  `GOV-APPROVAL-003`, bez niebezpiecznego fallbacku.
- Uwaga: review LLM było advisory. Poprawka wynika z niezależnej inspekcji kodu
  i zostanie potwierdzona deterministycznymi testami.

## Dowody walidacji

- `bash tests/governance-validator.test.sh` — PASS.
- `bash tests/governance-scripts.test.sh` — PASS.
- `bash tests/adoption-lock.test.sh` — PASS.
- `python3 -m py_compile scripts/governance_check.py` — PASS.
- `git diff --check` — PASS.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-005/`.
