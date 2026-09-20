# AMD Monitor

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

Visual direction: calm natural editorial — warm bone ground, serif display headings,
full-bleed archival photography under a dark overlay. Type is **Newsreader** (serif)
+ **Mulish** (sans), self-hosted in `static/fonts/` so it works offline at the demo.

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

### Photographic hero

```django
<section class="hero-photo"
         style="--hero-img: url('{% static 'images/hero-river.jpg' %}')">
  <div class="hero-photo__inner">
    <p class="eyebrow">West Virginia</p>
    <h1>Headline</h1>
    <p class="lede">Supporting sentence.</p>
    <p class="hero-credit">Photograph: ...</p>
  </div>
</section>
```

The overlay gradient is tuned so white text clears 4.5:1 **even over the photo's
brightest area**. If you swap in a lighter photo, re-check it before shipping.

### Layout & blocks

```html
<div class="wrap">...</div>          <!-- full width, max 1260px -->
<div class="wrap--prose">...</div>   <!-- reading measure, 66ch -->

<section class="block block--forest"><div class="wrap">...</div></section>
```

Block variants: `block--tint`, `block--paper`, `block--forest` (text flips to white).

### Editorial pieces

```html
<p class="eyebrow">The problem</p>
<p class="lede">A sentence that sets the stakes.</p>
<blockquote class="pullquote">A line worth pulling out.</blockquote>

<div class="bigstat">
  <span class="bigstat__value">12,400 miles</span>
  <span class="bigstat__label">of US waterways affected.</span>
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

`--ink` `--ink-2` `--ink-3` · `--ground` `--ground-2` `--paper` `--line` ·
`--forest` / `--forest-deep` (accent + links) · `--stain` (AMD) ·
`--sage` `--sky` (**fills only** — both fail as text) ·
`--good` `--warning` `--serious` `--critical` (+ `--*-text`) ·
`--acid-1`…`--acid-5` (pH ramp) · spacing `--s1`…`--s9`

Every text colour is contrast-checked at 4.5:1+ in both themes. If you add one,
check it first.

