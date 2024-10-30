import pytest


@pytest.mark.django_db
def test_user_create(django_user_model):
    django_user_model.objects.create_user(username="john", password="pass1234")

    assert django_user_model.objects.count() == 1
    user = django_user_model.objects.first()
    assert user.username == "john"
    assert user.is_active is True
    assert user.is_staff is False
