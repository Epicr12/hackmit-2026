"""Tests for the flexible risk-assessment pipeline."""

from django.test import Client, SimpleTestCase, TestCase

from risk_eval.pipeline import assess, list_capabilities, register_scorer
from risk_eval.pipeline.ingest import ingest
from risk_eval.pipeline.scorers import level_for


class IngestTests(SimpleTestCase):
    def test_list_of_objects(self):
        bundle = ingest([{"a": 1}, {"b": 2}])
        self.assertEqual(len(bundle.records), 2)
        paths = {f.path for f in bundle.features}
        self.assertIn("records[0].a", paths)
        self.assertIn("records[1].b", paths)

    def test_envelope(self):
        bundle = ingest({"records": [{"x": True}], "meta": {"site": "demo"}})
        self.assertEqual(bundle.meta["site"], "demo")
        self.assertEqual(bundle.records[0]["x"], True)


class HeuristicAssessTests(SimpleTestCase):
    def test_risk_like_fields_drive_score(self):
        result = assess(
            {
                "records": [
                    {"risk_score": 90, "label": "alpha"},
                    {"risk_score": 80, "label": "beta"},
                ]
            }
        )
        a = result["assessment"]
        self.assertGreaterEqual(a["score"], 75)
        self.assertEqual(a["level"], "critical")
        self.assertTrue(a["factors"])

    def test_empty_payload(self):
        result = assess({"records": []})
        self.assertEqual(result["assessment"]["score"], 0.0)
        self.assertEqual(result["assessment"]["level"], "good")

    def test_example_source(self):
        result = assess(source="example_generic")
        self.assertIn(result["assessment"]["level"], {"good", "warning", "serious", "critical"})
        self.assertEqual(result["meta"]["source"], "example_generic")

    def test_custom_scorer_extension(self):
        @register_scorer("always_mid")
        def always_mid(bundle, **opts):
            return {
                "score": 50.0,
                "level": "serious",
                "level_label": "Serious",
                "summary": "stub",
                "factors": [],
                "scorer": "always_mid",
            }

        try:
            result = assess({"records": [{"n": 1}]}, scorer="always_mid")
            self.assertEqual(result["assessment"]["score"], 50.0)
            self.assertIn("always_mid", list_capabilities()["scorers"])
        finally:
            from risk_eval.pipeline import registry

            registry.SCORERS.pop("always_mid", None)

    def test_level_for_boundaries(self):
        self.assertEqual(level_for(0)[0], "good")
        self.assertEqual(level_for(25)[0], "warning")
        self.assertEqual(level_for(50)[0], "serious")
        self.assertEqual(level_for(75)[0], "critical")


class AssessApiTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def test_capabilities(self):
        res = self.client.get("/risk/api/capabilities/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("heuristic", data["scorers"])
        self.assertIn("example_generic", data["sources"])

    def test_assess_post_raw_payload(self):
        # Fetch page first to get CSRF cookie.
        self.client.get("/risk/")
        csrf = self.client.cookies["csrftoken"].value
        res = self.client.post(
            "/risk/api/assess/",
            data='{"records":[{"risk_score":60}]}',
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf,
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("assessment", res.json())

    def test_assess_get_source(self):
        res = self.client.get("/risk/api/assess/?source=example_generic")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["meta"]["source"], "example_generic")

    def test_risk_page_renders(self):
        res = self.client.get("/risk/")
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Risk assessment agent")
        self.assertContains(res, "risk-form")
