import abc
import functools
import typing
from urllib.parse import (
    quote,
    unquote,
)

from addon_service.common.opaque import (
    make_opaque,
    unmake_opaque,
)


NATURAL_KEY_DELIMITER = ":"


class StaticDataclassModel(abc.ABC):
    """a django-model-like base class for statically defined, natural-keyed data
    (put duck-typing here for rest_framework_json_api)
    """

    ###
    # abstract methods

    @classmethod
    @abc.abstractmethod
    def do_get_by_natural_key(cls, *key_parts) -> typing.Self:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def natural_key(self) -> tuple[str, ...]:
        raise NotImplementedError

    ###
    # class methods

    @classmethod
    def get_by_pk(cls, pk: str):
        _natural_key_str = unmake_opaque(pk)
        return cls.get_by_natural_key_str(_natural_key_str)

    @classmethod
    def get_by_natural_key_str(cls, key_str: str):
        _key_parts = tuple(
            unquote(_key_segment)
            for _key_segment in key_str.split(NATURAL_KEY_DELIMITER)
        )
        return cls.get_by_natural_key(*_key_parts)

    @classmethod
    @functools.cache  # cache result by model and natural key
    def get_by_natural_key(cls, *key_parts) -> typing.Self:
        """get the static model instance for the given key

        runs `do_get_by_natural_key` once per natural key, caches result until app restart
        """
        return cls.do_get_by_natural_key(*key_parts)

    ###
    # instance methods

    @property
    def natural_key_str(self) -> str:
        return NATURAL_KEY_DELIMITER.join(
            quote(_key_segment) for _key_segment in self.natural_key
        )

    @property
    def pk(self) -> str:
        # duck-type django.db.Model.pk
        return make_opaque(self.natural_key_str)
