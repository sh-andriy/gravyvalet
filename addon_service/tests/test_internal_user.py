from django.urls import reverse
from rest_framework.test import APITestCase

from addon_service.tests.factories import InternalUserFactory


class TestInternalUser(APITestCase):
    def test_get(self):
        _user = InternalUserFactory(user_uri="http://osf.example/hurts1")
        _resp = self.client.get(
            reverse("internal-users-detail", kwargs={"pk": _user.pk}),
        )
        assert _resp.status_code == 200
        assert _resp.data["user_uri"] == "http://osf.example/hurts1"
