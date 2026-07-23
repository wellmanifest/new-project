# TODO

## Cel projektu

Zbudować pierwszą, kompletnie testowalną wersję systemu formalizującego intencje i ustalenia ludzi:

```text
NL / rozmowa / wytyczne tekstowe
→ LLM
→ formalny DSL
→ diagnoza braków i sprzeczności
→ walidacja Python
→ akceptacja użytkownika lub obu stron
→ TypeScript runtime
→ wygenerowany dokument, kontrakt albo opis zadania
→ wynik i audyt
```

DSL ma być czytelny dla człowieka i możliwy do jednoznacznego przetwarzania przez agentów AI oraz runtime.

System ma obsługiwać oba kierunki:

- NL → DSL
- DSL → NL / dokument końcowy

Pierwsza wersja ma działać wyłącznie na mockach i danych przykładowych.

---

## Etap 0 — analiza i zabezpieczenie repozytorium

- [x] Przeanalizować strukturę repozytorium.
- [x] Przeanalizować `README.md`.
- [x] Przeanalizować `POLICY.md`.
- [x] Przeanalizować `CONTRIBUTING.md`.
- [x] Przeanalizować materiały badawcze w `research/`.
- [x] Przeanalizować `project.sh`.
- [x] Zweryfikować przeniesienie historycznych folderów do `research/`.
- [x] Opisać aktualny cel projektu w `docs/architecture.md`.
- [x] Opisać rolę LLM, Python verifiera, runtime’u oraz ludzi uczestniczących w procesie.
- [x] Opisać, dlaczego `project.sh` jest albo nie jest używany w MVP.
- [x] Sprawdzić, czy żadna zawartość badawcza nie została utracona.
- [x] Doprowadzić repozytorium do kontrolowanego stanu bez przypadkowych usunięć.
- [x] Naprawić konfigurację pnpm i instalację zależności.

---

## Etap 1 — przypadki użycia i wymagania

Status: basic MVP scope, actors, single command flow, questions, and one-side approval are documented and covered; two-party conversation, text files, and full acceptance criteria remain open.


- [x] Zdefiniować zakres MVP.
- [x] Zdefiniować aktorów:
  - Human1 — autor intencji lub zleceniodawca,
  - Human2 — odbiorca, wykonawca albo druga strona umowy,
  - LLM — formalizacja i interpretacja,
  - Python verifier — walidacja znaczeniowa,
  - TypeScript runtime — walidacja techniczna, orkiestracja i renderowanie.
- [x] Zdefiniować przepływ dla pojedynczego polecenia użytkownika.
- [ ] Zdefiniować przepływ dla rozmowy dwóch stron.
- [ ] Zdefiniować przepływ dla wytycznych zapisanych w pliku tekstowym.
- [x] Zdefiniować proces akceptacji przez jedną stronę.
- [ ] Zdefiniować proces akceptacji przez obie strony kontraktu.
- [ ] Zdefiniować proces odrzucenia i ponownej edycji.
- [x] Zdefiniować proces zadawania pytań doprecyzowujących.
- [ ] Zdefiniować, kiedy dokument jest wystarczająco kompletny dla jego odbiorcy.
- [ ] Zdefiniować kryteria końcowego odbioru MVP.

---

## Etap 2 — specyfikacja Intent/Contract DSL

Status: narrow `office.dsl.v1` is implemented and tested; full Intent/Contract DSL remains open.


- [x] Zdefiniować kanoniczny model DSL.
- [x] Zdefiniować wersję języka.
- [x] Zdefiniować AST.
- [x] Zdefiniować JSON Schema.
- [x] Przygotować czytelną reprezentację DSL dla człowieka.
- [x] Zdefiniować konwersję JSON/AST → human-readable DSL.
- [ ] Zdefiniować konwersję DSL → dokument w języku naturalnym.

### Konstrukcje DSL

- [ ] `CONTRACT`
- [x] `TASK`
- [ ] `PARTY`
- [ ] `ROLE`
- [ ] `INTENT`
- [x] `SOURCE`
- [ ] `SUBJECT`
- [ ] `OBLIGATION`
- [ ] `DELIVERABLE`
- [ ] `DEADLINE`
- [ ] `PAYMENT`
- [x] `CONDITION`
- [ ] `ACCEPTANCE_CRITERIA`
- [ ] `EXCLUSION`
- [ ] `ASSUMPTION`
- [x] `QUESTION`
- [ ] `APPROVAL`
- [x] `OUTPUT`
- [ ] `RENDER`
- [x] `POLICY`

### Statusy informacji

- [x] `KNOWN`
- [ ] `CONFIRMED`
- [ ] `MISSING`
- [ ] `INCOMPLETE`
- [ ] `AMBIGUOUS`
- [ ] `CONFLICTING`
- [ ] `ASSUMED`
- [x] `REQUIRES_CONFIRMATION`
- [x] `REJECTED`

### Diagnostyka DSL

- [x] Wykrywanie brakujących danych.
- [ ] Wykrywanie niejednoznacznych terminów i wartości.
- [ ] Wykrywanie sprzecznych wypowiedzi stron.
- [ ] Wykrywanie założeń dodanych przez LLM.
- [ ] Wykrywanie elementów niezaakceptowanych przez obie strony.
- [x] Wykrywanie działań lub warunków, których nikt nie zlecił.
- [ ] Powiązanie każdego ustalenia ze źródłem w rozmowie lub pliku.
- [x] Generowanie konkretnych pytań dotyczących brakujących pól.

---

## Etap 3 — TypeScript runtime

Status: mock office-task runtime is implemented and tested; Human2, bilateral approval, contracts, and contract generators remain open.


- [x] Utworzyć parser DSL.
- [x] Utworzyć walidator strukturalny.
- [ ] Utworzyć walidator semantyczny.
- [x] Utworzyć TypeScript runtime.
- [x] Utworzyć state machine.
- [x] Utworzyć policy engine.
- [x] Utworzyć registry obsługiwanych operacji.
- [ ] Utworzyć mechanizm diagnozowania braków.
- [x] Utworzyć mechanizm pytań do Human1.
- [ ] Utworzyć mechanizm pytań do Human2.
- [x] Utworzyć proces akceptacji jednej strony.
- [ ] Utworzyć proces akceptacji obu stron.
- [x] Unieważniać akceptację po zmianie DSL lub planu.
- [x] Utworzyć hash zaakceptowanej wersji DSL.
- [x] Utworzyć renderer DSL → dokument NL.
- [ ] Utworzyć mockowy generator umowy.
- [ ] Utworzyć mockowy generator opisu zadania.
- [x] Utworzyć zapis audytu.
- [x] Utworzyć CLI dla Windows i Linux.

### Stany runtime’u

Status: runtime currently uses simplified states; target Human1/Human2 state names remain open.


- [x] `CREATED`
- [ ] `ANALYZING_INPUT`
- [x] `DSL_GENERATED`
- [x] `VALIDATING`
- [ ] `WAITING_FOR_INPUT_HUMAN1`
- [ ] `WAITING_FOR_INPUT_HUMAN2`
- [ ] `WAITING_FOR_APPROVAL_HUMAN1`
- [ ] `WAITING_FOR_APPROVAL_HUMAN2`
- [ ] `APPROVED`
- [x] `REJECTED`
- [ ] `RENDERING`
- [x] `SUCCEEDED`
- [x] `FAILED`
- [x] `DENIED`
- [x] `CANCELLED`

---

## Etap 4 — LLM planner

Status: mock planner for a single command is tested; OpenRouter, conversations, and file inputs remain open.


- [x] Utworzyć tryb mock działający bez internetu.
- [ ] Utworzyć opcjonalną integrację OpenRouter.
- [x] Obsłużyć wejście typu pojedyncza wypowiedź.
- [ ] Obsłużyć wejście typu historia rozmowy.
- [ ] Obsłużyć wejście typu plik z wytycznymi.
- [x] Generować wyłącznie wynik zgodny ze schematem.
- [ ] Oznaczać założenia utworzone przez LLM.
- [ ] Zachowywać źródło każdego ustalenia.
- [ ] Nie uzupełniać braków niepotwierdzonymi informacjami.
- [x] Generować propozycje pytań doprecyzowujących.
- [ ] Obsłużyć ponowne wygenerowanie DSL po odpowiedzi użytkownika.

---

## Etap 5 — Python verifier

Status: package and mock verifier are tested; full semantic validation for conversations, guideline files, and final documents remains open.


- [x] Utworzyć pakiet Python 3.11+.
- [x] Utworzyć tryb mock.
- [ ] Utworzyć opcjonalną integrację LiteLLM/OpenRouter.
- [ ] Walidować zgodność NL → DSL.
- [ ] Walidować zgodność historii rozmowy → DSL.
- [ ] Walidować zgodność wytycznych tekstowych → DSL.
- [ ] Walidować zgodność DSL → dokument końcowy.
- [ ] Sprawdzać pominięte ustalenia.
- [x] Sprawdzać działania i warunki dodane przez LLM.
- [ ] Sprawdzać sprzeczności.
- [ ] Sprawdzać niepotwierdzone założenia.
- [ ] Sprawdzać kompletność z perspektywy Human1.
- [ ] Sprawdzać kompletność z perspektywy Human2.
- [ ] Sprawdzać, czy odbiorca może jednoznacznie wykonać zadanie.
- [x] Zwracać wynik `PASS`, `FAIL` albo `NEEDS_REVIEW`.
- [x] Zwracać raport JSON możliwy do przetwarzania przez runtime.

---

## Etap 6 — struktura `examples`

Status: six flat examples validate offline; `scenario.json`, `in/`, `out/`, and diff runner remain open.


Każdy scenariusz ma mieć osobny folder:

```text
examples/<numer>-<nazwa>/
├── scenario.json
├── README.md
├── in/
│   ├── conversation.md lub input.md
│   ├── context.json
│   ├── parties.json
│   ├── policies.md
│   └── legal-guidelines.md
└── out/
    ├── expected.dsl
    ├── expected-validation.json
    ├── expected-questions.json
    ├── expected-document.md
    └── expected-audit.json
```

- [ ] Utworzyć wspólny format `scenario.json`.
- [ ] Utworzyć runner pojedynczego przykładu.
- [ ] Utworzyć runner wszystkich przykładów.
- [ ] Runtime ma pobierać dane wyłącznie z `in/`.
- [ ] Wygenerowane rezultaty zapisywać do katalogu tymczasowego.
- [ ] Porównywać rezultaty z `out/`.
- [ ] Uruchamiać Python verifier dla każdego scenariusza.
- [ ] Zwracać czytelny raport różnic.
- [ ] Umożliwić ponowne uruchomienie po zmianie danych wejściowych.
- [x] Umożliwić uruchomienie bez internetu.

### Scenariusze MVP

- [ ] `01-chat-to-dsl`
  - pojedyncza wypowiedź użytkownika,
  - formalizacja intencji,
  - brak dokumentu prawnego.

- [ ] `02-ambiguous-chat`
  - polecenie nieprecyzyjne,
  - wygenerowanie pytań,
  - brak zgadywania przez LLM.

- [ ] `03-two-party-conversation-to-contract`
  - historia rozmowy Human1 i Human2,
  - wykrycie uzgodnień,
  - wykrycie braków,
  - wygenerowanie projektu kontraktu.

- [ ] `04-conflicting-contract-terms`
  - strony podają sprzeczne kwoty albo terminy,
  - runtime blokuje renderowanie końcowej umowy.

- [ ] `05-service-contract`
  - rozmowa dotycząca wykonania strony internetowej,
  - zakres, cena, termin, kryteria odbioru,
  - umowa-zlecenie lub kontrakt usługowy.

- [ ] `06-employment-guidelines-to-contract`
  - plik tekstowy z wytycznymi,
  - DSL,
  - wykrycie braków,
  - mockowa umowa o pracę.

- [ ] `07-task-delegation`
  - użytkownik zleca zadanie drugiej osobie,
  - wykonawca, termin, rezultat, kryteria odbioru.

- [ ] `08-task-insufficient-for-recipient`
  - zleceniodawca akceptuje DSL,
  - odbiorca nadal nie ma wystarczających danych,
  - system generuje pytania do zleceniodawcy.

- [ ] `09-both-parties-approval`
  - obie strony muszą zatwierdzić ten sam hash DSL.

- [ ] `10-plan-changed-after-approval`
  - zmiana DSL unieważnia wcześniejsze akceptacje.

- [ ] `11-polish-language-and-diacritics`
  - polskie znaki,
  - odmiana nazwisk,
  - daty i kwoty w języku polskim,
  - brak utraty znaczenia.

- [ ] `12-informal-user-language`
  - potoczna, niepełna wypowiedź,
  - runtime diagnozuje brakujące elementy.

- [ ] `13-added-terms-by-llm`
  - LLM dodaje nieuzgodniony warunek,
  - Python verifier wykrywa problem.

- [ ] `14-source-traceability`
  - każde pole DSL ma wskazane źródło w rozmowie.

- [ ] `15-render-dsl-back-to-nl`
  - DSL renderowany do czytelnego opisu,
  - ponowne parsowanie nie zmienia znaczenia.

---

## Etap 7 — backend i frontend demonstracyjny

Status: backend and static frontend cover single input, DSL, plan, answer, confirmation, dry-run, and audit; upload, conversation history, source display, and final document remain open.


- [x] Utworzyć backend API korzystający z tego samego runtime’u co CLI.
- [x] Utworzyć frontend do wprowadzenia pojedynczej wypowiedzi.
- [ ] Dodać możliwość wklejenia historii rozmowy.
- [ ] Dodać możliwość przesłania pliku z wytycznymi.
- [x] Wyświetlać wygenerowany DSL.
- [ ] Wyświetlać źródła poszczególnych ustaleń.
- [ ] Wyświetlać braki, sprzeczności i założenia.
- [x] Obsłużyć odpowiedzi Human1 i Human2.
- [ ] Obsłużyć akceptację obu stron.
- [ ] Wyświetlać dokument końcowy.
- [x] Wyświetlać audyt.

---

## Etap 8 — testy

Status: Vitest and Python verifier tests pass for the current scope; full contract, language-quality, and example diff-runner tests remain open.


### Testy jednostkowe

- [x] Parser.
- [x] JSON Schema.
- [x] AST.
- [ ] Walidator semantyczny.
- [ ] Diagnostyka braków.
- [ ] Diagnostyka sprzeczności.
- [x] State machine.
- [x] Akceptacje i hashowanie.
- [x] Renderer DSL → NL.
- [x] Audyt.

### Testy integracyjne

- [x] NL → mock LLM → DSL.
- [ ] Conversation → mock LLM → DSL.
- [ ] Text guidelines → DSL.
- [ ] DSL → Python verifier.
- [x] DSL → pytania.
- [x] Odpowiedzi → aktualizacja DSL.
- [x] Akceptacja Human1.
- [ ] Akceptacja Human2.
- [ ] DSL → dokument końcowy.
- [x] Wynik → audyt.

### Testy regresyjne `examples`

- [ ] Uruchomić każdy folder `examples/*`.
- [ ] Porównać wygenerowany DSL z oczekiwanym rezultatem.
- [ ] Porównać listę braków i pytań.
- [ ] Porównać końcowy dokument.
- [ ] Porównać audyt.
- [ ] Wyświetlić różnice po zmianie danych wejściowych.

### Testy jakości języka

- [ ] Polskie znaki.
- [ ] Polskie daty i kwoty.
- [ ] Literówki.
- [ ] Język potoczny.
- [ ] Bardzo precyzyjne polecenia.
- [ ] Niepełne polecenia.
- [ ] Sprzeczne wypowiedzi stron.
- [ ] Różne style komunikacji z AI.

### Testy bezpieczeństwa i poprawności

- [x] Brak wykonania bez akceptacji.
- [ ] Brak dokumentu końcowego przy nierozwiązanych sprzecznościach.
- [ ] Brak automatycznego zgadywania danych.
- [ ] Wykrycie warunków dodanych przez LLM.
- [x] Unieważnienie akceptacji po zmianie DSL.
- [x] Odporność na prompt injection w rozmowie i danych.
- [x] Brak `eval` i wykonywania kodu generowanego przez LLM.
- [x] Brak prawdziwych operacji zewnętrznych w trybie mock.

---

## Etap 9 — komendy uruchomieniowe

Status: root commands `typecheck`, `test`, `test:e2e`, and `cli` exist; dedicated `example:run`, `examples:run`, `verify`, and Python test scripts remain open.


- [ ] Dodać komendę uruchamiającą pojedynczy przykład:

```bash
pnpm example:run 03-two-party-conversation-to-contract
```

- [ ] Dodać komendę uruchamiającą wszystkie przykłady:

```bash
pnpm examples:run
```

- [ ] Dodać komendę pełnej walidacji:

```bash
pnpm verify
```

- [x] Dodać komendę testów TypeScript.
- [ ] Dodać komendę testów Python.
- [x] Dodać pełny test E2E.
- [ ] Wszystkie domyślne komendy mają działać offline.

---

## Etap 10 — CI i dokumentacja

Status: main docs are updated; CI and separate spec/security/testing/install docs remain open.


- [ ] Dodać CI dla Windows.
- [ ] Dodać CI dla Linux.
- [ ] Dodać lint.
- [x] Dodać typecheck.
- [x] Dodać testy TypeScript.
- [x] Dodać testy Python.
- [ ] Dodać testy wszystkich przykładów.
- [ ] Dodać build backendu i frontendu.
- [x] Zaktualizować `README.md`.
- [x] Utworzyć `docs/architecture.md`.
- [ ] Utworzyć `docs/dsl-specification.md`.
- [ ] Utworzyć `docs/contract-workflow.md`.
- [ ] Utworzyć `docs/example-format.md`.
- [ ] Utworzyć `docs/security-model.md`.
- [ ] Utworzyć `docs/testing.md`.
- [ ] Utworzyć dokumentację Windows i Linux.
- [ ] Opisać konfigurację OpenRouter i LiteLLM.

---

## Etap 11 — zakończenie

Status: local validation for `0.1.0` is done; clean git status is pending the final commit and push.


- [ ] Uruchomić wszystkie przykłady.
- [x] Uruchomić pełny typecheck.
- [x] Uruchomić pełne testy TypeScript.
- [x] Uruchomić pełne testy Python.
- [x] Uruchomić pełne testy E2E.
- [ ] Sprawdzić brak zawieszonych procesów.
- [x] Sprawdzić zgodność dokumentacji z kodem.
- [x] Zaktualizować wszystkie pozycje w `TODO.md`.
- [x] Utworzyć `VERSION.md`.
- [x] Ustawić wersję MVP `0.1.0`.
- [x] Utworzyć lub zaktualizować `CHANGELOG.md`.
- [x] Wykonać końcowy audyt repozytorium.
- [ ] Potwierdzić czysty `git status`.

---

## Kryteria ukończenia MVP

Status: narrow Office DSL MVP criteria are met; full Intent/Contract criteria remain open.

MVP uznajemy za poprawnie wykonane, jeżeli:

- [x] Pojedyncza wypowiedź może zostać zamieniona na DSL.
- [ ] Historia rozmowy dwóch stron może zostać zamieniona na DSL.
- [ ] Plik z wytycznymi może zostać zamieniony na DSL.
- [ ] System wykrywa braki, sprzeczności i niejednoznaczności.
- [ ] System nie zgaduje brakujących danych.
- [ ] Python verifier wykrywa pominięcia i elementy dodane przez LLM.
- [x] Human1 może zaakceptować lub odrzucić DSL.
- [ ] Human2 może ocenić, czy DSL wystarcza do wykonania zadania.
- [ ] Kontrakt wymagający dwóch stron nie jest finalizowany bez obu akceptacji.
- [x] Runtime może wyrenderować DSL do czytelnego dokumentu.
- [ ] Dokument końcowy zachowuje znaczenie zaakceptowanego DSL.
- [ ] Każdy scenariusz w `examples/` można uruchomić ponownie.
- [ ] Zmiana wejścia powoduje ponowną walidację i czytelny raport różnic.
- [ ] Wszystkie testy domyślne działają offline.
- [ ] Testy przechodzą na Windows i Linux.
- [x] Wynik oraz audyt są czytelne dla człowieka i agenta AI.
