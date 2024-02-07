import dataclasses
from typing import ClassVar

from primitive_metadata import primitive_rdf as rdf


@dataclasses.dataclass(frozen=True)
class AddonCapability:
    iri: str
    label: rdf.Literal = dataclasses.field(compare=False)
    comment: rdf.Literal = dataclasses.field(compare=False)


class AddonCapabilities:
    # TODO: easy, explicit, stable map from subclass to IntEnum/choices

    declared_capability_set: ClassVar[  # set by __init_subclass__
        frozenset[AddonCapability]
    ]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.declared_capability_set = frozenset(
            _attr_value
            for _attr_name, _attr_value in cls.__dict__.items()
            if (
                not _attr_name.startswith("_")
                and isinstance(_attr_value, AddonCapability)
            )
        )
