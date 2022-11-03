from django.urls import include, path
from rest_framework.routers import DefaultRouter

from voterguide.api import views

router = DefaultRouter()
router.register(r"candidates", views.CandidateViewSet, basename="candidate")

# The API URLs are determined automatically by the router.
urlpatterns = [path("", include(router.urls))]
