# POLICY (RULE-DSL)

Ten plik NIE zawiera deklaracji w języku naturalnym. Zawiera **reguły proceduralne**:
z warunku (`WHEN`) wynika skutek (`THEN`). Reguły są deterministyczne i wykonywalne przez agenta.
Wzorzec zgodny z ekosystemem: `redsl` (`condition`/`action`/`priority`) oraz `doql` (`WHEN … THEN`).

## Gramatyka

```ebnf
RULE      = "RULE" ID ":" NEWLINE
            "WHEN" condition NEWLINE
            "THEN" action { NEWLINE "AND" action }
          [ NEWLINE "ELSE" action { NEWLINE "AND" action } ]
            NEWLINE "PRIORITY" ("P0"|"P1"|"P2")
          [ NEWLINE "SOURCE" ref ] .
FACT      = "FACT" path "=" value .
condition = term { ("AND"|"OR") term } .
term      = [ "NOT" ] atom .
atom      = value op value | fn "(" args ")" | "TRUE" | "FALSE" .
op        = "=="|"!="|">"|"<"|">="|"<="|"IN"|"NOT_IN"|"MATCHES" .
fn        = "EXISTS"|"MISSING"|"CONTAINS"|"CHANGED"|"COUNT" .
action    = verb args .
verb      = "BLOCK"|"FAIL"|"REQUIRE"|"FORBID"|"RUN"|"CREATE"|"UPDATE"
          | "DELEGATE"|"STOP"|"ASK"|"SET"|"EMIT"|"PASS"|"FLAG"|"GOTO" .
```

- **PRIORITY:** `P0` blokuje pracę (twardy warunek), `P1` wymagane przed publikacją, `P2` zalecane.
- **Rozstrzyganie konfliktów:** `user_command` > `repo_state` > `P0` > `P1` > `P2`.
- **Ewaluacja:** przy każdym gate (`pre_edit`, `pre_commit`, `pre_push`, `on_dependency_change`)
  wykonaj wszystkie reguły, których `WHEN` jest prawdziwe; zastosuj `THEN`.

## Fakty bazowe (stan repozytorium)

```dsl
FACT repo.name = "new-project"
FACT repo.kind = "documentation-standard"     # nie aplikacja
FACT repo.has.src = FALSE
FACT repo.has.tests = FALSE
FACT repo.has.ci = FALSE
FACT repo.has.docker = FALSE
FACT tools.registry = "C:/Users/Praca/fork/semcod, C:/Users/Praca/fork/oqlos"
FACT tools.forbidden_path = "C:/Users/Praca/fork/MatthiasLew"   # NIE czytać
```

---

## 1. Nazewnictwo (P0)

```dsl
RULE P-NAME-001:
  WHEN artifact.type == "repository" AND NOT MATCHES(artifact.name, "^[a-z0-9]+(-[a-z0-9]+)*$")
  THEN FAIL "repo name must be lowercase kebab-case"
  PRIORITY P0
  SOURCE POLICY§1.1

RULE P-NAME-002:
  WHEN artifact.name CONTAINS "_" OR MATCHES(artifact.name, "[A-Z]") OR CONTAINS(artifact.name, " ")
  THEN FAIL "no underscores, uppercase or spaces in names"
  PRIORITY P0
  SOURCE POLICY§1.1, §1.3

RULE P-NAME-003:
  WHEN artifact.type == "package"
  THEN REQUIRE package.name == repo.name
  PRIORITY P1
  SOURCE POLICY§1.2

RULE P-NAME-004:
  WHEN artifact.type IN ["file","directory"] AND NOT MATCHES(artifact.name, "^[a-z0-9._-]+$")
  THEN FAIL "file/dir names must be lowercase kebab-case (extensions allowed)"
  PRIORITY P1
  SOURCE POLICY§1.3
```

## 2. Modularność (P1)

```dsl
RULE P-MOD-001:
  WHEN COUNT(module.responsibilities) > 1
  THEN FLAG "split module: single responsibility violated"
  AND CREATE todo.item("refactor: split " + module.path)
  PRIORITY P1
  SOURCE POLICY§2.1

RULE P-MOD-002:
  WHEN module.exposes_internal == TRUE
  THEN FLAG "encapsulate internals; expose only defined interface"
  PRIORITY P2
  SOURCE POLICY§2.2

RULE P-MOD-003:
  WHEN new_component == TRUE AND MISSING(component.interface_doc)
  THEN BLOCK "component requires documented interface before merge"
  PRIORITY P1
  SOURCE POLICY§2.2, §2.4

RULE P-MOD-004:
  WHEN creating_directory == TRUE AND dir.name NOT_IN ["src","tests","docs","examples","scripts","config"]
  THEN ASK "non-standard top-level dir; confirm structure"
  PRIORITY P2
  SOURCE POLICY§2.3
```

## 3. Zależności (P0/P1)

```dsl
RULE P-DEP-001:
  WHEN adding_dependency == TRUE AND dependency.necessity == "unproven"
  THEN BLOCK "justify dependency: prove it cannot be built in-house"
  PRIORITY P1
  SOURCE POLICY§3.1, §3.2

RULE P-DEP-002:
  WHEN target_env == "production" AND dependency.version == "unpinned"
  THEN BLOCK "pin exact version for production dependency"
  PRIORITY P0
  SOURCE POLICY§3.1

RULE P-DEP-003:
  WHEN adding_dependency == TRUE AND MISSING(dependency.declaration_file)
  THEN FAIL "declare dependency in manifest (requirements.txt / pyproject.toml / package.json)"
  PRIORITY P1
  SOURCE POLICY§3.3

RULE P-DEP-004:
  WHEN dependency.license NOT_IN repo.allowed_licenses
  THEN BLOCK "incompatible license"
  PRIORITY P0
  SOURCE POLICY§3.2, §11.1

RULE P-DEP-005:
  WHEN CHANGED(dependency.version)
  THEN RUN test_suite
  AND REQUIRE changelog.note("dependency update")
  PRIORITY P1
  SOURCE POLICY§3.5
```

## 4. Bezpieczeństwo (P0)

```dsl
RULE P-SEC-001:
  WHEN CONTAINS(staged_diff, secret_pattern)
  THEN BLOCK "secret detected; remove before commit"
  PRIORITY P0
  SOURCE POLICY§8.1

RULE P-SEC-002:
  WHEN config.value.is_secret == TRUE AND config.source != "env"
  THEN FAIL "secrets must come from environment variables, not source"
  PRIORITY P0
  SOURCE POLICY§8.1

RULE P-SEC-003:
  WHEN endpoint.accepts_input == TRUE AND MISSING(endpoint.input_validation)
  THEN BLOCK "validate/sanitize external input"
  PRIORITY P1
  SOURCE POLICY§8.2

RULE P-SEC-004:
  WHEN security_advisory.severity IN ["high","critical"] AND dependency.affected == TRUE
  THEN BLOCK "update vulnerable dependency before release"
  PRIORITY P0
  SOURCE POLICY§8.3
```

## 5. Jakość i testy (P1)

```dsl
RULE P-QUA-001:
  WHEN module.role == "critical_logic" AND MISSING(module.unit_tests)
  THEN BLOCK "critical logic requires unit tests"
  PRIORITY P1
  SOURCE POLICY§7.2

RULE P-QUA-002:
  WHEN test_coverage < 80 AND repo.has.tests == TRUE
  THEN FLAG "coverage below 80%"
  PRIORITY P2
  SOURCE POLICY§7.2

RULE P-QUA-003:
  WHEN test.status == "failing"
  THEN FORBID delete_test
  AND FORBID mutate_expected_result_to_pass
  PRIORITY P0
  SOURCE POLICY§5.1, CONTRIBUTING(root)§9.4

RULE P-QUA-004:
  WHEN public_api.changed == TRUE AND MISSING(public_api.doc_update)
  THEN BLOCK "document public API change"
  PRIORITY P1
  SOURCE POLICY§7.3
```

## 6. Wersjonowanie i changelog (P1)

```dsl
RULE P-VER-001:
  WHEN change.type == "breaking"
  THEN REQUIRE version.bump == "MAJOR"
  PRIORITY P1
  SOURCE POLICY§7 (SemVer), README§13

RULE P-VER-002:
  WHEN change.type == "feature" AND change.compatible == TRUE
  THEN REQUIRE version.bump == "MINOR"
  PRIORITY P1
  SOURCE README§13

RULE P-VER-003:
  WHEN change.type == "fix"
  THEN REQUIRE version.bump == "PATCH"
  PRIORITY P1
  SOURCE README§13

RULE P-VER-004:
  WHEN release.publishable == TRUE AND MISSING(changelog.entry_for_version)
  THEN BLOCK "update CHANGELOG.md before release"
  PRIORITY P1
  SOURCE README§14

RULE P-VER-005:
  WHEN version.declared_in.count > 1 AND version.values_consistent == FALSE
  THEN FAIL "version must be consistent across all declared locations"
  PRIORITY P1
  SOURCE README§13
```

## 7. Zakres i cykl życia (P2)

```dsl
RULE P-SCO-001:
  WHEN feature.aligns_with_goals == FALSE
  THEN BLOCK "out of scope; document rationale or reject"
  PRIORITY P2
  SOURCE POLICY§10.1, §10.2

RULE P-SCO-002:
  WHEN feature.removal == TRUE AND MISSING(feature.deprecation_period)
  THEN BLOCK "deprecate before removing; provide migration guide"
  PRIORITY P1
  SOURCE POLICY§10.3

RULE P-SCO-003:
  WHEN policy.change == TRUE
  THEN REQUIRE separate_task
  AND REQUIRE rationale_documented
  PRIORITY P2
  SOURCE POLICY§12.1, README§17
```

## 8. Bramki wykonania (mapowanie gate → reguły)

```dsl
GATE pre_edit        => [P-NAME-*, P-MOD-003, P-SCO-001]
GATE on_dependency   => [P-DEP-*, P-SEC-004]
GATE pre_commit      => [P-SEC-001, P-SEC-002, P-QUA-003, P-NAME-*]
GATE pre_release     => [P-VER-*, P-QUA-001, P-SEC-*, P-SCO-002]
```
