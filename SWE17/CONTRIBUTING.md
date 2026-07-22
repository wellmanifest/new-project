# CONTRIBUTING — procedury pracy dla agentów AI (DSL)

Ten plik opisuje pracę agenta AI w języku proceduralnym. Każda sekcja zawiera procedury (`PROCEDURA`), reguły decyzyjne (`REGUŁA`) i funkcje pomocnicze (`FUNKCJA`). Agent powinien wykonywać kroki w podanej kolejności, chyba że polecenie użytkownika stanowi inaczej.

---

## Słownik

```text
task           := zadanie przekazane przez użytkownika
repo_state     := aktualny stan repozytorium (pliki, katalogi, git)
doc_set        := zbiór dokumentów: README.md, POLICY.md, CONTRIBUTING.md, project.sh, TODO.md
available_tool := narzędzie potwierdzone w repo_state lub w project.sh
available_agent:= agent potwierdzony w repo_state (kod, konfiguracja, sposób wywołania)
change         := modyfikacja pliku lub plików w repozytorium
test_result    := wynik uruchomienia testów
```

---

## Procedura główna: START(task)

```text
PROCEDURA START(task):
  WEJŚCIE:  task (opis zadania od użytkownika)
  WYJŚCIE:  plan lub raport o odmowie wykonania

  1. READ("CONTRIBUTING.md")
  2. READ("README.md")
  3. READ("POLICY.md")
  4. READ("project.sh") JEŚLI task.dotyczy_narzędzi LUB task.dotyczy_środowiska
  5. repo_state := COLLECT_GIT_STATUS()        // git status, git log --oneline -10
  6. repo_state.tree := LIST_DIRECTORY_TREE(depth=2)
  7. JEŚLI task.ma_więcej_niż_jeden_krok
       TO CREATE_OR_UPDATE("TODO.md", task)
  8. known_limitations := LOAD("GPT56Luna/ANALIZA-DOKUMENTACJI.md") JEŚLI EXISTS
  9. plan := ANALYZE(task, repo_state, known_limitations)
  10. ZWRÓĆ plan
```

---

## Procedura analizy wymagania

```text
PROCEDURA ANALYZE(task, repo_state, known_limitations):
  WEJŚCIE: task, repo_state, known_limitations
  WYJŚCIE: plan

  1. requirements := EXTRACT_REQUIREMENTS(task)
  2. DLA każdego r IN requirements:
       2.1. existing := FIND_EXISTING_SOLUTION(r, repo_state)
       2.2. JEŚLI existing.found
              TO r.strategy := REUSE(existing)
            W_PRZECIWNYM_RAZIE:
              r.strategy := IMPLEMENT(r)
  3. plan.steps := PRIORITIZE(requirements)
  4. plan.risks := KNOWN_RISKS(known_limitations)
  5. plan.acceptance_criteria := DEFINE_ACCEPTANCE_CRITERIA(task)
  6. ZWRÓĆ plan

FUNKCJA FIND_EXISTING_SOLUTION(requirement, repo_state):
  1. SEARCH narzędzia w project.sh
  2. SEARCH agenci (Tylko JEŚLI EXISTS kod/konfiguracja w repo_state)
  3. SEARCH skrypty w scripts/
  4. SEARCH workflow w .devin/workflows/
  5. SEARCH komponenty w src/ LUB packages/ JEŚLI EXISTS
  6. JEŚLI match.confidence >= HIGH
       TO ZWRÓĆ match
     W_PRZECIWNYM_RAZIE:
       ZWRÓĆ NOT_FOUND
```

---

## Procedura planowania

```text
PROCEDURA CREATE_OR_UPDATE("TODO.md", task):
  WEJŚCIE: task
  WYJŚCIE: TODO.md

  1. JEŚLI NOT EXISTS("TODO.md") TO CREATE("TODO.md", TEMPLATE)
  2. TODO.current_task := task
  3. TODO.priority := task.priority
  4. TODO.source := "użytkownik"
  5. TODO.acceptance_criteria := task.acceptance_criteria
  6. TODO.steps := task.plan.steps
  7. TODO.blockers := []
  8. WRITE("TODO.md", TODO)

SZABLON TODO:
```markdown
# TODO

## TASK-001 — {{task.title}}

- **Status:** IN_PROGRESS
- **Priorytet:** {{task.priority}}
- **Źródło:** {{task.source}}
- **Kryteria akceptacji:**
  {{task.acceptance_criteria}}

### Etapy

{{#each task.steps}}
- [ ] {{this}}
{{/each}}

### Nowe zadania wykryte podczas pracy

- [ ]
```
```

---

## Procedura delegacji

```text
PROCEDURA DELEGATE(step):
  WEJŚCIE: step (pojedynczy etap planu)
  WYJŚCIE: result

  1. JEŚLI step.type == "test"
       TO result := SELECT_AND_RUN_TEST_TOOL(step)
  2. JEŚLI step.type == "repair"
       TO result := SELECT_AND_RUN_REPAIR_TOOL(step)
  3. JEŚLI step.type == "validate"
       TO result := SELECT_AND_RUN_VALIDATOR(step)
  4. JEŚLI step.type == "todo_management"
       TO result := UPDATE("TODO.md", step)
  5. JEŚLI step.type == "diagnostics"
       TO result := RUN_DIAGNOSTICS(step)
  6. JEŚLI step.type == "documentation"
       TO result := EXECUTE_DOCUMENTATION_STEP(step)
  7. JEŚLI NO_MATCH
       TO result := EXECUTE_MANUALLY(step)
  8. ZWRÓĆ result

REGUŁA DELEGATE-01:
  WEJŚCIE: step, available_agent
  JEŚLI:   available_agent.exists AND available_agent.handles(step.type)
  TO:      result := CALL(available_agent, step)
  W_PRZECIWNYM_RAZIE:
            result := EXECUTE_MANUALLY(step) AND LOG("Agent " + available_agent.name + " not available; executed manually")
```

---

## Reguły wyboru narzędzi

```text
FUNKCJA SELECT_TOOL(purpose):
  1. JEŚLI purpose == "project_architecture" AND EXISTS("$VENV/bin/code2llm")
       TO ZWRÓĆ "$VENV/bin/code2llm ./ -f all -o ./project --no-chunk --exclude '*.md'"
  2. JEŚLI purpose == "duplicate_detection" AND EXISTS("$VENV/bin/redup")
       TO ZWRÓĆ "$VENV/bin/redup scan . --format toon --output ./project --ext .mjs,.js,.php,.sh"
  3. JEŚLI purpose == "code_quality" AND EXISTS("$VENV/bin/prefact")
       TO ZWRÓĆ "$VENV/bin/prefact -a -e \"examples/**\""
  4. JEŚLI purpose == "batch_llm" AND EXISTS("$VENV/bin/vallm")
       TO ZWRÓĆ "$VENV/bin/vallm batch . --recursive --format toon --output ./project"
  5. JEŚLI purpose == "doql_adopt" AND EXISTS("$VENV/bin/doql")
       TO ZWRÓĆ "$VENV/bin/doql adopt . --format less --output app.doql.less --force"
  6. JEŚLI purpose == "markdown_summary" AND EXISTS("$VENV/bin/sumd")
       TO ZWRÓĆ "$VENV/bin/sumd ."
  7. JEŚLI purpose == "report_summary" AND EXISTS("$VENV/bin/sumr")
       TO ZWRÓĆ "$VENV/bin/sumr ."
  8. JEŚLI purpose == "goal_management" AND EXISTS("$VENV/bin/goal")
       TO ZWRÓĆ "$VENV/bin/goal -a"
  9. W_PRZECIWNYM_RAZIE:
       ZWRÓĆ TOOL_NOT_AVAILABLE

REGUŁA TOOL-01:
  WEJŚCIE: tool_command
  JEŚLI:   tool_command IS_COMMENTED_IN("project.sh") AND task.requires_tool == FALSE
  TO:      DO_NOT_EXECUTE(tool_command)
  W_PRZECIWNYM_RAZIE: CONTINUE

REGUŁA TOOL-02:
  WEJŚCIE: tool_command, package
  JEŚLI:   project.sh.installs(package) AND project.sh.does_not_run(package)
  TO:      MARK_AS_INSTALLED_ONLY(package)
  W_PRZECIWNYM_RAZIE: CONTINUE
```

---

## Reguły wyboru agentów

```text
FUNKCJA SELECT_AGENT(role):
  1. agent_path := "subactor/" + role  // np. subactor/test-agent
  2. JEŚLI EXISTS(agent_path) AND EXISTS(agent_path / "README.md" OR agent_path / "run.sh" OR agent_path / "pyproject.toml")
       TO ZWRÓĆ agent_path
     W_PRZECIWNYM_RAZIE:
       ZWRÓĆ AGENT_NOT_CONFIRMED

PROCEDURA DELEGATE_TO_AGENT(role, input):
  WEJŚCIE: role, input
  WYJŚCIE: result

  1. agent := SELECT_AGENT(role)
  2. JEŚLI agent == AGENT_NOT_CONFIRMED
       TO result := FALLBACK_MANUAL(role, input)
     W_PRZECIWNYM_RAZIE:
       result := CALL(agent, input)
  3. ZWRÓĆ result

REGUŁA AGENT-01:
  WEJŚCIE: task
  JEŚLI:   task.requires_tests
  TO:      test_result := DELEGATE_TO_AGENT("test-agent", task)
          ELSE IF test-agent NOT CONFIRMED TO test_result := RUN_LOCAL_TESTS(task)
  W_PRZECIWNYM_RAZIE: CONTINUE

REGUŁA AGENT-02:
  WEJŚCIE: test_result
  JEŚLI:   test_result.failures > 0
  TO:      repair_result := DELEGATE_TO_AGENT("repair-agent", test_result)
          ELSE IF repair-agent NOT CONFIRMED TO repair_result := REPAIR_MANUALLY(test_result)
  W_PRZECIWNYM_RAZIE: CONTINUE

REGUŁA AGENT-03:
  WEJŚCIE: change
  JEŚLI:   change.needs_validation
  TO:      validation_result := DELEGATE_TO_AGENT("validator-agent", change)
          ELSE IF validator-agent NOT CONFIRMED TO validation_result := MANUAL_VALIDATION(change)
  W_PRZECIWNYM_RAZIE: CONTINUE
```

---

## Procedura testowania

```text
PROCEDURA TEST(scope):
  WEJŚCIE: scope (unit, integration, regression, startup, install, api, docker, e2e, multiplatform)
  WYJŚCIE: test_result

  1. runner := FIND_TEST_RUNNER(scope)
  2. JEŚLI runner EXISTS
       TO test_result := EXEC(runner, scope)
     W_PRZECIWNYM_RAZIE:
       test_result := { status: MISSING_RUNNER, message: "No runner for scope " + scope }
  3. JEŚLI test_result.status == FAILED
       TO log_failures(test_result)
  4. ZWRÓĆ test_result

REGUŁA TEST-01:
  WEJŚCIE: change
  JEŚLI:   change.modifies_code AND NOT change.has_tests
  TO:      REQUIRE_TESTS(change)
  W_PRZECIWNYM_RAZIE: CONTINUE

REGUŁA TEST-02:
  WEJŚCIE: test_result
  JEŚLI:   test_result.status == FAILED
  TO:      STOP("Fix failing tests before proceeding")
  W_PRZECIWNYM_RAZIE: CONTINUE
```

---

## Procedura walidacji i naprawy

```text
PROCEDURA VALIDATE(change):
  WEJŚCIE: change
  WYJŚCIE: validation_result

  1. validation_result := CHECK_POLICY_COMPLIANCE(change)
  2. JEŚLI validation_result.issues > 0
       TO REPORT(validation_result.issues)
  3. ZWRÓĆ validation_result

PROCEDURA REPAIR(issues):
  WEJŚCIE: issues (lista problemów)
  WYJŚCIE: repair_result

  1. DLA każdego issue IN issues:
       1.1. JEŚLI issue.auto_fixable
              TO APPLY_FIX(issue)
            W_PRZECIWNYM_RAZIE:
              TO REPORT_TO_USER(issue)
  2. repair_result := RERUN_TESTS_AND_VALIDATION()
  3. ZWRÓĆ repair_result

REGUŁA REPAIR-01:
  WEJŚCIE: issue
  JEŚLI:   issue.requires_architectural_decision
  TO:      STOP_AND_ASK_USER(issue)
  W_PRZECIWNYM_RAZIE: CONTINUE
```

---

## Procedura dokumentowania

```text
PROCEDURA DOCUMENT(change):
  WEJŚCIE: change
  WYJŚCIE: doc_status

  1. JEŚLI change.modifies_public_api
       TO UPDATE("README.md", change)
  2. JEŚLI change.modifies_tool_usage
       TO UPDATE("README.md §5", change)
  3. JEŚLI change.modifies_policy
       TO UPDATE("POLICY.md", change)
  4. JEŚLI change.modifies_workflow
       TO UPDATE("CONTRIBUTING.md", change)
  5. JEŚLI change.removes_feature
       TO MARK_DEPRECATED_OR_REMOVE_REFS(change)
  6. doc_status := VERIFY_REFS(all_docs)
  7. ZWRÓĆ doc_status
```

---

## Procedura commitów

```text
PROCEDURA COMMIT(change_set):
  WEJŚCIE: change_set
  WYJŚCIE: commit_result

  1. DLA każdego f IN change_set:
       1.1. diff := EXEC("git diff " + f)
       1.2. JEŚLI diff CONTAINS secret_pattern TO REJECT(f)
  2. JEŚLI change_set.count > 1 AND NOT change_set.coherent
       TO SPLIT(change_set)
  3. msg := GENERATE_COMMIT_MESSAGE(change_set)
  4. JEŚLI NOT msg MATCHES /^(feat|fix|test|docs|refactor|build|ci|chore|security)(\(.+\))?: .+/
       TO REJECT(msg)
  5. commit_result := EXEC("git commit", msg) // Tylko JEŚLI użytkownik zatwierdził lub wyraźnie zlecił
  6. ZWRÓĆ commit_result

REGUŁA COMMIT-01:
  WEJŚCIE: change_set
  JEŚLI:   change_set CONTAINS secret
  TO:      REJECT(change_set) AND ALERT("Secret detected")
  W_PRZECIWNYM_RAZIE: CONTINUE

REGUŁA COMMIT-02:
  WEJŚCIE: command
  JEŚLI:   command == "git push --force" OR command REMOVES_HISTORY
  TO:      STOP_AND_ASK_USER(command)
  W_PRZECIWNYM_RAZIE: CONTINUE
```

---

## Procedura zakończenia zadania

```text
PROCEDURA FINISH(task, plan):
  WEJŚCIE: task, plan
  WYJŚCIE: finish_report

  1. DLA każdego step IN plan.steps:
       1.1. JEŚLI step.status != DONE AND step.status != BLOCKED
              TO finish_report.complete := FALSE
  2. test_results := TEST(all_scopes)
  3. validation_results := VALIDATE(task.change_set)
  4. JEŚLI test_results.failures == 0 AND validation_results.issues == 0
       TO finish_report.quality := OK
     W_PRZECIWNYM_RAZIE:
       repair_results := REPAIR(test_results.failures + validation_results.issues)
       finish_report.quality := repair_results.quality
  5. DOCUMENT(task.change_set)
  6. JEŚLI task.is_publishable
       TO UPDATE("CHANGELOG.md", task)
       AND UPDATE_VERSION(task.version_bump)
  7. COMMIT(task.change_set)
  8. UPDATE("TODO.md")
  9. ZWRÓĆ finish_report
```

---

## Definition of Done

```text
FUNKCJA is_done(task):
  1. requirements_met := task.requirements.all(r => r.status == DONE OR r.status == BLOCKED_WITH_REASON)
  2. todo_updated := TODO.md IS_CURRENT
  3. tools_used := task.used_tools.all(t => t IN available_tools OR t == MANUAL)
  4. tests_run := test_result.status IN {PASSED, MISSING_RUNNER_WITH_EXPLANATION}
  5. issues_fixed := validation_result.issues == 0
  6. no_secrets := SCAN_SECRETS(task.change_set) == 0
  7. docs_current := DOCUMENT(task.change_set) == OK
  8. changelog_ok := NOT task.is_publishable OR CHANGELOG.md.updated
  9. version_ok := NOT task.is_publishable OR version_updated
  10. ZWRÓĆ requirements_met AND todo_updated AND tools_used AND tests_run AND issues_fixed AND no_secrets AND docs_current AND changelog_ok AND version_ok

REGUŁA DONE-01:
  WEJŚCIE: task
  JEŚLI:   is_done(task) == TRUE
  TO:      task := COMPLETED
  W_PRZECIWNYM_RAZIE:
            task := NOT_DONE
            ZGŁOŚ("Task does not meet Definition of Done")
```

---

## Procedura ciągłego doskonalenia

```text
PROCEDURA SELF_IMPROVE():
  1. gaps := []
  2. JEŚLI narzędzie_było_niewystarczające TO gaps.ADD("Consider new tool for " + tool.shortfall)
  3. JEŚLI etap_wymagał_ręcznej_pracy TO gaps.ADD("Consider automating " + step.name)
  4. JEŚLI brakuje_agenta TO gaps.ADD("Consider defining missing agent")
  5. JEŚLI standard_testów_wymaga_rozszerzenia TO gaps.ADD("Update test standards")
  6. JEŚLI przepływ_między_agentami_jest_niepoprawny TO gaps.ADD("Fix agent coordination")
  7. DLA każdego gap IN gaps:
       ADD_TO("TODO.md", gap)
```

---

## Ściągawka dla agenta

```text
1. START(task)               -> przeczytaj dokumenty, sprawdź git, strukturę, TODO.md
2. ANALYZE()                 -> znajdź istniejące rozwiązania lub zaplanuj implementację
3. DLA każdego step:
     3.1 DELEGATE(step)      -> wybierz narzędzie/agenta lub ręcznie
     3.2 TEST(scope)         -> uruchom testy
     3.3 VALIDATE(change)    -> sprawdź zgodność z POLICY
     3.4 REPAIR(issues)      -> napraw problemy
4. DOCUMENT(change)          -> aktualizuj README, CONTRIBUTING, POLICY, docs
5. FINISH(task)              -> changelog, wersja, commit, TODO.md
6. SELF_IMPROVE()            -> zapisz propozycje usprawnień
```
