"""exception classes for addon_toolkit"""


class AddonToolkitException(Exception):
    pass


class NotAnImp(AddonToolkitException):
    pass


class BadImp(AddonToolkitException):
    pass


class ImpTooAbstract(BadImp):
    pass


class ImpHasTooManyJobs(BadImp):
    pass


class NotAnOperation(AddonToolkitException):
    pass


class OperationNotImplemented(AddonToolkitException):
    pass


class OperationNotValid(AddonToolkitException):
    pass
