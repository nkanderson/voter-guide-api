import itertools
import json
import re
from datetime import date, datetime, timedelta

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe, foreign_key, seq
from rest_framework.test import force_authenticate

from voterguide.api.models import (
    Candidate,
    Endorser,
    Measure,
    MeasureEndorsement,
    Seat,
    SeatEndorsement,
)
from voterguide.api.views import (
    CandidateViewSet,
    EndorserViewSet,
    MeasureEndorsementViewSet,
    MeasureViewSet,
    SeatEndorsementViewSet,
    SeatViewSet,
)

pytestmark = pytest.mark.django_db


# Need to convert date string from json into date object for comparison
# to a model's date field
def date_hook(json_dict):
    for key, value in json_dict.items():
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


@pytest.mark.parametrize(
    "model, viewset",
    [
        (MeasureEndorsement, MeasureEndorsementViewSet),
        (SeatEndorsement, SeatEndorsementViewSet),
    ],
)
class TestEndorsements:
    def list_url(self, model):
        class_name = model.__name__.lower()
        return reverse(f"{class_name}-list")

    def detail_url(self, id, model):
        class_name = model.__name__.lower()
        return reverse(f"{class_name}-detail", kwargs={"pk": id})

    def compare_instance_url(self, instance, url):
        pk_match = re.search(r"/(\d+)/$", url)
        pk = int(pk_match[pk_match.lastindex])
        assert instance.pk == pk

    def compare_many_to_many(self, instance_field, url_list):
        # Extract list of instance IDs from URL list
        url_ids = [int(re.search(r"/(\d+)/$", url)[1]) for url in url_list]
        # Extract equivalent list of instance IDs from instance m2m field
        pks = list(instance_field.all().values_list("id", flat=True))
        assert pks == url_ids

    def recipe(self, model):
        endorser = Recipe(Endorser)
        match model.__name__:
            case "MeasureEndorsement":
                # Requires endorser & measure foreign keys
                measure = Recipe(Measure)
                endorsement_recipe = Recipe(
                    MeasureEndorsement,
                    election_date=seq(date(2022, 11, 8), timedelta(days=1)),
                    endorser=foreign_key(endorser),
                    measure=foreign_key(measure),
                )
            case "SeatEndorsement":
                # Requires endorser & seat foreign keys, & candidates many-to-many field,
                # which is taken care of by model bakery via `make_m2m`.
                seat = Recipe(
                    Seat,
                    level="S",
                    branch="L",
                    role="Senator",
                    body="S",
                    district=seq(1),
                    state="OR",
                )
                endorsement_recipe = Recipe(
                    SeatEndorsement,
                    election_date=seq(date(2022, 11, 8), timedelta(days=1)),
                    endorser=foreign_key(endorser),
                    seat=foreign_key(seat),
                    make_m2m=True,
                )
        return endorsement_recipe

    @pytest.fixture
    def data(
        self,
        model,
        endorser_serializer,
        measure_serializer,
        candidate_serializer,
        seat_serializer,
    ):
        match model.__name__:
            case "MeasureEndorsement":
                return {
                    "election_date": "2022-11-08",
                    "url": "https://example.com/endorsements",
                    "recommendation": "Y",
                    "endorser": endorser_serializer.data["url"],
                    "measure": measure_serializer.data["url"],
                }
            case "SeatEndorsement":
                return {
                    "election_date": "2022-11-08",
                    "url": "https://example.com/endorsements",
                    "endorser": endorser_serializer.data["url"],
                    "candidates": [candidate_serializer.data["url"]],
                    "seat": seat_serializer.data["url"],
                }

    def test_list(self, drf_rf, model, viewset):
        self.recipe(model).make(_quantity=3)
        request = drf_rf.get(self.list_url(model))
        view = viewset.as_view({"get": "list"})

        response = view(request).render()

        assert response.status_code == 200
        assert len(json.loads(response.content)) == 3

    @pytest.mark.parametrize("authenticated, status_code", [(True, 201), (False, 403)])
    def test_create(
        self,
        model,
        viewset,
        authenticated,
        status_code,
        drf_rf,
        user,
        data,
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

    def test_retrieve(self, drf_rf, model, viewset, data):
        resource = self.recipe(model).make()
        request = drf_rf.get(self.detail_url(resource.id, model))
        view = viewset.as_view({"get": "retrieve"})

        response = view(request, pk=resource.id).render()

        assert response.status_code == 200
        return_data = json.loads(response.content, object_hook=date_hook)
        assert return_data["id"] == resource.id
        for key in data.keys():
            # evaluate foreign keys
            if isinstance((resource_attr := getattr(resource, key)), models.Model):
                self.compare_instance_url(resource_attr, return_data[key])
            # evaluate many-to-many relationships
            elif isinstance((model._meta.get_field(key)), models.ManyToManyField):
                self.compare_many_to_many(resource_attr, return_data[key])
            # evaluate non-relational data
            else:
                assert return_data[key] == getattr(resource, key)

    @pytest.mark.parametrize("authenticated, status_code", [(True, 200), (False, 403)])
    def test_update(
        self,
        model,
        viewset,
        authenticated,
        status_code,
        drf_rf,
        user,
        data,
    ):
        resource = self.recipe(model).make()
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
                # evaluate foreign keys
                if isinstance((resource_attr := getattr(resource, key)), models.Model):
                    self.compare_instance_url(resource_attr, return_data[key])
                # evaluate many-to-many relationships
                elif isinstance((model._meta.get_field(key)), models.ManyToManyField):
                    self.compare_many_to_many(resource_attr, return_data[key])
                # evaluate non-relational data
                else:
                    assert return_data[key] == getattr(resource, key)

    @pytest.mark.parametrize("authenticated, status_code", [(True, 200), (False, 403)])
    def test_partial_update(
        self,
        model,
        viewset,
        authenticated,
        status_code,
        drf_rf,
        user,
        data,
    ):
        resource = self.recipe(model).make()
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
                # evaluate foreign keys
                if isinstance((resource_attr := getattr(resource, key)), models.Model):
                    self.compare_instance_url(resource_attr, return_data[key])
                # evaluate many-to-many relationships
                elif isinstance((model._meta.get_field(key)), models.ManyToManyField):
                    self.compare_many_to_many(resource_attr, return_data[key])
                # evaluate non-relational data
                else:
                    assert return_data[key] == getattr(resource, key)

    @pytest.mark.parametrize("authenticated, status_code", [(True, 204), (False, 403)])
    def test_destroy(
        self,
        model,
        viewset,
        authenticated,
        status_code,
        drf_rf,
        user,
    ):
        resource = self.recipe(model).make()
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
