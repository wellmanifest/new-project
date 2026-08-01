# Egzekwowanie `new-project`

`new-project` 0.8.0 rozdziela trzy warstwy, których nie wolno scalać:

1. Markdown wyjaśnia zasady ludziom i agentom.
2. Manifest, `intent.json` i walidator deterministycznie sprawdzają strukturę,
   stan oraz zakres.
3. Zewnętrzny GitHub Ruleset/CODEOWNERS dostarcza zaufaną zgodę i blokuje
   merge, którego lokalny agent nie może sam zatwierdzić.

## Adopcja w repozytorium docelowym

Skopiuj do `.governance/` zatwierdzony manifest, walidator, profile stacków oraz
lock z SHA-256 zarządzanych plików. Skopiuj również wrappery
`project/governance-check.sh` i `project/governance-check.bat`.

Manifest deklaruje wymagane pliki, Docker, aktywne/zamknięte statusy ticketów,
stany implementacyjne, ścieżki governance i profile technologiczne. Każdy nowy
ticket zawiera intent v2 z workstreamem, zakresem, zależnościami, konfliktami i
opcjonalnym routingiem przez ticket integracyjny. Zamknięte tickety intent v1
pozostają czytelne; aktywny ticket w manifeście v2 musi zostać jawnie
zmigrowany i ponownie zatwierdzony.

## Współpraca managera, developera i dwóch AI

- Manager jest właścicielem celu, priorytetu, kryteriów odbioru i akceptacji
  planu. Jego plik `user-*` tworzy/zmienia wyłącznie on lub trusted intake.
- Developer jest operatorem LLM w IDE, recenzentem technicznym i wykonawcą
  testów. Uruchomienie modelu przez developera nie zmienia autorstwa AI.
- AI implementujące ma własny `ai-{provider-or-instance}.md`, log, branch i
  worktree. Nie może rozszerzyć intencji ani zatwierdzić własnego diffu.
- Drugie AI pracuje nad innym, niekolidującym ticketem albo wykonuje read-only
  review. Dwa AI nie edytują równolegle tych samych plików.
- CI deterministycznie rozstrzyga bramkę. Review AI jest wyłącznie doradcze.

Manifest definiuje nazwane workstreamy i ich `ownedPaths`. Obowiązują:

1. maksymalnie jeden aktywny ticket implementacyjny na workstream;
2. brak nakładania aktywnych `allowedPaths` na konkretnych plikach repozytorium;
3. jeden branch/PR rozwiązuje się dokładnie do jednego aktywnego ticketu;
4. `dependsOn` tworzy acykliczny graf i wskazuje zakończone prerekwizyty;
5. aktywne `conflictsWith` blokuje wykonanie;
6. ścieżki współdzielone z `integration.requiredForPaths` zmienia wyłącznie
   ticket workstreamu integracyjnego; ticket zależny wskazuje go przez
   `integrationTicket`, ale to odwołanie nie przenosi własności ścieżek.

Branch/worktree jest izolacją operacyjną, nie zaufanym rozproszonym lockiem.
Przydział kolejnego numeru ticketu trzeba zserializować i włączyć do gałęzi
bazowej przed utworzeniem równoległych worktree; dwa odłączone worktree nie
mogą niezależnie przydzielić tego samego `ticket-{NNN}`.
Ostateczne porządkowanie równoległych PR-ów realizuje chroniony merge queue,
który ponownie uruchamia governance i testy na aktualnej bazie.

Lokalna kontrola:

```bash
./project/governance-check.sh --actor agent
```

Symulacja obowiązkowej zgody:

```bash
./project/governance-check.sh \
  --changed-file src/example.ts \
  --enforce-approval \
  --approval-source github-review \
  --approved-ticket ticket-018
```

Zgody nie zapisuje się jako sekret ani samodzielne twierdzenie agenta. W CI
źródłem `github-review` jest API Pull Request po niezależnym review. Przy zmianie
intencji lub diffu GitHub musi odrzucić stare approval.

## CI i ochrona repozytorium

Workflow `.github/workflows/governance.yml` jest reusable. Wywołujący przypina
zarówno workflow, jak i wejście `standard-ref` do tego samego pełnego SHA
opublikowanego commitu. Workflow odrzuca `standard-ref`, który nie jest pełnym,
40-znakowym SHA. Nie wolno używać ruchomego `@main`.

Po publikacji wersji w repozytorium docelowym dodaj:

```yaml
jobs:
  governance:
    uses: wellmanifest/new-project/.github/workflows/governance.yml@<FULL_SHA>
    permissions:
      contents: read
      pull-requests: read
    with:
      standard-ref: <FULL_SHA>
```

W GitHub Rulesets ustaw:

- tylko Pull Request do chronionej gałęzi;
- wymagany status `governance / enforce` oraz testy stacka;
- wymagany CODEOWNER i co najmniej jedna niezależna akceptacja;
- odrzucanie starych zgód po nowym pushu;
- wymagany merge queue z ponownym wykonaniem statusów po aktualizacji bazy;
- zakaz bypassu dla botów/agentów i ograniczony bypass administracyjny;
- ochronę `.github/workflows/**`, `.governance/**`, `AGENTS.md` oraz
  `project/ticket-*/user-*.md` przez CODEOWNERS.

Hook lokalny jest tylko szybką informacją. Nie jest granicą bezpieczeństwa,
ponieważ można go pominąć przez `--no-verify`.

## Profile technologiczne

`governance/stack-profiles.json` publikuje markery i rekomendowane bramki dla
Node.js, Python, Go, Rust, Java, Docker, frontend E2E, Terraform i Kubernetes.
Walidator sprawdza zgodność deklaracji z markerami; właściwe polecenia testowe
pozostają jawne w CI projektu i działają w przypiętych kontenerach.

LLM może komentować rozbieżności intencji, ale nie blokuje ani nie zatwierdza
merge. Wymagana decyzja używa wyłącznie deterministycznych kodów `GOV-*`.

## Ograniczenia zaufania

Osoba z nieograniczonym prawem administratora może zmienić reguły platformy.
Pełne egzekwowanie wymaga organizacyjnego Rulesetu lub required workflow poza
kontrolą pojedynczego repozytorium. Sam manifest ani hook nie może narzucić
zasad administratorowi posiadającemu prawo ich wyłączenia.
