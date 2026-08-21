# Ticket 099: Ship the worktree guard as a managed file and fail closed without its runner

- **ID**: ticket-099
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: EDIT
- **Utworzono**: 2026-08-21

## Cel i Zakres

`install-worktree-guard.sh` kopiował runner jako pliki nieśledzone. Dwa razy w
ciągu doby `git clean` usunął je z `subactor/core` i `subactor/www-sub-actor`,
podczas gdy podpięty `pre-commit` przetrwał — zostawiając bramkę, która
wyglądała na zainstalowaną i nie egzekwowała niczego.

## Kryteria Odbioru (Acceptance Criteria)
- [x] AC-01: Zbudowany adopter zawiera runner, checker i config jako pliki
  zarządzane.
- [x] AC-02: Fragment hooka bez runnera kończy się kodem 1 i podaje remediation,
  zamiast cicho przepuścić commit.
- [x] AC-03: Suite guarda nadal przechodzi.

## Ryzyka i Uwagi
- Fixture adopcji musi kopiować `worktree-guard.yaml` z korzenia; fixture, który
  pomija to, co pakiet dostarcza, testuje standard, który nie istnieje.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-099/`.
