# Preprompt & Wytyczne Techniczne (ticket-017)

- **Tytuł Zadania**: Lifecycle i sprzątanie branchy ticketowych
- **Utworzono**: 2026-08-05T10:01:56Z

## Wymagania i Ograniczenia Techniczne
- Zachowaj istniejący model: osobny branch/worktree na aktywny ticket i PR.
- Dodaj wyłącznie brakującą fazę sprzątania po zakończeniu PR-a.
- Automatyczne usuwanie jest dozwolone po merge; zamknięcie bez merge wymaga
  jawnej decyzji właściciela, ponieważ branch może zawierać niewłączone commity.
- Wymagaj GitHub `delete_branch_on_merge=true` i opisz audyt stanu spoczynku.
- Required governance pozostaje deterministyczny; LLM nie uczestniczy w decyzji.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Specyfikacja procesu: `docs/GOVERNANCE_ENFORCEMENT.md`
- Instrukcje adopcji: `template/files/AGENTS.template.md`

## Dyrektywy Wykonawcze dla Agenta AI
- Odczytaj niniejsze wytyczne techniczne oraz istniejące, human-owned notatki
  z `user-{github_username}.md`. Nie twórz ani nie modyfikuj ich za człowieka.
- Na tej podstawie zbuduj specyfikację wykonawczą w pliku `ai-codex.md` (rozumienie intencji, zakres prac, koncepcja, Kryteria Odbioru).
- Przed pisaniem kodu przedstaw plan w `ai-codex.md` oraz w `TODO.md` do weryfikacji człowieka (`P-CORE-008`).
- Kod wykonywalny, testy i skrypty badawcze zapisuj poza katalogiem ticketu;
  ticket przechowuje wyłącznie governance, decyzje, logi i dowody.
