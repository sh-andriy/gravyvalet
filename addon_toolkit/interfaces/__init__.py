import enum

from . import (
    citation,
    storage,
)
from ._base import BaseAddonInterface


__all__ = (
    "AllAddonInterfaces",
    "BaseAddonInterface",
    "storage",
    "citation",
)


class AllAddonInterfaces(enum.Enum):
    STORAGE = storage.StorageAddonInterface
    CITATION = citation.CitationServiceInterface
