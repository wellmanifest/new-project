# CONTRIBUTING — DSL operacyjny dla agenta AI

## 1. System

```dsl
SYSTEM agent-AI
  WEJSCIE:  repo_path, zadanie_uzytkownika
  WYJSCIE:  zmiany_w_repo, raport_weryfikacji, log_commitow

  REPOZYTORIUM new-project
    TYP:     standardy_dokumentacyjne, polityki, skrypt_analityczny
    ISTNIEJE: README.md, CONTRIBUTING.md, POLICY.md, LICENSE, project.sh, docs/README.md
    BRAK:     src/, tests/, CI, Docker, TODO.md (dynamiczny), CHANGELOG.md (dynamiczny)
```

## 2. Rejestr dokumentów

```dsl
REGISTRY dokumenty
  CONTRIBUTING.md  = ten_plik (entrypoint)
  README.md        = standard_pracy
  POLICY.md        = reguly_ograniczen_i_decyzji
  project.sh       = automatyzacja_srodowiska_i_narzedzi
  docs/README.md   = indeks_dokumentacji
  TODO.md          = kolejka_zadan (opcjonalny)
  CHANGELOG.md     = historia_zmian (opcjonalny)
```

## 3. Procedura start

```dsl
PROCEDURA start(zadanie):
  1. PRZECZYTAJ(CONTRIBUTING.md)
  2. PRZECZYTAJ(POLICY.md)
  3. PRZECZYTAJ(README.md)
  4. JESLI zadanie DOTYCZY(narzedzia, srodowisko, instalacja, project.sh) TO
       PRZECZYTAJ(project.sh)
  5. JESLI istnieje(docs/README.md) TO
       PRZECZYTAJ(docs/README.md)
  6. JESLI istnieje(TODO.md) TO
       PRZECZYTAJ(TODO.md)
  7. WYKONAJ(verify_state)
  8. JESLI zadanie WYMAGA_PLANU() TO
       WYKONAJ(create_or_update_TODO)
  9. WYKONAJ(plan_steps)
 10. WYKONAJ(execute_steps)
 11. WYKONAJ(verify_and_commit)
KONIEC
```

## 4. Funkcje pomocnicze

```dsl
FUNKCJA verify_state():
  status = git_status()
  log    = git_log(--oneline -10)
  struct = tree(-L 2) LUB ls -R
  ZAPISZ_DO_RAPORTU(status, log, struct)
  JESLI status ZAWIERA konflikty TO ZATRZYMAJ(zglos_konflikt)
KONIEC

FUNKCJA create_or_update_TODO():
  JESLI istnieje(TODO.md) TO
    ODCZYTAJ(TODO.md)
    DODAJ_ETAPY(zadanie)
    ZAPISZ(TODO.md)
  W_PRZECIWNYM_RAZIE
    UTWORZ(TODO.md)
    ZAPISZ(naglowek, etapy, kryteria_akceptacji, ryzyka)
  KONIEC
KONIEC

FUNKCJA plan_steps():
  etapy = PODZIEL(zadanie, logiczne_kroki)
  DLA kazdego etapu W etapy:
    okresl_wejscie(etap)
    okresl_wyjscie(etap)
    okresl_kryterium_akceptacji(etap)
    okresl_narzedzie_lub_agenta(etap)  // patrz REGULA reuse_first
    JESLI ryzyko(etap) > NISKIE TO
      DODAJ_DO(TODO.md, ryzyko)
  KONIEC
KONIEC
```

## 5. Reguła nadrzędna — reuse first

```dsl
REGULA reuse_first(etap):
  JESLI istnieje(narzedzie_lokalne, etap) I jest_wywolywalne(narzedzie_lokalne) TO
    UZYJ(narzedzie_lokalne, etap)
  W_PRZECIWNYM_RAZIE JESLI istnieje(skrypt, etap) TO
    UZYJ(skrypt, etap)
  W_PRZECIWNYM_RAZIE JESLI istnieje(workflow, etap) TO
    UZYJ(workflow, etap)
  W_PRZECIWNYM_RAZIE JESLI istnieje(agent_zewnetrzny, etap) I jest_wywolywalny(agent_zewnetrzny) TO
    UZYJ(agent_zewnetrzny, etap)
  W_PRZECIWNYM_RAZIE
    ZAIMPLEMENTUJ(etap, rozwiazanie_minimalne)
  KONIEC
KONIEC
```

## 6. Reguły stanu repozytorium

```dsl
REGULA nie_zakladaj_niepotwierdzonych():
  JESLI NIE istnieje(src/) LUB NIE istnieje(tests/) LUB NIE istnieje(CI) LUB NIE istnieje(Dockerfile) TO
    NIE_MOW("aplikacja jest gotowa")
    NIE_MOW("testy przeszly")
    NIE_MOW("CI dziala")
    NIE_MOW("Docker dziala")
    NIE_MOW("agent specjalistyczny jest dostepny bez weryfikacji")
  KONIEC
KONIEC

REGULA weryfikuj_agenta(nazwa_agenta):
  JESLI istnieje(kod_agenta) I istnieje(sposob_wywolania) TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE
    ZWROC_BLAD("agent " + nazwa_agenta + " nie jest potwierdzony w repozytorium")
  KONIEC
KONIEC
```

## 7. Reguły pracy podczas zmian

```dsl
REGULA minimalna_zmiana():
  DLA kazdej zmiany:
    OGRANICZ_ZAKRES(zmiana, jeden_logiczny_cel)
    PO_KAZDYM_ETAPIE WYKONAJ(git diff)
    JESLI git_diff ZAWIERA nieoczekiwane_zmiany TO
      PRZYWROC(lub_zatwierdz_po_weryfikacji)
  KONIEC
KONIEC

REGULA rozroznij_aktywne_zakomentowane():
  JESLI komenda ROZPOCZYNA_SIE_OD("#") TO
    UZNAC_ZA_ZAKOMENTOWANA
    NIE_WYKONUJ_BEZ_UZASADNIENIA
  W_PRZECIWNYM_RAZIE
    UZNAC_ZA_AKTYWNA
    MOZNA_WYKONAC_JESLI_BEZPIECZNA
  KONIEC
KONIEC
```

## 8. Reguły bezpieczeństwa

```dsl
REGULA zakazane_dzialania():
  JESLI akcja = usun_testy_bo_nie_przechodza TO ZABRON
  JESLI akcja = wylacz_testy_bez_uzasadnienia TO ZABRON
  JESLI akcja = zmien_oczekiwany_wynik_testu_dla_sukcesu TO ZABRON
  JESLI akcja = pomin_test_jako_zaliczony TO ZABRON
  JESLI akcja = zadeklaruj_testy_nieuruchomione TO ZABRON
  JESLI akcja = ukryj_blad_infrastruktury_testowej TO ZABRON
  JESLI akcja = force_push_bez_zgody TO ZABRON
  JESLI akcja = commit_sekretow_lub_danych_dostepowych TO ZABRON
  JESLI akcja = uruchom_force_lub_nadpisz_bez_weryfikacji TO ZABRON
KONIEC

REGULA sprawdz_sekrety_przed_commitem():
  JESLI diff ZAWIERA wzorzec_sekretu TO
    USUN_LUB_ZAMASKUJ(sekret)
    ZATRZYMAJ(zglos_wyciek)
  KONIEC
KONIEC
```

## 9. Reguły zatrzymania

```dsl
REGULA zatrzymaj_sie_i_zapytaj():
  JESLI wymagania_sa_sprzeczne_lub_niepelne TO ZATRZYMAJ
  JESLI akcja_jest_destrukcyjna(rm -rf, git push --force, nadpisanie_plikow) TO ZATRZYMAJ
  JESLI brakuje_danych_dostepowych TO ZATRZYMAJ
  JESLI dokumentacja_wyklucza_kod TO ZATRZYMAJ
  JESLI zadanie_wymaga_narzedzia_ktorego_nie_potwierdziles TO ZATRZYMAJ
  JESLI ryzyko_operacji > akceptowalne TO ZATRZYMAJ
KONIEC
```

## 10. Procedura commit i push

```dsl
PROCEDURA commit_and_push():
  1. JESLI diff_pusty TO ZWROC(bez_zmian)
  2. WYKONAJ(sprawdz_sekrety_przed_commitem)
  3. WYKONAJ(git diff --check)
  4. WYKONAJ(testy_jesli_dostepne)
  5. ZAKTUALIZUJ(TODO.md)
  6. ZAKTUALIZUJ(CHANGELOG.md) JESLI publikowalny_zakres
  7. WERSJA = aktualizuj_wersje_jesli_wymagane
  8. FORMUŁUJ_COMMIT(type(scope): opis)
  9. JESLI uzytkownik_zatwierdzil_lub_zlecil TO WYKONAJ(git push)
 10. W_PRZECIWNYM_RAZIE ZATRZYMAJ(czekaj_na_zgode)
KONIEC
```

## 11. Definition of Done

```dsl
CHECKLIST definition_of_done:
  [ ] wymagania_spełnione
  [ ] TODO.md_aktualne
  [ ] uzyto_wlasciwych_narzedzi_lub_agentow
  [ ] testy_wykonane_przez_wlasciwe_narzedzia (lub zgloszono_brak)
  [ ] wyniki_testow_sprawdzone
  [ ] problemy_naprawione
  [ ] testy_ponownie_uruchomione
  [ ] walidacja_zakonczona_powodzeniem
  [ ] docker_dziala_jesli_wymagany
  [ ] dokumentacja_aktualna
  [ ] changelog_zaktualizowany_jesli_publikowalny_zakres
  [ ] wersja_zaktualizowana_jesli_wymagane
  [ ] commity_logiczne
  [ ] push_wykonany_po_zgode
  [ ] brak_sekretow
  [ ] brak_nieopisanych_blokad
```

## 12. Rozstrzyganie konfliktów

```dsl
REGULA hierarchia_zrodel():
  PRIORYTET(zrodlo):
    1. bezposrednie_polecenie_uzytkownika
    2. rzeczywisty_stan_repozytorium
    3. POLICY.md
    4. README.md
    5. CONTRIBUTING.md (ten plik)
  JESLI dokumentacja_jest_sprzeczna_ze_stanem TO
    ZGLOS_ROZBIEEZNOSC
    POSTEPUJ_ZGODNIE_Z(priorytet_2)
  KONIEC
KONIEC
```

## 13. Ściągawka

```dsl
SCIAGAWKA:
  1. CZYTAJ: CONTRIBUTING.md -> POLICY.md -> README.md -> project.sh (jesli narzedzia)
  2. SPRAWDZ: git status, git log -10, tree -L 2
  3. PLANUJ: TODO.md dla zadan > 1 krok
  4. DZIALAJ: minimalne zmiany, diff po etapie
  5. WERYFIKUJ: sekrety, testy, odwolania, dokumentacja
  6. COMMIT: logiczne, po zgodzie push
  7. STOP: destrukcyjne, sprzeczne, niepotwierdzone
```