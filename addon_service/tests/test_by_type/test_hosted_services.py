import json

from django.conf import settings
from django.forms.models import model_to_dict
from django.urls import reverse
from rest_framework.test import APITestCase

from addon_service.models import AuthorizedStorageAccount
from addon_toolkit import AddonCapabilities

from .. import _factories
from .._helpers import MockOSF


def _make_post_payload(*, base_service, host_url):
    return {
        "data": {
            "type": "authorized-storage-accounts",
            "attributes": {
                "authorized_capabilities": [AddonCapabilities.ACCESS.name],
                "api_url_base": host_url,
            },
            "relationships": {
                "external_storage_service": {
                    "data": {
                        "type": "external-storage-services",
                        "id": base_service.id,
                    }
                },
            },
        }
    }


class TestImplicitlyCreateHostedServiceEntry(APITestCase):
    def setUp(self):
        super().setUp()
        self._user = _factories.UserReferenceFactory()
        self.client.cookies[settings.USER_REFERENCE_COOKIE] = self._user.user_uri
        self._mock_osf = MockOSF()
        self.enterContext(self._mock_osf.mocking())

    def test_post(self):
        base_service = _factories.ExternalStorageServiceFactory()
        self.assertEqual(base_service.api_url_base, "")
        self.assertFalse(base_service.authorized_storage_accounts.exists())

        hosted_api_base = "https://api.test/"
        _resp = self.client.post(
            reverse("authorized-storage-accounts-list"),
            _make_post_payload(base_service=base_service, host_url=hosted_api_base),
            format="vnd.api+json",
        )
        self.assertEqual(_resp.status_code, 201)

        account = AuthorizedStorageAccount.objects.get(
            pk=json.loads(_resp.rendered_content)["data"]["id"]
        )
        base_service.refresh_from_db()
        with self.subTest("POST with api_url_base does not modify base service"):
            self.assertEqual(base_service.api_url_base, "")

        with self.subTest("Created account points to the new service"):
            self.assertNotEqual(account.external_storage_service.id, base_service.id)

        created_service = account.external_storage_service
        with self.subTest("Created service has the correct api_url_base"):
            self.assertEqual(
                account.external_storage_service.api_url_base, hosted_api_base
            )

        created_service_dict = model_to_dict(created_service)
        base_service_dict = model_to_dict(base_service)
        with self.subTest("Created service copies other attributes from base service"):
            # Lists not hashable
            self.assertEqual(
                created_service_dict.pop("supported_scopes"),
                base_service_dict.pop("supported_scopes"),
            )
            self.assertEqual(
                dict(
                    set(base_service_dict.items()) - set(created_service_dict.items())
                ).keys(),
                {"id", "api_url_base", "modified"},
            )
            # model_to_dict excludes non-editable fields
            self.assertNotEqual(created_service.created, base_service.created)

        with self.subTest(
            "Second post with same api_url_base returns the previously created service"
        ):
            _resp2 = self.client.post(
                reverse("authorized-storage-accounts-list"),
                _make_post_payload(base_service=base_service, host_url=hosted_api_base),
                format="vnd.api+json",
            )
            self.assertEqual(_resp2.status_code, 201)

            account2 = AuthorizedStorageAccount.objects.get(
                pk=json.loads(_resp2.rendered_content)["data"]["id"]
            )

            self.assertEqual(
                account2.external_storage_service, account.external_storage_service
            )
