from datetime import date

import pytest
from django.db.utils import DataError, IntegrityError

from voterguide.api.models import Candidate, Endorser, Measure

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "model, data, model_string",
    [
        (
            Candidate,
            {"first_name": "Haley", "last_name": "Clark", "party": "D"},
            "Haley Clark - Democrat",
        ),
        (
            Candidate,
            {"first_name": "Wonderboy", "party": "G"},
            "Wonderboy - Pacific Green",
        ),
        (
            Candidate,
            {"first_name": "Malcolm", "last_name": "Levitan"},
            "Malcolm Levitan - Unknown",
        ),
        (
            Candidate,
            {
                "first_name": "John",
                "last_name": "Bosworth",
                "date_of_birth": date(1930, 1, 1),
            },
            "John Bosworth (born January 1, 1930) - Unknown",
        ),
        (
            Candidate,
            {
                "first_name": "Diane",
                "middle_name": "Kimberly",
                "last_name": "Gould",
                "date_of_birth": date(1940, 12, 31),
            },
            "Diane Kimberly Gould (born December 31, 1940) - Unknown",
        ),
        (
            Endorser,
            {"name": "Coalition of Communities of Color", "abbreviation": "CCC"},
            "Coalition of Communities of Color (CCC)",
        ),
        (
            Endorser,
            {
                "name": "Asian Pacific American Network of Oregon",
                "abbreviation": "APANO",
            },
            "Asian Pacific American Network of Oregon (APANO)",
        ),
        (
            Measure,
            {
                "name": "M114",
                "level": "S",
                "state": "OR",
                "election_date": date(2022, 11, 8),
            },
            "M114: election on November 8, 2022 in Oregon",
        ),
    ],
)
def test_create_valid_instance(model, data, model_string):
    resource = model.objects.create(**data)
    assert isinstance(resource, model)
    assert str(resource) == model_string


@pytest.mark.parametrize(
    "model, data, constraint_name",
    [
        (
            Candidate,
            {
                "first_name": "Cameron",
                "last_name": "Howe",
                "date_of_birth": date(1961, 1, 1),
            },
            "candidate_unique_first_last_dob",
        ),
        (
            Candidate,
            {
                "first_name": "Donna",
                "last_name": "Clark",
            },
            "candidate_unique_first_last_null_dob",
        ),
        (
            Candidate,
            {
                "first_name": "Joe",
                "date_of_birth": date(1947, 1, 1),
            },
            "candidate_unique_first_dob_null_last",
        ),
        (
            Candidate,
            {
                "first_name": "Gordon",
            },
            "candidate_unique_first_null_dob_last",
        ),
        (
            Measure,
            {
                "name": "M113",
                "level": "S",
                "state": "OR",
                "election_date": date(2022, 11, 8),
            },
            "measure_unique_name_date_state",
        ),
    ],
)
def test_unique_constraints(model, data, constraint_name):
    model.objects.create(**data)
    with pytest.raises(IntegrityError, match=constraint_name):
        model.objects.create(**data)


@pytest.mark.parametrize(
    "model, data, constraint_name",
    [
        (
            Measure,
            {
                "name": "M112",
                "level": "Z",
                "state": "OR",
                "election_date": date(2022, 11, 8),
            },
            "measure_level_valid",
        ),
        (
            Measure,
            {
                "name": "M112",
                "level": "S",
                "state": "ZZ",
                "election_date": date(2022, 11, 8),
            },
            "measure_state_valid",
        ),
    ],
)
def test_check_constraints(model, data, constraint_name):
    with pytest.raises(IntegrityError, match=constraint_name):
        model.objects.create(**data)


@pytest.mark.parametrize(
    "model, original, near_duplicate",
    [
        (
            Candidate,
            {
                "first_name": "Gordon",
            },
            {
                "first_name": "Gordon",
                "last_name": "Clark",
            },
        ),
        (
            Candidate,
            {
                "first_name": "Gordon",
            },
            {
                "first_name": "Gordon",
                "date_of_birth": date(1950, 1, 1),
            },
        ),
        (
            Candidate,
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
            Candidate,
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
            Candidate,
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
        (
            Measure,
            {
                "level": "S",
                "name": "M111",
                "state": "OR",
                "election_date": date(2022, 11, 8),
            },
            {
                "level": "S",
                "name": "M112",
                "state": "OR",
                "election_date": date(2022, 11, 8),
            },
        ),
        (
            Measure,
            {
                "level": "S",
                "name": "M111",
                "state": "OR",
                "election_date": date(2022, 5, 4),
            },
            {
                "level": "S",
                "name": "M111",
                "state": "OR",
                "election_date": date(2022, 11, 8),
            },
        ),
        (
            Measure,
            {
                "level": "S",
                "name": "M111",
                "state": "OR",
                "election_date": date(2022, 11, 8),
            },
            {
                "level": "S",
                "name": "M111",
                "state": "WA",
                "election_date": date(2022, 11, 8),
            },
        ),
    ],
)
def test_create_unique_resources(model, original, near_duplicate):
    resource1 = model.objects.create(**original)
    resource2 = model.objects.create(**near_duplicate)
    assert resource1.id != resource2.id


@pytest.mark.parametrize(
    "model, data",
    [
        (
            Candidate,
            {"first_name": "Invalid", "last_name": "Party", "party": "Democrat"},
        ),
        (
            Endorser,
            {
                "name": "Oregon League of Conservation Voters",
                "abbreviation": "Oregon League of Conservation Voters",
            },
        ),
        (
            Measure,
            {
                "name": "M112",
                "state": "Oregon",
                "level": "S",
                "election_date": date(2022, 11, 8),
            },
        ),
        (
            Measure,
            {
                "name": "M112",
                "state": "OR",
                "level": "County",
                "election_date": date(2022, 11, 8),
            },
        ),
    ],
)
def test_create_field_exceeds_max_length(model, data):
    with pytest.raises(DataError, match=r"value too long"):
        model.objects.create(**data)


# Candidate
@pytest.mark.parametrize(
    "data, full_name",
    [
        (
            {"first_name": "Wonderboy"},
            "Wonderboy",
        ),
        (
            {"first_name": "Malcolm", "last_name": "Levitan"},
            "Malcolm Levitan",
        ),
        (
            {
                "first_name": "Diane",
                "middle_name": "Kimberly",
                "last_name": "Gould",
            },
            "Diane Kimberly Gould",
        ),
    ],
)
def test_candidate_full_name(data, full_name):
    c = Candidate.objects.create(**data)
    assert c.full_name() == full_name


# Endorser
def test_endorser_unique_constraint():
    e1 = {"name": "Basic Rights Oregon", "abbreviation": "BRO"}
    e2 = {"name": "Bigly Republicans of Oregon", "abbreviation": "BRO"}
    Endorser.objects.create(**e1)
    with pytest.raises(IntegrityError, match=r"violates unique constraint"):
        Endorser.objects.create(**e2)
