from datetime import date

import pytest
from rest_framework.test import APIRequestFactory

from voterguide.accounts.models import CustomUser
from voterguide.api.models import Endorser, Measure, Seat
from voterguide.api.serializers import EndorserSerializer, MeasureSerializer


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
def endorser_serializer(endorser, drf_rf):
    return EndorserSerializer(endorser, context={"request": drf_rf.get("/")})


@pytest.fixture
def measure_serializer(measure, drf_rf):
    return MeasureSerializer(measure, context={"request": drf_rf.get("/")})
