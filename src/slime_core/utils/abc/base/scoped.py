"""
ABCs for scoped lifecycle management.
"""
from abc import ABC, abstractmethod
from slime_core.utils.typing.native import (
    Generic,
    TypeVar,
    Any,
    Generator,
    Union,
    Iterable,
    ContextManager,
    Tuple,
    Mapping,
    Callable,
    Container,
    FrozenSet
)
from slime_core.utils.typing.extension import (
    EmptyFlag,
    MISSING,
    Stop
)
from . import CoreContextGenerator, CoreBaseList

_EnterT_co = TypeVar("_EnterT_co", covariant=True)
_ScopedT = TypeVar("_ScopedT")
_ScopedManagerT = TypeVar("_ScopedManagerT")
_ScopedGuardT = TypeVar("_ScopedGuardT")

#
# Scoped ABC.
#

class CoreScopedManager(ABC, Generic[_ScopedT, _EnterT_co]):
    """
    ABC of ``ScopedManager``.
    """
    
    @abstractmethod
    def scoped_yield(self, scoped: _ScopedT) -> Generator[_EnterT_co, Any, Any]:
        """
        Generator function used to create a context manager.
        """
        pass
    
    @abstractmethod
    def scoped_ctxgen(self, scoped: _ScopedT) -> CoreContextGenerator[_EnterT_co, Any, Any, _EnterT_co]:
        """
        A mixin method that wraps the generator returned by ``scoped_yield`` and creates a 
        ``ContextGenerator``.
        """
        pass


class CoreScopedManagerContainer(CoreBaseList[_ScopedManagerT], ABC, Generic[_ScopedManagerT]):
    """
    ABC of ``ScopedManagerContainer``.
    """
    pass


class CoreScopedGuard(CoreScopedManager[_ScopedT, _EnterT_co], ABC, Generic[_ScopedT, _EnterT_co]):
    """
    ABC of ``ScopedGuard``.
    """
    # These attributes can be used to filter the guards to be called when some operations occur.
    guarded_attrs__: Union[EmptyFlag, Container[str]] = MISSING
    guarded_setattrs__: Union[EmptyFlag, Container[str]] = MISSING
    guarded_getattrs__: Union[EmptyFlag, Container[str]] = MISSING
    guarded_delattrs__: Union[EmptyFlag, Container[str]] = MISSING
    
    @abstractmethod
    def setattr_guard(self, __name: str, __value: Any) -> Union[Stop, None]:
        """
        Guard on attribute set.
        """
        pass
    
    @abstractmethod
    def getattr_guard(self, __name: str) -> Union[Stop, None]:
        """
        Guard on attribute get.
        """
        pass
    
    @abstractmethod
    def delattr_guard(self, __name: str) -> Union[Stop, None]:
        """
        Guard on attribute delete.
        """
        pass


class CoreScopedGuardContainer(CoreBaseList[_ScopedGuardT], ABC, Generic[_ScopedGuardT]):
    """
    ABC of ``ScopedGuardContainer``.
    """
    
    @abstractmethod
    def setattr_guard(
        self,
        __setattr_func: Callable[[str, Any], None],
        __name: str,
        __value: Any
    ) -> None:
        """
        A controller function that calls guards on ``setattr``.
        """
        pass
    
    @abstractmethod
    def getattr_guard(
        self,
        __getattr_func: Callable[[str], Any],
        __name: str
    ) -> Any:
        """
        A controller function that calls guards on ``getattr``.
        """
        pass
    
    @abstractmethod
    def delattr_guard(
        self,
        __delattr_func: Callable[[str], None],
        __name: str
    ) -> None:
        """
        A controller function that calls guards on ``delattr``.
        """
        pass


class CoreScoped(ABC, Generic[_ScopedManagerT]):
    """
    ABC of ``Scoped``.
    """
    # Attributes that won't be passed to the scoped guards.
    escaped_scoped_attrs__: FrozenSet[str] = frozenset([
        'scoped_managers__', 'scoped_guards__', 'escaped_scoped_attrs__', 
        'is_scoped_guard_enabled__', 'scoped__'
    ])
    # NOTE: These two attributes should be created by subclasses.
    scoped_managers__: CoreScopedManagerContainer[CoreScopedManager]
    scoped_guards__: CoreScopedGuardContainer[CoreScopedGuard]
    
    @abstractmethod
    def scoped__(
        self,
        __scoped_managers: Union[Iterable[_ScopedManagerT], EmptyFlag] = MISSING
    ) -> ContextManager[Tuple]:
        """
        Create a stack containing scoped context managers for initialization and cleanup. 
        The scoped object ``self`` is bound to the context managers.
        """
        pass
    
    @abstractmethod
    def is_scoped_guard_enabled__(self) -> bool:
        """
        Return a bool value indicating whether scoped guard is enabled.
        """
        pass

#
# Scoped Attr ABC.
#

class CoreScopedAttr(ABC):
    """
    ABC of ``ScopedAttr``.
    """
    
    @abstractmethod
    def assign__(self, attr_assign: Mapping[str, Any]) -> CoreContextGenerator:
        """
        Create a ``ScopedAttrAssign`` object and return ``scoped_gen`` with the 
        ``scoped`` object bound to ``self``.
        """
        pass
    
    @abstractmethod
    def restore__(self, attrs: Iterable[str]) -> CoreContextGenerator:
        """
        Create a ``ScopedAttrRestore`` object and return ``scoped_gen`` with the 
        ``scoped`` object bound to ``self``.
        """
        pass
