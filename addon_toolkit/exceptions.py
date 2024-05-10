# TODO: helpfully specific exceptions


class AddonToolkitException(Exception):
    pass


class NotAnImp(AddonToolkitException):
    pass


class BadImp(AddonToolkitException):
    pass


class ImpHasTooManyJobs(BadImp):
    pass


class ImpNotInstantiatable(BadImp):
    pass


class NotAnOperation(AddonToolkitException):
    pass


class OperationNotImplemented(AddonToolkitException):
    pass


class OperationNotValid(AddonToolkitException):
    pass
