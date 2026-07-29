# Wzorzec Projektowy: Narzędzie CLI w Rust (`rust-cli`)

Manifest jednoplikowy opisujący aplikację CLI w Rust budowaną Cargo.

## Zmienne wejściowe

| Zmienna | Opis | Przykład |
| :--- | :--- | :--- |
| `project_name` | Nazwa binarki/projektu | `mycli` |
| `crate_name` | Nazwa crate (snake_case) | `mycli` |

## Manifest

```yaml
variables:
  project_name: mycli
  crate_name: mycli

directories:
  - "{{ project_name }}"
  - "{{ project_name }}/src"

files:
  - path: "{{ project_name }}/Cargo.toml"
    type: config
    contents: |
      [package]
      name = "{{ crate_name }}"
      version = "0.1.0"
      edition = "2021"

      [dependencies]

  - path: "{{ project_name }}/src/main.rs"
    type: source
    contents: |
      fn greeting(name: &str) -> String {
          format!("Hello from {name}")
      }

      fn main() {
          println!("{}", greeting("{{ project_name }}"));
      }

      #[cfg(test)]
      mod tests {
          use super::*;

          #[test]
          fn test_greeting() {
              assert_eq!(greeting("x"), "Hello from x");
          }
      }

  - path: "{{ project_name }}/.gitignore"
    type: config
    contents: |
      /target
      Cargo.lock

  - path: "{{ project_name }}/README.md"
    type: docs
    contents: |
      # {{ project_name }}

      Narzędzie CLI w Rust wygenerowane z manifestu jednoplikowego.
```

## Jak wygenerować

1. Renderuj zmienne, utwórz strukturę z manifestu.
2. `cargo run` oraz `cargo test`.
