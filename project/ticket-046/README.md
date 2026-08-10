# Ticket 046: Migrate locked manifests and authorize bounded autonomy

- **ID**: ticket-046
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-10

## Cel i zakres

Naprawić migrację z legacy, w pełni zarządzanego manifestu do kontraktu
`extendable` opublikowanego w 0.14.0. Migrator ma użyć jako poprzedniej bazy
dokładnego target manifestu uwierzytelnionego przez jego hash w istniejącym
locku, a nie pristine default z historycznego commitu standardu.

Usunąć także redundantną bramkę ponownego pytania o zgodę po zapisaniu planu,
jeżeli samo bieżące polecenie użytkownika zleca wykonanie albo tryb autonomiczny.
Plan i `intent.json` nadal powstają przed implementacją, lecz są audytem i
granicą zakresu, a nie automatycznym powodem zatrzymania.

Problem został odtworzony na Goal 2.1.289 podczas próby przejścia z
new-project 0.11.0 do 0.14.0: legalny, hash-bound target różni się od defaultu
standardu i migracja błędnie kończy się komunikatem o brakującym
`$/approvalEvidence`.

## Kryteria odbioru

- [x] AC-01: Legacy manifest jest bazą migracji wyłącznie wtedy, gdy istniejący
  lock zawiera jego hash i hash zgadza się z dokładną zawartością pliku.
- [x] AC-02: Migracja dodaje nowe standard-owned wymagania, zachowuje
  target-owned workstreamy/ścieżki i tworzy zarządzany `manifest.base.json`.
- [x] AC-03: Zmieniony lub niezgodny z lockiem legacy manifest nadal kończy się
  fail-closed bez zapisu częściowej adopcji.
- [x] AC-04: Fresh adoption i istniejące upgrade'y `extendable` zachowują
  dotychczasowe zachowanie.
- [x] AC-05: Regresja o kształcie Goal 0.11.0→0.14.x przechodzi, a pełny Linux
  hub contract i `git diff --check` są zielone.
- [x] AC-06: Implementacja zostaje opublikowana jako pojedynczy PR, przechodzi
  Windows i niezależny exact-head Validator App review; immutable patch release
  pozostaje osobnym ticketem.
- [x] AC-07: Polecenie zlecające wykonanie lub tryb autonomiczny tworzy
  `SESSION_EXECUTION_AUTHORIZATION`; agent zapisuje plan i może przejść do
  implementacji bez osobnego pytania o tę samą zgodę.
- [x] AC-08: Brak autoryzacji dla destrukcji, sekretów, nowej koordynacji
  zewnętrznej albo materialnie nowego celu nadal zatrzymuje pracę, a agent nie
  może uznać własnej zgody za trusted merge evidence.
- [x] AC-09: Reguły huba i zarządzany downstream `AGENTS.md` opisują tę samą
  semantykę autonomii bez sprzecznego bezwarunkowego `STOP & WAIT`.

## Ryzyka i uwagi

- Zaufanie niewłaściwej lokalnej treści osłabiłoby standard. Dlatego źródłem
  legacy base może być tylko plik związany hashem przez poprawny istniejący
  lock; brak lub rozjazd hasha blokuje migrację.
- Naprawa nie zmienia listy target-owned pól i nie pozwala usunąć nowych
  wartości wymaganych przez bieżący managed base.
- Autonomia jest ograniczona zapisanym celem i `allowedPaths`; nie nadaje
  uprawnienia do destrukcji, obsługi sekretów, force-push ani self-approval.
- Nie modyfikuje Goal ani żadnego repozytorium downstream w tym ticketcie.

## Stan

`DONE / DONE`. Użytkownik jawnie zatwierdził `ticket-046` i polecił
wyłączenie powtórnej bramki zgody na rzecz autonomicznej realizacji. Zgoda
sesyjna obejmuje opisany bounded scope, ale nie zastępuje trusted merge review.
PR #73 przeszedł pełny Linux/Windows CI i exact-head review
`ifuri-validator-agent[bot]` dla `20a450b`, po czym został scalony jako
`main@cc898c1`. Patch release pozostaje osobnym ticketem.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-046/`.
