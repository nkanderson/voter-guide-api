from datetime import date

import pytest
from model_bakery import baker

from voterguide.api.models import Candidate, Endorser, Measure, MeasureEndorsement, Seat
from voterguide.api.serializers import (
    CandidateSerializer,
    EndorserSerializer,
    MeasureEndorsementSerializer,
    MeasureSerializer,
    SeatSerializer,
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
        (
            Seat,
            SeatSerializer,
            {
                "level": "S",
                "branch": "E",
                "role": "Governor",
                "state": "WA",
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


class TestMeasureEndorsementSerializer:
    @pytest.fixture
    def data(self, endorser_serializer, measure_serializer):
        return {
            "endorser": endorser_serializer.data["url"],
            "election_date": date(2022, 11, 8),
            "url": "https://example.com/endorsements",
            "measure": measure_serializer.data["url"],
            "recommendation": "Y",
        }

    def test_serialize_model(self, drf_rf):
        resource = baker.prepare(MeasureEndorsement)
        resource_serializer = MeasureEndorsementSerializer(
            resource, context={"request": drf_rf.get("/")}
        )
        assert resource_serializer.data

    @pytest.mark.django_db
    def test_serialized_data(self, data):
        resource_serializer = MeasureEndorsementSerializer(data=data)

        assert resource_serializer.is_valid()
        assert resource_serializer.errors == {}
        assert resource_serializer.validated_data
