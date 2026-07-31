# Wzorzec Projektowy: Stack wielokontenerowy (`docker-compose-stack`)

Manifest jednoplikowy opisujący stack aplikacji (API + baza danych + reverse proxy) uruchamiany przez Docker Compose.

## Zmienne wejściowe

| Zmienna | Opis | Przykład |
| :--- | :--- | :--- |
| `project_name` | Nazwa stacku | `myplatform` |
| `db_name` | Nazwa bazy danych | `appdb` |
| `db_user` | Użytkownik bazy | `appuser` |
| `api_port` | Port API | `8000` |

## Manifest

```yaml
variables:
  project_name: myplatform
  db_name: appdb
  db_user: appuser
  api_port: 8000

directories:
  - "{{ project_name }}"
  - "{{ project_name }}/api"
  - "{{ project_name }}/proxy"

files:
  - path: "{{ project_name }}/compose.yml"
    type: config
    contents: |
      services:
        db:
          image: postgres:16-alpine
          environment:
            POSTGRES_DB: {{ db_name }}
            POSTGRES_USER: {{ db_user }}
            POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
          volumes:
            - db_data:/var/lib/postgresql/data
        api:
          build: ./api
          environment:
            DATABASE_URL: postgresql://{{ db_user }}:${DB_PASSWORD:-changeme}@db:5432/{{ db_name }}
          depends_on:
            - db
          ports:
            - "{{ api_port }}:{{ api_port }}"
        proxy:
          image: nginx:alpine
          volumes:
            - ./proxy/nginx.conf:/etc/nginx/nginx.conf:ro
          ports:
            - "80:80"
          depends_on:
            - api
      volumes:
        db_data:

  - path: "{{ project_name }}/api/Dockerfile"
    type: config
    contents: |
      FROM python:3.12-slim
      WORKDIR /code
      COPY requirements.txt .
      RUN pip install --no-cache-dir -r requirements.txt
      COPY . .
      CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{{ api_port }}"]

  - path: "{{ project_name }}/api/requirements.txt"
    type: config
    contents: |
      fastapi==0.114.0
      uvicorn[standard]==0.30.6

  - path: "{{ project_name }}/api/main.py"
    type: source
    contents: |
      from fastapi import FastAPI

      app = FastAPI(title="{{ project_name }}")

      @app.get("/health")
      def health():
          return {"status": "ok"}

  - path: "{{ project_name }}/proxy/nginx.conf"
    type: config
    contents: |
      events {}
      http {
        upstream api { server api:{{ api_port }}; }
        server {
          listen 80;
          location / { proxy_pass http://api; }
        }
      }

  - path: "{{ project_name }}/.env.example"
    type: config
    contents: |
      DB_PASSWORD=changeme

  - path: "{{ project_name }}/README.md"
    type: docs
    contents: |
      # {{ project_name }}

      Stack wielokontenerowy wygenerowany z manifestu jednoplikowego.
```

## Jak wygenerować

1. Renderuj zmienne, utwórz strukturę z manifestu.
2. `docker compose up --build`.
