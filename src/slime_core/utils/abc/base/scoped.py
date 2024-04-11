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
    Mapping
)
from slime_core.utils.typing.extension import (
    EmptyFlag,
    MISSING
)
from . import CoreContextGenerator

_EnterT_co = TypeVar("_EnterT_co", covariant=True)
_ScopedT = TypeVar("_ScopedT")
_ScopedManagerT = TypeVar("_ScopedManagerT")

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


class CoreScoped(ABC, Generic[_ScopedManagerT]):
    """
    ABC of ``Scoped``.
    """
    
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
