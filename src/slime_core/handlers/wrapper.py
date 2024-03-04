from . import CoreHandler, CoreHandlerContainer
from slime_core.utils.base import (
    ContextGenerator,
    ContextManagerStack
)
from slime_core.utils.typing import (
    NOTHING,
    NoneOrNothing,
    Union,
    List,
    Callable,
    Generator,
    TypeVar,
    TYPE_CHECKING,
    Generic,
    STOP,
    Any
)
from slime_core.utils.exception import (
    HandlerBaseException,
    HandlerWrapperException
)
if TYPE_CHECKING:
    from slime_core.context.core import CoreContext
    from slime_core.context.compile import CoreCompile


__all__ = [
    'CoreHandlerWrapper',
    'CoreHandlerWrapperContainer'
]
_T = TypeVar("_T")
_YieldT_co = TypeVar("_YieldT_co", covariant=True)
_SendT_contra = TypeVar("_SendT_contra", contravariant=True)
_ReturnT_co = TypeVar("_ReturnT_co", covariant=True)
_CoreContextT = TypeVar("_CoreContextT", bound="CoreContext[CoreCompile]")
_CoreHandlerT = TypeVar("_CoreHandlerT", bound=CoreHandler["CoreContext", CoreHandler])
_CoreHandlerWrapperT = TypeVar("_CoreHandlerWrapperT", bound="CoreHandlerWrapper[CoreContext, CoreHandlerWrapper]")


class HandlerWrapperGenerator(
    ContextGenerator[_YieldT_co, _SendT_contra, _ReturnT_co],
    Generic[_YieldT_co, _SendT_contra, _ReturnT_co, _CoreHandlerWrapperT]
):
    """
    ``HandlerWrapperGenerator`` defines custom exception handling in the ``call__`` method 
    compared to ``ContextGenerator``.
    """
    
    def __init__(
        self,
        __gen: Generator[_YieldT_co, _SendT_contra, _ReturnT_co],
        __wrapper: _CoreHandlerWrapperT,
        *,
        exit_allowed: bool = True
    ) -> None:
        ContextGenerator.__init__(self, __gen, stop_allowed=exit_allowed)
        self.wrapper = __wrapper
    
    def call__(self, __caller: Callable[[], _T]) -> _T:
        try:
            return super().call__(__caller)
        # directly raise Handler Base Exception
        except HandlerBaseException:
            raise
        # wrap other Exception with Handler Wrapper Exception
        except Exception as e:
            raise HandlerWrapperException(exception_handler=self.wrapper, exception=e)


class CoreHandlerWrapper(
    CoreHandlerContainer[_CoreContextT, _CoreHandlerT],
    Generic[_CoreContextT, _CoreHandlerT, _CoreHandlerWrapperT]
):
    def handle(self, ctx: _CoreContextT) -> None:
        # Use ``ContextGenerator`` here rather than ``HandlerWrapperGenerator``, 
        # because when calling ``handle`` method, ``HandlerWrapper`` works as a 
        # normal ``HandlerContainer``.
        # The ``wrapped`` param is set to ``self``.
        with ContextGenerator(self.handle_yield(ctx, wrapped=self)) as val:
            if val is not STOP:
                super().handle(ctx)
    
    # yield method API
    def handle_yield(self, ctx: _CoreContextT, wrapped: _CoreHandlerT) -> Generator: yield
    
    def gen__(
        self,
        ctx: _CoreContextT,
        wrapped: _CoreHandlerT
    ) -> HandlerWrapperGenerator[Any, Any, Any, _CoreHandlerWrapperT]:
        """
        Creates a new ``HandlerWrapperGenerator`` that calls ``handle_yield`` method.
        """
        return HandlerWrapperGenerator(
            self.handle_yield(ctx, wrapped),
            self
        )


class CoreHandlerWrapperContainer(CoreHandlerContainer[_CoreContextT, _CoreHandlerWrapperT]):
    
    def __init__(
        self,
        wrappers: List[_CoreHandlerWrapperT],
        *,
        id: Union[str, NoneOrNothing] = NOTHING
    ) -> None:
        CoreHandlerContainer.__init__(self, wrappers, id=id)
    
    def handle(self, ctx: _CoreContextT, wrapped: _CoreHandlerT) -> None:
        with ContextManagerStack((
            wrapper.gen__(ctx, wrapped) for wrapper in self
        )) as vals:
            # Check whether the yielded value is ``STOP``.
            val = vals[-1] if len(vals) > 0 else True
            if val is not STOP:
                wrapped.handle(ctx)
