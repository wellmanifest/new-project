# POLICY — reguły proceduralne (DSL)

Ten plik zawiera reguły wyrażone w pseudokodzie proceduralnym. Każda reguła ma postać `JEŚLI ... TO ... W_PRZECIWNYM_RAZIE ...`. Reguły są grupowane w sekcje tematyczne. Agent AI powinien traktować je jako wykonywalne procedury decyzyjne.

---

## Słownik

```text
repo_name      := ciąg znaków identyfikujący repozytorium
package_name   := ciąg znaków identyfikujący pakiet
file_name      := ciąg znaków identyfikujący plik lub katalog
module         := jednostka kodu z jednym wyraźnym celem
dependency     := zewnętrzny pakiet wymagany przez projekt
secret         := hasło, token, klucz API, klucz prywatny, dane środowiskowe
change         := modyfikacja pliku w repozytorium
feature        := nowa funkcjonalność
version        := MAJOR.MINOR.PATCH zgodnie ze SemVer
```

---

## Sekcja A: Nazewnictwo

```text
REGUŁA A-01:
  WEJŚCIE:  repo_name
  JEŚLI:   repo_name MATCHES /^[a-z][a-z0-9-]*$/ AND repo_name NOT CONTAINS '_' AND repo_name NOT CONTAINS ' '
  TO:      repo_name := ACCEPTED
  W_PRZECIWNYM_RAZIE:
            repo_name := REJECTED
            ZGŁOŚ("Repository name must be lowercase, hyphen-separated and descriptive")

REGUŁA A-02:
  WEJŚCIE:  package_name
  JEŚLI:   package_name == repo_name OR package_name MATCHES /^[a-z][a-z0-9-]*$/
  TO:      package_name := ACCEPTED
  W_PRZECIWNYM_RAZIE:
            package_name := REJECTED
            ZGŁOŚ("Package name must match repository name and use hyphen-separated lowercase")

REGUŁA A-03:
  WEJŚCIE:  file_name
  JEŚLI:   file_name MATCHES /^[a-z][a-z0-9.-]*$/ AND file_name NOT CONTAINS ' '
  TO:      file_name := ACCEPTED
  W_PRZECIWNYM_RAZIE:
            file_name := REJECTED
            ZGŁOŚ("File/directory names must be lowercase, hyphen-separated and contain no spaces")
```

---

## Sekcja B: Struktura repozytorium

```text
PROCEDURA verify_structure(project_dir):
  WEJŚCIE:  project_dir
  WYJŚCIE:  report

  1. required_dirs := ["src", "tests", "docs", "examples", "scripts", "config"]
  2. required_files := ["README.md", "CONTRIBUTING.md", "POLICY.md", "LICENSE"]
  3. DLA każdego d IN required_dirs:
       JEŚLI EXISTS(project_dir / d) TO report.dirs[d] := OK
       W_PRZECIWNYM_RAZIE report.dirs[d] := MISSING
  4. DLA każdego f IN required_files:
       JEŚLI EXISTS(project_dir / f) TO report.files[f] := OK
       W_PRZECIWNYM_RAZIE report.files[f] := MISSING
  5. ZWRÓĆ report

REGUŁA B-01:
  WEJŚCIE:  report := verify_structure(project_dir)
  JEŚLI:   report.files["README.md"] == OK AND report.files["CONTRIBUTING.md"] == OK
  TO:      CONTINUE
  W_PRZECIWNYM_RAZIE:
            STOP("Create missing README.md or CONTRIBUTING.md before publishing")
```

---

## Sekcja C: Modułowość

```text
REGUŁA C-01:
  WEJŚCIE:  module
  JEŚLI:   module.purpose IS_DEFINED AND module.interface IS_DEFINED AND module.dependencies.count <= 3
  TO:      module := VALID
  W_PRZECIWNYM_RAZIE:
            module := INVALID
            ZGŁOŚ("Module must have one clear purpose, defined interface and minimal dependencies")

REGUŁA C-02:
  WEJŚCIE:  module_a, module_b
  JEŚLI:   module_a.imports(module_b) AND module_b.imports(module_a)
  TO:      ZGŁOŚ("Cyclic dependency detected; refactor to break coupling")
  W_PRZECIWNYM_RAZIE: CONTINUE

REGUŁA C-03:
  WEJŚCIE:  module
  JEŚLI:   EXISTS(test_file(module)) AND module.public_api IS_DOCUMENTED
  TO:      module := TESTABLE_AND_DOCUMENTED
  W_PRZECIWNYM_RAZIE:
            ZGŁOŚ("Module must be independently testable and documented")
```

---

## Sekcja D: Zarządzanie zależnościami

```text
PROCEDURA evaluate_dependency(dep):
  WEJŚCIE:  dep
  WYJŚCIE:  decision IN {ACCEPT, REJECT}

  1. necessary      := NOT can_build_inhouse(dep.functionality)
  2. mature         := dep.stable AND dep.maintained
  3. secure         := dep.no_known_vulnerabilities
  4. compatible     := dep.works_with(project_stack)
  5. licensed       := dep.license_compatible_with(project_license)
  6. JEŚLI necessary AND mature AND secure AND compatible AND licensed
       TO decision := ACCEPT
     W_PRZECIWNYM_RAZIE:
       decision := REJECT
       ZGŁOŚ("Dependency rejected: fails one of necessary/mature/secure/compatible/licensed")
  7. ZWRÓĆ decision

REGUŁA D-01:
  WEJŚCIE:  dep_list
  JEŚLI:   FOR EACH dep IN dep_list: dep.version IS_PINNED
  TO:      dep_list := REPRODUCIBLE
  W_PRZECIWNYM_RAZIE:
            ZGŁOŚ("All production dependencies must have pinned versions")

REGUŁA D-02:
  WEJŚCIE:  dep
  JEŚLI:   dep.type == "production" AND dep.type == "development"
  TO:      ZGŁOŚ("Production and development dependencies must be declared separately")
  W_PRZECIWNYM_RAZIE: CONTINUE

REGUŁA D-03:
  WEJŚCIE:  dep
  JEŚLI:   dep.security_advisory == TRUE
  TO:      MUST_UPDATE(dep) WITHIN minimal_reasonable_time
  W_PRZECIWNYM_RAZIE: CONTINUE
```

---

## Sekcja E: Jakość kodu

```text
REGUŁA E-01:
  WEJŚCIE:  function
  JEŚLI:   function.lines <= 40 AND function.does_one_thing
  TO:      function := ACCEPTED
  W_PRZECIWNYM_RAZIE:
            ZGŁOŚ("Function should be focused and small")

REGUŁA E-02:
  WEJŚCIE:  codebase
  JEŚLI:   codebase.test_coverage >= 0.80
  TO:      codebase := COVERAGE_OK
  W_PRZECIWNYM_RAZIE:
            codebase := COVERAGE_LOW
            ZGŁOŚ("Maintain test coverage above 80%")

REGUŁA E-03:
  WEJŚCIE:  code_change
  JEŚLI:   code_change.follows_style_guide AND code_change.has_meaningful_names
  TO:      code_change := STYLE_OK
  W_PRZECIWNYM_RAZIE:
            ZGŁOŚ("Code must follow style guide and use meaningful names")

REGUŁA E-04:
  WEJŚCIE:  component
  JEŚLI:   component.reusable AND component.configurable AND component.versioned
  TO:      component := DESIGN_OK
  W_PRZECIWNYM_RAZIE:
            ZGŁOŚ("Components should be reusable, configurable and versioned")
```

---

## Sekcja F: Testowanie

```text
PROCEDURA run_tests(scope):
  WEJŚCIE:  scope IN {unit, integration, regression, startup, install, api, docker, e2e, multiplatform}
  WYJŚCIE:  result

  1. runner := FIND_TEST_RUNNER(scope)
  2. JEŚLI runner EXISTS
       TO result := EXEC(runner, scope)
     W_PRZECIWNYM_RAZIE:
       result := MISSING_RUNNER
       ZGŁOŚ("No test runner for scope " + scope)
  3. ZWRÓĆ result

REGUŁA F-01:
  WEJŚCIE:  test_result
  JEŚLI:   test_result.status == FAILED
  TO:      MUST_REPAIR_BEFORE_MERGE(test_result.failures)
  W_PRZECIWNYM_RAZIE: CONTINUE

REGUŁA F-02:
  WEJŚCIE:  test
  JEŚLI:   test.status == SKIPPED AND test.reason IS_NOT_DOCUMENTED
  TO:      REJECT(test)
  W_PRZECIWNYM_RAZIE: CONTINUE

REGUŁA F-03:
  WEJŚCIE:  expected_result, actual_result
  JEŚLI:   expected_result != actual_result AND change_was_made_to(expected_result)
  TO:      REJECT(change)
  W_PRZECIWNYM_RAZIE: CONTINUE
```

---

## Sekcja G: Dokumentacja

```text
REGUŁA G-01:
  WEJŚCIE:  change
  JEŚLI:   change.modifies_public_api AND NOT change.updates_docs
  TO:      REJECT(change)
  W_PRZECIWNYM_RAZIE: CONTINUE

REGUŁA G-02:
  WEJŚCIE:  doc
  JEŚLI:   doc.refers_to_removed_element
  TO:      doc.mark_obsolete AND UPDATE_OR_REMOVE(doc)
  W_PRZECIWNYM_RAZIE: CONTINUE

REGUŁA G-03:
  WEJŚCIE:  feature
  JEŚLI:   feature.limitations IS_NOT_DOCUMENTED
  TO:      REQUIRE_DOCUMENTATION(feature.limitations)
  W_PRZECIWNYM_RAZIE: CONTINUE
```

---

## Sekcja H: Bezpieczeństwo

```text
REGUŁA H-01:
  WEJŚCIE:  change
  JEŚLI:   change.contains(secret)
  TO:      REJECT(change) AND ALERT("Secret detected in commit")
  W_PRZECIWNYM_RAZIE: CONTINUE

REGUŁA H-02:
  WEJŚCIE:  user_input
  JEŚLI:   user_input.source == external
  TO:      user_input := VALIDATE(user_input) AND SANITIZE(user_input)
  W_PRZECIWNYM_RAZIE: CONTINUE

REGUŁA H-03:
  WEJŚCIE:  dependency
  JEŚLI:   dependency.known_vulnerability == TRUE
  TO:      MUST_UPDATE_OR_REPLACE(dependency)
  W_PRZECIWNYM_RAZIE: CONTINUE

REGUŁA H-04:
  WEJŚCIE:  query
  JEŚLI:   query.uses_external_data AND NOT query.parameterized
  TO:      REJECT(query)
  W_PRZECIWNYM_RAZIE: CONTINUE
```

---

## Sekcja I: Zarządzanie zmianami (commity, wersje, changelog)

```text
REGUŁA I-01:
  WEJŚCIE:  commit_msg
  JEŚLI:   commit_msg MATCHES /^(feat|fix|test|docs|refactor|build|ci|chore|security)(\(.+\))?: .+/
  TO:      commit_msg := ACCEPTED
  W_PRZECIWNYM_RAZIE:
            commit_msg := REJECTED
            ZGŁOŚ("Commit message must use conventional commit format")

REGUŁA I-02:
  WEJŚCIE:  change_set
  JEŚLI:   change_set.count == 1 AND change_set.coherent
  TO:      change_set := ACCEPTED
  W_PRZECIWNYM_RAZIE:
            ZGŁOŚ("Commits should be atomic and logical")

REGUŁA I-03:
  WEJŚCIE:  version_change, public_api_change
  JEŚLI:   public_api_change.breaking == TRUE AND version_change.major == 0
  TO:      REJECT(version_change)
  W_PRZECIWNYM_RAZIE: CONTINUE

REGUŁA I-04:
  WEJŚCIE:  release_scope
  JEŚLI:   release_scope.is_publishable AND EXISTS("CHANGELOG.md")
  TO:      UPDATE("CHANGELOG.md", release_scope.changes)
  W_PRZECIWNYM_RAZIE:
            JEŚLI release_scope.is_publishable TO ZGŁOŚ("CHANGELOG.md is required for publishable releases")
```

---

## Sekcja J: Zakres i cykl życia funkcji

```text
REGUŁA J-01:
  WEJŚCIE:  feature_proposal
  JEŚLI:   feature_proposal.aligns_with(project_goals) AND feature_proposal.necessary_for_core
  TO:      feature_proposal := ACCEPT
  W_PRZECIWNYM_RAZIE:
            JEŚLI feature_proposal.can_be_plugin TO feature_proposal := PROPOSE_AS_PLUGIN
            W_PRZECIWNYM_RAZIE feature_proposal := REJECT

REGUŁA J-02:
  WEJŚCIE:  feature
  JEŚLI:   feature.deprecated AND feature.last_major_version >= current_major - 1
  TO:      feature := MAINTAIN_WITH_DEPRECATION_WARNING
  W_PRZECIWNYM_RAZIE:
            JEŚLI feature.deprecated TO feature := REMOVE_IN_NEXT_MAJOR
            W_PRZECIWNYM_RAZIE feature := KEEP
```

---

## Sekcja K: Zgodność prawna

```text
REGUŁA K-01:
  WEJŚCIE:  dependency
  JEŚLI:   dependency.license IN project.compatible_licenses
  TO:      dependency := LICENSE_OK
  W_PRZECIWNYM_RAZIE:
            dependency := LICENSE_REJECTED
            ZGŁOŚ("Dependency license is incompatible with project license")

REGUŁA K-02:
  WEJŚCIE:  third_party_code
  JEŚLI:   third_party_code.attribution == PROVIDED
  TO:      third_party_code := OK
  W_PRZECIWNYM_RAZIE:
            ZGŁOŚ("Third-party code must be properly attributed")
```

---

## Sekcja L: Ciągłe doskonalenie

```text
PROCEDURA review_policy():
  1. metrics := COLLECT(code_quality, test_coverage, security_incidents, process_effectiveness)
  2. JEŚLI metrics.show_regression
       TO TRIGGER(policy_update_proposal)
     W_PRZECIWNYM_RAZIE CONTINUE
  3. ZWRÓĆ metrics
```
