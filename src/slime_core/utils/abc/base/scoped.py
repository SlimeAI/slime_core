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
    FrozenSet,
)
from slime_core.utils.typing.extension import EmptyFlag, Missing, MISSING, Stop
from . import BaseListABC
from .execution import ContextGeneratorABC

_EnterT_co = TypeVar("_EnterT_co", covariant=True)
_ScopedT = TypeVar("_ScopedT")
_ScopedManagerT = TypeVar("_ScopedManagerT")
_ScopedGuardT = TypeVar("_ScopedGuardT")

#
# Scoped ABC.
#


class ScopedManagerABC(ABC, Generic[_ScopedT, _EnterT_co]):
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
    def scoped_ctxgen(
        self, scoped: _ScopedT
    ) -> ContextGeneratorABC[_EnterT_co, Any, Any, _EnterT_co]:
        """
        A mixin method that wraps the generator returned by ``scoped_yield`` and creates a
        ``ContextGenerator``.
        """
        pass


class ScopedManagerContainerABC(
    BaseListABC[_ScopedManagerT], ABC, Generic[_ScopedManagerT, _ScopedT]
):
    """
    ABC of ``ScopedManagerContainer``.
    """

    pass


class ScopedGuardABC(
    ScopedManagerABC[_ScopedT, _EnterT_co], ABC, Generic[_ScopedT, _EnterT_co]
):
    """
    ABC of ``ScopedGuard``.
    """

    @abstractmethod
    def setattr_guard_yield(
        self, __scoped: _ScopedT, __name: str, __value: Any
    ) -> Generator[Union[Stop, None], Any, Any]:
        """
        Guard on attribute set.
        """
        pass

    @abstractmethod
    def getattr_guard_yield(
        self, __scoped: _ScopedT, __name: str
    ) -> Generator[Union[Stop, None], Any, Any]:
        """
        Guard on attribute get.
        """
        pass

    @abstractmethod
    def delattr_guard_yield(
        self, __scoped: _ScopedT, __name: str
    ) -> Generator[Union[Stop, None], Any, Any]:
        """
        Guard on attribute delete.
        """
        pass


class ScopedGuardContainerABC(
    BaseListABC[_ScopedGuardT], ABC, Generic[_ScopedGuardT, _ScopedT]
):
    """
    ABC of ``ScopedGuardContainer``.
    """

    @abstractmethod
    def setattr_guard(
        self,
        __scoped: _ScopedT,
        __setattr_func: Callable[[str, Any], None],
        __name: str,
        __value: Any,
    ) -> None:
        """
        A controller function that calls guards on ``setattr``.
        """
        pass

    @abstractmethod
    def getattr_guard(
        self, __scoped: _ScopedT, __getattr_func: Callable[[str], Any], __name: str
    ) -> Any:
        """
        A controller function that calls guards on ``getattr``.
        """
        pass

    @abstractmethod
    def delattr_guard(
        self, __scoped: _ScopedT, __delattr_func: Callable[[str], None], __name: str
    ) -> None:
        """
        A controller function that calls guards on ``delattr``.
        """
        pass


class ScopedABC(ABC, Generic[_ScopedManagerT]):
    """
    ABC of ``Scoped``.
    """

    # Attributes that won't be passed to the scoped guards.
    # NOTE: ABC does not provide the specific implementation, so the computed class attribute is
    # manually set here.
    escaped_scoped_attrs__: Union[Iterable[str], Missing] = MISSING
    escaped_scoped_attrs_computed__: FrozenSet[str] = frozenset(
        [
            "scoped_managers__",
            "scoped_guards__",
            "escaped_scoped_attrs_computed__",
            "is_scoped_guard_enabled__",
            "scoped__",
            "escaped_scoped_attrs__",
        ]
    )
    # NOTE: These two attributes should be created by subclasses.
    scoped_managers__: ScopedManagerContainerABC[
        ScopedManagerABC["ScopedABC", Any], "ScopedABC"
    ]
    scoped_guards__: ScopedGuardContainerABC[
        ScopedGuardABC["ScopedABC", Any], "ScopedABC"
    ]

    @abstractmethod
    def scoped__(
        self, __scoped_managers: Union[Iterable[_ScopedManagerT], EmptyFlag] = MISSING
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


class ScopedAttrABC(ABC):
    """
    ABC of ``ScopedAttr``.
    """

    @abstractmethod
    def assign__(self, attr_assign: Mapping[str, Any]) -> ContextGeneratorABC:
        """
        Create a ``ScopedAttrAssign`` object and return ``scoped_gen`` with the
        ``scoped`` object bound to ``self``.
        """
        pass

    @abstractmethod
    def restore__(self, attrs: Iterable[str]) -> ContextGeneratorABC:
        """
        Create a ``ScopedAttrRestore`` object and return ``scoped_gen`` with the
        ``scoped`` object bound to ``self``.
        """
        pass
