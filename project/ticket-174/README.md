# Ticket 174: Adopt repository-namespaced worktrees v2

- **ID**: ticket-174
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-09-01

## Cel i zakres

Przypiąć wydany `wellmanifest/worktrees` v0.2.0 i rozprowadzić jeden układ
roboczy: `<workspace>/.worktrees/<repo>/<ticket-NNN>--<slug>`. Ticket obejmuje
projekcję schematu i checkera, instrukcje dla adopterów, testy regresyjne oraz
wydanie `new-project` 0.19.20 w tym samym materialnym PR.

## Kryteria odbioru

- [x] AC-01: dystrybuowany checker i schema są bajtowo związane z worktrees
      v0.2.0 oraz przyjmują układ z podfolderem repozytorium.
- [x] AC-02: płaski układ v1 i repo-local `.worktrees` są odrzucane.
- [x] AC-03: template wymaga jednego worktree na ticket i opisuje bezpieczną,
      nieautomatyczną migrację istniejących checkoutów.
- [x] AC-03a: allocator nie odrzuca poprawnego workstreamu wskutek `SIGPIPE`
      z pipeline `grep -q` pod `pipefail`.
- [x] AC-04: wersja 0.19.20 jest częścią tego materialnego changesetu, bez
      osobnego release-only ticketu ani PR-a.
- [ ] AC-05: testy adopcji, pełna bramka standardu i chroniony merge przechodzą.

## Ryzyka i uwagi

- Dodatkowy poziom katalogu wydłuża ścieżki, ale jednoznacznie grupuje checkouty
  repozytorium i usuwa kolizje nazw.
- Zmiana nazwy repozytorium zmienia namespace. Istniejących worktrees nie wolno
  przenosić automatycznie: najpierw trzeba sprawdzić dirty state, procesy/IDE,
  lease, PR oraz osiągalność HEAD, a następnie użyć dokładnego `git worktree move`.

## Granica katalogu

Ten katalog przechowuje minimalny kontrakt. Kod, schema i testy pozostają w
zwykłych katalogach źródłowych; surowe logi i terminalne receipty są poza Git.
