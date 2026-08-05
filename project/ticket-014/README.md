# Ticket 014: Kanoniczna klasyfikacja pracy BUG, FEATURE, SERVICE

- **ID**: ticket-014
- **Owner**: unresolved:human
- **Status**: IN_PROGRESS
- **Workflow state**: VALIDATION
- **Utworzono**: 2026-08-05

## Cel i zakres

Opublikować wersjonowany, deterministyczny kontrakt DSL klasyfikujący pracę na
dwóch niezależnych osiach: `kind` (`BUG`, `FEATURE`, `SERVICE`) i `priority`
(`P0`–`P3`). Kontrakt ma definiować kolejność `BUG > FEATURE > SERVICE`, ale
zachować zależności jako nadrzędne ograniczenie wykonania.

## Kryteria odbioru

- [x] AC-01: Kanoniczny dokument `new-project.work-classification/v1` i jego
  schemat są walidowane deterministycznie.
- [x] AC-02: Kolejność jest jednoznaczna: zależności, rodzaj pracy, priorytet,
  stabilny identyfikator.
- [x] AC-03: Reguły CC rozróżniają regresję (`BUG`) od istniejącego długu
  technicznego (`SERVICE`) i nie wymagają LLM.
- [x] AC-04: Artefakty klasyfikacji należą do wersjonowanego pakietu adopcji.
- [x] AC-05: Testy odrzucają nieznany rodzaj, nieznany priorytet, duplikaty
  kolejności oraz niepełną regułę CC.

## Ryzyka i mitygacje

- Zależność oznaczona jako `SERVICE` może odblokowywać `BUG`; dlatego porządek
  topologiczny ma pierwszeństwo przed rankingiem.
- Sam poziom CC nie dowodzi regresji; klasyfikacja używa porównania baseline →
  head albo oznaczenia długu istniejącego przed zmianą.
- Historyczne artefakty zachowują zgodność; wymagane pola pojawią się dopiero w
  nowych kontraktach konsumentów.

## Uczestnicy

- Human participant: unresolved; plik `user-*` nie został utworzony.
- Agent participant: [`ai-codex.md`](ai-codex.md)

## Granica katalogu

Ten katalog przechowuje plan, decyzje i dowody. Implementacja DSL i testy
pozostają w zwykłych katalogach repozytorium.

## Zatwierdzenie interaktywne

Użytkownik zatwierdził `ticket-014` 2026-08-05. Zatwierdzenie pozwala wykonać
zakres `intent.json`, ale nie zastępuje zaufanego merge approval.

## Walidacja

- `bash tests/governance-validator.test.sh` — PASS
- `bash tests/adoption-lock.test.sh` — PASS
- `bash tests/governance-scripts.test.sh` — PASS
- JSON syntax, `git diff --check` i skan nowych obejść fail-fast — PASS
