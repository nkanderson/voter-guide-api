from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.db.utils import DataError, IntegrityError

from voterguide.api.models import (
    Candidate,
    Endorser,
    Measure,
    MeasureEndorsement,
    Seat,
    SeatEndorsement,
)

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
                "name": "26-232",
                "level": "S",
                "state": "OR",
                "county": "Multnomah",
                "election_date": date(2022, 11, 8),
            },
            "26-232: election on November 8, 2022 in Oregon",
        ),
        (
            Seat,
            {
                "level": "F",
                "branch": "E",
                "role": "President",
            },
            "President at the Federal level",
        ),
        (
            Seat,
            {
                "level": "F",
                "branch": "L",
                "body": "S",
                "state": "CA",
            },
            "Senator at the Federal level in the state of California",
        ),
        (
            Seat,
            {
                "level": "F",
                "branch": "L",
                "role": "Representative",
                "body": "H",
                "district": 2,
                "state": "MN",
            },
            "Representative at the Federal level, district 2, in the state of Minnesota",
        ),
        (
            Seat,
            {
                "level": "S",
                "branch": "L",
                "role": "Senator",
                "body": "S",
                "district": 1,
                "state": "CA",
            },
            "Senator at the State level, district 1, in the state of California",
        ),
        (
            Seat,
            {
                "level": "S",
                "branch": "L",
                "body": "H",
                "district": 5,
                "state": "OR",
            },
            "Representative at the State level, district 5, in the state of Oregon",
        ),
        (
            Seat,
            {
                "level": "S",
                "branch": "E",
                "role": "Governor",
                "state": "OR",
            },
            "Governor at the State level in the state of Oregon",
        ),
        (
            Seat,
            {
                "level": "C",
                "branch": "E",
                "role": "Mayor",
                "state": "OR",
                "city": "Portland",
            },
            "Mayor at the City level in the city of Portland in the state of Oregon",
        ),
        (
            Seat,
            {
                "level": "T",
                "branch": "E",
                "role": "Commission Chair",
                "state": "OR",
                "county": "Multnomah",
            },
            "Commission Chair at the County level in Multnomah County in the state of Oregon",
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
                "first_name": "Joe",
                "date_of_birth": date(1947, 1, 1),
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
                "first_name": "Gordon",
            },
            "candidate_unique_first_last_null_dob",
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
        # NOTE: The following constraint exists at the database level, but the
        # `validate_unique` validation runs prior to the instance being committed
        # to the database. If that validation is removed, this test should be
        # enabled.
        # (
        #     Seat,
        #     {
        #         "level": "F",
        #         "branch": "E",
        #         "role": "President",
        #     },
        #     "seat_unique_role_level_null_state",
        # ),
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
        # NOTE: The following constraint exists at the database level, but the
        # Seat model's `clean` method runs validation prior to the instance being
        # committed to the database. If that validation is removed, this test
        # should be enabled.
        # (
        #     Seat,
        #     {
        #         "level": "I",
        #         "state": "WA",
        #         "role": "Governor",
        #     },
        #     "seat_level_valid",
        # ),
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
        # Unique on level
        (
            Seat,
            {
                "level": "F",
                "branch": "L",
                "body": "H",
                "district": "3",
                "state": "WA",
                "role": "Representative",
            },
            {
                "level": "S",
                "branch": "L",
                "body": "H",
                "district": "3",
                "state": "WA",
                "role": "Representative",
            },
        ),
        # Unique on branch
        (
            Seat,
            {
                "level": "F",
                "branch": "E",
                "role": "President",
            },
            {
                "level": "F",
                "branch": "O",
                "role": "President",
            },
        ),
        # Unique on role
        (
            Seat,
            {
                "level": "F",
                "role": "President",
            },
            {
                "level": "F",
                "role": "Vice President",
            },
        ),
        # Unique on body
        (
            Seat,
            {
                "level": "S",
                "body": "S",
                "district": "3",
                "state": "WA",
                "role": "Senator",
            },
            {
                "level": "S",
                "body": "H",
                "district": "3",
                "state": "WA",
                "role": "Senator",
            },
        ),
        # Unique on district
        (
            Seat,
            {
                "level": "F",
                "body": "H",
                "district": "3",
                "state": "WA",
                "role": "Representative",
            },
            {
                "level": "F",
                "body": "H",
                "district": "1",
                "state": "WA",
                "role": "Representative",
            },
        ),
        # Unique on state
        (
            Seat,
            {
                "level": "F",
                "body": "H",
                "district": "3",
                "state": "WA",
                "role": "Representative",
            },
            {
                "level": "F",
                "body": "H",
                "district": "3",
                "state": "OR",
                "role": "Representative",
            },
        ),
        # Unique on state
        (
            Seat,
            {
                "level": "S",
                "state": "WA",
                "role": "Governor",
            },
            {
                "level": "S",
                "state": "OR",
                "role": "Governor",
            },
        ),
        # Unique on city
        (
            Seat,
            {
                "level": "C",
                "city": "Portland",
                "role": "Mayor",
                "state": "OR",
            },
            {
                "level": "C",
                "city": "Pendleton",
                "role": "Mayor",
                "state": "OR",
            },
        ),
        # Unique on county
        (
            Seat,
            {
                "level": "T",
                "county": "Multnomah",
                "role": "Commission Chair",
                "state": "OR",
            },
            {
                "level": "T",
                "county": "Clackamas",
                "role": "Commission Chair",
                "state": "OR",
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


@pytest.mark.parametrize(
    "model, data, message",
    [
        (
            Seat,
            {"level": "F", "state": "SD"},
            "Role could not be determined",
        ),
        (
            Seat,
            {"level": "S", "body": "H", "state": "ZZ"},
            "State value is invalid",
        ),
        (
            Seat,
            {"level": "F", "role": "Senator", "body": "Z", "state": "MN"},
            "Body value is invalid",
        ),
        (
            Seat,
            {
                "role": "Governor",
                "level": "S",
            },
            "State field must be set",
        ),
        (
            Seat,
            {"role": "Mayor", "level": "C", "state": "SD"},
            "City field must be set",
        ),
        (
            Seat,
            {"role": "Commission Chair", "level": "T", "state": "OR"},
            "County field must be set",
        ),
        (
            Seat,
            {"level": "F", "branch": "L", "body": "H"},
            "State field must be set for all seats in the legislature",
        ),
        (
            Seat,
            {"level": "F", "role": "Representative", "branch": "L", "state": "CA"},
            "Body field must be set for all seats in the legislature",
        ),
        (
            Seat,
            {"level": "F", "body": "H", "state": "SD"},
            "District field must be set",
        ),
        (
            Seat,
            {"level": "S", "body": "S", "state": "SD"},
            "District field must be set",
        ),
    ],
)
def test_validations(model, data, message):
    with pytest.raises(ValidationError, match=message):
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


def test_running_for_seat_foreign_key():
    c = Candidate.objects.create(first_name="Ryan", last_name="Ray")
    s = Seat.objects.create(level="F", role="President")
    c.running_for_seat = s
    c.save()
    assert s.candidate_set.first() == c


def test_seat_foreign_key():
    c = Candidate.objects.create(first_name="Yo-Yo", last_name="Engberk")
    s = Seat.objects.create(level="F", role="President")
    c.seat = s
    c.save()
    assert s.incumbent.first() == c


# Endorser
def test_endorser_unique_constraint():
    e1 = {"name": "Basic Rights Oregon", "abbreviation": "BRO"}
    e2 = {"name": "Bigly Republicans of Oregon", "abbreviation": "BRO"}
    Endorser.objects.create(**e1)
    with pytest.raises(IntegrityError, match=r"violates unique constraint"):
        Endorser.objects.create(**e2)


# Seat
@pytest.mark.parametrize(
    "data",
    [
        {
            "level": "F",
            "branch": "E",
            "role": "President",
        },
        {
            "level": "S",
            "branch": "L",
            "role": "Representative",
            "body": "H",
            "district": 3,
            "state": "WA",
        },
    ],
)
def test_seat_unique_validation(data):
    Seat.objects.create(**data)
    with pytest.raises(ValidationError, match="Seat must be unique"):
        Seat.objects.create(**data)


# MeasureEndorsement
def test_measure_endorsement_create_valid_instance(endorser, measure):
    e = MeasureEndorsement.objects.create(
        endorser=endorser,
        election_date=date(2022, 11, 8),
        url="https://example.com/endorsements",
        measure=measure,
        recommendation="Y",
    )
    assert isinstance(e, MeasureEndorsement)
    assert str(e) == "BRO recommends Yes for measure 26-232"


class TestMeasureEndorsementUniqueConstraint:
    @pytest.fixture(autouse=True)
    def data(self, endorser, measure):
        return {
            "endorser": endorser,
            "election_date": date(2022, 11, 8),
            "url": "https://example.com/endorsements",
            "measure": measure,
            "recommendation": "Y",
        }

    def test_recommendation(self, data):
        MeasureEndorsement.objects.create(**data)
        with pytest.raises(
            IntegrityError,
            match="measure_endorsement_unique_endorser_election_date_measure",
        ):
            MeasureEndorsement.objects.create(
                **(dict(list(data.items()) + [("recommendation", "N")]))
            )

    def test_url(self, data):
        MeasureEndorsement.objects.create(**data)
        with pytest.raises(
            IntegrityError,
            match="measure_endorsement_unique_endorser_election_date_measure",
        ):
            MeasureEndorsement.objects.create(
                **(
                    dict(
                        list(data.items())
                        + [("url", "https://example.com/other-endorsements")]
                    )
                )
            )


def test_measure_endorsement_create_unique_resources(endorser, measure):
    m_data = {
        "election_date": date(2022, 11, 8),
        "url": "https://example.com/endorsements",
        "recommendation": "Y",
    }
    orig_endorser = Endorser.objects.get(pk=endorser.pk)
    orig_measure = Measure.objects.get(pk=measure.pk)
    m1 = MeasureEndorsement.objects.create(
        endorser=orig_endorser,
        measure=orig_measure,
        **m_data,
    )

    # Unique on date
    m2 = MeasureEndorsement.objects.create(
        endorser=orig_endorser,
        measure=orig_measure,
        **(dict(list(m_data.items()) + [("election_date", date(2022, 5, 17))])),
    )
    assert m1.id != m2.id

    # Unique on endorser
    endorser.pk = None
    endorser.abbreviation = "ABC"
    endorser._state.adding = True
    endorser.save()
    m3 = MeasureEndorsement.objects.create(
        endorser=endorser,
        measure=orig_measure,
        **m_data,
    )
    assert m1.endorser.id != m3.endorser.id
    assert m1.id != m3.id

    # Unique on measure
    measure.pk = None
    measure.name = "ABC123"
    measure._state.adding = True
    measure.save()
    m4 = MeasureEndorsement.objects.create(
        endorser=orig_endorser,
        measure=measure,
        **m_data,
    )
    assert m1.measure.id != m4.measure.id
    assert m1.id != m4.id


def test_measure_endorsement_measure_foreign_key(endorser, measure):
    e = MeasureEndorsement.objects.create(
        endorser=endorser,
        election_date=date(2022, 11, 8),
        url="https://example.com/endorsements",
        measure=measure,
        recommendation="Y",
    )
    assert e.measure == measure
    assert e.endorser == endorser


# SeatEndorsement
def test_seat_endorsement_create_valid_instance(endorser, seat):
    s = SeatEndorsement.objects.create(
        endorser=endorser,
        election_date=date(2022, 11, 8),
        url="https://example.com/endorsements",
        seat=seat,
    )
    assert isinstance(s, SeatEndorsement)
    assert str(s) == (
        "BRO is endorsing no one for Governor at the State level in the state of "
        "Oregon on November 8, 2022"
    )


def test_seat_endorsement_unique_constraint(endorser, seat):
    s_data = {
        "endorser": endorser,
        "election_date": date(2022, 11, 8),
        "url": "https://example.com/endorsements",
        "seat": seat,
    }
    SeatEndorsement.objects.create(**s_data)
    with pytest.raises(
        IntegrityError,
        match="seat_endorsement_unique_endorser_election_date_seat",
    ):
        SeatEndorsement.objects.create(
            **(
                dict(
                    list(s_data.items())
                    + [("url", "https://example.com/other-endorsements")]
                )
            )
        )


def test_seat_endorsement_create_unique_resources(endorser, seat):
    s_data = {
        "election_date": date(2022, 11, 8),
        "url": "https://example.com/endorsements",
    }
    orig_endorser = Endorser.objects.get(pk=endorser.pk)
    orig_seat = Seat.objects.get(pk=seat.pk)
    s1 = SeatEndorsement.objects.create(
        endorser=orig_endorser,
        seat=orig_seat,
        **s_data,
    )

    # Unique on date
    s2 = SeatEndorsement.objects.create(
        endorser=orig_endorser,
        seat=orig_seat,
        **(dict(list(s_data.items()) + [("election_date", date(2022, 5, 17))])),
    )
    assert s1.id != s2.id

    # Unique on endorser
    endorser.pk = None
    endorser.abbreviation = "ABC"
    endorser._state.adding = True
    endorser.save()
    s3 = SeatEndorsement.objects.create(
        endorser=endorser,
        seat=orig_seat,
        **s_data,
    )
    assert s1.endorser.id != s3.endorser.id
    assert s1.id != s3.id

    # Unique on seat
    seat.pk = None
    seat.role = "Lieutenant Governor"
    seat._state.adding = True
    seat.save()
    s4 = SeatEndorsement.objects.create(
        endorser=orig_endorser,
        seat=seat,
        **s_data,
    )
    assert s1.seat.id != s4.seat.id
    assert s1.id != s4.id


def test_seat_endorsement_seat_foreign_key(endorser, seat):
    s = SeatEndorsement.objects.create(
        endorser=endorser,
        election_date=date(2022, 11, 8),
        url="https://example.com/endorsements",
        seat=seat,
    )
    assert s.endorser == endorser
    assert s.seat == seat


def test_seat_endorsement_candidates_many_to_many(endorser, seat):
    s_data = {
        "seat": seat,
        "endorser": endorser,
        "url": "https://example.com/endorsements",
    }
    s = SeatEndorsement.objects.create(
        **s_data,
        election_date=date(2022, 11, 8),
    )
    s2 = SeatEndorsement.objects.create(**s_data, election_date=date(2022, 5, 17))

    # Test single candidate to endorsement
    c = Candidate.objects.create(first_name="Yo-Yo", last_name="Engberk")
    s.candidates.add(c)
    assert s.candidates.get() == c
    assert c.seatendorsement_set.get() == s
    assert str(s) == (
        "BRO is endorsing Yo-Yo Engberk for Governor at the State level in the "
        "state of Oregon on November 8, 2022"
    )

    # Test multiple candidates to endorsement
    c2 = Candidate.objects.create(first_name="Haley", last_name="Clark")
    s.candidates.add(c2)
    assert c2 in s.candidates.all()
    assert str(s) == (
        "BRO is endorsing Yo-Yo Engberk, Haley Clark for Governor at the State "
        "level in the state of Oregon on November 8, 2022"
    )

    # Test multiple endorsements to candidate
    c2.seatendorsement_set.add(s2)
    assert s2 in c2.seatendorsement_set.all()
    assert str(s2) == (
        "BRO is endorsing Haley Clark for Governor at the State level in the "
        "state of Oregon on May 17, 2022"
    )
