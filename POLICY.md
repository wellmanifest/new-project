# POLICY — DSL regułowy projektu

## 1. System

```dsl
SYSTEM polityka_projektu
  DOMENA:    nazewnictwo, modularnosc, zarzadzanie_zaleznosciami, technologie, jakosc_kodu, bezpieczenstwo, zasieg, zgodnosc
  ZASADA:    kazda_regula_ma_warunek_i_konsekwencje
```

## 2. Reguły nazewnictwa

```dsl
REGULA R001: nazwa_repozytorium
  DANE: repo_name
  JESLI repo_name PASUJE_DO /^[a-z0-9](-?[a-z0-9]+)*$/ TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE
    ZWROC_BLAD("R001: nazwa repozytorium musi byc lowercase i hyphen-separated; zakaz wielkich liter i podkreslnikow")
  KONIEC
KONIEC

REGULA R002: nazwa_pakietu
  DANE: package_name, repo_name
  JESLI package_name = repo_name TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE JESLI package_name PASUJE_DO /^[a-z0-9-]+$/ TO
    ZWROC_OSTRZEZENIE("R002: package_name powinien zgadzac sie z repo_name")
  W_PRZECIWNYM_RAZIE
    ZWROC_BLAD("R002: package_name musi byc lowercase i hyphen-separated")
  KONIEC
KONIEC

REGULA R003: nazwa_pliku_lub_katalogu
  DANE: path
  JESLI path ZAWIERA(spacja) LUB ZAWIERA(wielka_litera) LUB ZAWIERA(podkreslenie) TO
    ZWROC_BLAD("R003: nazwy plikow i katalogow musza byc lowercase, hyphen-separated, bez spacji")
  KONIEC
KONIEC
```

## 3. Reguły modularności

```dsl
REGULA R101: pojedyncza_odpowiedzialnosc
  DANE: module
  JESLI module.jednoznaczny_cel = PRAWDA
     I module.wejscie_jasne = PRAWDA
     I module.wyjscie_jasne = PRAWDA
     I module.zaleznosci = minimalne
     I module.testowalny = PRAWDA TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE
    ZWROC_BLAD("R101: modul musi miec jeden cel, jasne wejscie/wyjscie, minimalne zaleznosci i byc testowalny")
  KONIEC
KONIEC

REGULA R102: granice_modulow
  DANE: module_a, module_b
  JESLI sprzezenie(module_a, module_b) = niskie
     I kohezja(module_a) = wysoka
     I szczegoly_wewnetrzne(module_a) = ukryte
     I dokumentacja(module_a) = istnieje TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE
    ZWROC_BLAD("R102: moduly musza byc slabo sprzezone, spojne, hermetyzowane i udokumentowane")
  KONIEC
KONIEC

REGULA R103: struktura_katalogow
  DANE: tree
  JESLI istnieje(src) I istnieje(tests) I istnieje(docs) TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE
    ZWROC_OSTRZEZENIE("R103: zalecana struktura: src/, tests/, docs/, examples/, scripts/, config/")
  KONIEC
KONIEC

REGULA R104: projektowanie_komponentow
  DANE: component
  JESLI component.zakres = skupiony
     I (component.reusable = PRAWDA LUB uzasadniony_wyjatek)
     I component.konfigurowalny = PRAWDA
     I component.versioned = PRAWDA TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE
    ZWROC_BLAD("R104: komponent musi byc skupiony, konfigurowalny i wersjonowany; wielokrotne uzycie wymaga uzasadnienia")
  KONIEC
KONIEC
```

## 4. Reguły zarządzania zależnościami

```dsl
REGULA R201: dodaj_zaleznosc
  DANE: dependency
  JESLI dependency.necessary = FALSZ TO ZWROC_BLAD("R201: zaleznosc nie jest konieczna")
  JESLI dependency.mature = FALSZ TO ZWROC_BLAD("R201: zaleznosc nie jest dojrzala i stabilna")
  JESLI dependency.secure = FALSZ TO ZWROC_BLAD("R201: zaleznosc ma problemy bezpieczenstwa")
  JESLI dependency.compatible = FALSZ TO ZWROC_BLAD("R201: zaleznosc niekompatybilna ze stosem")
  JESLI dependency.license_ok = FALSZ TO ZWROC_BLAD("R201: licencja niekompatybilna")
  JESLI wszystkie_powyzsze = PRAWDA TO
    DODAJ_DO(plik_zaleznosci, dependency)
    ZWROC_OK
  KONIEC
KONIEC

REGULA R202: wersja_zaleznosci
  DANE: dependency
  JESLI dependency.version = pinned_lub_dokladna TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE
    ZWROC_OSTRZEZENIE("R202: wersja zaleznosci powinna byc przypieta dla reprodukowalnosci")
  KONIEC
KONIEC

REGULA R203: rozdziel_zaleznosci
  DANE: dependency
  JESLI dependency.uzywana_w_produkcji = PRAWDA TO
    DODAJ_DO(zaleznosci_produkcyjne)
  JESLI dependency.uzywana_w_rozwoju = PRAWDA TO
    DODAJ_DO(zaleznosci_rozwojowe)
  JESLI dependency.opcjonalna = PRAWDA TO
    OZNACZ_JAKO(opcjonalna)
  KONIEC
KONIEC

REGULA R204: aktualizuj_zaleznosc
  DANE: dependency, nowa_wersja
  1. PRZECZYTAJ(changelog)
  2. JESLI changelog ZAWIERA "breaking change" TO
       WYKONAJ(testy_przed_i_po)
       ZAPISZ(wymagane_zmiany_kodu)
     KONIEC
  3. AKTUALIZUJ_PO_JEDNEJ_NA_RAZ(dependency)
  4. WYKONAJ(testy_calego_projektu)
  5. JESLI testy = OK TO ZWROC_OK
  6. W_PRZECIWNYM_RAZIE COFNIJ_WERSJE_LUB_NAPRAW
KONIEC
```

## 5. Reguły praktyk — dozwolone i zabronione

```dsl
REGULA R301: dozwolone_praktyki
  DLA akcji W {pisz_kod, uzywaj_vcs, tworz_testy, semwer, changelog, ci_cd, dokumentacja, security, code_review, planowanie}:
    JESLI akcja.wykonana = PRAWDA I akcja.zgodna_z_policy = PRAWDA TO
      ZWROC_OK
    W_PRZECIWNYM_RAZIE
      ZWROC_OSTRZEZENIE("R301: oczekiwano praktyki " + akcji)
    KONIEC
  KONIEC
KONIEC

REGULA R302: zabronione_antywzorce
  DLA akcji W {duplikacja_funkcjonalnosci, pomijanie_testow, commit_sekretow, ignorowanie_podatnosci, kod_bez_dokumentacji, breaking_bez_wersji, pominiecie_review, ignorowanie_dlugu, dzialanie_bez_planu}:
    JESLI akcja.wykryta = PRAWDA TO
      ZWROC_BLAD("R302: zabronione dzialanie: " + akcji)
    KONIEC
  KONIEC
KONIEC
```

## 6. Reguły wyboru technologii

```dsl
REGULA R401: wybor_jezyka
  DANE: project_requirements, team_expertise, ecosystem, performance, maintenance
  JESLI project_requirements.spehnione_przez(team_expertise, ecosystem, performance, maintenance) = PRAWDA TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE
    ZWROC_BLAD("R401: jezyk nie spelnia wymagan projektu, ekipy, ekosystemu, wydajnosci lub utrzymania")
  KONIEC
KONIEC

REGULA R402: wybor_frameworka
  DANE: scope, complexity, support, docs, learning_curve, performance, integration
  JESLI ocena(scope, complexity, support, docs, learning_curve, performance, integration) >= akceptowalna TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE
    ZWROC_BLAD("R402: framework nie spelnia kryteriow wyboru")
  KONIEC
KONIEC

REGULA R403: wybor_narzedzia
  DANE: problem, tool
  JESLI tool.rozwiazuje(problem) = PRAWDA
     I tool.dojrzaly = PRAWDA
     I tool.dokumentacja = dobra
     I tool.license_ok = PRAWDA TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE
    ZWROC_BLAD("R403: narzedzie nie rozwiazuje problemu, nie jest dojrzale, slabo udokumentowane lub ma niekompatybilna licencje")
  KONIEC
KONIEC
```

## 7. Reguły jakości kodu

```dsl
REGULA R501: styl_kodu
  DLA pliku W kod:
    JESLI plik.zgodny_ze_stylem = PRAWDA
       I plik.formatowanie_spojne = PRAWDA
       I plik.nazwy_znaczace = PRAWDA
       I plik.funkcje_skupione = PRAWDA TO
      ZWROC_OK
    W_PRZECIWNYM_RAZIE
      ZWROC_OSTRZEZENIE("R501: styl kodu wymaga poprawy")
    KONIEC
  KONIEC
KONIEC

REGULA R502: testy_dla_krytycznej_logiki
  DLA logiki_krytycznej W kod:
    JESLI istnieje(test_jednostkowy) LUB istnieje(test_integracyjny) TO
      ZWROC_OK
    W_PRZECIWNYM_RAZIE
      ZWROC_BLAD("R502: krytyczna logika wymaga testow")
    KONIEC
  KONIEC
KONIEC

REGULA R503: pokrycie_testami
  DANE: coverage
  JESLI coverage >= 0.80 TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE
    ZWROC_OSTRZEZENIE("R503: pokrycie testami ponizej 80%")
  KONIEC
KONIEC

REGULA R504: dokumentacja
  DLA publicznego_api W kod:
    JESLI publiczne_api.opisane = PRAWDA
       I publiczne_api.przyklady_dzialaja = PRAWDA
       I publiczne_api.aktualne = PRAWDA TO
      ZWROC_OK
    W_PRZECIWNYM_RAZIE
      ZWROC_BLAD("R504: publiczne API i zlozone algorytmy wymagaja aktualnej dokumentacji z przykladami")
    KONIEC
  KONIEC
KONIEC
```

## 8. Reguły bezpieczeństwa

```dsl
REGULA R601: sekrety
  DLA sekretu W {haslo, token, klucz_api, certyfikat_prywatny}:
    JESLI sekret.wystepuje_w_diff = PRAWDA TO
      USUN_LUB_ZAMASKUJ(sekret)
      ZWROC_BLAD("R601: wykryto sekret w diff")
    KONIEC
  KONIEC
KONIEC

REGULA R602: walidacja_wejscia
  DLA dane_wejsciowe:
    JESLI dane_wejsciowe.zwalidowane = PRAWDA
       I dane_wejsciowe.oczyszczone = PRAWDA
       I dane_wejsciowe.queries_parametryzowane = PRAWDA
       I dane_wejsciowe.rate_limit = PRAWDA TO
      ZWROC_OK
    W_PRZECIWNYM_RAZIE
      ZWROC_BLAD("R602: dane wejsciowe musza byc zwalidowane, oczyszczone, queries parametryzowane i rate-limited")
    KONIEC
  KONIEC
KONIEC

REGULA R603: audyt_zaleznosci
  CO okres:
    WYKONAJ(npm_audit) LUB WYKONAJ(pip-audit)
    JESLI podatna_zaleznosc = wykryta TO
      ZAKTUALIZUJ_LUB_ZASTAP(podatna_zaleznosc)
    KONIEC
  KONIEC
KONIEC
```

## 9. Reguły komunikacji i współpracy

```dsl
REGULA R701: commit_message
  DANE: message
  JESLI message PASUJE_DO /^(feat|fix|test|docs|refactor|build|ci|chore|security)(\(.+\))?: .+/ TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE
    ZWROC_BLAD("R701: commit message musi byc w formacie conventional commits")
  KONIEC
KONIEC

REGULA R702: code_review
  PRZED merge:
    WYKONAJ(review)
    JESLI review.znajduje_podatnosci = PRAWDA TO NAPRAW
    JESLI review.pokrycie_testami = niewystarczajace TO UZUPELNIJ_TESTY
    JESLI review.dokumentacja_nieaktualna = PRAWDA TO ZAKTUALIZUJ_DOKUMENTACJE
    JESLI wszystkie_kryteria = OK TO ZWROC_OK
  KONIEC
KONIEC

REGULA R703: issue_tracking
  DLA issue:
    JESLI issue.tytul_opisowy = PRAWDA
       I issue.kroki_reprodukcji = PRAWDA
       I issue.kategoria = przypisana
       I issue.status = aktualny TO
      ZWROC_OK
    W_PRZECIWNYM_RAZIE
      ZWROC_OSTRZEZENIE("R703: issue wymaga opisowego tytulu, krokow reprodukcji, kategorii i aktualnego statusu")
    KONIEC
  KONIEC
KONIEC
```

## 10. Reguły zakresu i granic

```dsl
REGULA R801: zakres_projektu
  DANE: feature
  JESLI feature.zgodna_z_celami = PRAWDA
     I (feature.konieczna = PRAWDA LUB feature.plugin = PRAWDA)
     I feature.koszt_utrzymania <= akceptowalny
     I feature.alternatywy_rozwazone = PRAWDA TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE
    ZWROC_BLAD("R801: feature poza zakresem lub nieuzasadniona")
  KONIEC
KONIEC

REGULA R802: deprecjonowanie
  DANE: feature
  JESLI feature.usuwana = PRAWDA TO
    OZNACZ_JAKO(deprecated)
    WYDEDYKUJ_GUIDE(migracji)
    UTRZYMUJ_PRZEZ(major_version = obecna)
    USUN_W(major_version = nastepna)
  KONIEC
KONIEC
```

## 11. Reguły zgodności i licencji

```dsl
REGULA R901: licencje
  DANE: component
  JESLI component.licencja = wybrana
     I component.licencja_zaleznosci_kompatybilna = PRAWDA
     I component.atrybucje = kompletne TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE
    ZWROC_BLAD("R901: brak licencji, niekompatybilna licencja zaleznosci lub brak atrybucji")
  KONIEC
KONIEC

REGULA R902: zgodnosc_prawna
  DANE: project
  JESLI project.rodo = spelnione
     I project.ip = respektowane
     I project.dostepnosc = uwzgledniona
     I project.dokumentacja_zgodnosci = istnieje TO
    ZWROC_OK
  W_PRZECIWNYM_RAZIE
    ZWROC_OSTRZEZENIE("R902: braki w zgodnosci prawnej lub dostepnosci")
  KONIEC
KONIEC
```

## 12. Reguły ciągłego doskonalenia

```dsl
REGULA R1001: przeglad_polityki
  CO okres:
    WYKONAJ(review POLICY.md)
    JESLI zmiana_wymagana = PRAWDA TO
      ZAPROPONUJ_ZMIANE
      UZASADNIJ
      POINFORMUJ_ZESPOL
      WPROWADZ
      ZAKTUALIZUJ(CHANGELOG)
    KONIEC
  KONIEC
KONIEC

REGULA R1002: metryki
  CO okres:
    ZMIERZ(jakosc_kodu)
    ZMIERZ(pokrycie_testami)
    ZMIERZ(wydajnosc)
    ZMIERZ(incydenty_bezpieczenstwa)
    ZMIERZ(skutecznosc_procesu)
    ZAPISZ(metryki)
  KONIEC
KONIEC
```

## 13. Procedura rozstrzygania naruszeń

```dsl
PROCEDURA obsluz_naruszenie(regula, wykryty_stan):
  1. ZIDENTYFIKUJ(regula, wykryty_stan)
  2. JESLI wykryty_stan.poziom = BLAD TO
       ZATRZYMAJ(dalsza_praca)
       ZGLOS(wymagana_naprawa)
     KONIEC
  3. JESLI wykryty_stan.poziom = OSTRZEZENIE TO
       ZAPISZ_DO_RAPORTU(wykryty_stan)
       ROZWAZ(korekte)
     KONIEC
  4. JESLI wykryty_stan.poziom = OK TO
       KONTYNUUJ
     KONIEC
KONIEC
```
