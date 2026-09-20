"""Load the AMD seed dataset into the database.

Idempotent: re-running updates existing rows instead of duplicating them, so
teammates can pull and re-seed at any time.
"""
import json
from pathlib import Path

from django.core.management.base import BaseCommand

from mapview.models import CountyImpact, Stream

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "amd_seed.json"

MODELS = {
    "mapview.countyimpact": (CountyImpact, "fips"),
    "mapview.stream": (Stream, "name"),
}


class Command(BaseCommand):
    help = "Seed county AMD impact scores and stream monitoring points."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            default=str(FIXTURE),
            help="Path to the seed JSON (default: mapview/fixtures/amd_seed.json)",
        )

    def handle(self, *args, **options):
        path = Path(options["fixture"])
        if not path.exists():
            self.stderr.write(self.style.ERROR(f"fixture not found: {path}"))
            return

        records = json.loads(path.read_text())
        counts = {}

        for record in records:
            model_label = record["model"]
            if model_label not in MODELS:
                self.stderr.write(self.style.WARNING(f"skipping unknown model {model_label}"))
                continue

            model, key = MODELS[model_label]
            fields = dict(record["fields"])
            lookup = {key: fields.pop(key)}
            _, created = model.objects.update_or_create(**lookup, defaults=fields)

            bucket = counts.setdefault(model.__name__, [0, 0])
            bucket[0 if created else 1] += 1

        for name, (created, updated) in sorted(counts.items()):
            self.stdout.write(self.style.SUCCESS(f"{name}: {created} created, {updated} updated"))
