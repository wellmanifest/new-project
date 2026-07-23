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
- [ ] Doprowadzić repozytorium do kontrolowanego stanu bez przypadkowych usunięć.
- [ ] Naprawić konfigurację pnpm i instalację zależności.

---

## Etap 1 — przypadki użycia i wymagania

- [ ] Zdefiniować zakres MVP.
- [ ] Zdefiniować aktorów:
  - Human1 — autor intencji lub zleceniodawca,
  - Human2 — odbiorca, wykonawca albo druga strona umowy,
  - LLM — formalizacja i interpretacja,
  - Python verifier — walidacja znaczeniowa,
  - TypeScript runtime — walidacja techniczna, orkiestracja i renderowanie.
- [ ] Zdefiniować przepływ dla pojedynczego polecenia użytkownika.
- [ ] Zdefiniować przepływ dla rozmowy dwóch stron.
- [ ] Zdefiniować przepływ dla wytycznych zapisanych w pliku tekstowym.
- [ ] Zdefiniować proces akceptacji przez jedną stronę.
- [ ] Zdefiniować proces akceptacji przez obie strony kontraktu.
- [ ] Zdefiniować proces odrzucenia i ponownej edycji.
- [ ] Zdefiniować proces zadawania pytań doprecyzowujących.
- [ ] Zdefiniować, kiedy dokument jest wystarczająco kompletny dla jego odbiorcy.
- [ ] Zdefiniować kryteria końcowego odbioru MVP.

---

## Etap 2 — specyfikacja Intent/Contract DSL

- [ ] Zdefiniować kanoniczny model DSL.
- [ ] Zdefiniować wersję języka.
- [ ] Zdefiniować AST.
- [ ] Zdefiniować JSON Schema.
- [ ] Przygotować czytelną reprezentację DSL dla człowieka.
- [ ] Zdefiniować konwersję JSON/AST → human-readable DSL.
- [ ] Zdefiniować konwersję DSL → dokument w języku naturalnym.

### Konstrukcje DSL

- [ ] `CONTRACT`
- [ ] `TASK`
- [ ] `PARTY`
- [ ] `ROLE`
- [ ] `INTENT`
- [ ] `SOURCE`
- [ ] `SUBJECT`
- [ ] `OBLIGATION`
- [ ] `DELIVERABLE`
- [ ] `DEADLINE`
- [ ] `PAYMENT`
- [ ] `CONDITION`
- [ ] `ACCEPTANCE_CRITERIA`
- [ ] `EXCLUSION`
- [ ] `ASSUMPTION`
- [ ] `QUESTION`
- [ ] `APPROVAL`
- [ ] `OUTPUT`
- [ ] `RENDER`
- [ ] `POLICY`

### Statusy informacji

- [ ] `KNOWN`
- [ ] `CONFIRMED`
- [ ] `MISSING`
- [ ] `INCOMPLETE`
- [ ] `AMBIGUOUS`
- [ ] `CONFLICTING`
- [ ] `ASSUMED`
- [ ] `REQUIRES_CONFIRMATION`
- [ ] `REJECTED`

### Diagnostyka DSL

- [ ] Wykrywanie brakujących danych.
- [ ] Wykrywanie niejednoznacznych terminów i wartości.
- [ ] Wykrywanie sprzecznych wypowiedzi stron.
- [ ] Wykrywanie założeń dodanych przez LLM.
- [ ] Wykrywanie elementów niezaakceptowanych przez obie strony.
- [ ] Wykrywanie działań lub warunków, których nikt nie zlecił.
- [ ] Powiązanie każdego ustalenia ze źródłem w rozmowie lub pliku.
- [ ] Generowanie konkretnych pytań dotyczących brakujących pól.

---

## Etap 3 — TypeScript runtime

- [ ] Utworzyć parser DSL.
- [ ] Utworzyć walidator strukturalny.
- [ ] Utworzyć walidator semantyczny.
- [ ] Utworzyć TypeScript runtime.
- [ ] Utworzyć state machine.
- [ ] Utworzyć policy engine.
- [ ] Utworzyć registry obsługiwanych operacji.
- [ ] Utworzyć mechanizm diagnozowania braków.
- [ ] Utworzyć mechanizm pytań do Human1.
- [ ] Utworzyć mechanizm pytań do Human2.
- [ ] Utworzyć proces akceptacji jednej strony.
- [ ] Utworzyć proces akceptacji obu stron.
- [ ] Unieważniać akceptację po zmianie DSL lub planu.
- [ ] Utworzyć hash zaakceptowanej wersji DSL.
- [ ] Utworzyć renderer DSL → dokument NL.
- [ ] Utworzyć mockowy generator umowy.
- [ ] Utworzyć mockowy generator opisu zadania.
- [ ] Utworzyć zapis audytu.
- [ ] Utworzyć CLI dla Windows i Linux.

### Stany runtime’u

- [ ] `CREATED`
- [ ] `ANALYZING_INPUT`
- [ ] `DSL_GENERATED`
- [ ] `VALIDATING`
- [ ] `WAITING_FOR_INPUT_HUMAN1`
- [ ] `WAITING_FOR_INPUT_HUMAN2`
- [ ] `WAITING_FOR_APPROVAL_HUMAN1`
- [ ] `WAITING_FOR_APPROVAL_HUMAN2`
- [ ] `APPROVED`
- [ ] `REJECTED`
- [ ] `RENDERING`
- [ ] `SUCCEEDED`
- [ ] `FAILED`
- [ ] `DENIED`
- [ ] `CANCELLED`

---

## Etap 4 — LLM planner

- [ ] Utworzyć tryb mock działający bez internetu.
- [ ] Utworzyć opcjonalną integrację OpenRouter.
- [ ] Obsłużyć wejście typu pojedyncza wypowiedź.
- [ ] Obsłużyć wejście typu historia rozmowy.
- [ ] Obsłużyć wejście typu plik z wytycznymi.
- [ ] Generować wyłącznie wynik zgodny ze schematem.
- [ ] Oznaczać założenia utworzone przez LLM.
- [ ] Zachowywać źródło każdego ustalenia.
- [ ] Nie uzupełniać braków niepotwierdzonymi informacjami.
- [ ] Generować propozycje pytań doprecyzowujących.
- [ ] Obsłużyć ponowne wygenerowanie DSL po odpowiedzi użytkownika.

---

## Etap 5 — Python verifier

- [ ] Utworzyć pakiet Python 3.11+.
- [ ] Utworzyć tryb mock.
- [ ] Utworzyć opcjonalną integrację LiteLLM/OpenRouter.
- [ ] Walidować zgodność NL → DSL.
- [ ] Walidować zgodność historii rozmowy → DSL.
- [ ] Walidować zgodność wytycznych tekstowych → DSL.
- [ ] Walidować zgodność DSL → dokument końcowy.
- [ ] Sprawdzać pominięte ustalenia.
- [ ] Sprawdzać działania i warunki dodane przez LLM.
- [ ] Sprawdzać sprzeczności.
- [ ] Sprawdzać niepotwierdzone założenia.
- [ ] Sprawdzać kompletność z perspektywy Human1.
- [ ] Sprawdzać kompletność z perspektywy Human2.
- [ ] Sprawdzać, czy odbiorca może jednoznacznie wykonać zadanie.
- [ ] Zwracać wynik `PASS`, `FAIL` albo `NEEDS_REVIEW`.
- [ ] Zwracać raport JSON możliwy do przetwarzania przez runtime.

---

## Etap 6 — struktura `examples`

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
- [ ] Umożliwić uruchomienie bez internetu.

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

- [ ] Utworzyć backend API korzystający z tego samego runtime’u co CLI.
- [ ] Utworzyć frontend do wprowadzenia pojedynczej wypowiedzi.
- [ ] Dodać możliwość wklejenia historii rozmowy.
- [ ] Dodać możliwość przesłania pliku z wytycznymi.
- [ ] Wyświetlać wygenerowany DSL.
- [ ] Wyświetlać źródła poszczególnych ustaleń.
- [ ] Wyświetlać braki, sprzeczności i założenia.
- [ ] Obsłużyć odpowiedzi Human1 i Human2.
- [ ] Obsłużyć akceptację obu stron.
- [ ] Wyświetlać dokument końcowy.
- [ ] Wyświetlać audyt.

---

## Etap 8 — testy

### Testy jednostkowe

- [ ] Parser.
- [ ] JSON Schema.
- [ ] AST.
- [ ] Walidator semantyczny.
- [ ] Diagnostyka braków.
- [ ] Diagnostyka sprzeczności.
- [ ] State machine.
- [ ] Akceptacje i hashowanie.
- [ ] Renderer DSL → NL.
- [ ] Audyt.

### Testy integracyjne

- [ ] NL → mock LLM → DSL.
- [ ] Conversation → mock LLM → DSL.
- [ ] Text guidelines → DSL.
- [ ] DSL → Python verifier.
- [ ] DSL → pytania.
- [ ] Odpowiedzi → aktualizacja DSL.
- [ ] Akceptacja Human1.
- [ ] Akceptacja Human2.
- [ ] DSL → dokument końcowy.
- [ ] Wynik → audyt.

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

- [ ] Brak wykonania bez akceptacji.
- [ ] Brak dokumentu końcowego przy nierozwiązanych sprzecznościach.
- [ ] Brak automatycznego zgadywania danych.
- [ ] Wykrycie warunków dodanych przez LLM.
- [ ] Unieważnienie akceptacji po zmianie DSL.
- [ ] Odporność na prompt injection w rozmowie i danych.
- [ ] Brak `eval` i wykonywania kodu generowanego przez LLM.
- [ ] Brak prawdziwych operacji zewnętrznych w trybie mock.

---

## Etap 9 — komendy uruchomieniowe

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

- [ ] Dodać komendę testów TypeScript.
- [ ] Dodać komendę testów Python.
- [ ] Dodać pełny test E2E.
- [ ] Wszystkie domyślne komendy mają działać offline.

---

## Etap 10 — CI i dokumentacja

- [ ] Dodać CI dla Windows.
- [ ] Dodać CI dla Linux.
- [ ] Dodać lint.
- [ ] Dodać typecheck.
- [ ] Dodać testy TypeScript.
- [ ] Dodać testy Python.
- [ ] Dodać testy wszystkich przykładów.
- [ ] Dodać build backendu i frontendu.
- [ ] Zaktualizować `README.md`.
- [ ] Utworzyć `docs/architecture.md`.
- [ ] Utworzyć `docs/dsl-specification.md`.
- [ ] Utworzyć `docs/contract-workflow.md`.
- [ ] Utworzyć `docs/example-format.md`.
- [ ] Utworzyć `docs/security-model.md`.
- [ ] Utworzyć `docs/testing.md`.
- [ ] Utworzyć dokumentację Windows i Linux.
- [ ] Opisać konfigurację OpenRouter i LiteLLM.

---

## Etap 11 — zakończenie

- [ ] Uruchomić wszystkie przykłady.
- [ ] Uruchomić pełny typecheck.
- [ ] Uruchomić pełne testy TypeScript.
- [ ] Uruchomić pełne testy Python.
- [ ] Uruchomić pełne testy E2E.
- [ ] Sprawdzić brak zawieszonych procesów.
- [ ] Sprawdzić zgodność dokumentacji z kodem.
- [ ] Zaktualizować wszystkie pozycje w `TODO.md`.
- [ ] Utworzyć `VERSION.md`.
- [ ] Ustawić wersję MVP `0.1.0`.
- [ ] Utworzyć lub zaktualizować `CHANGELOG.md`.
- [ ] Wykonać końcowy audyt repozytorium.
- [ ] Potwierdzić czysty `git status`.

---

## Kryteria ukończenia MVP

MVP uznajemy za poprawnie wykonane, jeżeli:

- [ ] Pojedyncza wypowiedź może zostać zamieniona na DSL.
- [ ] Historia rozmowy dwóch stron może zostać zamieniona na DSL.
- [ ] Plik z wytycznymi może zostać zamieniony na DSL.
- [ ] System wykrywa braki, sprzeczności i niejednoznaczności.
- [ ] System nie zgaduje brakujących danych.
- [ ] Python verifier wykrywa pominięcia i elementy dodane przez LLM.
- [ ] Human1 może zaakceptować lub odrzucić DSL.
- [ ] Human2 może ocenić, czy DSL wystarcza do wykonania zadania.
- [ ] Kontrakt wymagający dwóch stron nie jest finalizowany bez obu akceptacji.
- [ ] Runtime może wyrenderować DSL do czytelnego dokumentu.
- [ ] Dokument końcowy zachowuje znaczenie zaakceptowanego DSL.
- [ ] Każdy scenariusz w `examples/` można uruchomić ponownie.
- [ ] Zmiana wejścia powoduje ponowną walidację i czytelny raport różnic.
- [ ] Wszystkie testy domyślne działają offline.
- [ ] Testy przechodzą na Windows i Linux.
- [ ] Wynik oraz audyt są czytelne dla człowieka i agenta AI.
