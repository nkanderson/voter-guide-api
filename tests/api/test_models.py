from datetime import date

import pytest
from django.db.utils import DataError, IntegrityError

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


@pytest.mark.parametrize(
    "original, constraint_name",
    [
        (
            {
                "first_name": "Cameron",
                "last_name": "Howe",
                "date_of_birth": date(1961, 1, 1),
            },
            "candidate_unique_first_last_dob",
        ),
        (
            {
                "first_name": "Donna",
                "last_name": "Clark",
            },
            "candidate_unique_first_last_null_dob",
        ),
        (
            {
                "first_name": "Joe",
                "date_of_birth": date(1947, 1, 1),
            },
            "candidate_unique_first_dob_null_last",
        ),
        (
            {
                "first_name": "Gordon",
            },
            "candidate_unique_first_null_dob_last",
        ),
    ],
)
def test_candidate_unique_constraints(original, constraint_name):
    Candidate.objects.create(**original)
    with pytest.raises(IntegrityError, match=constraint_name):
        Candidate.objects.create(**original)


@pytest.mark.parametrize(
    "original, near_duplicate",
    [
        (
            {
                "first_name": "Gordon",
            },
            {
                "first_name": "Gordon",
                "last_name": "Clark",
            },
        ),
        (
            {
                "first_name": "Gordon",
            },
            {
                "first_name": "Gordon",
                "date_of_birth": date(1950, 1, 1),
            },
        ),
        (
            {
                "first_name": "Gordon",
                "last_name": "Clark",
            },
            {
                "first_name": "Gordon",
                "last_name": "Clark",
                "date_of_birth": date(1950, 1, 1),
            },
        ),
        (
            {
                "first_name": "Gordon",
                "date_of_birth": date(1950, 1, 1),
            },
            {
                "first_name": "Gordon",
                "last_name": "Clark",
                "date_of_birth": date(1950, 1, 1),
            },
        ),
        (
            {
                "first_name": "Gordon",
                "last_name": "Clark",
                "date_of_birth": date(1950, 1, 2),
            },
            {
                "first_name": "Gordon",
                "last_name": "Clark",
                "date_of_birth": date(1950, 1, 1),
            },
        ),
    ],
)
def test_create_unique_candidates(original, near_duplicate):
    c1 = Candidate.objects.create(**original)
    c2 = Candidate.objects.create(**near_duplicate)
    assert c1.id != c2.id
