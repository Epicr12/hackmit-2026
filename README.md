# AMD Tracker

Tracking acid mine drainage in West Virginia and Appalachia.

## Setup (once)

```bash
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python manage.py migrate
./venv/bin/python manage.py seed_amd     # loads the map's county + stream data
```

## Run

```bash
./venv/bin/python manage.py runserver
```

Then open http://127.0.0.1:8000/

## Pages & owners

| Route       | App           | Template                                  | Owner  |
|-------------|---------------|-------------------------------------------|--------|
| `/`         | `home`        | `home/templates/home/home.html`            | Keshav |
| `/sensors/` | `sensor_info` | `sensor_info/templates/sensor_info/sensors.html` | |
| `/map/`     | `mapview`     | `mapview/templates/mapview/map.html`       | |
| `/risk/`    | `risk_eval`   | `risk_eval/templates/risk_eval/risk.html`  | |
| `/admin/`   | Django admin  | —                                          | |

The home, sensors and risk templates are still **placeholders** — overwrite them
freely. `/map/` is built out; see *Map data* below.

## Map data

`/map/` draws a choropleth of West Virginia and its bordering counties, shaded by an AMD
damage-intensity index, with stream monitoring points on top.

**The severity index is illustrative, not a regulatory dataset.** Scores are derived from
the documented AMD-affected watersheds (Cheat, Blackwater, Tygart Valley, Monongahela,
West Fork, Guyandotte, Tug Fork, Coal, Paint Creek, plus the neighbouring coalfields).
Swap in real numbers by editing `mapview/fixtures/amd_seed.json` and re-running
`manage.py seed_amd` — it upserts, so it is safe to re-run. Individual rows are also
editable in the Django admin.

Two pieces of data feed the page:

| What | Where | Served as |
|---|---|---|
| County boundaries | `static/geo/wv-region-counties.geojson` | static file (cached by the browser) |
| Severity scores | `CountyImpact` model | `/map/county-impact/` |
| Stream readings | `Stream` model | `/map/sensor-data/?sensor=<key>` |

The boundary file was filtered from the US Census cartographic boundary set
(public domain), mirrored at
`https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json`:
every West Virginia county, plus any county in KY, OH, PA, VA or MD whose centroid lies
within 0.65° (~45 miles) of the West Virginia line — 162 counties, 89 KB. Regenerate it
only if the region needs to change.

To add a sensor, add one entry to `SENSORS` in `mapview/views.py` and one field on
`Stream`; the dropdown and the API validation are both built from that dict.


## Conventions

- Shared templates go in `templates/` (project root); app pages stay in
  `<app>/templates/<app>/`.
- Shared CSS goes in `static/css/`.
- Don't commit `venv/` or `db.sqlite3` — both are gitignored.

## Troubleshooting

- **Every page 500s with `ImproperlyConfigured: The SECRET_KEY setting must not be
  empty`** — `SECRET_KEY` was removed from `hackmit/settings.py`. It's required even
  for local-only use (Django signs session cookies and CSRF tokens with it).
- **`/map/` is blank or shows a red error banner** — the county/stream data isn't
  loaded. Run `./venv/bin/python manage.py migrate && ./venv/bin/python manage.py seed_amd`.
- **`ModuleNotFoundError: No module named 'django'`** — activate the venv, or use
  `./venv/bin/python` instead of bare `python`.
