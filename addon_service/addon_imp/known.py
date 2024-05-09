import enum

from addon_imps.storage import BoxDotComImp, StorageImp


if __debug__:
    from addon_imps.storage import my_blarg
    BlargStorageImp = StorageImp(imp_cls=my_blarg.MyBlargStorage)


@enum.unique
class KnownAddonImps(enum.Enum):
    """enum with a name for each addon implementation class that should be known to the api"""

    # STORAGE Imps are all prefixed with 1
    if __debug__:
        BLARG = 1000 # USE X000 for test imps
    BOX_DOT_COM = 1001

    # ARCHIVE Imps are all prefixed with 2
    if __debug__:
        BLARCHIVE: 2000

    @property
    def imp(self):
        """Retrieve the correct AddonImp for the member"""
        match self:
            case KnownStorageAddonImps.BLARG:
                return BlargStorageImp
            case KnownStorageAddonImps.BOX_DOT_COM:
                return BoxDotComImp
            case _:
                raise ValueError(f"No concrete implementation for Addon {self.name}")

    @property
    def is_storage_imp(self):
        return 1000 <= self.value < 2000

    @property
    def is_archive_imp(self):
        return 2000 <= self.value < 3000 


def get_imp_by_name(imp_name):
    """Return a known AddonImp given its name"""
    for member in KnownAddonImps:
        imp = member.imp
        if member.name == imp_name or imp.name == imp_name:
            return imp
