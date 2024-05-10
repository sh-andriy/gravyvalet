import abc
import functools
import logging
import typing

from addon_service.common.opaque import (
    make_opaque,
    unmake_opaque,
)


_logger = logging.getLogger(__name__)


class CachedByArgs(type):
    """metaclass that caches new objects by constructor args -- same args get the same object

    careful: there's no cache size limit -- use only with bounded arg-space

    limitation: no keyword args; only positional args allowed
                (avoid duplicates from kwargs in different order)
    """

    @functools.cache
    def __call__(cls, *args):
        _logger.debug("CachedByArgs: new %s with args=%r", cls, args)
        return super().__call__(*args)


class StaticDataclassModel(metaclass=CachedByArgs):
    """a django-model-like base class for statically defined, natural-keyed data
    (put duck-typing here for rest_framework_json_api)
    """

    ###
    # abstract methods

    @classmethod
    @abc.abstractmethod
    def init_args_from_static_key(cls, key: str) -> tuple:
        raise NotImplementedError

    @property
    def static_key(self) -> str:
        raise NotImplementedError

    ###
    # class methods

    @classmethod
    def get_by_pk(cls, pk: str) -> typing.Self:
        _static_key = unmake_opaque(pk)
        return cls.get_by_static_key(_static_key)

    @classmethod
    def get_by_static_key(cls, static_key: str) -> typing.Self:
        _init_args = cls.init_args_from_static_key(static_key)
        return cls(*_init_args)

    ###
    # instance methods

    @property
    def pk(self):
        return make_opaque(self.static_key)
