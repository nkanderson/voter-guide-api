import pytest
from model_bakery import baker

from voterguide.api.models import Candidate, Endorser
from voterguide.api.serializers import CandidateSerializer, EndorserSerializer


class TestCandidateSerializer:
    def test_serialize_model(self, drf_rf):
        candidate = baker.prepare(Candidate)
        serializer = CandidateSerializer(
            candidate, context={"request": drf_rf.get("/")}
        )
        assert serializer.data

    def test_serialized_data(self):
        candidate_data = {"first_name": "Tom", "last_name": "Rendon", "party": "D"}
        serializer = CandidateSerializer(data=candidate_data)

        assert serializer.is_valid()
        assert serializer.errors == {}
        assert serializer.validated_data


class TestEndorserSerializer:
    def test_serialize_model(self, drf_rf):
        endorser = baker.prepare(Endorser)
        serializer = EndorserSerializer(endorser, context={"request": drf_rf.get("/")})
        assert serializer.data

    @pytest.mark.django_db
    def test_serialized_data(self):
        endorser_data = {"name": "Willamette Week", "abbreviation": "WW"}
        serializer = EndorserSerializer(data=endorser_data)

        assert serializer.is_valid()
        assert serializer.errors == {}
        assert serializer.validated_data
