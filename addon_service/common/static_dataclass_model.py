import abc
import dataclasses
import typing
import weakref
from urllib.parse import (
    quote,
    unquote,
)

from addon_service.common.opaque import (
    make_opaque,
    unmake_opaque,
)


NaturalKey = tuple[str, ...]
NATURAL_KEY_DELIMITER = ":"


class StaticDataclassModel(abc.ABC):
    """a django-model-like base class for statically defined, natural-keyed data
    (put duck-typing here for rest_framework_json_api)
    """
            
    def __new__(cls, natural_key, *args, **kwargs):
        """Check the cache for key and return the cached model
        OR create and cache a new instance based on provided args
        """
        _model_instance_cache = _StaticCache.for_cls(cls)
        return _model_instance_cache.setdefault(
            natural_key, super.__new__(*args, **kwargs)
        )

    ###
    # abstract methods

    @classmethod
    @abc.abstractmethod
    def from_natural_key(cls, key: NaturalKey) -> typing.Self: ...

    @property
    @abc.abstractmethod
    def natural_key(self) -> NaturalKey: ...

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
    def get_by_natural_key(cls, key: NaturalKey) -> typing.Self:
        """get the static model instance for the given key

        runs `from_natural_key` once per natural key, caches result until app restart
        """
        _cache = _StaticCache.for_class(cls)
        try:
            _gotten = _cache.by_natural_key[key]
        except KeyError:
            return cls.from_natrual_key(*key_parts)
        return _gotten

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


@dataclasses.dataclass
class _StaticCache:
    by_natural_key: dict[NaturalKey, typing.Any] = dataclasses.field(
        default_factory=dict
    )
    __caches_by_class: typing.ClassVar[
        weakref.WeakKeyDictionary[type, "_StaticCache"]
    ] = weakref.WeakKeyDictionary()

    @staticmethod
    def for_class(any_class: type) -> "_StaticCache":
        try:
            return _StaticCache.__caches_by_class[any_class]
        except KeyError:
            _new = _StaticCache()
            _StaticCache.__caches_by_class[any_class] = _new
            return _new
