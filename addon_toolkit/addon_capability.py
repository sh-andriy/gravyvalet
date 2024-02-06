import dataclasses
import enum

from primitive_metadata import primitive_rdf as rdf


@dataclasses.dataclass(frozen=True)
class DeclaredAddonCapability:
    iri: str
    label: rdf.Literal
    comment: rdf.Literal

    # TODO:
    @classmethod
    def from_int(cls, addon_capability_int: int):
        return cls(IntAddonCapability(addon_capability_int).name)

    def __int__(self):  # allows casting to integer with `int(addon_capability)`
        return int(IntAddonCapability[self.name])


class StorageCapability:
    ACCESS = DeclaredAddonCapability(
        iri=GRAVY.access_capability,
        label=rdf.literal("access capability", language="en"),
        comment=rdf.literal("allows access to data items", langugae="en"),
    )
    BROWSE = DeclaredAddonCapability(
        iri=GRAVY.browse_capability,
        label=rdf.literal("browse capability", language="en"),
        comment=rdf.literal(
            "allows browsing relation graphs among items",
            langugae="en",
        ),
    )
    UPDATE = DeclaredAddonCapability(
        iri=GRAVY.update_capability,
        label=rdf.literal("update capability", language="en"),
        comment=rdf.literal("allows updating and adding items", langugae="en"),
    )
    COMMIT = DeclaredAddonCapability(
        iri=GRAVY.commit_capability,
        label=rdf.literal("commit capability", language="en"),
        comment=rdf.literal("allows ", langugae="en"),
    )
