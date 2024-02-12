import dataclasses
import weakref


@dataclasses.dataclass
class Declarator:
    """add declarative metadata to python functions using decorators"""

    dataclass: type
    target_fieldname: str
    static_kwargs: dict | None = None

    # private storage linking a decorated class or function to data gleaned from its decorator
    __declarations_by_target: weakref.WeakKeyDictionary = dataclasses.field(
        default_factory=weakref.WeakKeyDictionary,
    )

    def __post_init__(self):
        assert any(
            _field.name == self.target_fieldname
            for _field in dataclasses.fields(self.dataclass)
        ), f'expected field "{self.target_fieldname}" on dataclass "{self.dataclass}"'

    def __call__(self, **decorator_kwargs):
        def _decorator(decorator_target) -> type:
            self.declare(decorator_target, decorator_kwargs)
            return decorator_target

        return _decorator

    def with_kwargs(self, **static_kwargs):
        # note: shared __declarations_by_target
        return dataclasses.replace(self, static_kwargs=static_kwargs)

    def declare(self, decorator_target, decorator_kwargs: dict):
        self.__declarations_by_target[decorator_target] = self.dataclass(
            **decorator_kwargs,
            **(self.static_kwargs or {}),
            **{self.target_fieldname: decorator_target},
        )

    def get_declaration(self, target):
        try:
            return self.__declarations_by_target[target]
        except KeyError:
            raise ValueError(f"no declaration found for {target}")


class ClassDeclarator(Declarator):
    """add declarative metadata to python classes using decorators"""

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
