from datetime import date

import pytest
from model_bakery import baker

from voterguide.api.models import Candidate, Endorser, Measure
from voterguide.api.serializers import (
    CandidateSerializer,
    EndorserSerializer,
    MeasureSerializer,
)


@pytest.mark.parametrize(
    "model, serializer, data",
    [
        (
            Candidate,
            CandidateSerializer,
            {"first_name": "Tom", "last_name": "Rendon", "party": "D"},
        ),
        (
            Endorser,
            EndorserSerializer,
            {"name": "Willamette Week", "abbreviation": "WW"},
        ),
        (
            Measure,
            MeasureSerializer,
            {
                "name": "M112",
                "level": "C",
                "state": "WA",
                "election_date": date(2022, 11, 8),
            },
        ),
    ],
)
class TestSerializer:
    def test_serialize_model(self, drf_rf, model, serializer, data):
        resource = baker.prepare(model)
        resource_serializer = serializer(resource, context={"request": drf_rf.get("/")})
        assert resource_serializer.data

    @pytest.mark.django_db
    def test_serialized_data(self, model, serializer, data):
        resource_serializer = serializer(data=data)

        assert resource_serializer.is_valid()
        assert resource_serializer.errors == {}
        assert resource_serializer.validated_data
