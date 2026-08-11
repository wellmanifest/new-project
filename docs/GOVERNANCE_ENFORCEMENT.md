# Egzekwowanie `new-project`

`new-project` 0.9.0 rozdziela trzy warstwy, których nie wolno scalać:

1. Markdown wyjaśnia zasady ludziom i agentom.
2. Manifest, `intent.json` i walidator deterministycznie sprawdzają strukturę,
   stan oraz zakres.
3. Zewnętrzny GitHub Ruleset/CODEOWNERS dostarcza zaufaną zgodę i blokuje
   merge, którego lokalny agent nie może sam zatwierdzić.

## Adopcja w repozytorium docelowym

Skopiuj do `.governance/` zatwierdzony manifest, walidator, profile stacków oraz
lock z SHA-256 zarządzanych plików. `governance/lock.schema.json` definiuje
publikowaną proweniencję locka i powinien być walidowany w procesie adopcji.
Skopiuj również wrappery
`project/governance-check.sh` i `project/governance-check.bat`.

Preferowana adopcja używa pełnego SHA opublikowanego commita:

```bash
python3 /path/to/new-project/scripts/create_adoption_lock.py \
  --target-root /path/to/target-repository \
  --source-revision <FULL_PUBLISHED_SHA>
```

Skrypt czyta zarządzane pliki z obiektu Git, zachowuje istniejący dopasowany
wersją manifest docelowy, atomowo zapisuje pliki i lock oraz odmawia driftu.
Aktualizacja różniących się plików wymaga jawnego `--upgrade` po przeglądzie.

### Atomowa aktualizacja zarządzanego pakietu

Gdy upgrade jednego opublikowanego pakietu zmienia więcej plików niż zwykły
budżet ticketu albo przecina ich normalne workstreamy, aktywny intent v3 może
zadeklarować transakcję:

```json
{
  "delivery": {
    "standardAdoption": {
      "sourceRepository": "wellmanifest/new-project",
      "fromRevision": "<40-znakowy SHA obecnego wydania>",
      "toRevision": "<40-znakowy SHA nowego wydania>"
    }
  }
}
```

Wyjątek nie powiększa ticketu i nie przenosi zwykłej własności. Walidator
odejmuje z normalnego rozliczenia tylko zmienione targety ze strategią
`managed`, dla których package manifesty, locki i hashe base/head tworzą
spójny kontrakt. Nowy target musi być nieobecny w bazie oraz występować jako
`managed` i zgadzać się z hashem head locka. Aktualizowany target musi mieć
ciągłość `managed` i poprawny hash po obu stronach.

Seed manifest, `.governance/manifest.lock.json`, changelog i każda ścieżka
spoza tak wyliczonego zbioru pozostają zwykłym diffem. Nadal muszą rozwiązać
się do jednego aktywnego ticketu, jego `allowedPaths`, workstreamu i budżetu.
Brak base, zmienionego locka, pełnych różnych SHA albo jakakolwiek niespójność
emituje istniejący kod synchronizacji `GOV-SYNC-001` i nie przyznaje wyjątku.

Transakcję przygotowuje się przez `goal governance adopt --check`, przegląda
pełny plan zmian i dopiero potem wykonuje jawny upgrade. Lock i intent należą
do checkoutu PR, więc są dowodem strukturalnym, a nie merge authorization.
Protected review/attestation związane z repozytorium, PR-em, current HEAD,
ticketem i aktorem pozostaje obowiązkowe dokładnie tak samo jak dla każdego
innego implementation diffu.

Bazowy manifest jest stack-neutral: nie wymaga Dockerfile ani Compose i nie
deklaruje stacku `docker`. Target korzystający z kontenerów rozszerza własny
`.governance/manifest.json`: dodaje Dockerfile do `requiredFiles`, ustawia
`docker.required` na `true` i dodaje `docker` do `stacks`. Schema, profile i
walidator zachowują pełne egzekwowanie tego jawnego opt-in.

Manifest deklaruje wymagane pliki, opcjonalny Docker, aktywne/zamknięte statusy ticketów,
stany implementacyjne, ścieżki governance i profile technologiczne. Każdy nowy
ticket zawiera intent v2 z workstreamem, zakresem, zależnościami, konfliktami i
opcjonalnym routingiem przez ticket integracyjny. Zamknięte tickety intent v1
pozostają czytelne; aktywny ticket w manifeście v2 musi zostać jawnie
zmigrowany i ponownie zatwierdzony.

Tylko `IN_PROGRESS` oznacza aktywnego właściciela implementacji i rezerwuje
workstream oraz `allowedPaths`. `BACKLOG`, `PLAN` i `BLOCKED` zachowują plan,
zależności i dowody, ale nie blokują kolejki. Przed zmianą kodu taki ticket musi
wrócić do `IN_PROGRESS` oraz stanu `EDIT`, `VALIDATION` lub `PUBLICATION`.

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

Starsza symulacja review człowieka pozostaje kompatybilna lokalnie:

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
Reviewer musi dodatkowo należeć do jawnego wejścia `trusted-reviewers` reusable
workflow. Lista loginów jest konfiguracją bezpieczeństwa repozytorium
docelowego i musi być chroniona przez CODEOWNERS; sam fakt, że reviewer nie jest
autorem PR, nie stanowi dowodu uprawnienia.

### Approval evidence v1

Chroniony workflow materializuje decyzję jako
`new-project.approval-evidence/v1`. Dokument zawiera źródło, repozytorium,
numer PR, dokładny 40-znakowy `headSha`, jeden ticket oraz aktora. Powstaje w
`runner.temp`, poza checkoutem. Walidator odrzuca evidence znajdujące się w
repozytorium, bo autor PR mógłby je sam zmienić.

Źródła zaufania są rozłączne:

- `github-review`: `actor.type=User`, dokładny login w `trusted-reviewers`,
  review `APPROVED` dla bieżącego HEAD;
- `github-app-review`: `actor.type=Bot`, dokładny login wraz z `[bot]` w
  `trusted-validator-apps`, review `APPROVED` dla bieżącego HEAD;
- `signed-attestation`: podpis i issuer zweryfikowane poza checkoutem, a
  predicate type równy
  `https://wellmanifest.dev/attestations/validator/v1`.

Samo `user.type=Bot`, pole `verified: true` w pliku PR ani komentarz modelu nie
stanowią zaufania. Dla atestacji chroniony krok Sigstore/GitHub Attestations
najpierw weryfikuje podpis, issuer i subject, a dopiero potem tworzy ephemeral
evidence. Schemat znajduje się w
`governance/approval-evidence.schema.json`.
Publikowany reusable workflow rozwiązuje bezpośrednio ścieżki GitHub review;
repozytorium wybierające signed attestation musi dodać równoważny chroniony
resolver podpisu i wywołać ten sam walidator z `--approval-evidence` oraz
oczekiwanymi bindingami.

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
      trusted-reviewers: alice,bob
      trusted-validator-apps: validator-agent[bot]
```

Co najmniej jedna z dwóch list authority musi być niepusta. Nie wolno wpisywać
loginów botów do `trusted-reviewers` ani loginów ludzi do
`trusted-validator-apps`. Caller workflow, obie listy, `.governance/**` i
CODEOWNERS muszą być chronione tak, aby PR nie mógł sam rozszerzyć allowlisty.

    Adopcja wydania jest trwała dopiero, gdy lock zawiera opublikowany pełny
    `sourceRevision` i `publicationStatus: published`. Hash lokalnego pliku wykrywa
    zmianę, ale `sourceRevision: null` lub `publicationStatus: uncommitted` nie
    pozwala odtworzyć źródła standardu i nie może być finalnym dowodem publikacji.

W GitHub Rulesets ustaw:

- tylko Pull Request do chronionej gałęzi;
- wymagany status `governance / enforce` oraz testy stacka;
- wymagany CODEOWNER i co najmniej jedna niezależna akceptacja;
- odrzucanie starych zgód po nowym pushu;
- wymagany merge queue z ponownym wykonaniem statusów po aktualizacji bazy;
- `delete_branch_on_merge=true`, aby zmergowany head branch znikał
  automatycznie;
- zakaz bypassu dla botów/agentów i ograniczony bypass administracyjny;
- ochronę `.github/workflows/**`, `.governance/**`, `AGENTS.md` oraz
  `project/ticket-*/user-*.md` przez CODEOWNERS.

### Lifecycle brancha ticketowego

Branch/worktree jest izolacją na czas aktywnego ticketu i PR-a, a nie trwałym
archiwum. Po merge GitHub usuwa head branch przez
`delete_branch_on_merge=true`. Zamknięcie PR-a bez merge nie jest zgodą na
utratę pracy: branch pozostaje do chwili jawnej decyzji właściciela o jego
odrzuceniu.

Stan spoczynku repozytorium jest jednoznaczny:

```text
open pull requests = 0
remote branches = [default branch]
```

Branch inny niż default branch musi być headem otwartego PR-a. Odstępstwo jest
osieroconym branchem i wymaga decyzji: przywrócić PR, zintegrować pracę albo
jawnie ją odrzucić. Sam walidator jest read-only i nie usuwa branchy.

## Jedno źródło nazw wymaganych checków

Nazwy checków wymaganych na `main` dla tego repozytorium mają **jedno źródło**:

```text
governance/required-checks.json  →  field requiredCheckNames
```

Obecna wartość: `test`, `windows-governance`.

Bramka `scripts/check_required_checks.py` (CI: job `test`) porównuje to źródło z
jobami top-level w `.github/workflows/ci.yml` i failuje, gdy brakuje nazwy po
którejkolwiek stronie. Circular governance checks ignorowane przez zewnętrznego
Validatora (`governance / enforce` i warianty) są zapisane w tym samym pliku w
`circularGovernanceChecksIgnoredByValidator` i **nie** są jobami workflow hubu.

### Konsumenci zewnętrzni

| konsument | jak ma czytać ten sam zestaw |
|---|---|
| GitHub Ruleset `main-governance-protection` | ręcznie utrzymać `requiredCheckNames` (brak odczytu rulesetu z CI bez admin API) |
| `subactor/validator-agent` | `DIRECT_PR_REQUIRED_CHECKS` oraz `DIRECT_PR_SCAN_CONFIG["wellmanifest/new-project"].required_checks` **muszą** być równe `requiredCheckNames`; skrypt `bin/dispatch-direct-pr.sh` też |
| Dokumentacja / agenci | wskazują na `governance/required-checks.json`, nie na skopiowaną listę w prozie |

Hardcoding podzbioru (np. tylko `test`) jest defektem tej samej klasy co ticket-025:
lista zakresu rozjeżdża się z rzeczywistością i Validator może wystawić zaufane
APPROVE dla zestawu, którego ruleset i tak nie wpuści — albo odwrotnie, nie
sprawdzić checku, który jest wymagany.

## Log decyzji autonomicznych

Kontrakt: `CONTRIBUTING.md` (`DOCUMENT DECISION_LOG`, reguły `C-DECISION-001`–
`004`), schema `governance/decision-record.schema.json`, runtime
`scripts/decision_record.py`, kody `GOV-DECISION-001`…`004`.

| Kto emituje | Kiedy | Gdzie |
|---|---|---|
| `ifuri-validator-agent` (validator-agent) | po deterministycznej bramce checków / unsafe, przed lub wraz z review | `project/{ticket}/decisions.md` (append fence `dsl`) `decision_dsl` w raporcie runu + fence w body review |
| `repair-agent` | gdy zainstalowany i mutuje kod | ten sam plik decyzji ticketu naprawy; na `wellmanifest` dziś nie zainstalowany |
| Agent lokalny (Claude/Codex/…) | gdy decyzja zmienia stan repo poza samym scaffoldem | ten sam kontrakt; **nie** zastępuje review App |

Wpis **wyprowadza się** z `t2c.change-evaluation/v1` gdy ocena istnieje
(`scripts/decision_record.py` helper `from_change_evaluation`). Pole `ADVISORY`
może nieść werdykt LLM; `VERDICT AUTHORITY` musi pozostać `DETERMINISTIC`.
Odtworzenie: `python3 scripts/decision_record.py validate-dsl PATH`.

Surowy `ai-{PROVIDER}-logs.txt` pozostaje logiem EXEC/STDOUT (NOTATION_STANDARDS)
i **nie** jest logiem decyzji.

## Integracja `validator-agent` z istniejącym repozytorium

Integrację wykonuje się w osobnych, zatwierdzonych ticketach obu repozytoriów.
Nie należy rozszerzać istniejącego trybu repair o ukryte wyjątki. Validator
powinien otrzymać jawny tryb `validate-pr` z wejściami:

```text
repository, pullRequest, headSha, ticket, correlationId
```

Tryb ten:

1. pobiera wyłącznie wskazane repozytorium i dokładny `headSha`;
2. sprawdza, że PR nadal wskazuje ten SHA i ticket jest aktywnym właścicielem
   diffu;
3. uruchamia governance gate oraz testy zadeklarowane przez ticket;
4. nie wymaga Issue z innej kolejki, gałęzi `ticket/*` ani
   `.ifuri/repair/TODO.md`;
5. nie dodaje `VERSION`, `CHANGELOG.md` ani innych ścieżek poza
   `intent.json.allowedPaths`;
6. po sukcesie wystawia review dla dokładnego SHA jako dedykowana GitHub App
   albo generuje podpisaną atestację z tymi samymi bindingami.

Minimalny profil GitHub App to odczyt contents/metadata oraz zapis review Pull
Requests; każde dodatkowe uprawnienie wymaga uzasadnienia. App musi być
zainstalowana w repozytorium docelowym przed próbą review. Odpowiedź HTTP 401 z
endpointu instalacji oznacza błąd uwierzytelnienia/JWT i nie dowodzi ani
instalacji, ani jej braku — należy naprawić autoryzację App i dopiero potem
zweryfikować instalację.

Dla `semcod/todo2code` migracja polega na zastąpieniu lokalnej reguły
„akceptuj dowolny niezależny `User`” przypiętym reusable workflow oraz wpisaniu
dokładnego loginu Validator App do `trusted-validator-apps`. Nie należy zmieniać
warunku na ogólne `User || Bot`. Workflow najpierw rozwiązuje jeden ticket
właściwy dla diffu, więc inne równoległe tickety nie rozszerzają approval.

Konfiguracja operacyjna Validatora używa:

```text
LLM_MODEL_VALIDATOR=openrouter/z-ai/glm-5.2
```

Gemini 3.1 Pro Preview nie jest używany w tej roli. Wybór modelu wpływa na koszt
i jakość analizy, ale nie na authority: o wyniku merge nadal rozstrzygają
deterministyczne testy, chroniona tożsamość i evidence.

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
