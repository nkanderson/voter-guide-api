import itertools
import json
from datetime import datetime

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import force_authenticate

from voterguide.api.models import Candidate, Endorser, Measure, Seat
from voterguide.api.views import (
    CandidateViewSet,
    EndorserViewSet,
    MeasureViewSet,
    SeatViewSet,
)

pytestmark = pytest.mark.django_db


# Need to convert date string from json into date object for comparison
# to a model's date field
def date_hook(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            pass
    return json_dict


@pytest.mark.parametrize(
    "model, viewset, data, baker_fields",
    [
        (
            Candidate,
            CandidateViewSet,
            {
                "first_name": "Haley",
                "last_name": "Clark",
                "party": "D",
            },
            [],
        ),
        (
            Endorser,
            EndorserViewSet,
            {
                "name": "Service Employees International Union",
                "abbreviation": "SEIU",
            },
            [],
        ),
        (
            Measure,
            MeasureViewSet,
            {
                "name": "M114",
                "state": "OR",
                "level": "T",
                "election_date": "2022-11-08",
            },
            [],
        ),
        (
            Seat,
            SeatViewSet,
            {
                "level": "S",
                "branch": "E",
                "role": "Governor",
                "state": "WA",
            },
            ["role", "state", "county", "city"],
        ),
    ],
)
class TestList:
    def list_url(self, model):
        class_name = model.__name__.lower()
        return reverse(f"{class_name}-list")

    def test_list(self, drf_rf, model, viewset, data, baker_fields):
        baker.make(model, _quantity=3, _fill_optional=baker_fields)
        request = drf_rf.get(self.list_url(model))
        view = viewset.as_view({"get": "list"})

        response = view(request).render()

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 3

    @pytest.mark.parametrize("authenticated, status_code", [(True, 201), (False, 403)])
    def test_create(
        self,
        authenticated,
        status_code,
        drf_rf,
        user,
        model,
        viewset,
        data,
        baker_fields,
    ):
        request = drf_rf.post(
            self.list_url(model),
            content_type="application/json",
            data=json.dumps(data, cls=DjangoJSONEncoder),
        )
        if authenticated:
            force_authenticate(request, user=user)
        view = viewset.as_view({"post": "create"})

        response = view(request).render()

        assert response.status_code == status_code
        if authenticated:
            return_data = json.loads(response.content)
            assert model.objects.get(pk=return_data["id"])
            for key in data:
                assert return_data[key] == data[key]


@pytest.mark.parametrize(
    "model, viewset, data, baker_fields",
    [
        (
            Candidate,
            CandidateViewSet,
            {
                "first_name": "Joanie",
                "last_name": "Clark",
                "party": "W",
            },
            [],
        ),
        (
            Endorser,
            EndorserViewSet,
            {
                "name": "Sierra Club",
                "abbreviation": "SC",
            },
            [],
        ),
        (
            Measure,
            MeasureViewSet,
            {
                "name": "M114",
                "state": "OR",
                "level": "T",
                "election_date": "2022-11-08",
            },
            [],
        ),
        (
            Seat,
            SeatViewSet,
            {
                "role": "Governor",
                "level": "S",
                "branch": "E",
                "state": "WA",
            },
            ["role", "state", "county", "city"],
        ),
    ],
)
class TestDetail:
    def detail_url(self, id, model):
        class_name = model.__name__.lower()
        return reverse(f"{class_name}-detail", kwargs={"pk": id})

    def test_retrieve(self, drf_rf, model, viewset, data, baker_fields):
        resource = baker.make(model, _fill_optional=baker_fields)
        request = drf_rf.get(self.detail_url(resource.id, model))
        view = viewset.as_view({"get": "retrieve"})

        response = view(request, pk=resource.id).render()

        assert response.status_code == 200
        return_data = json.loads(response.content, object_hook=date_hook)
        assert return_data["id"] == resource.id
        for key in data.keys():
            assert return_data[key] == getattr(resource, key)

    @pytest.mark.parametrize("authenticated, status_code", [(True, 200), (False, 403)])
    def test_update(
        self,
        authenticated,
        status_code,
        drf_rf,
        user,
        model,
        viewset,
        data,
        baker_fields,
    ):
        resource = baker.make(model, _fill_optional=baker_fields)
        new_data = json.dumps(data, cls=DjangoJSONEncoder)
        request = drf_rf.put(
            self.detail_url(resource.id, model),
            content_type="application/json",
            data=new_data,
        )
        view = viewset.as_view({"put": "update"})
        if authenticated:
            force_authenticate(request, user=user)

        response = view(request, pk=resource.id).render()

        assert response.status_code == status_code

        if authenticated:
            return_data = json.loads(response.content, object_hook=date_hook)
            new_data = json.loads(response.content, object_hook=date_hook)
            resource.refresh_from_db()

            assert return_data["id"] == resource.id
            for key in data.keys():
                assert return_data[key] == getattr(resource, key) == new_data[key]

    @pytest.mark.parametrize("authenticated, status_code", [(True, 200), (False, 403)])
    def test_partial_update(
        self,
        authenticated,
        status_code,
        drf_rf,
        user,
        model,
        viewset,
        data,
        baker_fields,
    ):
        resource = baker.make(model, _fill_optional=baker_fields)
        first_key, *rest_keys = list(data.keys())
        update_data = dict(itertools.islice(data.items(), 1))
        request = drf_rf.patch(
            self.detail_url(resource.id, model),
            content_type="application/json",
            data=json.dumps(update_data, cls=DjangoJSONEncoder),
        )
        view = viewset.as_view({"patch": "partial_update"})
        if authenticated:
            force_authenticate(request, user=user)

        assert update_data[first_key] != getattr(resource, first_key)

        response = view(request, pk=resource.id).render()

        assert response.status_code == status_code
        if authenticated:
            return_data = json.loads(response.content, object_hook=date_hook)
            update_data = json.loads(response.content, object_hook=date_hook)

            resource.refresh_from_db()
            assert (
                return_data[first_key]
                == getattr(resource, first_key)
                == update_data[first_key]
            )
            for key in rest_keys:
                assert return_data[key] == getattr(resource, key)

    @pytest.mark.parametrize("authenticated, status_code", [(True, 204), (False, 403)])
    def test_destroy(
        self,
        authenticated,
        status_code,
        drf_rf,
        user,
        model,
        viewset,
        data,
        baker_fields,
    ):
        resource = baker.make(model, _fill_optional=baker_fields)
        resource_id = resource.id
        request = drf_rf.delete(self.detail_url(resource.id, model))
        if authenticated:
            force_authenticate(request, user=user)
        view = viewset.as_view({"delete": "destroy"})

        response = view(request, pk=resource_id).render()

        assert response.status_code == status_code

        if authenticated:
            with pytest.raises(
                ObjectDoesNotExist, match=r"matching query does not exist"
            ):
                model.objects.get(pk=resource_id)
