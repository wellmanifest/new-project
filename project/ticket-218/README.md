# Ticket 218: Reuse-first work admission and proportional governance

- **ID**: ticket-218
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-09-13

## Cel i zakres

Przed developmentem obserwuj pracę obok main; kontynuuj, pomóż tylko do
odczytu, uzgodnij fenced handoff lub kolejkę przed nową alokacją. Zachowaj
proporcjonalne dowody i brak rekurencyjnych ticketów/worktree/decision records.
Implementacja obejmuje kontrolę startu i alokator, schemat raportu, dokumentację,
testy oraz projekcje wersji 0.20.26 w jednym materialnym changesecie (24 pliki).

Użytkownik jawnie zlecił publikację przez PR i niezależny Validator/merge,
następnie aktualizację adopterów. Zadania adopterów pozostają w ich własnych
repozytoriach. Uczestnicy: unresolved:human oraz agent:taskand. Nie tworzy się
nowego worktree na potrzeby kontynuacji. Nie edytuje się cudzych primary.

Baza została uzgodniona przez fast-forward istniejącego worktree do
`d54878a105a20d84dd554f205bc177dcacc8730a` i trójstronne przeniesienie własnego
delta; zachowano upstream SQLite, >=3-cyfrowe ID i wszystkie nowe kontrakty.
Poprzedni snapshot: `receipt:work-start-20260913/before-reconciliation`,
SHA-256 `6617a34b2fd36cc30175a4b17cdb93d60693eef3bac100442e7cb98ac269e115`.
To odtwarzalny dowód lokalny, nie review approval.

## Kryteria odbioru

- [x] AC-01: Źródło/szablon chronią reuse-first, brak rekurencji i jawny refresh.
- [x] AC-02: Zamknięta klasyfikacja czynności i historyczny replay mają regresje.
- [ ] AC-03: Wymagane bramki oraz niezależny review odnoszą się do exact head.
- [x] AC-04: Regresje realnego Git sprawdzają worktree, pending delta, kolejkę,
  brak skutków i odrzucenie alokacji przed rezerwacją numeru.

Wynik: [procedura work admission](../../error/GOV-WORK-START.md) i reguły w CONTRIBUTING.md.
Testy lokalne w przypiętym Python 3.12 z Node.js:
`receipt:work-start-20260913/tests-final`. Publikacja i immutable release
pozostają osobnymi etapami wymagającymi weryfikacji zdalnej.

## Ryzyka i granice

Preflight jest obserwacją lokalnego klonu, nie globalnym schedulerem ani
authority writera. Wymaga ponownego odczytu, lease/CAS i niezależnego gate.
Istniejące foreign/legacy/dirty checkouty i historyczne decyzje pozostają
nietknięte. Bez blanket ignore, force push, automatycznego cleanup i
samozatwierdzenia. Raw logs i snapshoty pozostają w prywatnym magazynie.
