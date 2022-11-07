import json

import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import force_authenticate

from voterguide.api.models import Candidate
from voterguide.api.views import CandidateViewSet

pytestmark = pytest.mark.django_db


class TestCandidateList:
    url = reverse("candidate-list")

    def test_candidate_list(self, drf_rf):
        baker.make(Candidate, _quantity=3)
        request = drf_rf.get(self.url)
        view = CandidateViewSet.as_view({"get": "list"})

        response = view(request).render()

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 3

    def test_candidate_create_unauthenticated(self, drf_rf):
        candidate_data = {"first_name": "Joanie", "last_name": "Clark"}
        request = drf_rf.post(
            self.url, content_type="application/json", data=json.dumps(candidate_data)
        )
        view = CandidateViewSet.as_view({"post": "create"})

        response = view(request).render()

        assert response.status_code == 403

    def test_candidate_create_authenticated(self, drf_rf, user):
        candidate_data = {"first_name": "Joanie", "last_name": "Clark"}
        request = drf_rf.post(
            self.url, content_type="application/json", data=json.dumps(candidate_data)
        )
        force_authenticate(request, user=user)
        view = CandidateViewSet.as_view({"post": "create"})

        response = view(request).render()

        assert response.status_code == 201
        return_data = json.loads(response.content)
        assert return_data["first_name"] == "Joanie"
        assert return_data["last_name"] == "Clark"


class TestCandidateDetail:
    def detail_url(self, id):
        return reverse("candidate-detail", kwargs={"pk": id})

    def test_candidate_retrieve(self, drf_rf):
        candidate = baker.make(Candidate)
        request = drf_rf.get(self.detail_url(candidate.id))
        view = CandidateViewSet.as_view({"get": "retrieve"})

        response = view(request, pk=candidate.id).render()

        assert response.status_code == 200
        return_data = json.loads(response.content)
        assert return_data["first_name"] == candidate.first_name
        assert return_data["id"] == candidate.id

    def test_candidate_update_unauthenticated(self, drf_rf):
        candidate = baker.make(Candidate)
        new_data = {"first_name": "Haley", "last_name": "Clark"}
        request = drf_rf.put(
            self.detail_url(candidate.id),
            content_type="application/json",
            data=json.dumps(new_data),
        )
        view = CandidateViewSet.as_view({"put": "update"})

        response = view(request, pk=candidate.id).render()

        assert response.status_code == 403

    def test_candidate_update_authenticated(self, drf_rf, user):
        candidate = baker.make(Candidate)
        new_data = {"first_name": "Haley", "last_name": "Clark"}
        request = drf_rf.put(
            self.detail_url(candidate.id),
            content_type="application/json",
            data=json.dumps(new_data),
        )
        view = CandidateViewSet.as_view({"put": "update"})
        force_authenticate(request, user=user)

        response = view(request, pk=candidate.id).render()

        assert response.status_code == 200
        return_data = json.loads(response.content)
        assert return_data["first_name"] == "Haley"
        assert return_data["last_name"] == "Clark"
        assert return_data["id"] == candidate.id

    def test_candidate_partial_update_unauthenticated(self, drf_rf):
        candidate = baker.make(Candidate)
        update_data = {"party": "D"}
        request = drf_rf.patch(
            self.detail_url(candidate.id),
            content_type="application/json",
            data=json.dumps(update_data),
        )
        view = CandidateViewSet.as_view({"patch": "partial_update"})

        response = view(request, pk=candidate.id).render()

        assert response.status_code == 403

    def test_candidate_partial_update_authenticated(self, drf_rf, user):
        candidate = baker.make(Candidate)
        update_data = {"party": "D"}
        request = drf_rf.patch(
            self.detail_url(candidate.id),
            content_type="application/json",
            data=json.dumps(update_data),
        )
        view = CandidateViewSet.as_view({"patch": "partial_update"})
        force_authenticate(request, user=user)

        response = view(request, pk=candidate.id).render()

        assert response.status_code == 200
        return_data = json.loads(response.content)
        assert return_data["party"] != candidate.party
        assert return_data["first_name"] == candidate.first_name
        assert return_data["last_name"] == candidate.last_name
        assert return_data["id"] == candidate.id

    def test_candidate_destroy_unauthenticated(self, drf_rf):
        candidate = baker.make(Candidate)
        request = drf_rf.delete(self.detail_url(candidate.id))
        view = CandidateViewSet.as_view({"delete": "destroy"})

        response = view(request, pk=candidate.id).render()

        assert response.status_code == 403

    def test_candidate_destroy_authenticated(self, drf_rf, user):
        candidate = baker.make(Candidate)
        request = drf_rf.delete(self.detail_url(candidate.id))
        view = CandidateViewSet.as_view({"delete": "destroy"})
        force_authenticate(request, user=user)

        response = view(request, pk=candidate.id).render()

        assert response.status_code == 204
