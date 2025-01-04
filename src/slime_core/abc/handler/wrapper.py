from abc import ABC, abstractmethod
from slime_core.utils.abc.base.execution import CoreContextGenerator
from slime_core.utils.typing.native import TypeVar, Union, Generator, Generic
from . import CoreHandlerContainer

_HandlerT = TypeVar("_HandlerT")
_HandlerContainerT = TypeVar("_HandlerContainerT")
_HandlerWrapperT = TypeVar("_HandlerWrapperT")
_HandlerWrapperContainerT = TypeVar("_HandlerWrapperContainerT")
_ContextT = TypeVar("_ContextT")


class CoreHandlerWrapper(
    CoreHandlerContainer[
        _HandlerT,
        _HandlerContainerT,
        _HandlerWrapperT,
        _HandlerWrapperContainerT,
        _ContextT,
    ],
    ABC,
    Generic[
        _HandlerT,
        _HandlerContainerT,
        _HandlerWrapperT,
        _HandlerWrapperContainerT,
        _ContextT,
    ],
):
    @abstractmethod
    def handle(self, ctx: _ContextT) -> None:
        """
        NOTE: This method should be overridden.
        """
        pass

    @abstractmethod
    def handle_yield(
        self, ctx: _ContextT, wrapped: Union[_HandlerT, _HandlerWrapperT]
    ) -> Generator:
        """
        Core handler wrapper API for custom operations.
        """
        pass

    @abstractmethod
    def handle_ctxgen(self, ctx: _ContextT, wrapped: _HandlerT) -> CoreContextGenerator:
        """
        A mixin method that wraps the generator returned by ``handle_yield`` into
        a ``ContextGenerator``.
        """
        pass


class CoreHandlerWrapperContainer(
    CoreHandlerContainer[
        _HandlerT,
        _HandlerContainerT,
        _HandlerWrapperT,
        _HandlerWrapperContainerT,
        _ContextT,
    ],
    ABC,
    Generic[
        _HandlerT,
        _HandlerContainerT,
        _HandlerWrapperT,
        _HandlerWrapperContainerT,
        _ContextT,
    ],
):
    @abstractmethod
    def handle(self, ctx: _ContextT, wrapped: _HandlerT) -> None:
        """
        NOTE: This method should be overridden.
        """
        pass
