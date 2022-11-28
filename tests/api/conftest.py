from datetime import date

import pytest
from rest_framework.test import APIRequestFactory

from voterguide.accounts.models import CustomUser
from voterguide.api.models import Candidate, Endorser, Measure, Seat
from voterguide.api.serializers import (
    CandidateSerializer,
    EndorserSerializer,
    MeasureSerializer,
    SeatSerializer,
)


@pytest.fixture
def user():
    return CustomUser.objects.create(
        email="moira@rosebud.motel", password="sunr1se_3@y"
    )


@pytest.fixture
def drf_rf():
    return APIRequestFactory()


@pytest.fixture
@pytest.mark.django_db
def endorser():
    return Endorser.objects.create(name="Basic Rights Oregon", abbreviation="BRO")


@pytest.fixture
@pytest.mark.django_db
def measure():
    return Measure.objects.create(
        name="26-232",
        level="S",
        state="OR",
        county="Multnomah",
        election_date=date(2022, 11, 8),
    )


@pytest.fixture
@pytest.mark.django_db
def seat():
    return Seat.objects.create(
        level="S",
        branch="E",
        role="Governor",
        state="OR",
    )


@pytest.fixture
@pytest.mark.django_db
def candidate():
    return Candidate.objects.create(
        first_name="Cameron",
        last_name="Howe",
        date_of_birth=date(1961, 1, 1),
    )


@pytest.fixture
def endorser_serializer(endorser, drf_rf):
    return EndorserSerializer(endorser, context={"request": drf_rf.get("/")})


@pytest.fixture
def measure_serializer(measure, drf_rf):
    return MeasureSerializer(measure, context={"request": drf_rf.get("/")})


@pytest.fixture
def seat_serializer(seat, drf_rf):
    return SeatSerializer(seat, context={"request": drf_rf.get("/")})


@pytest.fixture
def candidate_serializer(candidate, drf_rf):
    return CandidateSerializer(candidate, context={"request": drf_rf.get("/")})
