from factory.django import DjangoModelFactory
from addon_service.internal_user.models import InternalUser


class UserFactory(DjangoModelFactory):
    class Meta:
        model = InternalUser
