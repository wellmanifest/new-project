# CONTRIBUTING (RULE-DSL)

Ten plik NIE jest instrukcją w języku naturalnym. Definiuje **proceduralny przepływ pracy**
jako reguły `WHEN → THEN`. Współpracuje z `POLICY.md` (RULE-DSL): CONTRIBUTING steruje
*procesem*, POLICY egzekwuje *zasady*. Gramatyka i operatory jak w `POLICY.md`.

## Model wykonania

```dsl
STATE = { phase: START|PLAN|WORK|VERIFY|PUBLISH|STOP }
LOOP: on każdym kroku ewaluuj reguły, których WHEN==TRUE, w kolejności PRIORITY (P0→P2).
PRIORITY: P0 = twardy warunek (przerywa), P1 = wymagane, P2 = zalecane.
CONFLICT: user_command > repo_state > POLICY.P0 > CONTRIBUTING.P0 > README > P1 > P2.
```

## Fakty bazowe

```dsl
FACT repo.kind = "documentation-standard"       # nie aplikacja
FACT sot.process = "Opus48Medium/CONTRIBUTING.md"   # ten plik = proces
FACT sot.rules   = "Opus48Medium/POLICY.md"         # zasady
FACT sot.full    = "README.md"                      # pełny standard (PL)
FACT env.venv    = "venv/bin"
FACT tools.registry = "C:/Users/Praca/fork/semcod, C:/Users/Praca/fork/oqlos"
FACT tools.forbidden_path = "C:/Users/Praca/fork/MatthiasLew"   # NIE czytać
FACT agents.subactor.available = FALSE           # brak kodu/wywołania w repo
```

---

## 1. Start sesji (P0)

```dsl
RULE R-START-001:
  WHEN phase == START
  THEN READ [sot.process, sot.rules, sot.full]
  AND RUN "git status" AND RUN "git log --oneline -10"
  AND SET phase = PLAN
  PRIORITY P0

RULE R-START-002:
  WHEN task.touches_tools == TRUE
  THEN READ "project.sh"
  PRIORITY P0

RULE R-START-003:
  WHEN reference.target MISSING
  THEN FORBID use(reference.target)
  AND FLAG "referenced artifact does not exist"
  PRIORITY P0
```

## 2. Planowanie (P1)

```dsl
RULE R-PLAN-001:
  WHEN phase == PLAN AND task.steps > 1
  THEN CREATE_OR_UPDATE "TODO.md" WITH [stages, acceptance_criteria, risks]
  AND SET phase = WORK
  PRIORITY P1

RULE R-PLAN-002:
  WHEN phase == PLAN AND task.steps <= 1
  THEN SET phase = WORK
  PRIORITY P1

RULE R-PLAN-003:
  WHEN capability.needed == TRUE AND EXISTS(tool_for(capability))
  THEN FORBID reimplement(capability)
  AND DELEGATE capability TO tool_for(capability)
  PRIORITY P1
  SOURCE README§2
```

## 3. Wybór i uruchamianie narzędzi (P1)

Klasyfikacja z `project.sh` (stan potwierdzony):

```dsl
FACT tool.active   = ["code2llm","redup","prefact","doql","sumd","sumr"]
FACT tool.installed_only = ["regix","glon","code2logic"]   # zainstalowane, nie wywoływane
FACT tool.commented = ["vallm","goal"]                     # poza bieżącym przepływem

RULE R-TOOL-001:
  WHEN need == "env_setup"
  THEN RUN "bash ./project.sh"
  PRIORITY P1

RULE R-TOOL-002:
  WHEN tool IN tool.active
  THEN RUN env.venv + "/" + tool WITH documented_args
  PRIORITY P1

RULE R-TOOL-003:
  WHEN tool IN tool.installed_only
  THEN REQUIRE read_docs(tool) BEFORE run(tool)
  AND FORBID assume(tool.behavior)
  PRIORITY P1

RULE R-TOOL-004:
  WHEN tool IN tool.commented
  THEN FORBID run(tool) UNLESS justification_recorded
  PRIORITY P0

RULE R-TOOL-005:
  WHEN tool.command CONTAINS "--force"
  THEN REQUIRE diff_review BEFORE and AFTER run
  PRIORITY P0
```

Referencja poleceń aktywnych:

```dsl
CMD code2llm = "venv/bin/code2llm ./ -f all -o ./project --no-chunk --exclude '*.md'"
CMD redup    = "venv/bin/redup scan . --format toon --output ./project --ext .mjs,.js,.php,.sh"
CMD prefact  = "venv/bin/prefact -a -e 'examples/**'"
CMD doql     = "venv/bin/doql adopt . --format less --output app.doql.less --force"
CMD sumd     = "venv/bin/sumd ."
CMD sumr     = "venv/bin/sumr ."
```

## 4. Delegacja i agenci (P0)

```dsl
RULE R-AGENT-001:
  WHEN task.requires_agent == TRUE AND agents.subactor.available == FALSE
  THEN FORBID call_agent_by_name
  AND GOTO R-AGENT-002
  PRIORITY P0

RULE R-AGENT-002:
  WHEN fallback_needed == TRUE AND task.kind == "documentation"
  THEN RUN "git diff --check" AND RUN "git diff"
  AND REQUIRE reference_consistency_check
  PRIORITY P1

RULE R-AGENT-003:
  WHEN fallback_needed == TRUE AND task.kind == "code" AND MISSING(test_runner)
  THEN EMIT limitation("no test runner found")
  AND FORBID claim("tests passed")
  PRIORITY P0
```

## 5. Dyscyplina edycji (P0/P1)

```dsl
RULE R-EDIT-001:
  WHEN phase == WORK
  THEN REQUIRE change.minimal == TRUE
  AND RUN "git diff" AFTER each stage
  PRIORITY P1

RULE R-EDIT-002:
  WHEN statement.claims_available(x) AND EXISTS(x) == FALSE
  THEN FAIL "do not describe unverified artifacts as available"
  PRIORITY P0

RULE R-EDIT-003:
  WHEN doc.contradicts(repo_state)
  THEN CREATE todo.item("resolve doc/reality mismatch") 
  AND EMIT flag
  PRIORITY P1
```

## 6. Publikacja: commit i push (P0)

```dsl
RULE R-PUB-001:
  WHEN phase == PUBLISH
  THEN RUN "git diff"
  AND REQUIRE PASS(POLICY.GATE pre_commit)
  PRIORITY P0

RULE R-PUB-002:
  WHEN commit.pending == TRUE
  THEN REQUIRE MATCHES(commit.message, "^(feat|fix|test|docs|refactor|build|ci|chore|security)(\\(.+\\))?: .+")
  PRIORITY P1
  SOURCE README§12

RULE R-PUB-003:
  WHEN scope.publishable == TRUE
  THEN REQUIRE PASS(POLICY.GATE pre_release)   # wersja + changelog + testy
  PRIORITY P1

RULE R-PUB-004:
  WHEN action IN ["commit","push"] AND user_approval == FALSE AND explicit_task == FALSE
  THEN STOP AND ASK "confirm commit/push"
  PRIORITY P0

RULE R-PUB-005:
  WHEN action == "git push --force" OR action == "history_rewrite"
  THEN BLOCK "requires explicit human consent"
  PRIORITY P0
```

## 7. Warunki zatrzymania (P0)

```dsl
RULE R-STOP-001:
  WHEN requirements.contradictory == TRUE OR requirements.incomplete == TRUE
  THEN STOP AND ASK
  PRIORITY P0

RULE R-STOP-002:
  WHEN action.destructive == TRUE          # rm -rf, force push, overwrite
  THEN STOP AND ASK
  PRIORITY P0

RULE R-STOP-003:
  WHEN credentials.missing == TRUE
  THEN STOP AND ASK
  PRIORITY P0

RULE R-STOP-004:
  WHEN path_access(tools.forbidden_path) requested
  THEN BLOCK "MatthiasLew is off-limits"
  PRIORITY P0

RULE R-STOP-005:
  WHEN backlog.empty == TRUE OR all_tasks.blocked == TRUE
  THEN SET phase = STOP
  PRIORITY P1
```

## 8. Definition of Done (asercje przejścia PUBLISH→STOP)

```dsl
ASSERT DoD:
  REQUIRE sot_references.valid == TRUE
  REQUIRE described_flow == actual_files
  REQUIRE unverified_items.flagged == TRUE
  REQUIRE tool.active SEPARATED_FROM tool.commented
  REQUIRE PASS(POLICY.GATE pre_commit)
  REQUIRE git_diff.no_accidental_changes == TRUE
  REQUIRE git_diff.no_secrets == TRUE
  REQUIRE todo.gaps_and_risks_recorded == TRUE
  ON_FAIL: STOP AND report(unsatisfied_assertions)
```

## 9. Ściągawka (kolejność ewaluacji)

```dsl
START → R-START-* → PLAN → R-PLAN-* → WORK → (R-TOOL-*, R-AGENT-*, R-EDIT-*)
      → VERIFY(POLICY gates) → PUBLISH → R-PUB-* → ASSERT DoD → STOP
```
