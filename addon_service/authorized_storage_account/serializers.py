from rest_framework_json_api import serializers
from rest_framework_json_api.relations import (
    HyperlinkedRelatedField,
    ResourceRelatedField,
)
from rest_framework_json_api.utils import get_resource_type_from_model

from addon_service.common.serializer_fields import ReadOnlyResourceRelatedField
from addon_service.models import (
    AuthorizedStorageAccount,
    ConfiguredStorageAddon,
    ExternalAccount,
    ExternalCredentials,
    ExternalStorageService,
    UserReference,
)


RESOURCE_NAME = get_resource_type_from_model(AuthorizedStorageAccount)


class AuthorizedStorageAccountSerializer(serializers.HyperlinkedModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Check if it's a POST request and remove the field as it's not in our FE spec
        if "context" in kwargs and kwargs["context"]["request"].method == "POST":
            self.fields.pop("configured_storage_addons", None)

    url = serializers.HyperlinkedIdentityField(
        view_name=f"{RESOURCE_NAME}-detail", required=False
    )
    account_owner = ReadOnlyResourceRelatedField(
        many=False,
        queryset=UserReference.objects.all(),
        related_link_view_name=f"{RESOURCE_NAME}-related",
    )
    external_storage_service = ResourceRelatedField(
        queryset=ExternalStorageService.objects.all(),
        many=False,
        related_link_view_name=f"{RESOURCE_NAME}-related",
    )
    configured_storage_addons = HyperlinkedRelatedField(
        many=True,
        queryset=ConfiguredStorageAddon.objects.active(),
        related_link_view_name=f"{RESOURCE_NAME}-related",
        required=False,
    )
    username = serializers.CharField(
        write_only=True
    )  # placeholder for ExternalCredentials integrity only not auth
    password = serializers.CharField(
        write_only=True
    )  # placeholder for ExternalCredentials integrity only not auth

    included_serializers = {
        "account_owner": "addon_service.serializers.UserReferenceSerializer",
        "external_storage_service": "addon_service.serializers.ExternalStorageServiceSerializer",
        "configured_storage_addons": "addon_service.serializers.ConfiguredStorageAddonSerializer",
    }

    def create(self, validate_data):
        session_user_uri = self.context["request"].session.get("user_reference_uri")
        account_owner, _ = UserReference.objects.get_or_create(
            user_uri=session_user_uri
        )
        external_storage_service = validate_data["external_storage_service"]
        # TODO(ENG-5189): Update this once credentials format is finalized
        credentials, _ = ExternalCredentials.objects.get_or_create(
            oauth_key=validate_data["username"],
            oauth_secret=validate_data["password"],
        )

        external_account, _ = ExternalAccount.objects.get_or_create(
            owner=account_owner,
            credentials=credentials,
            credentials_issuer=external_storage_service.credentials_issuer,
        )

        return AuthorizedStorageAccount.objects.create(
            external_storage_service=external_storage_service,
            external_account=external_account,
        )

    class Meta:
        model = AuthorizedStorageAccount
        fields = [
            "url",
            "account_owner",
            "configured_storage_addons",
            "default_root_folder",
            "external_storage_service",
            "username",
            "password",
        ]
