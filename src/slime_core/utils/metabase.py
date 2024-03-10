"""
``metabase`` defines helper classes with specified metaclasses, allowing 
users to specify metaclasses in their custom classes through inheritance.
"""
from .typing import (
    MISSING,
    Any,
    Callable,
    FrozenSet,
    Tuple
)
from .metaclass import (
    _ReadonlyAttrMetaclass,
    InitOnceMetaclass,
    SingletonMetaclass
)
from functools import partial

#
# Readonly attributes.
#

class ReadonlyAttr(metaclass=_ReadonlyAttrMetaclass):
    """
    Make specified attributes readonly.
    """
    __slots__ = ()
    # ``readonly_attr__`` can be specified by each class. It denotes the 
    # newly added readonly attributes in the current class.
    # ``readonly_attr_computed__`` is computed by ``_ReadonlyAttrMetaclass`` 
    # when the class is created. It will inherit ``readonly_attr_computed__`` 
    # in the base classes and additionally add ``readonly_attr__`` defined in 
    # the current class.
    readonly_attr__: Tuple[str, ...] = ()
    readonly_attr_computed__: FrozenSet[str] = frozenset()
    # ``missing_readonly__``, ``empty_readonly__``: 
    # Whether empty value or ``MISSING`` value of a specified attribute 
    # is still readonly.
    missing_readonly__: bool = False
    empty_readonly__: bool = False

    def __setattr__(self, __name: str, __value: Any) -> None:
        return self.attr_mod__(
            __name,
            partial(super().__setattr__, __name, __value)
        )

    def __delattr__(self, __name: str) -> None:
        return self.attr_mod__(
            __name,
            partial(super().__delattr__, __name)
        )

    def attr_mod__(self, __name: str, __mod_func: Callable[[], None]) -> None:
        """
        Method that checks readonly attributes and apply ``__mod_func`` if certain 
        requirements are met, else raise ``APIMisused`` exception.

        ``__mod_func``: partial function of ``__setattr__``, ``__delattr__`` or other 
        attribute modification functions.
        """
        # Directly modify attr here for performance optimization.
        if __name not in self.readonly_attr_computed__:
            return __mod_func()

        hasattr__ = hasattr(self, __name)
        attr__ = getattr(self, __name, MISSING)

        # Whether empty value or ``MISSING`` value is readonly.
        if (
            (not hasattr__ and not self.empty_readonly__) or
            (attr__ is MISSING and not self.missing_readonly__)
        ):
            return __mod_func()
        else:
            from .exception import APIMisused
            raise APIMisused(f'``{__name}`` in class ``{type(self)}`` is a readonly attribute.')

#
# InitOnce Base
#

class InitOnceBase(metaclass=InitOnceMetaclass):
    """
    Helper class that implements ``InitOnce`` using inheritance.
    """
    pass

#
# Singleton base class
#

class Singleton(metaclass=SingletonMetaclass):
    """
    Helper class that creates a Singleton class using inheritance.

    Note that it works for each class (even subclasses) independently.

    Example:

    ```Python
    from slime_core.utils.bases import Singleton
    class A(Singleton): pass

    # B inherits A
    class B(A): pass

    print(A() is A())  # True
    print(B() is B())  # True
    print(A() is B())  # False

    \"""
    These two values are different, because ``SingletonMetaclass`` sets ``__instance`` 
    separately for each class it creates.
    \"""
    print(A._SingletonMetaclass__instance)
    print(B._SingletonMetaclass__instance)
    ```
    """
    __slots__ = ()
