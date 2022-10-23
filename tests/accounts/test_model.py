import pytest

from voterguide.accounts.models import CustomUser

pytestmark = pytest.mark.django_db

user_data = {"email": "test@example.com", "password": "supersecret1234"}


def test_create_user():
    user = CustomUser.objects.create(**user_data)
    assert isinstance(user, CustomUser) == True
