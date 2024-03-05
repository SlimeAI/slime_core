from . import CoreHandlerContainer
from slime_core.utils.typing import (
    TypeVar,
    Union,
    Generator
)
from abc import ABC, abstractmethod

_HandlerT = TypeVar("_HandlerT")
_HandlerContainerT = TypeVar("_HandlerContainerT")
_HandlerWrapperT = TypeVar("_HandlerWrapperT")
_HandlerWrapperContainerT = TypeVar("_HandlerWrapperContainerT")
_ContextT = TypeVar("_ContextT")


class CoreHandlerWrapper(
    CoreHandlerContainer[_HandlerT, _HandlerContainerT, _HandlerWrapperT, _HandlerWrapperContainerT, _ContextT],
    ABC
):
    @abstractmethod
    def handle(self, ctx: _ContextT) -> None:
        """
        NOTE: This method should be overridden.
        """
        pass
    
    @abstractmethod
    def handle_yield(self, ctx: _ContextT, wrapped: Union[_HandlerT, _HandlerWrapperT]) -> Generator:
        """
        Core handler wrapper API for custom operations.
        """
        pass


class CoreHandlerWrapperContainer(
    CoreHandlerContainer[_HandlerT, _HandlerContainerT, _HandlerWrapperT, _HandlerWrapperContainerT, _ContextT],
    ABC
):
    @abstractmethod
    def handle(self, ctx: _ContextT, wrapped: _HandlerT) -> None:
        """
        NOTE: This method should be overridden.
        """
        pass
