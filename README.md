# Hospital Management System (MVP)

Backend-only Hospital Management System built with Django and Django REST Framework.

## Features
- JWT authentication with role-based access: `ADMIN`, `DOCTOR`, `PATIENT`
- User, doctor, patient profile management
- Appointment booking with doctor overlap validation
- Prescription and invoice modules
- Dashboard analytics with Redis cache
- OpenAPI schema + Swagger UI
- Dockerized local environment and Render deployment blueprint

## Stack
- Django, DRF, SimpleJWT
- PostgreSQL
- Redis
- Gunicorn + Whitenoise
- Docker / Docker Compose

## Choose Run Mode
- If Docker is unavailable on your machine, use native mode first.
- Native mode uses SQLite and starts fastest.
- Docker mode uses PostgreSQL + Redis services from `docker-compose.yml`.

## Native Quick Start (Recommended First)
1. Run:
   - `scripts\run_native.cmd`
2. App URL:
   - `http://127.0.0.1:8000/`
3. Docs URL:
   - `http://127.0.0.1:8000/api/docs/`

What this script does:
- Creates `.env` from `.env.native.example` if missing
- Creates and uses project-local virtual environment `.venv`
- Installs requirements in `.venv`
- Runs preflight checks
- Applies migrations
- Starts Django server on `127.0.0.1:8000`
- Root path `/` redirects to `/api/docs/`

Optional:
- Setup only, no server:
  - `scripts\run_native.cmd --no-server`

## Docker Quick Start
1. Make sure Docker Desktop is installed and running.
2. Verify:
   - `docker --version`
   - `docker compose version`
3. Run:
   - `scripts\run_docker.cmd`
4. App URL:
   - `http://127.0.0.1:8000/`

What this script does:
- Verifies Docker and Compose availability
- Creates `.env` from `.env.docker.example` if missing
- Runs docker preflight checks
- Starts containers with build

Optional:
- Validate only, no container startup:
  - `scripts\run_docker.cmd --no-up`

## Environment Templates
- Native: `.env.native.example`
- Docker: `.env.docker.example`
- Compatibility fallback: `.env.example`

## Manual Commands
- Native preflight:
  - `.venv\Scripts\python.exe scripts\preflight.py --mode native --python-executable ".venv\Scripts\python.exe"`
- Docker preflight:
  - `python scripts\preflight.py --mode docker`
- Tests:
  - `.venv\Scripts\python.exe manage.py test`
- Strict native audit:
  - `scripts\audit_native.cmd`

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| `'docker' is not recognized` | Docker Desktop is not installed or not on PATH | Install Docker Desktop, restart terminal, run `docker --version` |
| Startup fails with missing `.env` | Runtime expects environment file | Copy correct template: `copy .env.native.example .env` or `copy .env.docker.example .env` |
| Native mode fails with DB host `db` | Docker DB URL used outside Docker | Set `DATABASE_URL=sqlite:///db.sqlite3` in `.env` for native mode |
| Docker preflight fails with sqlite/redis empty values | Native `.env` used for Docker mode | Replace `.env` with `copy /Y .env.docker.example .env` then rerun `scripts\run_docker.cmd` |
| Port `8000` already in use | Another process is using it | Stop the process or run `python manage.py runserver 127.0.0.1:8001` |

## API Docs
- Swagger UI: `/api/docs/`
- OpenAPI JSON: `/api/schema/`

## Key Endpoints
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/refresh/`
- `GET /api/v1/auth/me/`
- `POST/GET /api/v1/users/`
- `PATCH /api/v1/users/{id}/status/`
- `POST/GET /api/v1/doctors/`
- `GET/PATCH /api/v1/doctors/{id}/`
- `POST /api/v1/patients/`
- `GET/PATCH /api/v1/patients/{id}/`
- `POST/GET /api/v1/appointments/`
- `PATCH /api/v1/appointments/{id}/status/`
- `POST /api/v1/prescriptions/`
- `GET/PATCH /api/v1/prescriptions/{id}/`
- `POST/GET /api/v1/invoices/`
- `PATCH /api/v1/invoices/{id}/status/`
- `GET /api/v1/dashboard/overview/`

## Deployment
- Render blueprint: `render.yaml`
- Set `DJANGO_SETTINGS_MODULE=config.prod` in production.
