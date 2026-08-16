# Preprompt & Wytyczne Techniczne (ticket-089)

- **Tytuł Zadania**: Required-checks SSOT: per-repo instance and a gate that runs
- **Utworzono**: 2026-08-16T10:57:06Z

## Wymagania i Ograniczenia Techniczne
- Zaimplementuj wymagania zgodnie z opisaną architekturą projektu.
- Przestrzegaj odizolowanego środowiska Docker. `./project.sh` / `project.bat`
  uruchamia najpierw deterministyczny governance gate, a opcjonalną analizę
  wyłącznie przez obraz przypięty digestem SHA-256.

## Podlinkowane Zasoby i Dokumentacja Specyfikacji
- Dokumentacja Zarządcza Hub: https://github.com/wellmanifest/new-project
- Specyfikacja modułu: {Wpisz odnośnik do dokumentacji technicznej lub pliku}

## Dyrektywy Wykonawcze dla Agenta AI
- Odczytaj niniejsze wytyczne techniczne oraz istniejące, human-owned notatki
  z `user-{github_username}.md`. Nie twórz ani nie modyfikuj ich za człowieka.
- Na tej podstawie zbuduj specyfikację wykonawczą w pliku `ai-claude.md` (rozumienie intencji, zakres prac, koncepcja, Kryteria Odbioru).
- Przed pisaniem kodu zapisz plan w `ai-claude.md`, `TODO.md` i
  `intent.json`. Polecenie zlecające wykonanie lub tryb autonomiczny tworzy
  `SESSION_EXECUTION_AUTHORIZATION`; realizuj zapisany zakres bez ponownego
  pytania o tę samą zgodę (`P-CORE-008`).
- Osobnej władzy wymagają destrukcja, sekrety, nowa koordynacja zewnętrzna
  oraz materialnie nowy cel. Jeżeli zapisany outcome obejmuje publikację,
  autoryzacja sesji pozwala uruchomić zadeklarowany chroniony proces dostawy i
  jego merge po exact-head trusted approval bez ponownego pytania. Sama
  autoryzacja sesji nigdy nie jest approval evidence, a agent nie scala
  bezpośrednio.
- Kod wykonywalny, testy i skrypty badawcze zapisuj poza katalogiem ticketu;
  ticket przechowuje wyłącznie governance, decyzje, logi i dowody.

---

## Defekt

`.governance/required-checks.json` deklaruje sam siebie źródłem prawdy dla
`requiredCheckNames` i nakazuje zewnętrznym konsumentom (validator-agent,
ruleset GitHuba) czytać właśnie ten plik. Zahardkodowanie podzbioru jest w tej
nocie nazwane „defektem governance tej samej klasy co ticket-025".

Plik jest jednak dystrybuowany ze `strategy: "managed"`, czyli przypięty po
SHA-256 jako bajt-w-bajt identyczny u wszystkich adoptujących. Plik z danymi
per-repozytorium nie może być jednocześnie identyczny wszędzie. W efekcie w
każdym z 23 repozytoriów deklaruje `repository: wellmanifest/new-project` i
checki `test | windows-governance`.

Zgodność deklaracji z faktycznie egzekwowanymi rulesetami: **2 z 23**
(`dsl`, `poa` — te akurat używają checków hubu).

## Dlaczego nikt tego nie zauważył

Bramka, która miała tego pilnować, jest martwa u adoptujących.

`governance/package-manifest.json:20` przenosi skrypt przy pakowaniu:

    scripts/check_required_checks.py  ->  .governance/check_required_checks.py

ale nie koryguje zaszytej w nim ścieżki. Skrypt liczy
`repo_root() = Path(__file__).resolve().parents[1]` i szuka
`SOURCE_REL = Path("governance/required-checks.json")` — bez kropki.

* w hubie skrypt leży w `scripts/`, więc `parents[1]` to korzeń repo, a
  `governance/` istnieje → działa;
* u adoptującego skrypt leży w `.governance/`, `parents[1]` to też korzeń repo,
  ale katalogu `governance/` tam nie ma → `FileNotFoundError`.

Do tego `scripts/governance_check.py` nigdy tej bramki nie wywołuje, a managed
workflow adoptującego (`new-project-governance.yml`) też nie. Hub uruchamia ją
wyłącznie z własnego `.github/workflows/ci.yml:48`. Bramka jest więc
dystrybuowana do 23 repozytoriów jako kod, który nigdzie nie jest wykonywany, a
gdyby został wykonany — zakończyłby się wyjątkiem, nie komunikatem bramki.

## Trzeci defekt: bramka i ruleset mówią o czym innym

Nawet po naprawieniu ścieżki `requiredCheckNames` pozostaje niejednoznaczne,
bo dwaj konsumenci wymagają **różnych nazw tego samego checka**:

* ruleset GitHuba wymaga nazwy wyświetlanej, czyli pola `name:` joba —
  `governance / remote lifecycle`;
* bramka porównuje z **kluczem joba**, bo `JOB_LINE` łapie
  `^  ([A-Za-z0-9_-]+):` — czyli `remote-lifecycle`.

Te dwie wartości pokrywają się wyłącznie w hubie, gdzie joby nie mają
nadpisanego `name:` (`test`, `windows-governance`). U adoptującego:

    .github/workflows/new-project-governance.yml
      15:  remote-lifecycle:
      16:    name: governance / remote lifecycle     <- tego wymaga ruleset

Adoptujący nie jest więc w stanie napisać pliku, który jest jednocześnie
prawdziwy wobec rulesetu i przechodzi bramkę. Sama zmiana strategii dystrybucji
tego nie usuwa — dlatego naprawa musi objąć również parser.

## Rozwiązanie

Lekarstwo istnieje już w słowniku standardu. `package-manifest.json` zna trzy
strategie: `managed` (34 pliki), `seed` (2) i `extendable` (1).

`extendable` jest dokładnie tym wzorcem: `governance/manifest.default.json`
trafia do `.governance/manifest.json`, gdzie repozytorium wpisuje własne
wartości, ograniczone przypiętym `manifest.schema.json`. To samo należy
zastosować do required-checks:

1. `governance/required-checks.json` → `strategy: "extendable"`.
2. Nowy `governance/required-checks.schema.json` → `strategy: "managed"`,
   ograniczający instancję (wymagane `repository`, `workflowFile`,
   niepusta `requiredCheckNames`).
3. `scripts/check_required_checks.py` — rozwiązywać źródło względem położenia
   samego skryptu (najpierw obok skryptu, potem fallback na
   `root/governance/`), zamiast zgadywać `parents[1]` plus stała ścieżka.
4. `scripts/check_required_checks.py` — czytać `name:` joba jako publikowaną
   nazwę checka, z fallbackiem na klucz joba, żeby bramka i ruleset porównywały
   tę samą wartość.
5. `scripts/governance_check.py` — wywołać bramkę, żeby fałszywa deklaracja
   zamykała się fail-closed zamiast przechodzić niezauważona.

Punkty 3 i 4 są zweryfikowane w piaskownicy — patrz
`check_required_checks.patch` obok tego pliku:

    TEST 1 hub (regresja)        OK  required=['test','windows-governance']
    TEST 2 adoptujący (.governance/)  OK  required=['governance / remote lifecycle']
    TEST 3 brak pliku            komunikat bramki z listą sprawdzonych ścieżek,
                                 zamiast traceback FileNotFoundError

## Zakres

Ten ticket zmienia **wyłącznie hub**. Nie zmienia nazw checków w żadnym
repozytorium ani nie podbija wersji standardu u adoptujących. Uzupełnienie
instancji w 21 repozytoriach to osobna praca, wykonalna dopiero po tej zmianie —
dziś każde takie repozytorium musiałoby wybierać między zgodnością z lockiem a
prawdziwością pliku.

## Uwaga proceduralna

`project/new-ticket.sh` odmawia utworzenia nowego ticketu, gdy istnieje
niedokończony. W chwili przygotowania tej treści `ticket-088` („Offer and brand
commercial SSOT standards") był świeżo utworzony i miał wyłącznie scaffold.
Numer `089` jest więc propozycją — nadać go dopiero po domknięciu 088 albo za
jawną zgodą człowieka na `--force-new`.

## Dowody

    $ jq -r '.repository' */.governance/required-checks.json | sort -u
    wellmanifest/new-project          # wszystkie 23 repozytoria

    $ cd autonomy && python3 .governance/check_required_checks.py
    FileNotFoundError: [Errno 2] No such file or directory:
      '.../autonomy/governance/required-checks.json'

    $ cd new-project && python3 scripts/check_required_checks.py
    required-checks gate OK: source=governance/required-checks.json
      required=['test', 'windows-governance'] published=['test', 'windows-governance']

    $ grep -n check_required_checks scripts/governance_check.py
    (brak wyników)
