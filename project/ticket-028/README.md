# Ticket 028: Require every pull request to name its active ticket

- **ID**: ticket-028
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-06

## Cel i Zakres

`P-CORE-015` dopuszcza `github-app-review` jako zaufane zatwierdzenie merge'a i
jednocześnie żąda `ASSERT APPROVAL_IDENTIFIES_CURRENT_ACTIVE_TICKET`. Dziś nic
w tym repozytorium nie wymusza, żeby pull request w ogóle nazywał swój ticket —
więc żaden zewnętrzny walidator nie jest w stanie tego assertu spełnić.

Dowód, nie hipoteza. Skan `wellmanifest/new-project` wykonany przez
`ifuri-validator-agent` 2026-08-06 pominął trzy z czterech otwartych PR-ów:

```
Skipped wellmanifest/new-project#37: no ticket in `Ticket:` body line, ticket/NNN- branch or title
Skipped wellmanifest/new-project#36: no ticket in `Ticket:` body line, ticket/NNN- branch or title
Skipped wellmanifest/new-project#34: no ticket in `Ticket:` body line, ticket/NNN- branch or title
```

PR #34 jest przypadkiem granicznym wartym zapamiętania: jego opis odwołuje się
do „ticket 020" i „tickets 018 and 021", nie mając własnego ticketu. Atrybucja
po prozie zatwierdziłaby go pod cudzym ticketem, więc walidator celowo tego nie
robi — i słusznie pomija PR.

Zakres: konwencja atrybucji plus bramka, która ją egzekwuje. Poza zakresem
pozostaje jakakolwiek zmiana w tym, kto merguje — to `ticket-029`.

## Kryteria Odbioru (Acceptance Criteria)

- [ ] AC-01: Konwencja atrybucji jest zapisana w `CONTRIBUTING.md` — linia
  `Ticket: ticket-NNN` w opisie PR albo gałąź `ticket/NNN-*` — z jawnym
  stwierdzeniem, że wzmianka o cudzym tickecie w prozie atrybucją nie jest.
- [ ] AC-02: Bramka w `tests/` odrzuca zestaw zmian bez wyprowadzalnego
  ticketu i przyjmuje każdą z dwóch dopuszczonych form; test niesie przypadek
  negatywny wzorowany na treści PR #34.
- [ ] AC-03: Bramka jest uruchamiana przez `.github/workflows/ci.yml` i jest
  wymieniona wśród wymaganych checków w `docs/GOVERNANCE_ENFORCEMENT.md`.
- [ ] AC-04: Dowód: PR realizujący ten ticket jest pomijany przez skan
  walidatora przed zmianą i atrybuowany po niej.

## Ryzyka i Uwagi

- Ryzyko: wymóg zablokuje pilny hotfix bez ticketu. Mitygacja: bramka orzeka o
  atrybucji, nie o istnieniu katalogu — `ticket/NNN-*` wystarczy, a numer
  przydziela alokator w kilka sekund.
- Uwaga: `#34`, `#36` i `#37` są otwarte i nieatrybuowalne. Ten ticket nie
  naprawia ich wstecz; ich autorzy muszą dodać linię `Ticket:` albo zmienić
  nazwę gałęzi.
- Uwaga: `#34` i `#35` są dodatkowo `DIRTY` (konflikt z `main`), a `#34` ma
  pięć nierozwiązanych wątków od `copilot-pull-request-reviewer` przy regule
  `required_review_thread_resolution: true`. To blokady niezależne od
  atrybucji.

## Uczestnicy

- Human participant: unresolved; `user-*` is created only by its human owner
  or a trusted intake boundary.
- Agent participant: `ai-claude.md`

## Granica katalogu

Ten katalog przechowuje governance, decyzje, logi i dowody. Kod wykonywalny,
skrypty badawcze i testy należą do zwykłych katalogów źródłowych repozytorium,
nie do `project/ticket-028/`.
