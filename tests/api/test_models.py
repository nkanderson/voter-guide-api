import pytest
from django.db.utils import DataError

from voterguide.api.models import Candidate

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "data, c_string, full_name",
    [
        (
            {"first_name": "First", "last_name": "Last", "party": "D"},
            "First Last - Democrat",
            "First Last",
        ),
        (
            {"first_name": "No_last_name", "party": "G"},
            "No_last_name - Pacific Green",
            "No_last_name",
        ),
        (
            {"first_name": "Unknown", "last_name": "Party"},
            "Unknown Party - Unknown",
            "Unknown Party",
        ),
    ],
)
def test_create_valid_candidate(data, c_string, full_name):
    candidate = Candidate.objects.create(**data)
    assert isinstance(candidate, Candidate)
    assert str(candidate) == c_string
    assert candidate.full_name() == full_name


def test_create_invalid_candidate():
    data = {"first_name": "Invalid", "last_name": "Party", "party": "Democrat"}
    with pytest.raises(DataError, match=r"value too long"):
        Candidate.objects.create(**data)
