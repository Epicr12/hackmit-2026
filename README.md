# AMD Tracker

Tracking acid mine drainage in West Virginia and Appalachia.

## Setup (once)

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python manage.py migrate
```

## Run

```bash
./venv/bin/python manage.py runserver
```

Then open http://127.0.0.1:8000/

## AMD risk assessment (`/risk/`)

The **Am I at risk?** page takes a location, matches nearby readings from
`data/amd_sensors.json`, and asks Cursor for a risk assessment.

```bash
export CURSOR_API_KEY="cursor_..."   # from https://cursor.com/dashboard/integrations
./venv/bin/python manage.py runserver
```

## Pages & owners

| Route       | App           | Template                                  | Owner  |
|-------------|---------------|-------------------------------------------|--------|
| `/`         | `home`        | `home/templates/home/home.html`            | Keshav |
| `/sensors/` | `sensor_info` | `sensor_info/templates/sensor_info/sensors.html` | |
| `/map/`     | `mapview`     | `mapview/templates/mapview/map.html`       | |
| `/risk/`    | `risk_eval`   | `risk_eval/templates/risk_eval/risk.html`  | |
| `/admin/`   | Django admin  | —                                          | |

All four page templates are currently **placeholders** — overwrite them freely.

## Conventions

- Shared templates go in `templates/` (project root); app pages stay in
  `<app>/templates/<app>/`.
- Shared CSS goes in `static/css/`.
- Don't commit `venv/` or `db.sqlite3` — both are gitignored.

## Troubleshooting

- **Every page 500s with `ImproperlyConfigured: The SECRET_KEY setting must not be
  empty`** — `SECRET_KEY` was removed from `hackmit/settings.py`. It's required even
  for local-only use (Django signs session cookies and CSRF tokens with it).
- **`ModuleNotFoundError: No module named 'django'`** — activate the venv, or use
  `./venv/bin/python` instead of bare `python`.
