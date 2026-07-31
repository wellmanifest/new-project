# Wzorzec Projektowy: Narzędzie CLI w Go (`go-cli`)

Manifest jednoplikowy opisujący aplikację CLI w Go z modułem i testami.

## Zmienne wejściowe

| Zmienna | Opis | Przykład |
| :--- | :--- | :--- |
| `project_name` | Nazwa projektu | `mycli` |
| `module_path` | Ścieżka modułu Go | `github.com/example/mycli` |

## Manifest

```yaml
variables:
  project_name: mycli
  module_path: github.com/example/mycli

directories:
  - "{{ project_name }}"
  - "{{ project_name }}/cmd/{{ project_name }}"
  - "{{ project_name }}/internal/app"

files:
  - path: "{{ project_name }}/go.mod"
    type: config
    contents: |
      module {{ module_path }}

      go 1.22

  - path: "{{ project_name }}/cmd/{{ project_name }}/main.go"
    type: source
    contents: |
      package main

      import (
          "fmt"
          "{{ module_path }}/internal/app"
      )

      func main() {
          fmt.Println(app.Greeting("{{ project_name }}"))
      }

  - path: "{{ project_name }}/internal/app/app.go"
    type: source
    contents: |
      package app

      func Greeting(name string) string {
          return "Hello from " + name
      }

  - path: "{{ project_name }}/internal/app/app_test.go"
    type: test
    contents: |
      package app

      import "testing"

      func TestGreeting(t *testing.T) {
          if Greeting("x") != "Hello from x" {
              t.Fatal("unexpected greeting")
          }
      }

  - path: "{{ project_name }}/.gitignore"
    type: config
    contents: |
      /bin/
      *.exe

  - path: "{{ project_name }}/README.md"
    type: docs
    contents: |
      # {{ project_name }}

      Narzędzie CLI w Go wygenerowane z manifestu jednoplikowego.
```

## Jak wygenerować

1. Renderuj zmienne, utwórz strukturę z manifestu.
2. `go run ./cmd/{{ project_name }}` oraz `go test ./...`.
