---
participant-id: agent:claude
participant: claude
role: agent
ticket: ticket-113
---
# Participant: claude (AI agent)

## Understanding

Domknięcie długu zaciągniętego świadomie w `ticket-107`. Tamten slice musiał
wybrać między dwoma hostami a naprawą fixture'u adopcyjnego; wybrał fixture,
bo bez niego slice nie był weryfikowalny. Ten ticket oddaje resztę.

## Execution plan

1. Dodać oba hosty do `governance/agent-hosts.json`.
2. Dodać pliki huba i szablony adopterów.
3. Rozesłać je przez `package-manifest.json` jako managed.

## Actual changes

- `governance/agent-hosts.json`: hosty `aider` i `copilot`; kontrakt obejmuje
  teraz sześć hostów.
- `.aider.conf.yml`, `.github/copilot-instructions.md`: pliki huba.
- `template/files/aider.template.yml`,
  `template/files/copilot-instructions.template.md`: wersje dla adopterów.
- `governance/package-manifest.json`: dwa wpisy managed; 55 plików w pakiecie.

Zwrot z wcześniejszej decyzji: `tests/agent-hosts.test.sh` nie wymagał żadnej
edycji. Fixture generuje pliki hostów z kontraktu od `ticket-107`, więc oba
nowe hosty są pokryte automatycznie. Gdyby lista pozostała wpisana ręcznie,
ten ticket musiałby ją poprawiać — i mógłby o tym zapomnieć.

Dowody: `agent_host_check` PASS, `tests/agent-hosts.test.sh` PASS,
`tests/adoption-lock.test.sh` PASS, brama `GOV-PASS`.

## Blockers

- None inside the recorded intent.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion.
