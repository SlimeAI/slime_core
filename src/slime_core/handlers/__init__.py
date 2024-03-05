from slime_core.utils.common import Count
from slime_core.utils.abcs.base import (
    CoreMutableBiListItem,
    CoreBiList,
    CoreCompositeStructure
)
from slime_core.utils.typing import (
    Iterable,
    Callable,
    TypeVar,
    Generic,
    Union,
    EmptyFlag,
    NoneOrNothing,
    Pass,
    Any,
    Tuple,
    Dict,
    List,
    Type,
    Nothing
)
from abc import ABC, abstractmethod

_ContextT = TypeVar("_ContextT")
_HandlerT = TypeVar("_HandlerT")
_HandlerContainerT = TypeVar("_HandlerContainerT")
_HandlerWrapperT = TypeVar("_HandlerWrapperT")
_HandlerWrapperContainerT = TypeVar("_HandlerWrapperContainerT")


class CoreHandler(
    CoreCompositeStructure[_HandlerT],
    CoreMutableBiListItem[_HandlerT, _HandlerContainerT],
    ABC,
    Generic[_HandlerT, _HandlerContainerT, _HandlerWrapperT, _HandlerWrapperContainerT, _ContextT]
):
    """
    ABC for all handlers.
    
    Generics:
    
    ```Python
    CoreHandler[
        _HandlerT: CoreHandler,
        _HandlerContainerT: CoreHandlerContainer,
        _HandlerWrapperT: CoreHandlerWrapper,
        _HandlerWrapperContainerT: CoreHandlerWrapperContainer,
        _ContextT
    ]
    ```
    """
    # For generating unique handler ids.
    gen_handler_id__: Count

    #
    # Core APIs.
    #

    @abstractmethod
    def handle(self, ctx: _ContextT) -> None:
        """
        Custom handling operations.
        """
        pass

    @abstractmethod
    def __call__(self, ctx: _ContextT) -> None:
        """
        Wrapper method for calling ``handle``. Implements enhanced operations (e.g., 
        exception handling, launch hook call, etc.)
        """
        pass
    
    #
    # Handler search operations.
    #
    
    @abstractmethod
    def get_by_id(self, __id: str) -> _HandlerT:
        """
        Get the handler by handler id.
        """
        pass
    
    @abstractmethod
    def get_by_class(
        self,
        __class: Union[Type, Tuple[Type, ...]]
    ) -> List[_HandlerT]:
        """
        Get the handlers that are instances of ``__class``.
        """
        pass
    
    @abstractmethod
    def get_by_filter(
        self,
        __func: Callable[[_HandlerT], bool]
    ) -> List[_HandlerT]:
        """
        Get the handlers by the given filter function.
        """
        pass
    
    #
    # Handler display APIs.
    #
    
    @abstractmethod
    def display(self, *args, **kwargs) -> None:
        """
        Display the handler structure.
        """
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        """
        Simple handler str formatter.
        """
        pass
    
    @abstractmethod
    def get_display_attr_dict(self) -> Dict[str, Any]:
        """
        Return the names and values of attributes to be displayed.
        """
        pass
    
    #
    # Handler attribute operations.
    #
    
    @abstractmethod
    def get_class_name(self) -> str:
        """
        Get the class name of the handler (for display).
        """
        pass

    @abstractmethod
    def get_id(self) -> str:
        """
        Get the id of the handler.
        """
        pass

    @abstractmethod
    def set_id(self, __id: Union[str, EmptyFlag]) -> None:
        """
        Set id of the handler. If the given ``__id`` is ``EmptyFlag``, then set the value 
        of ``gen_handler_id__`` to the handler.
        """
        pass
    
    @abstractmethod
    def get_exec_ranks(self) -> Union[Iterable[int], NoneOrNothing, Pass]:
        """
        Get exec_ranks of the handler.
        """
        pass
    
    @abstractmethod
    def set_exec_ranks(self, __exec_ranks: Union[Iterable[int], NoneOrNothing, Pass]) -> None:
        """
        Set exec_ranks of the handler.
        """
        pass

    @abstractmethod
    def get_wrappers(self) -> Union[_HandlerWrapperContainerT, Nothing]:
        """
        Get the handler wrappers of the handler (if any).
        """
        pass
    
    @abstractmethod
    def set_wrappers(self, __wrappers: Union[Iterable[_HandlerWrapperT], EmptyFlag]) -> None:
        """
        Set the handler wrappers. If ``__wrappers`` is ``EmptyFlag``, then set wrappers 
        to ``NOTHING``.
        """
        pass
    
    @abstractmethod
    def get_lifecycle(self, *args, **kwargs):
        """
        TODO: The lifecycle feature is to be implemented.
        """
        pass
    
    @abstractmethod
    def set_lifecycle(self, *args, **kwargs):
        """
        TODO: The lifecycle feature is to be implemented.
        """
        pass


class CoreHandlerContainer(
    CoreHandler[_HandlerT, _HandlerContainerT, _HandlerWrapperT, _HandlerWrapperContainerT, _ContextT],
    CoreBiList[_HandlerT],
    ABC
):
    """
    ABC for HandlerContainers.
    """
    pass
