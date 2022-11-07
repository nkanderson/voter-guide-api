import pytest
from rest_framework.test import APIRequestFactory

from voterguide.accounts.models import CustomUser


@pytest.fixture
def user():
    return CustomUser.objects.create(
        email="moira@rosebud.motel", password="sunr1se_3@y"
    )


@pytest.fixture
def drf_rf():
    return APIRequestFactory()
