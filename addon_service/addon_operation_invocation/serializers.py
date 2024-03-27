from rest_framework_json_api import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from rest_framework_json_api.utils import get_resource_type_from_model

from addon_service.common import view_names
from addon_service.common.enums.serializers import EnumNameChoiceField
from addon_service.common.invocation import InvocationStatus
from addon_service.common.serializer_fields import DataclassRelatedDataField
from addon_service.models import (
    AddonOperationInvocation,
    AddonOperationModel,
    ConfiguredStorageAddon,
    UserReference,
)
from addon_toolkit.operation import AddonOperationType


RESOURCE_TYPE = get_resource_type_from_model(AddonOperationInvocation)


class AddonOperationInvocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AddonOperationInvocation
        fields = [
            "url",
            "invocation_status",
            "operation_kwargs",
            "operation_result",
            "operation",
            "by_user",
            "thru_addon",
            "created",
            "modified",
        ]

    url = serializers.HyperlinkedIdentityField(
        view_name=view_names.detail_view(RESOURCE_TYPE)
    )
    invocation_status = EnumNameChoiceField(enum_cls=InvocationStatus, read_only=True)
    operation_kwargs = serializers.JSONField()
    operation_result = serializers.JSONField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)

    thru_addon = ResourceRelatedField(
        many=False,
        queryset=ConfiguredStorageAddon.objects.all(),
        related_link_view_name=view_names.related_view(RESOURCE_TYPE),
    )

    by_user = ResourceRelatedField(
        many=False,
        read_only=True,
        related_link_view_name=view_names.related_view(RESOURCE_TYPE),
    )

    operation = DataclassRelatedDataField(
        dataclass_model=AddonOperationModel,
        related_link_view_name=view_names.related_view(RESOURCE_TYPE),
    )

    included_serializers = {
        "thru_addon": "addon_service.serializers.ConfiguredStorageAddonSerializer",
        "operation": "addon_service.serializers.AddonOperationSerializer",
        "by_user": "addon_service.serializers.UserReferenceSerializer",
    }

    def create(self, validated_data):
        _operation = validated_data["operation"]
        _invocation = AddonOperationInvocation.objects.create(
            operation_identifier=_operation.natural_key_str,
            operation_kwargs=validated_data["operation_kwargs"],
            thru_addon=validated_data["thru_addon"],
            by_user=UserReference.objects.all().first(),  # TODO: infer user from request!
        )
        match _operation.operation_type:
            case AddonOperationType.REDIRECT | AddonOperationType.IMMEDIATE:
                _addon_instance = (
                    _operation.imp_cls()
                )  # TODO: consistent imp_cls instantiation (with params, probably)
                _invocation.perform_invocation(_addon_instance)  # block until done
            case AddonOperationType.EVENTUAL:
                raise NotImplementedError("TODO: enqueue task")
            case _:
                raise ValueError(f"unknown operation type: {_operation.operation_type}")
        return _invocation