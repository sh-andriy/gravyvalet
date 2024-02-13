import dataclasses
import weakref


@dataclasses.dataclass
class Declarator:
    """Declarator: add declarative metadata in python using decorators and dataclasses

    define a dataclass with fields you want declared in your decorator, plus a field
    to hold the object of declaration:
    >>> @dataclasses.dataclass
    ... class TwoPartGreetingDeclaration:
    ...     a: str
    ...     b: str
    ...     on: object

    use that dataclass to define a declarator:
    >>> greet = Declarator(TwoPartGreetingDeclaration, object_field='on')

    use the declarator as a decorator to create a declaration:
    >>> @greet(a='hey', b='hello')
    ... def _hihi():
    ...     pass

    use the declarator to access declarations by object:
    >>> greet.get_declaration(_hihi)
    TwoPartGreetingDeclaration(a='hey', b='hello', on=<function _hihi at 0x...>)

    use `.with_kwargs` to create aliased decorators with static values:
    >>> ora = greet.with_kwargs(b='ora')
    >>> @ora(a='kia')
    ... def _kia_ora():
    ...     pass

    and find that aliased decoration via the original declarator:
    >>> greet.get_declaration(_kia_ora)
    TwoPartGreetingDeclaration(a='kia', b='ora', on=<function _kia_ora at 0x...>)
    """

    declaration_dataclass: type
    object_field: str
    static_kwargs: dict | None = None

    # private storage linking a decorated class or function to data gleaned from its decorator
    __declarations_by_target: weakref.WeakKeyDictionary = dataclasses.field(
        default_factory=weakref.WeakKeyDictionary,
    )

    def __post_init__(self):
        assert dataclasses.is_dataclass(
            self.declaration_dataclass
        ), f"expected dataclass, got {self.declaration_dataclass}"
        assert any(
            _field.name == self.object_field
            for _field in dataclasses.fields(self.declaration_dataclass)
        ), f'expected field "{self.object_field}" on dataclass "{self.declaration_dataclass}"'

    def __call__(self, **decorator_kwargs):
        def _decorator(decorator_target):
            self.declare(decorator_target, decorator_kwargs)
            return decorator_target

        return _decorator

    def with_kwargs(self, **static_kwargs):
        """convenience for decorators that differ only by static field values"""
        # note: shared __declarations_by_target
        return dataclasses.replace(self, static_kwargs=static_kwargs)

    def declare(self, decorator_target, decorator_kwargs: dict):
        # dataclass validates decorator kwarg names
        self.__declarations_by_target[decorator_target] = self.declaration_dataclass(
            **decorator_kwargs,
            **(self.static_kwargs or {}),
            **{self.object_field: decorator_target},
        )

    def get_declaration(self, target):
        try:
            return self.__declarations_by_target[target]
        except KeyError:
            raise ValueError(f"no declaration found for {target}")


class ClassDeclarator(Declarator):
    """add declarative metadata to python classes using decorators

    (same as Declarator but with additional methods that only make
    sense when used to decorate classes, and allow for inheritance
    and class instances)
    """

    def get_declaration_for_class_or_instance(self, type_or_object: type | object):
        _cls = (
            type_or_object if isinstance(type_or_object, type) else type(type_or_object)
        )
        return self.get_declaration_for_class(_cls)

    def get_declaration_for_class(self, cls: type):
        for _cls in cls.__mro__:
            try:
                return self.get_declaration(_cls)
            except ValueError:  # TODO: more helpful exception
                pass
        raise ValueError(f"no declaration found for {cls}")
