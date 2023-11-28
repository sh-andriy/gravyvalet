from django.test import TestCase
from .factories import UserFactory


class TestTestCase(TestCase):
    def test_tests(self):
        """Simple base test to test test infrastructure"""
        pass

    def test_model(self):
        """Simple base test to test test models"""
        user = UserFactory(user_guid="hurts")
        user.save()
        assert user.user_guid == "hurts"
