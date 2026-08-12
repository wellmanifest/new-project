# Ticket 063: Domknięcie cyklu życia workspace i branchy

- **ID**: ticket-063
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-12

## Cel i zakres

Usunąć lukę, przez którą po zakończonych pilotach pozostają lokalne worktree,
duplikaty klonów i branche bez PR, mimo że zdalny stan spoczynkowy jest opisany
w polityce. Standard ma rozróżniać aktywny workspace od zakończonego zadania,
zabraniać niszczenia unikalnych danych i wymagać sprawdzalnego sprzątnięcia po
merge, publikacji albo jawnej decyzji o porzuceniu pilota.

Pakiet adopcyjny dostarczy lokalny audyt workspace uruchamiany przez Goal oraz
samodzielny workflow targetu sprawdzający na GitHubie `delete_branch_on_merge`,
otwarte PR-y i osierocone branche. CI nie ma dostępu do filesystemu komputera
deweloperskiego, dlatego lokalne sprzątnięcie pozostaje terminalnym obowiązkiem
agenta potwierdzanym audytem, a nie pozorną kontrolą serwerową.

## Kryteria odbioru

- [x] AC-01: Polecenie użytkownika upoważnia do lokalnego audytu, naprawy
  standardu i usunięcia wyłącznie zweryfikowanych artefaktów pilotażowych.
- [x] AC-02: DSL i instrukcje agenta definiują bezpieczny terminalny cleanup
  worktree, klonów i lokalnych branchy, z ochroną dirty/unreachable danych.
- [x] AC-03: Deterministyczny audyt wykrywa dodatkowe linked worktree i
  niezależne klony tego samego repozytorium, nie wykonując usuwania.
- [x] AC-04: Pakiet adopcyjny instaluje audyt workspace oraz workflow CI, który
  sprawdza rzeczywisty zdalny lifecycle branchy i używa wyłącznie immutable
  akcji z runtime Node.js 24.
- [x] AC-05: Testy focused, pełny Linux contract i Ruff przechodzą, a audyt
  `~/github/semcod` nie pomija żadnego zachowanego wyjątku.

## Ryzyka i uwagi

- Żaden checker nie usuwa danych. Cleanup wymaga uprzedniego potwierdzenia, że
  HEAD jest zintegrowany albo materiał został jawnie sklasyfikowany jako
  porzucony pilot.
- Workflow CI widzi GitHub, ale nie lokalne dyski; lokalny checker widzi dysk,
  ale nie zastępuje serwerowego review ani ustawień repozytorium.
- Nie usuwać aktywnego kandydata standardu ani unikalnej implementacji Goal
  przed ich integracją lub zachowaniem w zaufanym refie.

## Dowody zakończenia

- PR #89 został scalony jako `b477b9221838fa292817fb8e64bdd9723046191a`.
- Post-merge run `31551977984` przeszedł kompletny Linux contract oraz bramkę
  Windows na dokładnym merge commitcie.
- Validator `31551863706` użył GLM 5.2 na dokładnym headzie
  `a09cdeb9bb57093107fed269bf879f29d3ee6e10`: pięć chunków, `APPROVE`, zero
  findings. Wcześniejsze dwa trafne findings zostały poprawione i ponownie
  zweryfikowane.
- todo2code `20260812T005033Z-ddf4d049` wymagał GLM 5.2 na finalnym headzie,
  lecz skonfigurowany klucz nadal otrzymał limit tygodniowy. Run zakończył się
  fail-closed na NL, bez grafu i bez fallbacku.

## Uczestnicy

- Human participant: unresolved; `user-*` jest tworzony wyłącznie przez jego
  właściciela albo zaufaną granicę intake.
- Agent participant: `ai-codex.md`.
