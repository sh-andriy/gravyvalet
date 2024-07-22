from django.core.exceptions import ValidationError as ModelValidationError
from rest_framework_json_api import serializers
from rest_framework_json_api.relations import (
    HyperlinkedRelatedField,
    ResourceRelatedField,
)
from rest_framework_json_api.utils import get_resource_type_from_model

from addon_service.authorized_account.serializers import AuthorizedAccountSerializer
from addon_service.common import view_names
from addon_service.models import (
    AuthorizedStorageAccount,
    ConfiguredStorageAddon,
    ExternalStorageService,
    UserReference,
)


RESOURCE_TYPE = get_resource_type_from_model(AuthorizedStorageAccount)


class AuthorizedStorageAccountSerializer(AuthorizedAccountSerializer):
    external_storage_service = ResourceRelatedField(
        queryset=ExternalStorageService.objects.all(),
        many=False,
        related_link_view_name=view_names.related_view(RESOURCE_TYPE),
    )
    configured_storage_addons = HyperlinkedRelatedField(
        many=True,
        queryset=ConfiguredStorageAddon.objects.active(),
        related_link_view_name=view_names.related_view(RESOURCE_TYPE),
        required=False,
    )

    included_serializers = {
        "account_owner": "addon_service.serializers.UserReferenceSerializer",
        "external_storage_service": "addon_service.serializers.ExternalStorageServiceSerializer",
        "configured_storage_addons": "addon_service.serializers.ConfiguredStorageAddonSerializer",
        "authorized_operations": "addon_service.serializers.AddonOperationSerializer",
    }

    def create_external_service(self, validated_data: dict) -> ExternalStorageService:
        return validated_data["external_storage_service"]

    def create_authorized_account(
        self,
        external_service: ExternalStorageService,
        validated_data: dict,
    ) -> AuthorizedStorageAccount:
        session_user_uri = self.context["request"].session.get("user_reference_uri")
        account_owner, _ = UserReference.objects.get_or_create(
            user_uri=session_user_uri
        )
        try:
            return AuthorizedStorageAccount.objects.create(
                _display_name=validated_data.get("display_name", ""),
                external_storage_service=external_service,
                account_owner=account_owner,
                authorized_capabilities=validated_data.get("authorized_capabilities"),
                api_base_url=validated_data.get("api_base_url", ""),
            )
        except ModelValidationError as e:
            raise serializers.ValidationError(e)

    class Meta:
        model = AuthorizedStorageAccount
        fields = [
            "id",
            "url",
            "display_name",
            "account_owner",
            "api_base_url",
            "auth_url",
            "authorized_capabilities",
            "authorized_operations",
            "authorized_operation_names",
            "configured_storage_addons",
            "credentials",
            "default_root_folder",
            "external_storage_service",
            "initiate_oauth",
            "credentials_available",
        ]
