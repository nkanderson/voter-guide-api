from datetime import date

import pytest
from django.db.utils import DataError, IntegrityError

from voterguide.api.models import Candidate, Endorser

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "data, c_string, full_name",
    [
        (
            {"first_name": "Haley", "last_name": "Clark", "party": "D"},
            "Haley Clark - Democrat",
            "Haley Clark",
        ),
        (
            {"first_name": "Wonderboy", "party": "G"},
            "Wonderboy - Pacific Green",
            "Wonderboy",
        ),
        (
            {"first_name": "Malcolm", "last_name": "Levitan"},
            "Malcolm Levitan - Unknown",
            "Malcolm Levitan",
        ),
        (
            {
                "first_name": "John",
                "last_name": "Bosworth",
                "date_of_birth": date(1930, 1, 1),
            },
            "John Bosworth (born January 1, 1930) - Unknown",
            "John Bosworth",
        ),
        (
            {
                "first_name": "Diane",
                "middle_name": "Kimberly",
                "last_name": "Gould",
                "date_of_birth": date(1940, 12, 31),
            },
            "Diane Kimberly Gould (born December 31, 1940) - Unknown",
            "Diane Kimberly Gould",
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


@pytest.mark.parametrize(
    "data, e_string",
    [
        (
            {"name": "Coalition of Communities of Color", "abbreviation": "CCC"},
            "Coalition of Communities of Color (CCC)",
        ),
        (
            {
                "name": "Asian Pacific American Network of Oregon",
                "abbreviation": "APANO",
            },
            "Asian Pacific American Network of Oregon (APANO)",
        ),
    ],
)
def test_create_endorser(data, e_string):
    endorser = Endorser.objects.create(**data)
    assert isinstance(endorser, Endorser)
    assert str(endorser) == e_string


def test_endorser_unique_constraint():
    e1 = {"name": "Basic Rights Oregon", "abbreviation": "BRO"}
    e2 = {"name": "Bigly Republicans of Oregon", "abbreviation": "BRO"}
    Endorser.objects.create(**e1)
    with pytest.raises(IntegrityError, match=r"violates unique constraint"):
        Endorser.objects.create(**e2)


def test_create_invalid_endorser():
    with pytest.raises(DataError, match=r"value too long"):
        Endorser.objects.create(
            name="Oregon League of Conservation Voters",
            abbreviation="Oregon League of Conservation Voters",
        )
