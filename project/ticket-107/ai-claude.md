---
participant-id: agent:claude
participant: claude
role: agent
ticket: ticket-107
---
# Participant: claude (AI agent)

## Understanding

Slice dystrybucyjny zapowiedziany w `ticket-106`. Kontrakt host-agnostyczny był
egzekwowany tylko tam, gdzie istniał, czyli w hubie. Zadanie: rozesłać go
kanałem, który już działa, i naprawić instalator.

## Execution plan

1. Dopisać pliki hostów, hooka i sam kontrakt do `package-manifest.json` jako
   `managed`, zachowując zwarty format tego pliku.
2. Dodać szablony adopterów w `template/files/`, odrębne od plików huba.
3. Przepisać instalator tak, żeby czytał kontrakt i manifest zamiast listy
   wpisanej na sztywno, i rozdzielić aktywację w miejscu od bootstrapu.
4. Wyprowadzić fixture testowy z kontraktu, żeby nie zostawał w tyle.

## Actual changes

- `governance/package-manifest.json`: osiem nowych wpisów `managed` —
  `CLAUDE.md`, `GEMINI.md`, reguła Cursora, `.aider.conf.yml`,
  `.githooks/pre-commit`, `.governance/agent-hosts.json`, jego schema i
  `.governance/agent_host_check.py`.
- `template/files/`: trzy szablony adopterów; treść huba i adoptera różnią
  się, tak jak w przypadku `AGENTS.template.md`.
- `scripts/install-agent-hosts.sh`: przepisany, `--check`, aktywacja w miejscu,
  bootstrap sterowany manifestem.
- `tests/agent-hosts.test.sh`: fixture generuje pliki hostów z kontraktu;
  bootstrap musi dostarczyć również sam kontrakt.
- `tests/adoption-lock.test.sh`: fixture kopiuje każde źródło z
  `package-manifest.json` zamiast listy wpisanej ręcznie.

Dwa defekty wyszły dopiero przy uruchomieniu, nie przy czytaniu kodu:

1. Bootstrap kopiował wyłącznie pliki hostów, więc target nie dostawał
   `agent-hosts.json` i nie dawał się aktywować. Zbiór kopiowanych plików
   obejmuje teraz również źródło kontraktu.
2. `local x; x="$(cmd)"` maskuje kod wyjścia, więc brak kontraktu nie przerywał
   skryptu, tylko szedł dalej z pustą wartością i ustawiał
   `core.hooksPath=`. Deklaracja jest teraz oddzielona od przypisania.

Dowody: wszystkie 11 zestawów `tests/*.test.sh` PASS, `agent_host_check` PASS,
`audit_diagnostics` 74 kody bez findings, brama `GOV-PASS`.

## Blockers

- Hosty `aider` i `copilot` nie zmieściły się w limicie dziewięciu plików i są
  zapisane jako non-goals. Kolejność cięć była wymuszona: naprawa fixture'u
  adopcyjnego jest warunkiem weryfikowalności tego slice'u, więc miała
  pierwszeństwo przed dwoma dodatkowymi hostami.
- New authority is still required for destructive action, secret access, new
  external coordination or material objective expansion.
