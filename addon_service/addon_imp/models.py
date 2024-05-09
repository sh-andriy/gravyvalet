import dataclasses

from django.utils.functional import cached_property

import .known as known_addon_imps
from addon_service.common.static_dataclass_model import StaticDataclassModel
from addon_toolkit import AddonImp


# dataclass wrapper for addon_toolkit.AddonImp that sufficiently
# meets rest_framework_json_api expectations on a model class
@dataclasses.dataclass(frozen=True)
class AddonImpModel(StaticDataclassModel):
    imp: AddonImp

    def __new__(self, imp):
        return super().__new__(cache_key=imp.natural_key, imp=imp)

    @classmethod
    def from_natural_key(cls, key):
        (_addon_imp_name,) = key
        return cls(known_addon_imps.get_imp_by_name(_addon_imp_name))

    ###
    # instance methods

    @property
    def natural_key(self):
        return self.imp.natural_key

    @cached_property
    def name(self) -> str:
        return self.imp.imp_name

    @cached_property
    def imp_cls(self) -> type:
        return self.imp.imp_cls

    @cached_property
    def protocol_docstring(self) -> str:
        return self.imp.addon_protocol.protocol_cls.__doc__ or ""

    @cached_property
    def imp_docstring(self) -> str:
        return self.imp.imp_cls.__doc__ or ""

    @cached_property
    def implemented_operations(self) -> frozenset[AddonOperationModel]:
        # local import to avoid circular import
        # (AddonOperationModel and AddonImpModel need to be mutually aware of each other in order to populate their respective relationship fields)
        from addon_service.addon_operation.models import AddonOperationModel

        return frozenset(
            AddonOperationModel(_op_imp) for _op_imp in self.imp.get_operation_imps()
        )


    def get_operation_imp(self, operation_name: str):
        # local import to avoid circular import
        # (AddonOperationModel and AddonImpModel need to be mutually aware of each other in order to populate their respective relationship fields)
        from addon_service.addon_operation.models import AddonOperationModel

        return AddonOperationModel(
            self.imp.get_operation_imp_by_name(operation_name)
        )

    class JSONAPIMeta:
        resource_name = "addon-imps"
