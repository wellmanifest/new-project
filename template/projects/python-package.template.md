# Wzorzec Projektowy: Pakiet Python (`python-package`)

Manifest jednoplikowy opisujący kompletną strukturę pakietu Python (layout `src/`, testy `pytest`, konfiguracja `pyproject.toml`). Renderuj przez własny generator (Jinja2) lub narzędzie zgodne z modelem manifestu.

## Zmienne wejściowe

| Zmienna | Opis | Przykład |
| :--- | :--- | :--- |
| `project_name` | Nazwa repozytorium/projektu (kebab-case) | `my-app` |
| `package_name` | Nazwa importowalnego pakietu (snake_case) | `my_app` |
| `author` | Autor / właściciel | `Jan Kowalski` |
| `python_version` | Minimalna wersja Pythona | `3.11` |

## Manifest

```yaml
variables:
  project_name: my-app
  package_name: my_app
  author: Jan Kowalski
  python_version: "3.11"

directories:
  - "{{ project_name }}"
  - "{{ project_name }}/src/{{ package_name }}"
  - "{{ project_name }}/tests"

files:
  - path: "{{ project_name }}/pyproject.toml"
    type: config
    contents: |
      [build-system]
      requires = ["setuptools>=68"]
      build-backend = "setuptools.build_meta"

      [project]
      name = "{{ project_name }}"
      version = "0.1.0"
      description = "Generated project"
      requires-python = ">={{ python_version }}"
      authors = [{ name = "{{ author }}" }]

      [tool.pytest.ini_options]
      testpaths = ["tests"]

  - path: "{{ project_name }}/src/{{ package_name }}/__init__.py"
    type: source
    contents: |
      __version__ = "0.1.0"

  - path: "{{ project_name }}/src/{{ package_name }}/main.py"
    type: source
    contents: |
      def main() -> None:
          print("Hello from {{ project_name }}")

      if __name__ == "__main__":
          main()

  - path: "{{ project_name }}/tests/test_main.py"
    type: test
    contents: |
      from {{ package_name }}.main import main

      def test_main_runs(capsys):
          main()
          assert "Hello" in capsys.readouterr().out

  - path: "{{ project_name }}/README.md"
    type: docs
    contents: |
      # {{ project_name }}

      Pakiet Python wygenerowany z manifestu jednoplikowego.

  - path: "{{ project_name }}/.gitignore"
    type: config
    contents: |
      __pycache__/
      *.py[cod]
      .venv/
      dist/
      build/
      *.egg-info/
```

## Jak wygenerować

1. Wczytaj blok `yaml` z tego pliku.
2. Renderuj zmienne (`{{ ... }}`) silnikiem Jinja2 z sekcją `variables` jako kontekstem.
3. Utwórz katalogi z `directories`, zapisz pliki z `files` (`path` + `contents`).
