# Wellmanifest SemVer

Standard Semantycznego Wersjonowania (SemVer) i Potoków CI/CD dla heterogenicznych systemów rozproszonych łączących komputery brzegowe (np. Raspberry Pi 5) oraz mikrokontrolery sterujące z oprogramowaniem układowym (np. M5Stack CoreS3 / ESP32-S3).

Wersja normatywna: **0.1.0**. HOME: `wellmanifest`.

---

## Kluczowe zasady standardu

- **Separacja wersji (`SEMVER-001`)**: Rozdzielenie wersji systemu, hosta brzegowego (Linux/RPi5) oraz firmware mikrokontrolera (ESP32-S3).
- **Niezmienna tożsamość binarna (`SEMVER-002`)**: Każda wersja SemVer firmware jest powiązana z unikalnym skrótem kompilacji (`ELF SHA256`) i skrótem binarnym (`SHA256`).
- **Definicje zmian SemVer w sprzęcie (`SEMVER-005` - `SEMVER-007`)**:
  - `MAJOR`: zmiana pinoutu/GPIO, zmiana układu partycji Flash, zmiana protokołu komunikacji.
  - `MINOR`: nowy sterownik, nowy moduł peryferyjny (np. obsługa COMMU TTL UART), nowe endpointy bez utraty wstecznej zgodności.
  - `PATCH`: bugfixy pętli sterowania, optymalizacje timeoutów, poprawki mechanizmu safe-state.
- **Wymóg bezpiecznego stanu spoczynku (`SEMVER-012`)**: Blokada flashowania (HTTP 409 Conflict), jeśli silniki, pompy lub zawory są aktywne.
- **A/B Dual-Bank OTA (`SEMVER-013`)**: Zapis do partycji nieaktywnej z ochroną `If-Match`.
- **Samo-weryfikacja i sprzętowy rollback (`SEMVER-015` - `SEMVER-016`)**: Stan `pending_verify` po reboocie i automatyczny powrót do poprzedniego obrazu w razie awarii.
- **Separacja Git Merge od flashowania sprzętu (`SEMVER-018`)**: Zgodnie z `wellmanifest/merge`, commit na `main` nie flashuje automatycznie mikrokontrolerów.

---

## Narzędzia i weryfikacja zgodności

Walidator jest deterministyczny, czyta deklaracje w trybie offline i nie wymaga fizycznego dostępu do sprzętu:

```bash
# Uruchomienie testów jednostkowych
python3 -m unittest discover -s tests -v

# Walidacja przykładowego manifestu wydania
python3 operations/conformance.py examples/heterogeneous-release-manifest.json

# Wynik w formacie JSON
python3 operations/conformance.py examples/heterogeneous-release-manifest.json --json
```

---

## Spis dokumentów

- [Pełna specyfikacja standardu](docs/information/embedded-semver-standard.md)
- [Katalog reguł normatywnych (`policy.json`)](policy.json)
- [Manifest DSL (`dsl-manifest.json`)](dsl-manifest.json)
- [Schemat manifestu wydania (`schemas/embedded-release.schema.json`)](schemas/embedded-release.schema.json)
- [Schemat macierzy sprzętowej (`schemas/hardware-matrix.schema.json`)](schemas/hardware-matrix.schema.json)
- [Schemat atestacji potoku (`schemas/pipeline-run.schema.json`)](schemas/pipeline-run.schema.json)
- [Przykłady (`examples/`)](examples/)
