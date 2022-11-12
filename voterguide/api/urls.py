from django.urls import include, path
from rest_framework.routers import DefaultRouter

from voterguide.api import views

router = DefaultRouter()
router.register(r"candidates", views.CandidateViewSet, basename="candidate")
router.register(r"endorsers", views.EndorserViewSet, basename="endorser")
router.register(r"measures", views.MeasureViewSet, basename="measure")

# The API URLs are determined automatically by the router.
urlpatterns = [path("", include(router.urls))]
