# Egzekwowalność standardów Wellmanifest

Status dokumentu: audyt i minimalny kontrakt docelowy.

Data migawki: 2026-08-20.

Zakres: 15 repozytoriów wskazanych w ticket-095

## Wniosek

Standaryzacja jest realnie stosowana, ale nie jest jeszcze spójnie
egzekwowalna. Warstwa governance procesu zmian jest dojrzała w większości
repozytoriów, natomiast conformance domeny ma trzy różne poziomy:

1. siedem standardów domenowych ma lokalny walidator, workflow domenowy i
   wymagany status przed zmianą `main`;
2. kilka repozytoriów ma poprawny walidator lokalny, ale test nie jest wymagany
   przez CI lub ochronę brancha;
3. `performance` jest szkieletem planowanego standardu, a nie działającym
   kontraktem.

Najważniejszy problem systemowy to rozdzielenie zielonego governance od
zielonego standardu. Potwierdził to `policy-dsl`: governance przechodzi, lecz
pełny test domenowy wykrywa drift żywych danych cenowych. Drugi problem to
nieprawdziwa deklaracja required-checks w adopterach: wszystkie sprawdzone
`.governance/required-checks.json` nadal opisują workflow huba zamiast własnego
repozytorium.

## Co znaczy „egzekwowalne”

Standard jest egzekwowalny dopiero wtedy, gdy wszystkie poniższe warstwy są
spełnione. Nie wolno używać sukcesu jednej warstwy jako dowodu innej.

| Warstwa | Wymagany dowód |
| --- | --- |
| S0 — kontrakt | wersja, dokument normatywny, zamknięty model/schema i przykłady negatywne |
| S1 — conformance lokalne | deterministyczne polecenie kończy się non-zero po naruszeniu kontraktu |
| S2 — integralność | normatywne artefakty i zależności są związane digestem oraz immutable revision |
| S3 — CI | polecenie S1 jest uruchamiane dla PR i zmiany chronionej gałęzi |
| S4 — ochrona merge | rzeczywisty ruleset/branch protection wymaga dokładnej nazwy checka S3 |
| S5 — adopcja/runtime | adopter weryfikuje własne dane i bindingi; drift tworzy finding/ticket i blokuje efekt |

Ocena `EGZEKWOWANY` w tej migawce wymaga S1, S3 i S4. S5 jest osobnym
warunkiem dla standardów posiadających żywych adopterów.

## Macierz repozytoriów

`Local` oznacza wykonany w tym audycie test domenowy. `Main` opisuje odczytany
2026-08-20 aktywny GitHub ruleset albo klasyczną ochronę brancha, a nie samą
obecność pliku workflow.

| Repozytorium | Wersja | Local | CI domeny | Main wymaga domeny | Ocena |
| --- | ---: | --- | --- | --- | --- |
| `dsl` | `0.1.0-dev` | PASS: self-test i manifest | częściowo | `test`, `windows-governance` | CZĘŚCIOWO |
| `code-dsl` | `0.1.0-dev` | PASS: 9 testów | brak | tylko remote lifecycle | NIE |
| `autonomy` | `0.8.1` | PASS: 35 testów + self-test | tak | autonomy conformance | EGZEKWOWANY |
| `git-lifecycle` | `0.1.0-dev` | PASS: conformance | tak | lifecycle conformance | EGZEKWOWANY |
| `env-dsl` | `0.1.0-dev` | PASS: 12 testów + self-test | brak | brak ochrony | NIE |
| `merge` | `0.1.0-dev` | PASS: conformance + CQRS | tak | `conformance` | EGZEKWOWANY |
| `new-project` | `0.18.1` | PASS: governance i required-checks | tak | `test`, `windows-governance` | EGZEKWOWANY (hub) |
| `policy-dsl` | `0.2.0-dev` | FAIL: 40 PASS, 1 drift danych | brak | tylko remote lifecycle | NIE |
| `poa` | `0.1.0` | PASS: conformance | tak | `test`, `windows-governance` | EGZEKWOWANY |
| `performance` | `0.1.0` | brak implementacji domeny | brak | tylko remote lifecycle | SZKIELET |
| `project-ssot` | `0.2.0-dev` | PASS: 37 testów | brak | brak ochrony | NIE |
| `ssot` | `0.2.0-dev` | PASS: 19 testów | brak | brak ochrony | NIE |
| `ticket-lifecycle` | `0.1.0-dev` | PASS: conformance | tak | lifecycle conformance | EGZEKWOWANY |
| `twin-lifecycle` | `0.2.0-dev` | PASS: conformance | tak | lifecycle conformance | EGZEKWOWANY |
| `validation-attestation` | `0.1.0-dev` | PASS: 15 testów + self-test | tak | attestation conformance | EGZEKWOWANY |

### Doprecyzowanie oceny `dsl`

Workflow `dsl/.github/workflows/ci.yml` uruchamia `dsl_check.py self-test` i
kontrole JSON, lecz nie wykonuje `dsl_check.py validate`, `standards` ani
pełnego `gate` dla własnego `profiles/dsl-manifest.json`. Manifest przechodzi
`validate` i `standards`, ale ręczne `gate` kończy się `DSL-FINDINGS-002`, bo
brakuje wymaganego raportu producenta findings. Chroniony check jest więc
ważny, lecz nie dowodzi pełnej zgodności DSL repozytorium.

## Governance i immutable adoption

- Dwanaście repozytoriów ma adopcję `.governance/manifest.json`; hub ma własny
  `governance/manifest.hub.json`. `ssot` i `project-ssot` nie mają governance
  ani workflow.
- Lokalne governance gates przeszły dla huba i 11 adopterów. `performance`
  nie przeszło z powodu nieśledzonego `__pycache__` w `.governance/` oraz
  nieaktualnej `acceptedBaseSha` aktywnego ticketu.
- Adopterzy są przypięci do wydań `new-project` od `0.14.0` do `0.18.1` i do
  hashy zarządzanych plików. To poprawnie wykrywa byte drift, ale nie gwarantuje,
  że przypięta konfiguracja opisuje właściwe repozytorium.
- `dsl-manifest.json` istnieje w ośmiu repozytoriach i wszystkie osiem
  manifestów przeszło `dsl_check validate` oraz `dsl_check standards`.
  Pozostałe standardy często pinują własne schema/grammar w skryptach
  conformance, lecz nie publikują jednolitego manifestu zależności.

## Potwierdzone defekty

### P0 — required-checks adopterów nie są ich źródłem prawdy

Każdy zbadany adopter niesie tę samą instancję:

- `repository: wellmanifest/new-project`;
- `workflowFile: .github/workflows/ci.yml`;
- `requiredCheckNames: [test, windows-governance]`.

To nie odpowiada np. `autonomy`, gdzie aktywny ruleset wymaga
`governance / remote lifecycle` i `standards / autonomy conformance`.
Uruchomienie dostarczonego checkera przeciw rzeczywistemu workflow kończy się
niepowodzeniem. Stara wersja checkera szuka ponadto domyślnie
`governance/required-checks.json`, mimo że w adopterze plik leży pod
`.governance/`.

Poprawka istnieje już na `new-project/main`: instancja ma strategię
`extendable`, checker rozpoznaje layout adoptera i waliduje nazwy publikowanych
jobów. W chwili audytu `main` był jednak 69 commitów przed wydanym tagiem
`v0.18.1`, więc żaden adopter nie mógł przypiąć tej poprawki jako nowego
immutable release.

Skutek: GitHub może obecnie egzekwować właściwe statusy, ale agent lub narzędzie
czytające deklarowany SSOT required-checks otrzyma nieprawdę. Nie wolno na tej
podstawie automatycznie zatwierdzać ani publikować zmian.

### P0 — governance nie wykrywa driftu danych domenowych

Pełne testy `policy-dsl` reprodukują:

```text
saas-start amount_monthly_minor expected 9700, got 5000
```

Oczekiwanie pochodzi z `profiles/sales/offer-catalog.json`, a obserwowana
wartość z żywego
`subactor/www-sub-actor/src/php_app/config/plans.json`. Repozytorium ma tylko
workflow remote lifecycle, więc domain/data test nie blokuje merge.

Dodatkowo test wskazuje żywy checkout absolutną ścieżką
`/home/tom/github/...`. Na innym hoście jest pomijany, czyli identyczny commit
może przejść bez tej samej obserwacji. Binding adoptera musi być parametrem lub
machine-readable URI/revision, a brak zadeklarowanego adoptera w profilu
produkcyjnym ma być błędem, nie `skip`.

### P1 — brak domenowej bramki lub ochrony `main`

- `code-dsl`, `env-dsl` i `policy-dsl` mają działające lokalne testy, ale nie
  mają workflow domenowego wymaganego przed merge.
- `ssot` i `project-ssot` mają walidatory oraz poprawne manifesty, ale nie mają
  ani CI, ani ochrony `main`, ani adopcji governance.
- `performance` nie ma jeszcze schema, walidatora, fixtures ani conformance.
  Nie powinno być przedstawiane jako opublikowany, egzekwowalny standard.
- `dsl` wymaga własnego manifestu i pełnego gate w chronionym CI, nie tylko
  self-testu implementacji walidatora.

### P1 — nieprzenośne źródła w POA

Normatywny seed `poa/standard/seed/p0p1-tickets.v1.json` oraz validator
`standard/ticket_queue.py` wymagają `file:///home/tom/github/if-uri`.
Conformance przechodzi, lecz kontrakt jest związany z jednym kontem i układem
dysku. Źródło powinno być repozytoryjnym URI z immutable revision i digestem;
lokalna ścieżka może być jedynie rozwiązywalnym parametrem wykonania.

### P2 — drift dokumentacji i wersji

- `autonomy` ma `VERSION=0.8.1`, podczas gdy root README nadal opisuje status
  `0.8.0`.
- `validation-attestation` ma implementację, test domenowy i chroniony check,
  lecz README nadal mówi „governed implementation pending”.
- Standardy używają niejednolitego położenia manifestu (`root`, `profiles/`,
  `examples/`) albo wyłącznie pinów zaszytych w conformance. Automatyczny
  katalog nie powinien zgadywać tych miejsc.

## Minimalny kontrakt docelowy

Każde repozytorium deklarowane jako standard MUST spełniać poniższe zasady:

1. Root `dsl-manifest.json` MUST publikować identyfikator, wersję, status
   publikacji, wszystkie normatywne artefakty i ich SHA-256.
2. Zależność od innego standardu MUST zawierać repozytorium, pełny immutable
   revision, wersję/profil i digest konsumowanego artefaktu. Sam skrót commita
   lub ścieżka hosta nie wystarcza.
3. Jedno kanoniczne polecenie `conformance --all` MUST obejmować pozytywne i
   negatywne przypadki, integralność digestów oraz zamknięcie diagnostyk.
4. Workflow `standard-conformance` MUST uruchamiać to polecenie dla PR, push do
   `main` i ręcznego replay. Nazwa publikowanego joba MUST być stabilna.
5. Target-owned `.governance/required-checks.json` MUST mapować każdy wymagany
   check na rzeczywisty workflow. Ten sam katalog MUST być czytany przez
   governance gate, ruleset reconciliation i agenta publikującego.
6. Aktywna ochrona `main` MUST wymagać governance oraz domain conformance ze
   strict head update. Odczyt hostowanej reguły jest częścią okresowego audytu.
7. Repozytorium z żywym adopterem MUST publikować osobny `adoption-conformance`:
   pin źródła, odczyt danych, porównanie, timestamp/freshness i receipt. Brak
   wymaganego źródła produkcyjnego MUST fail closed.
8. `README`, `VERSION`, manifest i status wydania MUST być sprawdzane jednym
   testem spójności. Wersja `*-dev` nie może deklarować stabilnej publikacji.
9. Standard bez S1–S4 MUST jawnie mieć status `draft` lub `reference-only` i
   nie może autoryzować efektu runtime.

## Kolejność wdrożenia

### Etap 1 — odzyskać prawdziwe bramki

1. Wydać bieżący `new-project/main` jako nową immutable wersję po standardowej
   walidacji i exact-head approval.
2. Upgrade adopterów i utworzyć w każdym target-owned required-checks zgodne z
   rzeczywistym CI oraz rulesetem.
3. Dodać `standard-conformance` i ochronę `main` do `code-dsl`, `env-dsl` i
   `policy-dsl`; poprawić pełny gate `dsl`.
4. Naprawić drift `policy-dsl` versus WWW przez rozstrzygnięcie właściwego
   HOME danych, nie przez zmianę testu pod aktualną wartość.

### Etap 2 — domknąć katalog standardów

1. Ujednolicić root manifest i dependency lock we wszystkich standardach.
2. Podłączyć `ssot` i `project-ssot` do governance, CI i ochrony brancha.
3. Oznaczyć `performance` jako draft do czasu dostarczenia schema, fixtures,
   walidatora i chronionego conformance.
4. Usunąć host-specific ścieżki z `policy-dsl` i `poa`.

### Etap 3 — autonomiczna obserwacja danych

Wykorzystać istniejące role Subactor zamiast tworzyć jednego wszechwładnego
agenta:

- observer zbiera wersjonowane snapshoty kodu, konfiguracji i danych;
- validator wykonuje domain oraz adoption conformance i wydaje exact-subject
  attestation;
- planner tworzy bounded remediation intent/ticket;
- implementer naprawia wyłącznie `allowedPaths`;
- publisher działa dopiero po niezależnej atestacji i chronionych checkach.

Nowy model LLM nie jest wymagany. Potrzebne są wspólne capability/skill dla
`standard-audit` i `adoption-conformance`, które wywołują deterministyczne
narzędzia; skill nie może sam przyznawać merge/effect authority. Najpierw
należy ustabilizować opisany wyżej kontrakt i katalog, aby automatyzacja nie
powielała obecnych rozbieżności.

## Dowody i odtwarzanie

Audyt wykonano na bieżących checkoutach; dwa nie były na `main`:
`policy-dsl@ticket/015-llm-credential-publication` (tree już scalone do
`origin/main`) oraz `project-ssot@feat/capability-block-v2`.

Kluczowe polecenia:

```bash
./project/governance-check.sh --actor agent
python3 /home/tom/github/wellmanifest/dsl/src/dsl_check.py \
  validate --root <repo> <dsl-manifest.json>
python3 /home/tom/github/wellmanifest/dsl/src/dsl_check.py \
  standards --root <repo> <dsl-manifest.json>
python3 -m unittest discover -s tests -v
python3 standard/conformance.py --all
gh api repos/wellmanifest/<repo>/rulesets
gh api repos/wellmanifest/<repo>/branches/main/protection
```

Wszystkie osiem DSL manifests przeszło `validate` i `standards`. Wszystkie
uruchomione lokalne suite poza pełnym `policy-dsl` przeszły; `performance` nie
ma suite domenowego. Szczegółowy rejestr refów i wyników znajduje się w
`project/ticket-095/ai-codex-logs.txt`.
