from django.test import TestCase

from ._factories import InternalUserFactory


class TestTestCase(TestCase):
    def test_tests(self):
        """Simple base test to test test infrastructure"""
        pass

    def test_model(self):
        """Simple base test to test test models"""
        user = InternalUserFactory(user_uri="http://osf.example/hurts")
        user.save()
        self.assertEqual(user.user_uri, "http://osf.example/hurts")
