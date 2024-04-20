"""
``metabase`` defines helper classes with specified metaclasses, allowing 
users to specify metaclasses in their custom classes through inheritance.
"""
from functools import partial
from slime_core.utils.typing.native import (
    Any,
    Callable,
    FrozenSet,
    Tuple,
    Union,
    Type,
    Iterable
)
from slime_core.utils.typing.extension import (
    MISSING,
    Missing
)
from slime_core.utils.abc.metaclass.metabase import (
    CoreClassAttrCompute
)
from slime_core.utils.exception import APIMisused
from . import (
    ComputedClassAttrMetaclass,
    ReadonlyAttrMetaclass,
    SingletonMetaclass
)

#
# Computed class attributes.
#

class ClassAttrCompute(CoreClassAttrCompute):
    """
    Set class attribute computation rules.
    """
    
    def __init__(
        self,
        name: str,
        computed_name: str,
        escaped_types: Iterable[Type] = (type('never_type', (object,), {}),),
        compute_func: Union[Callable[[Any, Tuple[Any]], Any], Missing] = MISSING
    ) -> None:
        """
        NOTE: We set the default value of ``escaped_types`` to a tuple that contains a 
        newly created type ``never_type``. Although through tests, we found that an empty 
        type tuple can be accepted by ``isinstance``, but we have not found this feature 
        explicitly explained in the official Python document. So for compatibility, the 
        ``never_type`` tuple is used as the default value.
        """
        # NOTE: The following attributes should NOT be changed after init.
        self.__name = name
        self.__computed_name = computed_name
        # Set escaped types.
        self.__escaped_types = tuple(escaped_types)
        if Missing in self.__escaped_types:
            raise APIMisused(
                '``Missing`` type in ``slime_core.utils.typing.extension`` is not allowed '
                'in the escaped types.'
            )
        self.__compute_func = compute_func
        # Use '-' as the separator, because attribute names do not allow '-'.
        self.__hashable = f'{name}-{computed_name}'
        self.__hash_value = hash(self.__hashable)
    
    def get_name(self) -> str:
        return self.__name

    def get_computed_name(self) -> str:
        return self.__computed_name
    
    def get_escaped_types(self) -> Tuple[Type, ...]:
        return self.__escaped_types

    def get_compute_func(self) -> Callable[[Any, Tuple[Any]], Any]:
        return (
            self.default_compute_func 
            if self.__compute_func is MISSING 
            else self.__compute_func
        )
    
    def __hash__(self) -> int:
        return self.__hash_value
    
    def __eq__(self, __other: Union["ClassAttrCompute", Any]) -> bool:
        return (
            isinstance(__other, ClassAttrCompute) and 
            self.__hashable == __other.__hashable
        )
    
    @staticmethod
    def default_compute_func(attr: Union[Iterable, Missing], computed_base_attrs: Tuple[Iterable]) -> FrozenSet:
        attr = set(attr) if attr is not MISSING else set()
        attr.update(*computed_base_attrs)
        return frozenset(attr)


class ComputedClassAttr(metaclass=ComputedClassAttrMetaclass):
    class_attr_compute__: Iterable[ClassAttrCompute] = ()
    class_attr_compute_computed__: FrozenSet[ClassAttrCompute]

#
# Readonly attributes.
#

class ReadonlyAttr(ComputedClassAttr, metaclass=ReadonlyAttrMetaclass):
    """
    Make specified attributes readonly. There are some special cases where 
    the attributes may be allowed to be changed:
    
    - The attribute does not exist.
    - The attribute is ``MISSING``.
    
    Whether changes of the attributes are allowed in the above cases is 
    controlled by the class attributes (see as follows).

    Class attributes:
        ``readonly_attr__``: Can be specified by each class. It denotes the 
        newly added readonly attributes in the current class.
        
        ``missing_readonly__``: Whether the attribute is readonly when it is 
        ``MISSING``. If it is set to False, then the specified readonly 
        attributes which are ``MISSING`` can be changed. Otherwise if it is 
        True, the specified readonly attributes can not be changed even when 
        they are ``MISSING``. If it is an ``Iterable``, then only attributes 
        in the ``Iterable`` will follow the 'missing readonly' rule.
        
        ``empty_readonly__``: Whether the attribute is readonly when it does
        not exist. The attribute setting is similar to ``missing_readonly__``.
    """
    __slots__ = ()
    class_attr_compute__ = (
        ClassAttrCompute('readonly_attr__', 'readonly_attr_computed__', escaped_types=(bool,)),
        ClassAttrCompute('missing_readonly__', 'missing_readonly_computed__', escaped_types=(bool,)),
        ClassAttrCompute('empty_readonly__', 'empty_readonly_computed__', escaped_types=(bool,))
    )
    readonly_attr__: Union[Iterable[str], bool] = ()
    readonly_attr_computed__: Union[FrozenSet[str], bool]
    missing_readonly__: Union[Iterable[str], bool] = False
    missing_readonly_computed__: Union[FrozenSet[str], bool]
    empty_readonly__: Union[Iterable[str], bool] = False
    empty_readonly_computed__: Union[FrozenSet[str], bool]

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
        if not self.check_readonly__(__name, self.readonly_attr_computed__):
            return __mod_func()

        # Whether empty value or ``MISSING`` value is readonly.
        if (
            (
                not hasattr(self, __name) and 
                not self.check_readonly__(__name, self.empty_readonly_computed__)
            ) or 
            (
                # The default value of ``getattr`` is set to ``None`` rather than ``MISSING`` 
                # to determine whether the attribute is really ``MISSING``.
                getattr(self, __name, None) is MISSING and 
                not self.check_readonly__(__name, self.missing_readonly_computed__)
            )
        ):
            return __mod_func()
        else:
            from slime_core.utils.exception import APIMisused
            raise APIMisused(f'``{__name}`` in class ``{type(self)}`` is a readonly attribute.')
    
    @staticmethod
    def check_readonly__(name: str, readonly_setting: Union[FrozenSet[str], bool]) -> bool:
        """
        Check whether ``name`` matches ``readonly_setting`` (which can be ``readonly_attr_computed__``, 
        ``missing_readonly_computed__``, ``empty_readonly_computed__``, etc.).
        """
        return (
            readonly_setting is True or 
            (
                readonly_setting is not False and 
                name in readonly_setting
            )
        )

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
