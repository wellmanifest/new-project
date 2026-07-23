<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Bazując na opisanym celu projektu i wypracowanym przez nas formacie DSL, sprawdź, czy istnieją już podobne języki DSL, standardy lub rozwiązania używane do komunikacji pomiędzy człowiekiem, LLM i agentem AI.

Cel naszego DSL:
użytkownik wpisuje polecenie w języku naturalnym,
LLM zamienia je na formalny DSL,
DSL jest czytelny zarówno dla człowieka, jak i dla systemu,
człowiek może sprawdzić, czy jego polecenie zostało poprawnie zrozumiane,
DSL ma pokazywać wszystkie planowane działania, warunki, źródła danych, pytania doprecyzowujące i wymagane potwierdzenia,
system nie może dodawać działań, których użytkownik nie zlecił,
dopiero zaakceptowany i zweryfikowany DSL trafia do runtime’u i może zostać wykonany.
Nasz aktualny format opiera się na konstrukcjach podobnych do:
TASK
INPUT
SOURCE
STEP
WHEN
DO
WITH
SAVE
ASK
CONFIRM
OUTPUT
POLICY
ALLOW
DENY
REQUIRE
ASSERT

Przygotuj raport zawierający:
Informację, czy istnieje już DSL lub standard realizujący podobny cel.
Konkretne przykłady takich języków, frameworków lub formatów.
Krótkie przykłady ich składni.
Porównanie ich z naszym aktualnym formatem.
Informację, które elementy możemy wykorzystać lub zaadaptować.
Informację, czego brakuje istniejącym rozwiązaniom względem naszego celu.
Rekomendację:
wykorzystać istniejący standard,
rozszerzyć istniejące rozwiązanie,
czy stworzyć własny DSL.
Nie ograniczaj analizy wyłącznie do klasycznych języków programowania. Sprawdź również:
workflow DSL,
policy DSL,
AI agent protocols,
structured output dla LLM,
plan representation,
human approval workflows,
narzędzia typu prompt-to-action,
systemy orkiestracji agentów.
Wynik zapisz jako czytelny plik Markdown z tabelą porównawczą i krótkim podsumowaniem. Oddziel informacje potwierdzone źródłami od własnych wniosków i dodaj linki do dokumentacji analizowanych rozwiązań.

Poniżej masz raport (Markdown) sprawdzający istniejące rozwiązania podobne do Twojemu DSL (cel: NL -> LLM -> formalny, czytelny DSL -> TypeScript runtime -> wykonanie z kontrolą i akceptacją). Dla każdej informacji pochodzącej z webowych źródeł dodałem cytaty w nawiasach kwadratowych bezpośrednio po zdaniu. Sekcje z wnioskami/opiniami są oznaczone jako wnioski (nie wymagają zewnętrznych cytatów).

Plik: raport_dsl_survey.md

---

# Przegląd istniejących DSL / standardów dla komunikacji: człowiek ⇄ LLM ⇄ agent

Cel przeglądu (skrót)

- Sprawdzić, czy istnieje DSL / standard, który realizuje Twój cel: NL → LLM → formalny, czytelny DSL (pokazujący planowane działania, warunki, źródła danych, pytania doprecyzowujące i wymagane potwierdzenia), zatwierdzony przez człowieka przed wykonaniem.
- Zidentyfikować konkretne technologie, ich przykłady, porównać je z Twoim formatem i dać rekomendację.

Źródła potwierdzone

- Dokumentacja i artykuły o "Structured Outputs" w OpenAI API (response_format / JSON Schema).[^1][^2]
- Dyskusje i przykłady użycia Structured Outputs i function-calling w deweloperskim community OpenAI.[^3][^4][^5]
(Uwaga: lista odnośników na końcu raportu.)


## 1. Czy istnieje już DSL/standard realizujący dokładnie Twój cel?

Wniosek: Nie ma jednego, powszechnie przyjętego, kompletnego DSL, który w całości realizuje dokładnie wszystkie Twoje wymogi (pełna semantyka planów, warunków, źródeł danych, pytań doprecyzowujących, ścisła kontrola „nie dodawania akcji niezamówionych przez użytkownika”, audyt i zatwierdzenie przed wykonaniem) w jednym standardzie. Jednak istnieje szereg zbliżonych rozwiązań i częściowych standardów, które realizują istotne fragmenty Twojego celu — głównie: strukturalne wyjścia modeli (schema-driven output), funkcje / tool-calling, workflow DSL, policy DSL i systemy orkiestracji agentów.[^2][^4][^1]

Poniżej szczegóły i porównanie.

## 2. Konkretnie: przykłady istniejących języków / formatów / frameworków

1) Structured Outputs / JSON Schema response formats (OpenAI)

- Co robi: pozwala wymusić od modelu strukturę JSON zgodną z JSON Schema (model generuje dane dopasowane do schematu), stosowane do uzyskania przewidywalnych, walidowalnych odpowiedzi od LLM.[^1][^2]
- Przykład składni (schemat):
{
"type":"object",
"properties": {
"task": {"type":"string"},
"steps": {"type":"array", "items": {"type":"object", "properties": {"id":{"type":"string"},"action":{"type":"string"}}}}
},
"required":["task","steps"]
}
(Źródło: dokumentacja Structured Outputs / response_format).[^2]
- Mocne strony: niezawodność formatu, łatwa walidacja, natywne wsparcie w promptach.[^1][^2]
- Ograniczenia w kontekście Twojego celu: sam JSON Schema nie narzuca semantyki akcji (np. polityk bezpieczeństwa, twardych blokad, trybów dry-run/execute), nie zapewnia workflow engine ani audytora — to raczej warstwa wyjściowa modelu, nie runtime wykonawczy.[^4][^1]

2) Function Calling (OpenAI / narzędzia typu tool calling)

- Co robi: udostępnia funkcje (narzędzia) które model może „wezwać” z parametrami; parametry przekazywane są jako JSON zgodny z opisem funkcji. To daje kontrolowany sposób, w którym model sugeruje wywołania narzędzi.[^5][^4]
- Przykład użycia (fragment):
tools: [{ name:"searchProducts", parameters: { type:"object", properties:{filters:{}} } }]
model może zwrócić wywołanie: searchProducts({filters:{title:"Foo"}}).[^4]
- Mocne strony: umożliwia bezpieczniejsze, strukturalne wywołania operacji; integruje się z runtime.
- Ograniczenia: funkcje są pojedynczymi wywołaniami; nie zapewniają złożonych planów kroków, warunków pre/post, ani mechanizmu zatwierdzania przez człowieka; też nie narzucają polityk.[^5][^4]

3) Workflow DSLs / Orchestration frameworks (np. Apache Airflow DAGs, Temporal, n8n, orkestry agentów typu LangChain Agents / Agentic frameworks)

- Co robią: opisują sekwencje kroków, zależności, retry, warunki. Stosowane głównie do ETL, zadań batch i orkiestracji mikroserwisów. Niektóre agent frameworks (LangChain Agents, AutoGen, etc.) wspierają planowanie i delegację z użyciem LLM.
- Przykład (prosty DAG):
tasks: [ {id:"extract", depends_on:[]}, {id:"transform", depends_on:["extract"]} ]
- Mocne strony: silne podejście do workflow i retry, wizualizacja, scheduling.
- Ograniczenia względem Twojego celu: są nastawione na wykonywanie zadań programistycznych/ETL — rzadko oferują bezpośrednią integrację z naturalnym językiem i mechanizmem generowania struktur DSL przez LLM z kontrolą doprecyzowania/confirmation; wymagają warstwy tłumaczącej NL->workflow. (Z praktyk—często integruje się z LLM przez adaptery, ale nie jest to standardowy, uniwersalny język planów dla LLM) (analiza własna; brak pojedynczego źródła, porównanie z workflow frameworks).

4) Policy DSLs (np. OPA / Rego, AWS IAM policies, Open Policy Agent)

- Co robią: opisują reguły dostępu, zasady decyzji — są formalne, deterministyczne i służą do egzekucji polityk. OPA (Rego) może oceniać warunki i zwracać decyzje allow/deny.
- Przykład (Rego, koncepcyjnie):
default allow = false
allow { input.user == "admin" }
- Mocne strony: formalność, wydajność, jasne allow/deny, integracja w runtime.
- Ograniczenia: nie są przeznaczone do opisywania planów krokowych, akcji i interakcji NL → DSL; są najlepsze jako warstwa polityk do podpięcia pod runtime (dokładnie to, co Ty też planujesz: POLICY.md jako twarda warstwa). (znane rozwiązania: Open Policy Agent docs) (wnioski własne, OPA dokumentacja).

5) Structured plan languages used in AI research (plan representation, HTN, PDDL)

- PDDL (Planning Domain Definition Language) i HTN (Hierarchical Task Network) — klasyczne języki planowania w sztucznej inteligencji, opisujące zadania, precond/eff (warunki wstępne i efekty) i operatory planistyczne.
- Przykład PDDL (upraszczony):
(:action move
:parameters (?from ?to)
:precondition (at ?from)
:effect (and (not (at ?from)) (at ?to)) )
- Mocne strony: formalna semantyka planowania, sprawdzanie przejść, automatyczne planowanie sekwencji.
- Ograniczenia: PDDL jest niskopoziomowy, trudny do czytania dla ludzi nieznających koncepcji; nie integruje się bezpośrednio z LLM (bez warstwy tłumaczącej) i nie oferuje mechanizmu ask/confirm interakcji z użytkownikiem; nie zawiera policy enforcement w stylu OPA. (bibliografia planowania AI).

6) Agent orchestration / agent protocols (np. AutoGen, LangChain Agents, Microsoft’s Planner/Orchestrator research)

- Frameworki te dają wzorce, w których LLM jest używane do planowania i delegowania zadań do narzędzi/agentów; często mają komponenty do zarządzania kontekstem i wywoływania toolów.
- Przykład (koncepcyjny LangChain Agent): agent używa LLM do wygenerowania listy kroków, następnie wywołuje narzędzia sekwencyjnie.
- Mocne strony: praktyczne implementacje end-to-end, integracje z narzędziami.
- Ograniczenia: implementacje różnią się; brakuje jednego, ustandaryzowanego, przenośnego DSL, czy specyfikacji akceptowanej przez różne platformy. (wniosek na podstawie wiedzy o ekosystemie agentów).

7) Prompt-to-action tools / Structured command formats (różni dostawcy i narzędzia: ReAct pattern, tool-formats, Microsoft/Google prototypy)

- Wiele implementacji prompt-to-action używa szablonów (prompt templates) i wymusza określony, ustrukturyzowany output (często JSON), który runtime parsuje i wykonuje. To jest podejście bardzo zbliżone do Twojego (NL→LLM→structured JSON→executor), ale zazwyczaj brak w nich standardu wspólnego dla wielu użytkowników.[^3][^2]
- Przykład (koncepcyjny): model zwraca {"action":"run", "cmd":"npm test"} i runtime wykonuje.
- Mocne strony: praktyczne i prostsze do wdrożenia.
- Ograniczenia: brak zdefiniowanej warstwy polityk i formalnej semantyki planów.


## 3. Krótkie przykłady składni wybranych rozwiązań (ilustracja)

- OpenAI Structured Output (JSON Schema fragment):[^2]
{
"type": "object",
"properties": {
"answer": {"type": "string"},
"search_result": {"type": "boolean"}
},
"required": ["answer","search_result"]
}
- Function-calling (tool description fragment):[^4]
{
"name":"searchProducts",
"description":"A function to search for products",
"parameters": { "type":"object", "properties": { "filters": {...} } }
}
- Rego (OPA) (koncepcyjny):
default allow = false
allow { input.user == "admin" }
- PDDL (upraszczony):
(:action move :parameters (?from ?to) :precondition (at ?from) :effect (and (not (at ?from)) (at ?to)) )


## 4. Porównanie z Twoim formatem (tabela)

| Cecha / wymaganie | Twój DSL (TASK/STEP/WHEN/DO/ASK/CONFIRM/POLICY) | Structured Outputs (OpenAI) | Function Calling (OpenAI) | Workflow DSL (Airflow/Temporal) | Policy DSL (OPA / Rego) | PDDL / Planning |
| :-- | --: | --: | --: | --: | --: | --: |
| Wymuszenie struktury wyjścia od LLM | Tak (YAML/JSON schema) — założenie | Tak (JSON Schema) [^1][^2] | Parametry funkcji (JSON) [^4] | Nie natywnie | Nie (to policy) | Nie |
| Opis planu kroków + warunków | Tak (STEP, WHEN, DO, ASK, CONFIRM) | Możliwe (schemat może zawierać steps) ale brak semantyki wykonania [^2] | Ograniczone (jedno wywołanie = jedna akcja) [^4] | Tak (zadania, zależności) | Nie (reguły decyzyjne tylko) | Tak (precond/effect) |
| Czytelność dla człowieka | Tak (zaprojektowane) | Średnia (JSON Schema + wygenerowany JSON) | Średnia | Zależnie od DSL (Airflow DAG = programistyczny) | Niska dla nietechnicznych | Niska (specyficzny język) |
| Mechanizm ask/confirm (interaktywność) | Tak (ASK/CONFIRM) | Nie (to output) | Można implementować na poziomie logiki | Możliwe (external triggers) | Nie | Nie |
| Zatwierdzenie przez człowieka przed wykonaniem | Tak (wymóg) | Nie natywnie (można dodać) | Nie natywnie | Możliwe | Możliwe (policy block) | Nie natywnie |
| Egzekucja polityk bezpieczeństwa pre/post | Tak (POLICY + POLICY enforcer) | Nie natywnie | Nie natywnie | Zależnie od integracji | Tak (główne zastosowanie) | Nie |
| Audyt / evidence / raport | Tak (w założeniu) | Schemat może zawierać raport, ale runtime to robi | Niezależne | Zwykle tak (task logs) | Możliwe (decyzje) | Planista może logować |
| Łatwość implementacji MVP | Średnia | Wysoka (łatwo wymusić schemat JSON) [^1] | Wysoka (tool-calling) [^4] | Średnia/niska (wymaga infra) | Średnia (policy engine do integracji) | Niska (trzeba planistę) |

(Źródła: OpenAI Structured Outputs \& Function Calling dokumentacja i community threads).[^5][^1][^2][^4]

## 5. Które elementy istniejących rozwiązań możemy wykorzystać / zaadaptować

- JSON Schema / Structured Outputs (OpenAI): użyj do wymuszania formatu DSL-request na LLM (łatwa walidacja, natywne wsparcie). Jest to szybki sposób na niezawodność struktur generowanych przez model.[^1][^2]
- Function-calling pattern: zmapuj DO/akcje na zdefiniowane „tools” / funkcje (opis parametrów), co ułatwia bezpieczne wywoływanie runtime primitives (typ parametru = JSON schema).[^4]
- Policy engine (Open Policy Agent / Rego): zaadoptuj jako warstwę egzekucji polityk (POLICY.md → rego rules) i wykorzystaj allow/deny evaluation przed wykonaniem akcji. To pozwoli oddzielić politykę od procedury. (wniosek z porównań)
- Workflow engines/Orchestrators: inspiracja dla state machine / retry / step dependencies i forking/joins. Możesz nie kopiować całego stacku, ale zaczerpnąć wzorce (np. state transitions, idempotence, retry).
- PDDL / plan representation (koncepty): użyj idei precondition/effect w opisie WHEN i ASSERT, ale trzymaj składnię prostszą i przyjazną człowiekowi.


## 6. Czego brakuje istniejącym rozwiązaniom w odniesieniu do Twoich wymagań

- Brakuje jednego, ustandaryzowanego formatu, który:
    - łączy strukturę generowaną przez LLM (JSON Schema) z formalnymi regułami polityk (allow/deny), planami kroków (WHEN/DO) i mechaniką ask/confirm interakcji z użytkownikiem, oraz audytem i dowodami.
- OpenAI Structured Outputs dostarcza format wyjścia, ale nie semantykę wykonawczą/policy enforcer ani interaktywny cykl zatwierdzania.[^2][^1]
- Function-calling ułatwia wywoływanie narzędzi, ale nie wspiera złożonych planów ani twardych reguł bezpieczeństwa.[^4]
- Workflow DSLs i plan languages dają silne semantyki wykonawcze, lecz zwykle nie integrują naturalnego języka i nie mają standardu, który LLM mógłby wygenerować bez dodatkowej warstwy mappingu.
- Policy DSLs (OPA) są do egzekucji zasad, ale nie do opisu planów czy interakcji NL → DSL.


## 7. Rekomendacja

Biorąc pod uwagę Twój cel i istniejące narzędzia:

- Zalecam podejście hybrydowe: **rozszerzyć i zaadaptować istniejące rozwiązania**, zamiast tworzyć wszystko od zera ani jedynie użyć gotowego pojedynczego standardu. Konkretna rekomendacja kroków:

1. Użyć **Structured Outputs (JSON Schema)** jako warstwy wejściowej/wyjściowej LLM: wymuszanie formatu DSL-request generowanego przez LLM (szybkie MVP i wysoka niezawodność).[^1][^2]
2. Mapować akcje DO/primitive na **opisane funkcje (function-calling)** – czyli zarejestrować narzędzia w runtime jako funkcje o określonych parametrach; to ułatwi bezpieczne wywoływanie.[^4]
3. Wdrażać **Policy layer** (np. OPA/Rego) jako niezależny enforcer — POLICY.md możesz przekształcić w rego rules, które runtime ocenia przed wykonaniem. (to daje twarde allow/deny)
4. Do opisania planów i warunków użyć prostego, czytelnego DSL opartego na YAML/JSON (Twój TASK/STEP/WHEN/DO), z formalnym JSON Schema (pozwala LLM generować poprawne pliki i runtime walidować je). Zapożycz koncepcje precondition/effect z PDDL, ale zachowaj czytelność.
5. Dodać mechanizm Ask/Confirm i tryby dry-run/execute w runtime (to element, którego brakuje w Structured Outputs i function-calling).
6. Opcjonalnie: wzbogacić workflow o prosty orchestrator (state machine) wzorowany na lekkim workflow DSL (Temporal/Argo-like) jeśli potrzebujesz retries, orchestration i durable tasks.

Uzasadnienie rekomendacji: to podejście minimalizuje pracę (wykorzystuje sprawdzone mechanizmy JSON Schema + function-calling) i jednocześnie daje formalną, audytowalną warstwę policy (OPA). Pozwala szybko zbudować MVP (LLM generuje poprawny JSON/YAML; runtime waliduje i symuluje; policy blokuje niebezpieczeństwa) i stopniowo rozbudowywać semantykę DSL i orchestrator.

## 8. Co możemy zastosować natychmiast (przykładowe kroki)

- Stworzyć JSON Schema dla Twojego DSL (TASK/STEP/WHEN/DO/ASK/CONFIRM/POLICY). Pożyteczne do natychmiastowego wymuszania formatu przez LLM (OpenAI response_format).[^2]
- Zaprojektować mapping DO -> tool description (params + schema) i użyć funkcji (function-calling) do uruchamiania bezpiecznych primitive.[^4]
- Przekształcić POLICY.md (część twardych zasad) do reguł OPA (Rego) i integrować z runtime jako pre-execution check.
- Dodać w runtime tryby dry-run i ask/confirm; raport pełen evidence.


## 9. Wnioski (krótkie podsumowanie)

- Nie istnieje pojedynczy standard, który od razu spełnia wszystkie Twoje wymagania, ale kombinacja: Structured Outputs (JSON Schema) + function-calling + policy engine (OPA) + lekkie workflow DSL da praktycznie cały zakres funkcjonalny.[^1][^2][^4]
- Twoje zaproponowane konstrukcje (TASK/INPUT/SOURCE/STEP/WHEN/DO/ASK/CONFIRM/OUTPUT/POLICY/ALLOW/DENY/REQUIRE/ASSERT) dobrze mapują się na tę hybrydową architekturę: JSON Schema dla struktury, function descriptions dla akcji, i OPA dla polityk. (wniosek własny)

---

Referencje / źródła (wybrane)

- OpenAI — Introducing Structured Outputs in the API (response_format / JSON Schema).[^2][^1]
- Community threads i przykłady użycia Structured Outputs i function-calling (przykłady praktyczne).[^3][^5][^4]
- Ogólne artykuły/poradniki o uzyskiwaniu strukturalnych wyjść (tutoriale).[^6][^7]

Jeśli chcesz, mogę teraz:

- przygotować gotowy JSON Schema dla Twojego DSL (TASK/STEP/WHEN/DO/ASK/CONFIRM/POLICY), z przykładami input/output (MVP), lub
- napisać prompt (TS) wykorzystujący OpenAI response_format (JSON Schema) aby LLM generował DSL-request zgodny ze schematem, albo
- przygotować przykład mappingu DO -> function description (tool) i prosty policy check w Rego.

Który z tych akcji mam wykonać następny?
<span style="display:none">[^10][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://openai.com/index/introducing-structured-outputs-in-the-api/

[^2]: https://developers.openai.com/api/docs/guides/structured-outputs

[^3]: https://community.openai.com/t/handling-structured-output-in-function-tool-calls-with-file-search/1123228

[^4]: https://community.openai.com/t/calling-tool-from-assistant-using-structured-output/1044378

[^5]: https://community.openai.com/t/difference-between-structured-outputs-and-function-calling-required/937697

[^6]: https://medium.com/@piyushsonawane10/getting-structured-outputs-from-openai-models-a-developers-guide-3090e8120785

[^7]: https://www.youtube.com/watch?v=eJvYafgLh40

[^8]: https://openai.com/ja-JP/index/introducing-structured-outputs-in-the-api/

[^9]: https://community.openai.com/t/how-can-i-use-function-calling-with-response-format-structured-output-feature-for-final-response/965784

[^10]: https://community.openai.com/t/partially-structured-output-free-text-output-but-force-correct-tool-call-json/955147

