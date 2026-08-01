# Transit Verify

A USSD-based commuter reporting system for unauthorized transit violations on minibus taxis in Addis Ababa. Commuters report violations via a USSD menu (no smartphone or app required); reports are aggregated into verified anomalies for Terminal Managers to act on, with Supervisor oversight and
read-only field access for Traffic Police Officers.


* **Project Demonstration Video:** [Watch the Video Link Here](https://youtu.be/AgeH8x3nqzQ)
* **Schema documentation:** [docs/erd.md](docs/erd.md)
* **Software Requirements Specification (SRS):** [Read the SRS Document](https://docs.google.com/document/d/1PKSSGhavbGcwu34jpGCTqUm32Pu8fndm_ppkmLbH_fY/edit?usp=sharing)
* **Live Public Application:** [Access the Live App Portal](https://ydejene.pythonanywhere.com/)


## Stack

Flask + Jinja2 (server-rendered, no frontend framework) + SQLite.

## Setup

```bash
git clone https://github.com/ydejene/transit-verify
cd transit-verify

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

Deployed on [PythonAnywhere](https://www.pythonanywhere.com) — its free tier gives a persistent home directory, so the SQLite database survives web-app reloads (unlike Render/Railway's ephemeral disks).

1. Create a free PythonAnywhere account.
2. **Consoles tab → Bash console:**
   ```bash
   git clone https://github.com/<your-username>/transit-verify.git
   cd transit-verify
   mkvirtualenv --python=/usr/bin/python3.10 transit-verify-venv
   pip install -r requirements.txt
   ```
3. **Web tab → "Add a new web app" → "Manual configuration"** (not the
   Flask template), matching Python version to the venv above.
4. On the Web tab, set:
   - **Virtualenv**: `/home/<your-username>/.virtualenvs/transit-verify-venv`
   - **Source code**: `/home/<your-username>/transit-verify`
5. Open the **WSGI configuration file** link on the Web tab and replace its
   contents with:
   ```python
   import sys
   path = '/home/<your-username>/transit-verify'
   if path not in sys.path:
       sys.path.insert(0, path)

   from app import create_app
   application = create_app()
   ```
6. Set a real secret key (back in the Bash console):
   ```bash
   mkdir -p instance
   echo 'SECRET_KEY = "paste-a-real-random-value-here"' > instance/config.py
   ```
7. Initialize and seed the database (same console, venv active):
   ```bash
   flask --app app init-db
   python seed.py
   python seed_demo_anomalies.py   # optional
   ```
8. **Web tab → green "Reload" button.**
9. Visit `https://<your-username>.pythonanywhere.com` and confirm the
   login page loads.
10. For the Africa's Talking sandbox, use
    `https://<your-username>.pythonanywhere.com/ussd` as the callback URL.

`gunicorn`/`Procfile` are kept in the repo as a Render/Railway path if ever
needed, but aren't used by the PythonAnywhere deployment above.

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
