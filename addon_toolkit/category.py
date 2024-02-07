import dataclasses
import enum
from typing import Iterator

from .interface import AddonInterface
from .operation import AddonOperation


@dataclasses.dataclass(frozen=True)
class AddonCategory:
    capabilities: type[enum.StrEnum]
    base_interface: type[AddonInterface]

    def operations_declared(
        self,
        *,
        capability_id: str | None = None,
    ) -> Iterator[AddonOperation]:
        for _interface_cls in self.base_interface.__mro__:
            yield from AddonOperation.operations_declared_on_interface(
                _interface_cls, capability_id=capability_id
            )

    def operations_implemented(
        self,
        interface_cls: type[AddonInterface],
        capability_id: str | None = None,
    ) -> Iterator[AddonOperation]:
        assert issubclass(interface_cls, self.base_interface)
        for _op in self.operations_declared(capability_id=capability_id):
            if _op.is_implemented_on(interface_cls):
                yield _op
