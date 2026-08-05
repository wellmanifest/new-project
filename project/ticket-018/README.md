# Ticket 018: Deterministyczny audyt lifecycle branchy GitHub

- **ID**: ticket-018
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-05

## Cel i zakres

Dodać deterministyczny audyt stanu branchy GitHub do centralnego reusable
workflow. Chroniony workflow pobiera wyłącznie fakty z GitHub API, zapisuje
zamknięty snapshot JSON, a lokalny skrypt bez dostępu do sieci sprawdza:
`delete_branch_on_merge`, obecność default branchu oraz brak branchy, które nie
są headem żadnego otwartego PR-a.

## Kryteria odbioru

- [x] AC-01: Walidator przyjmuje wyłącznie wersjonowany, ściśle walidowany
  snapshot i nie wykonuje połączeń sieciowych ani mutacji Git/GitHub.
- [x] AC-02: `delete_branch_on_merge=false` emituje stabilny blocking
  diagnostic z remediacją.
- [x] AC-03: Branch inny niż default branch i wewnętrzne heady otwartych PR-ów
  jest raportowany jako osierocony; przy zerowej liczbie PR-ów dozwolony jest
  wyłącznie default branch.
- [x] AC-04: Forkowe heady PR-ów nie są błędnie wymagane w repozytorium bazowym,
  a brak wewnętrznego heada jest odrzucany jako sprzeczny snapshot.
- [x] AC-05: Reusable workflow zbiera fakty przez GitHub API i uruchamia
  walidator przy każdym wywołaniu przez chroniony caller obsługujący `push`,
  `pull_request`, `pull_request_review` i wywołania ręczne.
- [x] AC-06: Pozytywne i negatywne fixture przechodzą w CI bez `todo2code`, LLM
  ani zewnętrznej biblioteki runtime.

## Ryzyka i mitygacje

- Dane GitHub są stanem zewnętrznym; workflow zapisuje dokładny snapshot jako
  granicę między akwizycją a deterministyczną decyzją.
- Forkowy PR nie tworzy brancha w repozytorium bazowym; walidator uwzględnia
  wyłącznie heady pochodzące z tego samego repozytorium.
- Automatyczne usuwanie dotyczy merge; walidator niczego nie usuwa i nie może
  utracić niezmergowanej pracy.
- `todo2code` ma lokalne portfolio refów, ale nie zna ustawień GitHub; pozostaje
  opcjonalnym źródłem analizy semantycznej, nie zależnością required gate.

## Zatwierdzenie interaktywne

Użytkownik zatwierdził `ticket-018` 2026-08-05 razem z ticketem 017. Zależność
017 została formalnie zamknięta w PR #21 jako `b45ce07`, dlatego ticket może
przejść do `EDIT`. Zgoda interaktywna nie zastępuje exact-head merge approval.

## Walidacja

- `bash tests/governance-scripts.test.sh` — PASS.
- `bash tests/governance-validator.test.sh` — PASS.
- `bash tests/branch-lifecycle.test.sh` — PASS.
- `bash tests/adoption-lock.test.sh` — PASS.
- Kompilacja Python, parsowanie obu workflow YAML, walidacja JSON i
  `git diff --check` — PASS.
- Lokalny PowerShell jest niedostępny; istniejący test Windows pozostaje
  wymaganym jobem CI na `windows-latest`.

## Dowód publikacji

- PR: `wellmanifest/new-project#24`.
- Approved head: `c57f203b8d2a4c4e25beefa0ccfebe215a3b45cd`.
- Validator: `ifuri-validator-agent[bot]`, model advisory
  `openrouter/z-ai/glm-5.2`.
- Merge commit: `89ddf4262291ad533eab2aa5513d33575925b972`.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-codex.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-018/`.
