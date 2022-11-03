from model_bakery import baker

from voterguide.api.models import Candidate
from voterguide.api.serializers import CandidateSerializer


def test_serialize_model():
    candidate = baker.prepare(Candidate)
    serializer = CandidateSerializer(candidate)
    assert serializer.data


def test_serialized_data():
    candidate_data = {"first_name": "First", "last_name": "Last", "party": "D"}
    serializer = CandidateSerializer(data=candidate_data)

    assert serializer.is_valid()
    assert serializer.errors == {}
