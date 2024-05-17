"""exception classes for addon_toolkit"""


class AddonToolkitException(Exception):
    pass


class NotAnImp(AddonToolkitException):
    pass


class ImpNotValid(AddonToolkitException):
    pass


class ImpTooAbstract(ImpNotValid):
    pass


class ImpHasTooManyJobs(ImpNotValid):
    pass


class ImpMissingInterface(ImpNotValid):
    pass


class NotAnOperation(AddonToolkitException):
    pass


class OperationNotImplemented(AddonToolkitException):
    pass


class OperationNotValid(AddonToolkitException):
    pass
