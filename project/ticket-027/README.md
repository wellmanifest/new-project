# Ticket 027: Sledzenie egzekwowania regul governance

- **ID**: ticket-027
- **Owner**: unresolved:human
- **Status**: DONE
- **Workflow state**: DONE
- **Utworzono**: 2026-08-05

## Cel i zakres

`POLICY.md` i `CONTRIBUTING.md` deklarują kontrakt jako bloki `RULE`.
`scripts/governance_check.py` egzekwuje jego część jako stabilne kody `GOV-*`.
**Nic nie łączyło tych dwóch warstw.**

Pomiar, nie przypuszczenie:

| | |
| --- | --- |
| reguł normatywnych | **144** |
| kodów egzekwujących | **39** |
| identyfikatorów reguł występujących w walidatorze | **0** |
| kodów `GOV-*` występujących w polityce | **0** |

Reguła mogła stracić swój check, a check przeżyć swoją regułę — i żadna bramka by
tego nie zauważyła. To ta sama klasa błędu co tickety 021 i 025, tylko między
dokumentem a walidatorem zamiast wewnątrz narzędzia.

## Wdrożone

`scripts/audit_rule_enforcement.py` wyprowadza **obie strony**: reguły z
dokumentów, kody z kodu źródłowego walidatora. Ręcznie zapisane jest wyłącznie
**skojarzenie** w `governance/rule-enforcement.json`, bo to wiedza, której parser
nie odtworzy — a że obie strony są wyprowadzane, rozjazd którejkolwiek natychmiast
failuje.

Reguła, której nie da się egzekwować mechanicznie, deklaruje
`enforcement: "manual"` z powodem. Luka jest wtedy **widoczna**, a nie nieobecna.

`tests/rule-enforcement.test.sh` sprawdza kontrakt na żywym repo i dwie mutacje
na kopii, więc checkout nigdy nie jest modyfikowany.

## Znalezisko uboczne w `wellm` — istotne dla wyboru parsera

Reguły czyta frontend `policy-sh@1` z `wellm`, żeby gramatyka miała jednego
właściciela. Przy weryfikacji okazało się, że **`PolicyDialect.looks_like_policy()`
gubi 30 reguł**: sprawdza wyłącznie pierwszą niepustą linię bloku, więc blok
zaczynający się od danych (`"Dockerfile",`) jest odrzucany w całości. Przepadały
całe rodziny `C-DOCKER`, `C-ENV` i `C-EVALUATION`.

`probe()` na tym samym wejściu daje **0.98**, a `parse()` czyta te bloki
poprawnie. Narzędzie używa więc `probe()`, nie `looks_like_policy()`. Po tej
zmianie parser `wellm` i lokalny fallback zgadzają się co do **144**.

Warte zgłoszenia do `wellm`: dwie sondy tego samego dialektu dają sprzeczne
odpowiedzi na to samo źródło.

## Kryteria odbioru

- [x] AC-01: Obie strony wyprowadzane; ręczne jest tylko skojarzenie.
- [x] AC-02: Mapowanie wskazujące nieistniejący kod failuje.
- [x] AC-03: Mapowanie reguły, która zniknęła, failuje.
- [x] AC-04: Reguła bez mechanicznego egzekwowania deklaruje `manual` z powodem.
- [x] AC-05: Liczba reguł jest przypięta, więc regresja parsera jest widoczna.
- [ ] AC-06: Wszystkie 144 reguły sklasyfikowane. Otwarte celowo — to praca
      redakcyjna dla właściciela kontraktu, nie coś, co agent ma zmyślić.
      `--require-complete` włącza ten wymóg, gdy klasyfikacja się domknie.

## Dowód wykonania

- Mutacja „nieistniejący kod" → exit 1 ze wskazaniem `P-CORE-014 -> GOV-DOES-NOT-EXIST`.
- Mutacja „reguła usunięta" → exit 1 ze wskazaniem `P-GONE-999`.
- Przywrócenie → exit 0.
- Sześć zestawów regresyjnych przechodzi.

## Zależność

Dotyka `ci.yml`, tak jak otwarty PR ticketu 025. Ten, który wejdzie drugi,
wymaga rebase. Strażnik kompletności listy z ticketu 025 obejmie ten zestaw
automatycznie.
