---
participant-id: agent:claude
participant: claude
role: agent
ticket: ticket-106
---
# Participant: claude (AI agent)

## Understanding

Zadanie od Foundera: sprawić, żeby standardy Wellmanifest dało się realnie
narzucić dowolnemu narzędziu AI, a nie tylko opisać w `AGENTS.md`, i żeby
zasady były kontrolowane technicznie — również na styku paczek i CI.

Audyt stanu przed zmianą (39 katalogów w workspace, 25 adopterów):

- `AGENTS.md` w 37/39 repozytoriów i jest managed z digestem — zero driftu.
- `CLAUDE.md`, `GEMINI.md`, reguła Cursora, `.githooks/pre-commit` tylko w
  hubie (1/39). Brak `.aider.conf.yml`, instrukcji Copilota, `.windsurfrules`,
  `.pre-commit-config.yaml` w całym workspace.
- `core.hooksPath` nieustawiony w hubie, w 25 adopterach i w 12 worktree —
  jedyny tool-agnostyczny egzekutor był martwy wszędzie.
- Kody `GOV-AGENT-HOST-001..003` istniały wyłącznie w hooku; nie było ich w
  `diagnostics.json` ani w `rule-enforcement.json`, bo `audit_diagnostics.py`
  nie skanował `.githooks`.
- Żaden `pyproject.toml` ani `package.json` nie miał deklaracji governance;
  `GOV-STACK-001` sprawdza tylko obecność markera, nigdy jego zawartości.

Wniosek prowadzący do projektu: plik instrukcji nie jest egzekucją. Egzekwują
tylko trzy warstwy — hook gita, CI z ochroną brancha, i lifecycle scripts
menedżera paczek. Trzecia była całkowicie niewykorzystana.

## Execution plan

1. Zadeklarować kontrakt raz w `governance/agent-hosts.json` plus schema.
2. Napisać `scripts/agent_host_check.py` jako samodzielne CLI i wpiąć je do
   `governance_check.py` tym samym wzorcem, którym wpięty jest
   `decision_record`.
3. Zarejestrować nowe kody z runbookami i rozesłać runbooki adopterom.
4. Pokryć przypadki negatywne w `tests/agent-hosts.test.sh`.
5. Dystrybucję i job CI wydzielić do zależnych slice'ów.

## Actual changes

- `governance/agent-hosts.json` + `governance/agent-hosts.schema.json`: SSOT
  hostów, hooka i bindingów pakietowych.
- `scripts/agent_host_check.py`: walidator `GOV-AGENT-HOST-004..006` i
  `GOV-PACKAGING-001..003`; `--actor ci` pomija sprawdzenie lokalne, którego
  runner nie może spełnić.
- `scripts/governance_check.py`: `check_agent_hosts` w `run_governance_checks`.
- `governance/diagnostics.json`: 68 → 74 kody, każdy nowy z runbookiem.
- `governance/package-manifest.json`: rozsyła oba runbooki do adopterów jako
  managed, bo rejestracja kodu z `documentation` obliguje do dostarczenia pliku.
- `error/GOV-AGENT-HOST.md`, `error/GOV-PACKAGING.md`: kanoniczne runbooki.
- `tests/agent-hosts.test.sh`: fixture adoptera z sześcioma przypadkami
  negatywnymi i dwoma pozytywnymi.

Dowody wykonania:

- `python3 scripts/agent_host_check.py --root .` → `GOV-AGENT-HOST-PASS`.
- `bash tests/agent-hosts.test.sh` → `agent-hosts.test.sh OK`.
- `python3 scripts/audit_diagnostics.py --root .` → `74 codes, 0 findings`.
- Wszystkie 11 zestawów `tests/*.test.sh` → PASS.
- `./project/governance-check.sh --actor agent` → `GOV-PASS`.

## Blockers

- Brama odrzuciła pierwotny zakres przez `GOV-BUDGET-001`: 17 plików
  implementacji przy limicie 9 z `manifest.hub.json`. Zakres został podzielony
  zgodnie z remediacją, a nie rozszerzony. Slice dystrybucyjny i slice CI
  czekają na merge tego ticketu, bo `maxActiveTicketsPerWorkstream` wynosi 1,
  a hub ma jeden workstream.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion.
