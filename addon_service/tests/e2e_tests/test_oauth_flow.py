from asgiref.sync import async_to_sync
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase

from addon_service.common.aiohttp_session import (
    close_singleton_client_session__blocking,
    get_singleton_client_session,
)
from addon_service.common.credentials_formats import CredentialsFormats
from addon_service.models import AuthorizedStorageAccount
from addon_service.tests import (
    _factories,
    _helpers,
)
from addon_toolkit import AddonCapabilities


MOCK_ACCESS_TOKEN = "access"
MOCK_REFRESH_TOKEN = "refresh"


def _make_post_payload(*, external_service, capabilities=None, credentials=None):
    return {
        "data": {
            "type": "authorized-storage-accounts",
            "attributes": {
                "authorized_capabilities": [AddonCapabilities.ACCESS.name],
                "initiate_oauth": True,
            },
            "relationships": {
                "external_storage_service": {
                    "data": {
                        "type": "external-storage-services",
                        "id": external_service.id,
                    }
                },
            },
        }
    }


class TestOAuth2Flow(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls._user = _factories.UserReferenceFactory()
        cls._service = _factories.ExternalStorageServiceFactory()

    def setUp(self):
        super().setUp()
        self.addCleanup(close_singleton_client_session__blocking)
        self._mock_service = _helpers.MockExternalService(self._service)
        self._mock_service.configure_static_tokens(
            access=MOCK_ACCESS_TOKEN, refresh=MOCK_REFRESH_TOKEN
        )

        self.client.cookies[settings.USER_REFERENCE_COOKIE] = self._user.user_uri
        self._mock_osf = _helpers.MockOSF()
        self.enterContext(self._mock_osf.mocking())

    def test_oauth_account_setup(self):
        with self.subTest("Preconditions"):
            self.assertEqual(
                self._service.credentials_format, CredentialsFormats.OAUTH2
            )

        # Set up Account
        _resp = self.client.post(
            reverse("authorized-storage-accounts-list"),
            _make_post_payload(external_service=self._service),
            format="vnd.api+json",
        )
        _account = AuthorizedStorageAccount.objects.get(id=_resp.data["id"])

        with self.subTest("Account Initial Conditions"):
            self.assertIsNotNone(_account.auth_url)
            self.assertIsNone(_account.oauth2_token_metadata.refresh_token)
            self.assertIsNone(_account.credentials)

        self._mock_service.set_internal_client(self.client)

        async_to_sync(self._get)(_account)

        _account.refresh_from_db()
        with self.subTest("Credentials set post-exchange"):
            self.assertEqual(_account.credentials.access_token, MOCK_ACCESS_TOKEN)
        with self.subTest("Refresh token set post-exchange"):
            self.assertEqual(
                _account.oauth2_token_metadata.refresh_token, MOCK_REFRESH_TOKEN
            )

    async def _get(self, _account: AuthorizedStorageAccount):
        aiohttp_client_session = await get_singleton_client_session()
        async with self._mock_service.mocking():
            return await aiohttp_client_session.get(_account.auth_url)
