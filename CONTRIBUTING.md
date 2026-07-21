# CONTRIBUTING.md

## 1. Cel dokumentu

Ten dokument określa wspólny standard tworzenia i rozwijania projektów przez ludzi oraz agentów AI.

Dokument jest przeznaczony do użycia w każdym nowym projekcie.

Nie opisuje szczegółowej technologii konkretnego repozytorium. Określa natomiast:

* obowiązkowy przebieg pracy,
* sposób planowania zadań,
* sposób wykorzystywania dostępnych agentów i narzędzi,
* minimalne wymagania dotyczące struktury projektu,
* minimalne wymagania dotyczące testów,
* wymagania dotyczące konteneryzacji,
* zasady wersjonowania,
* zasady prowadzenia changelogu,
* zasady tworzenia commitów i publikowania zmian.

Szczegóły konkretnego projektu powinny znajdować się w jego dokumentacji, konfiguracji i skryptach.

---

## 2. Zasada nadrzędna

Przed tworzeniem własnego rozwiązania agent MUSI sprawdzić, czy dane zadanie może zostać wykonane przez:

1. istniejącego agenta,
2. istniejące narzędzie,
3. istniejący skrypt,
4. istniejący workflow,
5. istniejący komponent dostępny w organizacji.

Agent NIE POWINIEN odtwarzać funkcjonalności, która już istnieje.

Główny agent powinien koordynować pracę i delegować zadania do właściwych narzędzi oraz agentów.

---

## 3. Rozpoczęcie pracy

Przed rozpoczęciem implementacji agent MUSI:

1. przeczytać `CONTRIBUTING.md`,
2. przeczytać dokumentację projektu,
3. sprawdzić strukturę repozytorium,
4. sprawdzić bieżący stan Git,
5. sprawdzić dostępne narzędzia i agentów,
6. sprawdzić istniejące testy i automatyzacje,
7. utworzyć albo zaktualizować `TODO.md`,
8. podzielić zadanie na mniejsze etapy,
9. przypisać etapy do odpowiednich agentów lub narzędzi,
10. dopiero wtedy rozpocząć pracę.

Agent NIE MOŻE rozpoczynać większej implementacji bez planu zapisanego w `TODO.md`.

---

## 4. TODO.md

### 4.1. Przeznaczenie

`TODO.md` jest dynamiczną kolejką pracy.

Zawiera:

* aktualne zadanie,
* kolejne zadania,
* etapy realizacji,
* kryteria akceptacji,
* wykryte problemy,
* blokady,
* zadania dopisane podczas działania agentów.

`TODO.md` odpowiada na pytanie:

> Co należy wykonać jako następne?

`CONTRIBUTING.md` odpowiada na pytanie:

> W jaki sposób należy wykonywać pracę?

### 4.2. Ciągła pętla pracy

Podczas wykonywania zadania można dopisywać nowe pozycje do `TODO.md`.

Agent powinien:

1. zakończyć aktualny bezpieczny etap,
2. ponownie odczytać `TODO.md`,
3. uwzględnić nowe zadania,
4. kontynuować pracę bez przerywania całej pętli,
5. przechodzić do kolejnych zadań, dopóki są one wykonalne.

Agent może zatrzymać pracę tylko wtedy, gdy:

* nie ma więcej zadań,
* wszystkie zadania są zablokowane,
* wymagana jest decyzja człowieka,
* potrzebne są niedostępne dane dostępowe,
* dalsza operacja jest ryzykowna,
* wymagania są sprzeczne.

### 4.3. Przykładowy format

```markdown
# TODO

## TASK-001 — Nazwa zadania

- **Status:** IN_PROGRESS
- **Priorytet:** P1
- **Źródło:** użytkownik
- **Kryteria akceptacji:**
  - wymaganie 1,
  - wymaganie 2.

### Etapy

- [x] Analiza projektu
- [x] Wybór odpowiednich narzędzi
- [ ] Implementacja
- [ ] Testy wykonane przez narzędzia testujące
- [ ] Walidacja
- [ ] Dokumentacja
- [ ] Wersja i changelog
- [ ] Commit i push

### Nowe zadania wykryte podczas pracy

- [ ] TASK-002 — ...
```

---

## 5. Dostępne narzędzia

W tej sekcji należy opisać narzędzia dostępne dla agentów.

Opis każdego narzędzia powinien zawierać:

* nazwę,
* przeznaczenie,
* rodzaje obsługiwanych zadań,
* sposób uruchomienia,
* dane wejściowe,
* wynik działania,
* ograniczenia,
* sytuacje, w których należy go użyć.

Nie należy wpisywać informacji, które nie zostały potwierdzone w dokumentacji narzędzia.

### Format opisu

```markdown
### Nazwa narzędzia

**Przeznaczenie:**

Opis potwierdzonego działania.

**Użyj do:**

- zadanie 1,
- zadanie 2.

**Nie używaj do:**

- zadanie 1,
- zadanie 2.

**Sposób uruchomienia:**

Opis albo odwołanie do dokumentacji.

**Wynik działania:**

Opis spodziewanego rezultatu.

**Ograniczenia:**

- ograniczenie 1,
- ograniczenie 2.
```

---

## 6. Dostępni agenci

Każdy dostępny agent powinien mieć opisany rzeczywisty zakres odpowiedzialności.

Opis powinien bazować na:

* dokumentacji agenta,
* kodzie agenta,
* faktycznie obsługiwanych wejściach,
* faktycznie generowanych wynikach.

Nie należy ustalać działania agenta wyłącznie na podstawie jego nazwy.

### Format opisu

```markdown
### Nazwa agenta

**Repozytorium:**

Adres lub nazwa repozytorium.

**Odpowiedzialność:**

Potwierdzony zakres działania.

**Użyj, gdy:**

- sytuacja 1,
- sytuacja 2.

**Dane wejściowe:**

Opis wymaganych danych.

**Wynik:**

Opis generowanego rezultatu.

**Ograniczenia:**

- ograniczenie 1,
- ograniczenie 2.
```

---

## 7. Standard tworzenia nowego projektu

Każdy nowy projekt powinien posiadać co najmniej:

* czytelny `README.md`,
* `CONTRIBUTING.md`,
* `TODO.md` podczas pracy agentów,
* mechanizm wersjonowania,
* `CHANGELOG.md`,
* konfigurację środowiska bez sekretów,
* testy,
* automatyczny sposób uruchomienia testów,
* konfigurację CI,
* środowisko Docker, jeżeli projekt może zostać uruchomiony w kontenerze,
* instrukcję uruchomienia,
* instrukcję rozwoju projektu,
* jasny podział katalogów.

Agent powinien dobrać konkretne technologie do rodzaju projektu.

Dokument nie narzuca:

* języka programowania,
* frameworka,
* systemu testowego,
* obrazu bazowego Docker,
* menedżera pakietów,
* konkretnego dostawcy CI.

---

## 8. Docker

Jeżeli charakter projektu pozwala na konteneryzację, agent MUSI przygotować środowisko Docker.

Celem środowiska Docker jest:

* uruchomienie projektu bez ręcznej konfiguracji hosta,
* odtworzenie wymaganych zależności,
* zapewnienie powtarzalnego środowiska,
* umożliwienie automatycznego testowania,
* sprawdzenie instalacji projektu od zera,
* uproszczenie pracy ludzi i agentów.

Środowisko Docker powinno:

* budować się automatycznie,
* uruchamiać projekt,
* uruchamiać wymagane zależności,
* umożliwiać wykonanie testów,
* nie zawierać sekretów,
* używać kontrolowanych wersji zależności,
* posiadać mechanizm sprawdzania gotowości aplikacji, gdy ma to zastosowanie,
* umożliwiać wyczyszczenie środowiska po testach.

Agent powinien przygotować odpowiednie pliki, przykładowo:

* `Dockerfile`,
* `.dockerignore`,
* `compose.yaml` lub odpowiednik,
* skrypt uruchomienia,
* skrypt testowy.

Dobór dokładnej struktury zależy od konkretnego projektu.

Nie należy tworzyć Dockera wyłącznie dla samego faktu jego posiadania, jeżeli projekt nie może lub nie powinien działać w kontenerze. Taka decyzja musi zostać uzasadniona w dokumentacji projektu.

---

## 9. Testowanie

### 9.1. Zasada delegowania

Testy powinny być tworzone, uruchamiane i sprawdzane przede wszystkim przez dostępne narzędzia oraz agentów testujących.

Główny agent powinien:

1. określić wymagane scenariusze testowe,
2. przekazać zadanie odpowiedniemu agentowi lub narzędziu,
3. odebrać wynik testów,
4. sprawdzić raport,
5. przekazać wykryte problemy do odpowiedniego narzędzia naprawczego,
6. ponownie uruchomić testy po poprawkach.

Główny agent NIE POWINIEN ręcznie tworzyć pełnego zestawu testów, jeżeli dostępny agent testujący może wykonać to zadanie.

### 9.2. Kiedy główny agent może zmieniać testy

Główny agent może samodzielnie utworzyć albo zmienić testy, gdy:

* nie istnieje odpowiednie narzędzie testujące,
* narzędzie testujące nie obsługuje danego przypadku,
* wygenerowany test jest niepoprawny,
* test nie działa z powodu zmienionego interfejsu,
* test nie odzwierciedla rzeczywistego wymagania,
* naprawiany błąd wymaga natychmiastowego testu regresyjnego,
* automatyczny agent testujący zakończył pracę błędem,
* konieczna jest ręczna naprawa infrastruktury testowej.

Przed ręczną zmianą testów agent powinien zapisać przyczynę w `TODO.md`.

### 9.3. Minimalne wymagania

Projekt powinien posiadać odpowiednie do swojego charakteru:

* testy jednostkowe,
* testy integracyjne,
* testy regresyjne,
* testy uruchomienia,
* testy instalacji,
* testy API lub kontraktowe,
* testy Docker,
* testy end-to-end,
* testy wieloplatformowe.

Nie każdy projekt wymaga wszystkich rodzajów testów. Agent testujący powinien ustalić właściwy zakres.

### 9.4. Zakazane działania

Agent NIE MOŻE:

* usuwać testów tylko dlatego, że nie przechodzą,
* wyłączać testów bez udokumentowanej przyczyny,
* zmieniać oczekiwanego rezultatu testu wyłącznie w celu uzyskania pozytywnego wyniku,
* przedstawiać pominiętego testu jako zaliczonego,
* deklarować wykonania testów, które nie zostały uruchomione,
* ukrywać błędów infrastruktury testowej.

---

## 10. Walidacja i naprawa

Po implementacji projekt powinien przejść przez osobne etapy:

1. testowanie,
2. walidację zgodności z wymaganiami,
3. wykrywanie problemów,
4. naprawę,
5. ponowne testowanie,
6. końcową walidację.

Jeżeli dostępni są wyspecjalizowani agenci, każdy etap powinien zostać przekazany właściwemu agentowi.

Przykładowy przepływ:

```text
Główny agent
→ agent testujący
→ agent walidujący
→ agent naprawczy
→ agent testujący
→ końcowa walidacja
```

Dokładny podział odpowiedzialności musi wynikać z rzeczywistej dokumentacji agentów.

---

## 11. Dokumentacja

Dokumentacja musi być aktualizowana razem z kodem.

Po zmianie agent powinien sprawdzić:

* czy sposób instalacji jest aktualny,
* czy sposób uruchomienia jest aktualny,
* czy konfiguracja jest opisana,
* czy nowe funkcje są opisane,
* czy ograniczenia są opisane,
* czy przykłady nadal działają,
* czy dokumentacja nie odwołuje się do usuniętych elementów.

Dokumentacja nie może deklarować funkcji ani platform, które nie zostały sprawdzone.

---

## 12. Commity i push

Agent powinien wykonywać małe, logiczne commity po zakończeniu spójnego etapu.

Nie należy wykonywać jednego ogromnego commita po zakończeniu całego projektu.

Zalecany format:

```text
<type>(<scope>): <krótki opis>
```

Przykładowe typy:

* `feat`
* `fix`
* `test`
* `docs`
* `refactor`
* `build`
* `ci`
* `chore`
* `security`

Przed commitem agent MUSI:

1. sprawdzić zmienione pliki,
2. sprawdzić diff,
3. sprawdzić przypadkowe zmiany,
4. sprawdzić sekrety,
5. wykonać odpowiednie testy,
6. zaktualizować `TODO.md`.

Push powinien zostać wykonany po poprawnym commicie i wymaganej walidacji.

Agent NIE MOŻE wykonywać force push ani operacji usuwających historię bez wyraźnej zgody.

---

## 13. Wersjonowanie

Każdy projekt powinien mieć jednoznacznie określoną wersję.

Zalecanym standardem jest Semantic Versioning:

```text
MAJOR.MINOR.PATCH
```

* `PATCH` — kompatybilne poprawki,
* `MINOR` — nowe kompatybilne funkcje,
* `MAJOR` — zmiany niekompatybilne.

Dokładne miejsce przechowywania wersji zależy od technologii projektu.

Może to być przykładowo:

* `VERSION`,
* `pyproject.toml`,
* `package.json`,
* plik projektu,
* manifest aplikacji.

Wersja musi być spójna we wszystkich wymaganych miejscach.

---

## 14. CHANGELOG.md

Po zakończeniu publikowalnego zakresu agent MUSI zaktualizować `CHANGELOG.md`.

Changelog powinien zawierać informacje istotne dla:

* użytkownika,
* programisty,
* osoby wdrażającej projekt,
* kolejnego agenta.

Powinien opisywać:

* nowe funkcje,
* zmienione zachowanie,
* naprawione błędy,
* usunięte elementy,
* zmiany bezpieczeństwa,
* zmiany niekompatybilne,
* wymagane migracje.

Changelog nie powinien być kopią historii commitów.

---

## 15. Zakończenie pracy

Po zakończeniu pełnego zakresu agent MUSI:

1. upewnić się, że wszystkie zadania zostały wykonane albo opisane jako zablokowane,
2. odebrać wyniki od agentów testujących,
3. upewnić się, że testy przechodzą,
4. wykonać walidację,
5. naprawić wykryte problemy,
6. ponownie wykonać testy,
7. zaktualizować dokumentację,
8. zaktualizować `CHANGELOG.md`,
9. zaktualizować wersję,
10. wykonać logiczne commity,
11. wykonać push,
12. zaktualizować `TODO.md`,
13. przejść do kolejnego zadania, jeżeli istnieje.

---

## 16. Definition of Done

Praca jest zakończona, gdy:

* [ ] wymagania zostały spełnione,
* [ ] zadania w `TODO.md` są aktualne,
* [ ] użyto właściwych agentów i narzędzi,
* [ ] testy zostały wykonane przez właściwe narzędzia,
* [ ] wyniki testów zostały sprawdzone,
* [ ] wykryte problemy zostały naprawione,
* [ ] testy zostały ponownie uruchomione,
* [ ] walidacja zakończyła się powodzeniem,
* [ ] Docker działa, jeżeli jest wymagany,
* [ ] dokumentacja jest aktualna,
* [ ] changelog został zaktualizowany,
* [ ] wersja została zaktualizowana,
* [ ] utworzono logiczne commity,
* [ ] wykonano push,
* [ ] nie dodano sekretów,
* [ ] nie pozostawiono nieopisanych blokad.

---

## 17. Self-improvement

Po zakończeniu większego zakresu agent powinien sprawdzić:

* czy istniejące narzędzia były wystarczające,
* czy któryś etap wymagał zbędnej pracy ręcznej,
* czy brakuje nowego agenta lub skryptu,
* czy standard testów wymaga rozszerzenia,
* czy dokumentacja narzędzi jest kompletna,
* czy przepływ między agentami jest poprawny,
* czy można skrócić pracę kolejnych agentów.

Propozycje poprawy powinny zostać dopisane do `TODO.md`.

Zmiany standardu powinny być wprowadzane jako osobne, udokumentowane zadania.
