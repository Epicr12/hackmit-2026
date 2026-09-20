from django.urls import path

from . import views

urlpatterns = [
    path("", views.risk_page, name="risk"),
    path("api/capabilities/", views.capabilities_api, name="risk_capabilities"),
    path("api/assess/", views.assess_api, name="risk_assess"),
]
