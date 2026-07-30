# Transit Verify

A USSD-based commuter reporting system for unauthorized transit violations on minibus taxis in Addis Ababa. Commuters report violations via a USSD menu (no smartphone or app required); reports are aggregated into verified anomalies for Terminal Managers to act on, with Supervisor oversight and
read-only field access for Traffic Police Officers.

Schema documentation: [docs/erd.md](docs/erd.md).

## Stack

Flask + Jinja2 (server-rendered, no frontend framework) + SQLite.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS/Linux

pip install -r requirements.txt
pip install -r requirements-dev.txt   # only needed for tests/linting

flask --app app init-db         # creates the schema
python seed.py                  # populates reference data + demo accounts

python run.py                   # http://127.0.0.1:5000

python seed_demo_anomalies.py   # optional: ~60 anomalies for testing pagination/filters at scale
```

## Demo accounts

For grading/evaluation only.

| Role                         | Email                    | Password       |
| ---------------------------- | ------------------------ | -------------- |
| Terminal Manager (Megenagna) | a.kebede@transit.gov.et  | Manager123!    |
| Terminal Manager (Bole)      | s.girma@transit.gov.et   | Manager123!    |
| Terminal Manager (Saris)     | y.bekele@transit.gov.et  | Manager123!    |
| Supervisor                   | m.tesfaye@transit.gov.et | Supervisor123! |
| Officer                      | officer@transit.gov.et   | Officer123!    |

## Running tests

```bash
pytest
```

Tests run against a temporary SQLite database created per test session — local `instance/` database is never touched.

## Testing the USSD flow

The webhook lives at `POST /ussd` and expects Africa's Talking's standard form fields (`sessionId`, `text`; `phoneNumber` is received but never read, stored, or logged). Point an Africa's Talking sandbox channel at the deployed URL's `/ussd` endpoint to test the full menu end-to-end.

## Deployment

Deployed on [PythonAnywhere](https://www.pythonanywhere.com) — its free tier gives a persistent home directory, so the SQLite database survives web-app reloads (unlike Render/Railway's ephemeral disks). Configuration is done through their Web tab (WSGI file + virtualenv path), not a `Procfile`. Set a real `SECRET_KEY` via `instance/config.py` on the server — locally it falls back to a dev-only key, which is intentionally insecure and must not be used in production.

`gunicorn`/`Procfile` are kept in the repo as a Render/Railway path if ever needed, but aren't used by the current PythonAnywhere deployment.

## Project layout

```
app/
  routes/          auth.py, dashboard.py, ussd.py — HTTP layer only
  services/        anomaly_service.py, ussd_service.py — business logic
  templates/
    pages/         login.html, dashboard.html
    components/    navbar, filter_bar, anomaly_table, status_modal
  static/
    css/           main.css (global) + per-page/component CSS
    js/            per-component JS
    img/           logo.svg, favicon.svg
  __init__.py      app factory
  database.py      SQLite connection + schema init (flask init-db)
  database.sql     schema DDL
  config.py        thresholds (anomaly/spam windows), DB path
docs/
  erd.md           schema documentation
tests/
  conftest.py      test fixtures (isolated temp DB)
  test_*.py        auth, dashboard, anomaly_service, ussd_service
seed.py            reference data + demo account seeding
seed_demo_anomalies.py   optional bulk anomaly generator for testing at scale
run.py             local dev entry point
Procfile           deployment start command
requirements.txt   runtime dependencies
requirements-dev.txt   test/lint tooling
```
