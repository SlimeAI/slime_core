"""
ABC for execution control.
"""

from abc import ABC, abstractmethod
from slime_core.utils.typing.native import (
    ContextManager,
    TypeVar,
    Generic,
    Generator,
    Any,
    Union,
    Tuple,
)
from slime_core.utils.typing.extension import Stop
from . import BaseGeneratorABC, BaseListABC

_BaseGeneratorT = TypeVar("_BaseGeneratorT")


class BaseGeneratorQueueABC(
    BaseListABC[_BaseGeneratorT], ABC, Generic[_BaseGeneratorT]
):
    """
    ABC of ``BaseGeneratorQueue``.
    """

    @abstractmethod
    def queue(self) -> Union[Generator[Tuple, Any, Any], ContextManager[Tuple]]:
        """
        Queue execution. NOTE: This method should be implemented by either using
        ``@contextmanager`` or directly returning a context manager.
        """
        pass


_YieldT_co = TypeVar("_YieldT_co", covariant=True)
_SendT_contra = TypeVar("_SendT_contra", contravariant=True)
_ReturnT_co = TypeVar("_ReturnT_co", covariant=True)
_EnterT_co = TypeVar("_EnterT_co", covariant=True)


class ContextGeneratorABC(
    BaseGeneratorABC[_YieldT_co, _SendT_contra, _ReturnT_co],
    ContextManager[_EnterT_co],
    Generic[_YieldT_co, _SendT_contra, _ReturnT_co, _EnterT_co],
):
    """
    ABC of ``ContextGenerator``.
    """

    pass


class ContextManagerStackABC(
    BaseListABC[ContextManager[_EnterT_co]], ABC, Generic[_EnterT_co]
):
    """
    ABC of ``ContextManagerStack``.
    """

    @abstractmethod
    def stack(self) -> Union[Generator[Tuple, Any, Any], ContextManager[Tuple]]:
        """
        Stack execution. NOTE: This method should be implemented by either using
        ``@contextmanager`` or directly returning a context manager.
        """
        pass

    @staticmethod
    @abstractmethod
    def check_stop(values: Tuple[Union[Stop, Any], ...]) -> bool:
        """
        Check whether the stack enter execution has normally finished or stopped.
        NOTE: This is implemented by checking the yielded values of ``stack`` method.
        Return ``True`` if the stack stopped.

        ``values``: The yielded values of ``stack``.
        """
        pass


class GeneralYieldContextABC(ABC, Generic[_EnterT_co]):
    """
    Provide a method template for yield context.
    """

    @abstractmethod
    def gen_yield(self, *args, **kwargs) -> Generator[_EnterT_co, Any, Any]:
        """
        A generator method used to build a context manager.
        """
        pass

    @abstractmethod
    def gen_ctxgen(
        self, *args, **kwargs
    ) -> ContextGeneratorABC[_EnterT_co, Any, Any, _EnterT_co]:
        """
        A mixin method that wraps the generator returned by ``gen_yield`` into
        a ``ContextGenerator``.
        """
        pass
