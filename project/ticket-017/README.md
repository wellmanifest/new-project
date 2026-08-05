# Ticket 017: Lifecycle i sprzątanie branchy ticketowych

- **ID**: ticket-017
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: PUBLICATION
- **Utworzono**: 2026-08-05

## Cel i zakres

Domknąć cykl życia krótkotrwałego brancha ticketowego: branch izoluje pracę
do czasu review, po merge jest automatycznie usuwany, a po zamknięciu bez merge
może zostać usunięty dopiero po jawnej decyzji właściciela. W stanie spoczynku,
gdy repozytorium nie ma otwartych PR-ów, jedynym zdalnym branchem ma być branch
domyślny.

## Kryteria odbioru

- [x] AC-01: Normatywna polityka rozróżnia merge od zamknięcia bez merge i
  nie pozwala usuwać niezintegrowanej pracy bez decyzji właściciela.
- [x] AC-02: Instrukcje źródłowe i adoptowany `AGENTS.md` wymagają ustawienia
  GitHub `delete_branch_on_merge=true`.
- [x] AC-03: Dokumentacja egzekwowania definiuje stan spoczynku: brak
  otwartych PR-ów oznacza wyłącznie branch domyślny na `origin`.
- [x] AC-04: Test deterministyczny wykrywa usunięcie lub rozjazd wymaganych
  markerów lifecycle w polityce, instrukcjach i szablonie adopcji.
- [x] AC-05: Zmiana mieści się w pięciu plikach standardu, nie dodaje zależności
  ani mechanizmu opartego na LLM.

## Ryzyka i mitygacje

- Automatyczne kasowanie brancha po zamknięciu bez merge mogłoby utracić pracę;
  dlatego automatyzacja obejmuje tylko merge, a zwykłe zamknięcie wymaga jawnej
  decyzji właściciela.
- Reguła może zostać pomylona z zakazem branchy; dlatego dokumentacja zachowuje
  branch jako wymaganą izolację podczas aktywnego PR-a.
- Ustawienie GitHub jest stanem zewnętrznym; lokalny test waliduje kontrakt i
  instrukcję, a stan repozytorium sprawdzi zależny ticket 018.

## Zatwierdzenie interaktywne

Użytkownik zatwierdził `ticket-017` 2026-08-05 razem z zależnym ticketem 018.
Zgoda obejmuje wykonanie po formalnym domknięciu ticketu 016, ale nie zastępuje
niezależnego exact-head merge approval.

## Walidacja

- `bash tests/governance-scripts.test.sh` — PASS.
- `bash tests/governance-validator.test.sh` — PASS.
- `bash tests/adoption-lock.test.sh` — PASS.
- `git diff --check` i walidacja JSON — PASS.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-017/`.
