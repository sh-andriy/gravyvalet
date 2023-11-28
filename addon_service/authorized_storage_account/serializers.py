from rest_framework_json_api import serializers
from rest_framework_json_api.relations import SerializerMethodResourceRelatedField

from addon_service.models import (
    AuthorizedStorageAccount,
    InternalUser,
    ExternalService,
)


class AuthorizedStorageAccountSerializer(serializers.ModelSerializer):
    account_owner = SerializerMethodResourceRelatedField(
        model=InternalUser,
        method_name='_get_account_owner',
    )
    external_service = SerializerMethodResourceRelatedField(
        model=ExternalService,
        method_name='_get_external_service',
    )

    class Meta:
        model = AuthorizedStorageAccount
        fields = [
            'default_root_folder',
            'external_storage_service',
            'account_owner',
            'external_service',
        ]

    def _get_account_owner(self, instance: AuthorizedStorageAccount):
        return instance.external_account.owner

    def _get_external_service(self, instance: AuthorizedStorageAccount):
        return instance.external_account.external_service
