from django.apps import AppConfig


class RiskEvalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "risk_eval"

    def ready(self):
        # Import built-in scorers/sources so @register_* hooks populate.
        from risk_eval.pipeline import scorers as _scorers  # noqa: F401
        from risk_eval.pipeline import sources as _sources  # noqa: F401
