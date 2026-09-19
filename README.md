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

## Component cheatsheet

Every page extends `templates/base.html`. Styles live in `static/css/main.css` —
**don't write page-specific CSS**; add to `main.css` so all pages benefit.

Visual direction: stark and typographic, flat saturated colour on white. Type is
**Outfit**, self-hosted in `static/fonts/` — no CDN, so it works offline at the demo.

### Page skeleton

```django
{% extends "base.html" %}
{% block title %}Sensors{% endblock %}
{% block body_class %}page--app{% endblock %}   {# page--editorial for prose pages #}

{% block extra_head %}<link rel="stylesheet" href="...leaflet.css">{% endblock %}
{% block content %}...{% endblock %}
{% block extra_js %}<script src="...leaflet.js"></script>{% endblock %}
```

Third-party CSS goes in `extra_head`, JS in `extra_js` — **not** inline in `content`.
That keeps everyone out of `base.html` and avoids merge conflicts.

### Layout

```html
<div class="wrap">...</div>          <!-- full width, max 1240px -->
<div class="wrap--prose">...</div>   <!-- reading measure, 62ch -->

<section class="block block--brand">  <!-- full-bleed colour band -->
  <div class="wrap">...</div>
</section>
```

Block variants: `block--tint` (grey), `block--brand` (blue), `block--stain` (orange),
`block--yellow`. Text colour flips automatically inside each.

### Display type & big numbers (editorial pages)

```html
<p class="eyebrow">The problem</p>
<h1 class="display">Acid mine<br>drainage</h1>
<p class="lede">One sentence that sets the stakes.</p>

<div class="bigstat">
  <span class="bigstat__value">12,400</span>
  <span class="bigstat__label">miles of US waterways affected.</span>
</div>
```

### Status badge — any "how bad is it" indicator

Vocabulary matches the `severity()` helper, so DB and UI never disagree.

```html
<span class="badge badge--good">Healthy</span>
<span class="badge badge--warning">Elevated</span>
<span class="badge badge--serious">Serious</span>
<span class="badge badge--critical">Critical</span>
```

Always keep the text label — colour alone is not accessible.

### Table, stats, cards, buttons, meter

```html
<div class="table-wrap"><table class="table">
  <thead><tr><th>Site</th><th>pH</th><th>Status</th></tr></thead>
  <tbody><tr><td>Cheat River</td><td class="num">3.2</td>
    <td><span class="badge badge--critical">Critical</span></td></tr></tbody>
</table></div>

<div class="stats"><div class="stat">
  <p class="stat__label">Sites monitored</p>
  <div class="stat__value">12</div>
  <p class="stat__source">Live sensor network</p>
</div></div>

<a class="btn btn--primary" href="/map/">See the map</a>
<div class="meter"><div class="meter__fill" style="width:62%"></div></div>

<div class="linkcards linkcards--3">
  <a class="linkcard" href="/map/"><h3>Live map</h3><p>Where it's happening.</p></a>
</div>
```

### Colour tokens

Use variables, never raw hex — that's what makes dark mode work.

`--ink` `--ink-2` `--ink-3` · `--ground` `--ground-2` `--line` ·
`--brand` / `--brand-ink` · `--stain` (fills) / `--stain-text` (text) ·
`--pop-yellow` `--pop-mint` (block fills only, never text) ·
`--good` `--warning` `--serious` `--critical` (+ `--*-text` variants) ·
`--acid-1`…`--acid-5` (pH ramp) · spacing `--s1`…`--s9`

Every text colour is contrast-checked at 4.5:1 or better in both themes. If you add
one, check it first.

