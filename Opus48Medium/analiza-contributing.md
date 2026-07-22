# Analiza dokumentacji pod kątem czytelności dla agentów AI

**Zakres zlecenia (od szefa):**
1. Sprawdzić, czy aktualny plik w `docs/` oddaje logikę działania, czego brakuje i czy czegoś nie zapomniano.
2. Przeanalizować pracę i zasady, którymi się kierowano, na podstawie historii commitów Git, i zapisać to w formie notatki.
3. Ocenić, czy `CONTRIBUTING.md` jest zrozumiały dla agentów AI.

**Analizowane pliki:** `CONTRIBUTING.md`, `README.md`, `POLICY.md`, `project.sh`, `docs/`, `.devin/workflows/analyze-documentation.md`

---

## 1. Odpowiedź wprost: czy CONTRIBUTING.md jest zrozumiały dla agentów AI?

**Częściowo.** Dokument jest dobrze ustrukturyzowany i czytelny w izolacji, ale zawiera odwołania do zasobów, których agent nie jest w stanie zweryfikować ani uruchomić. W obecnej postaci agent zrozumie *intencję*, ale nie będzie mógł wykonać części instrukcji dosłownie (np. „deleguj do test-agent”), bo brak jest ich definicji lub sposobu wywołania.

Ocena: **dobra forma, niespójna z rzeczywistością repozytorium.**

---

## 2. Czy `docs/` oddaje logikę działania?

**Katalog `docs/` jest PUSTY.** To najważniejsze ustalenie.

Z historii Git wynika, że kompleksowy standard (dokument w języku polskim) wędrował:

- commit `0ae1938 adds CONTRIBUTING` — standard powstał w `CONTRIBUTING.md` (561 linii),
- commit `7a37b2e Update` — standard przeniesiony do `docs/README.md`, `CONTRIBUTING.md` mocno okrojony, dodano `project.sh`,
- commit `f55fc06 update` (HEAD) — `docs/README.md` przeniesiony do głównego `README.md`, dodano `POLICY.md` i workflow.

Efekt: **`docs/` zostało puste, a odwołania do `docs/README.md` są nieaktualne (martwe).**

Odwołania do nieistniejącego `docs/README.md`:
- `POLICY.md` (sekcja „Questions?”) wskazuje na `docs/README.md`.
- `.devin/workflows/analyze-documentation.md` (kroki 2, 4, 6) instruuje agenta, aby czytał i edytował `docs/README.md`.

Agent wykonujący workflow trafi na plik, którego nie ma — to wprost złamie „logikę działania”, o którą pyta szef.

---

## 3. Główne rozbieżności (czego brakuje / o czym zapomniano)

### 3.1. Niekompletna lista narzędzi względem `project.sh`

`project.sh` instaluje/uruchamia: **regix, prefact, vallm, redup, glon, code2logic, code2llm, doql, sumd, sumr, goal**.

`CONTRIBUTING.md` oraz `README.md §5` opisują tylko: code2llm, redup, prefact, vallm, doql, sumd, sumr, goal.

**Brakuje opisu: `regix`, `glon`, `code2logic`** — są w skrypcie, ale nieudokumentowane. Zgodnie z zasadą z workflow („każde narzędzie użyte w automatyzacji powinno być udokumentowane”) to luka.

### 3.2. Agenci bez potwierdzonego istnienia

`CONTRIBUTING.md` i `README.md §6` opisują agentów: `test-agent`, `repair-agent`, `validator-agent`, `todo-agent`, `doctor-agent` (repo `github.com/subactor/subactor/...`).

W repozytorium **nie ma żadnej definicji, konfiguracji ani sposobu wywołania tych agentów.** Ironicznie sam `README.md §6` ostrzega: „Nie należy ustalać działania agenta wyłącznie na podstawie jego nazwy” oraz „opis powinien bazować na dokumentacji/kodzie agenta” — a mimo to opisy wyglądają na wygenerowane z samych nazw. Dla agenta AI to instrukcje niewykonalne: nie da się „delegować do test-agent”, jeśli nie wiadomo, jak go uruchomić.

### 3.3. Konflikt/niejasna hierarchia dokumentów

- `README.md` (główny) nosi tytuł `# CONTRIBUTING.md`, choć jest to plik README — mylące.
- `CONTRIBUTING.md` mówi: „Read README.md for project overview”, ale `README.md` to w rzeczywistości pełny standard pracy (po polsku), a nie przegląd projektu.
- Powstają odwołania w pętli: `POLICY.md` → `CONTRIBUTING.md` i `docs/README.md`; `CONTRIBUTING.md` → `README.md`; brak jednego jasnego „single source of truth”.

Zasada z workflow mówi wprost: kompleksowa dokumentacja w `docs/`, pliki w root mają tylko *odsyłać*. Obecny stan jest odwrotny.

### 3.4. Niespójność językowa

`CONTRIBUTING.md` i `POLICY.md` są po angielsku; główny standard (`README.md`) po polsku. Dla agenta AI to wykonalne, ale utrudnia spójność i utrzymanie.

### 3.5. Brak konkretnych komend w CONTRIBUTING.md

`CONTRIBUTING.md` wymienia narzędzia z nazwy, ale nie podaje sposobu uruchomienia ani nie odsyła do `README.md §5`, gdzie są komendy `$VENV/bin/...`. Agent musi sam odgadnąć powiązanie.

---

## 4. Rekomendacje (uszeregowane)

1. **Zrealizowane:** przywrócono `docs/README.md` jako indeks i zaktualizowano workflow, aby nie wskazywał nieistniejącego wcześniej pliku.
2. **Zrealizowane częściowo:** ustalono źródła prawdy, utworzono operacyjny `CONTRIBUTING.md` i poprawiono nagłówek `README.md`; pełne rozdzielenie ogólnego standardu od opisu projektu pozostaje osobnym zadaniem.
3. **Częściowo zrealizowane:** `Opus48Medium/CONTRIBUTING.md` oznacza `regix`, `glon` i `code2logic` jako instalowane, ale nieuruchamiane; nadal brakuje potwierdzonej dokumentacji ich działania.
4. **Otwarte:** zweryfikować zewnętrznych agentów `subactor` albo utrzymywać ich jako niepotwierdzonych i korzystać z fallbacku.
5. **Zrealizowane:** lokalny `CONTRIBUTING.md` zawiera konkretne komendy i rozróżnia aktywne oraz zakomentowane polecenia.
6. **Zrealizowane częściowo:** instrukcja w `Opus48Medium` jest po polsku; całe repozytorium nadal zawiera dokumenty anglojęzyczne.
7. **Zrealizowane:** workflow `analyze-documentation.md` wskazuje aktualny układ `GPT56Luna` + `docs/README.md`.

> Status po analizie: utworzono `Opus48Medium/CONTRIBUTING.md` jako lokalną, operacyjną instrukcję dla agentów AI. Pozostałe rekomendacje dotyczące zmian w skrypcie, weryfikacji zewnętrznych agentów i dalszego porządkowania dokumentacji pozostają osobnymi zadaniami.

---

## 5. Refleksja na bazie historii Git (punkt 2 od szefa)

Historia commitów pokazuje ewolucję i zastosowane zasady:

| Commit | Działanie | Zasada / wniosek |
|--------|-----------|------------------|
| `b302616 Initial commit` | tylko `LICENSE` | start repozytorium |
| `0ae1938 adds CONTRIBUTING` | pełny standard (PL) w `CONTRIBUTING.md` | najpierw spisano standard pracy |
| `7a37b2e Update` | standard → `docs/README.md`; `CONTRIBUTING.md` okrojony; dodano `project.sh` | próba wdrożenia zasady „root odsyła, docs = źródło” + automatyzacja narzędzi |
| `f55fc06 update` (HEAD) | `docs/README.md` → `README.md`; dodano `POLICY.md`, nowy `CONTRIBUTING.md`, workflow | rozdzielenie zasad (POLICY) od standardu; **efekt uboczny: puste `docs/` i martwe odwołania** |

**Zaobserwowane zasady pracy:**
- Dokumentacja przed implementacją (standard powstał jako pierwszy).
- Dążenie do „single source of truth” i delegacji do wyspecjalizowanych narzędzi/agentów.
- Automatyzacja przez `project.sh` (venv + łańcuch narzędzi analizy kodu).
- Format opisu narzędzi/agentów: Przeznaczenie / Użyj do / Sposób uruchomienia / Wynik / Ograniczenia.

**Główna lekcja:** przy przenoszeniu plików nie zaktualizowano odwołań — dlatego dokumentacja rozjechała się z rzeczywistą strukturą. Przyszłe przenoszenie plików powinno obejmować aktualizację wszystkich odwołań (wyszukanie nazwy pliku przed commitem). Utworzony `CONTRIBUTING.md` stosuje tę zasadę: wskazuje źródła prawdy, opisuje aktywne i zakomentowane polecenia oraz zawiera fallback dla niedostępnych agentów specjalistycznych.
