# Wzorzec Projektowy: Mikroserwis FastAPI (`fastapi-microservice`)

Manifest jednoplikowy opisujący mikroserwis FastAPI z konteneryzacją Docker i testami.

## Zmienne wejściowe

| Zmienna | Opis | Przykład |
| :--- | :--- | :--- |
| `project_name` | Nazwa serwisu | `orders-api` |
| `package_name` | Nazwa pakietu (snake_case) | `orders_api` |
| `port` | Port aplikacji | `8000` |

## Manifest

```yaml
variables:
  project_name: orders-api
  package_name: orders_api
  port: 8000

directories:
  - "{{ project_name }}"
  - "{{ project_name }}/app"
  - "{{ project_name }}/tests"

files:
  - path: "{{ project_name }}/requirements.txt"
    type: config
    contents: |
      fastapi==0.114.0
      uvicorn[standard]==0.30.6
      pytest==8.3.2
      httpx==0.27.2

  - path: "{{ project_name }}/app/__init__.py"
    type: source
    contents: ""

  - path: "{{ project_name }}/app/main.py"
    type: source
    contents: |
      from fastapi import FastAPI

      app = FastAPI(title="{{ project_name }}")

      @app.get("/health")
      def health() -> dict:
          return {"status": "ok"}

  - path: "{{ project_name }}/tests/test_health.py"
    type: test
    contents: |
      from fastapi.testclient import TestClient
      from app.main import app

      client = TestClient(app)

      def test_health():
          resp = client.get("/health")
          assert resp.status_code == 200
          assert resp.json() == {"status": "ok"}

  - path: "{{ project_name }}/Dockerfile"
    type: config
    contents: |
      FROM python:3.12-slim
      WORKDIR /code
      COPY requirements.txt .
      RUN pip install --no-cache-dir -r requirements.txt
      COPY . .
      EXPOSE {{ port }}
      CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "{{ port }}"]

  - path: "{{ project_name }}/compose.yml"
    type: config
    contents: |
      services:
        api:
          build: .
          ports:
            - "{{ port }}:{{ port }}"

  - path: "{{ project_name }}/.gitignore"
    type: config
    contents: |
      __pycache__/
      .venv/
      *.py[cod]

  - path: "{{ project_name }}/README.md"
    type: docs
    contents: |
      # {{ project_name }}

      Mikroserwis FastAPI wygenerowany z manifestu jednoplikowego.
```

## Jak wygenerować

1. Renderuj zmienne, utwórz strukturę z manifestu.
2. `docker compose up --build` lub `uvicorn app.main:app --reload`.
