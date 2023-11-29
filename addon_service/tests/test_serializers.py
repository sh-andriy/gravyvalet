import json
from addon_service.tests.factories import InternalUserFactory
from django.test import TestCase
from addon_service.internal_user.serializers import InternalUserSerializer
from addon_service.internal_user.models import InternalUser

from rest_framework import viewsets
from rest_framework_json_api.renderers import JSONRenderer


class TestViewSet(viewsets.ModelViewSet):
    queryset = InternalUser.objects.all()
    serializer_class = InternalUserSerializer


def render_test_data(instance):
    serializer = InternalUserSerializer(instance=instance)
    renderer = JSONRenderer()
    renderer_context = {"view": TestViewSet()}
    data = renderer.render(serializer.data, renderer_context=renderer_context)
    return json.loads(data)


class TestBaseSerializer(TestCase):
    """Simple base test to test serializer models"""

    def test_serializer(self):
        user = InternalUserFactory(user_uri="http://osf.example/hurts1")
        data = render_test_data(user)
        assert data["data"]["attributes"]["user_uri"] == "http://osf.example/hurts1"
