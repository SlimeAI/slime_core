from slime_core.utils.common import (
    Count,
    dict_to_key_value_str_list,
    concat_format
)
from slime_core.utils.typing import (
    NOTHING,
    Nothing,
    NoneOrNothing,
    Union,
    List,
    Callable,
    Iterable,
    Tuple,
    is_none_or_nothing,
    TypeVar,
    Pass,
    PASS,
    TYPE_CHECKING,
    Generic
)
from slime_core.utils.base import (
    CompositeStructure,
    CompositeDFS,
    MutableBiListItem,
    BiList,
    BaseList
)
from slime_core.utils.exception import (
    HandlerException,
    HandlerTerminate,
    HandlerBreak,
    HandlerContinue,
    HandlerWrapperException
)
from functools import partial
from abc import ABC, abstractmethod
import slime_core.logging.logger as logger

if TYPE_CHECKING:
    from slime_core.context.core import CoreContext
    from slime_core.context.compile import CoreCompile

_CoreContextT = TypeVar("_CoreContextT", bound="CoreContext[CoreCompile]")
_CoreHandlerT = TypeVar("_CoreHandlerT", bound="CoreHandler[CoreContext, CoreHandler]")


class CoreHandler(
    CompositeStructure,
    MutableBiListItem,
    ABC,
    Generic[_CoreContextT, _CoreHandlerT]
):
    """
    Base class for all handlers.
    """
    # for generating unique id
    _handler_id_gen = Count()
    
    def __init__(
        self,
        *,
        id: Union[str, NoneOrNothing] = NOTHING,
        exec_ranks: Union[Iterable[int], NoneOrNothing, Pass] = PASS,
        wrappers: Union[Iterable["CoreHandlerWrapper"], NoneOrNothing] = NOTHING,
        lifecycle=NOTHING
    ):
        CompositeStructure.__init__(self)
        MutableBiListItem.__init__(self)
        
        self.set_id(id)
        self.set_exec_ranks(exec_ranks)
        self.set_wrappers(wrappers)
        # TODO: lifecycle
        # self.set_lifecycle()

    @abstractmethod
    def handle(self, ctx: _CoreContextT) -> None: pass

    def __call__(self, ctx: _CoreContextT) -> None:
        try:
            wrappers = self.get_wrappers()
            exec_ranks = self.get_exec_ranks()
            
            if is_none_or_nothing(wrappers):
                ctx.hook_ctx.launch.call(partial(self.handle, ctx), exec_ranks=exec_ranks)
            else:
                ctx.hook_ctx.launch.call(partial(wrappers.handle, ctx, self), exec_ranks=exec_ranks)
        #
        # Handler Interrupt
        #
        except HandlerTerminate as ht:
            # set ``raise_handler`` to the nearest handler
            if is_none_or_nothing(ht.raise_handler):
                ht.raise_handler = self
            raise
        except (HandlerBreak, HandlerContinue):
            raise
        #
        # Handler Wrapper Exception (should be in front of ``HandlerException``)
        #
        except HandlerWrapperException as hwe:
            # output the original exception handler, and raise it as a normal handler exception
            logger.core_logger.error(str(hwe))
            raise HandlerException(exception_handler=self, exception=hwe.exception)
        #
        # Handler Exception
        #
        except HandlerException:
            raise
        #
        # other Exception(s)
        #
        except Exception as e:
            raise HandlerException(exception_handler=self, exception=e)
    
    #
    # Handler Search Operations
    #
    
    def composite_iterable__(self) -> Nothing: return NOTHING
    
    def get_by_id(self, __id: str) -> _CoreHandlerT:
        results = CompositeDFS(self, lambda handler: handler.get_id() == __id)
        if len(results) > 1:
            logger.core_logger.warning(f'Duplicate id found in the Handler: {str(self)}.')
        return NOTHING if len(results) < 1 else results[0]
    
    def get_by_class(self, __class: Union[type, Tuple[type, ...]]) -> List[_CoreHandlerT]:
        return CompositeDFS(self, lambda handler: isinstance(handler, __class))
    
    def get_by_filter(self, __func: Callable[[_CoreHandlerT], bool]) -> List[_CoreHandlerT]:
        return CompositeDFS(self, __func)
    
    def __str__(self) -> str:
        class_name = self.get_class_name()
        
        display_attr_list = dict_to_key_value_str_list(self.get_display_attr_dict())
        attr = concat_format('(', display_attr_list, ')', break_line=False, item_sep=', ')
        
        return f'{class_name}{attr}'
    
    def get_class_name(self) -> str:
        return type(self).__name__

    def get_id(self) -> Union[str, Nothing]:
        return self.__id

    def set_id(self, __id: Union[str, NoneOrNothing]) -> None:
        if is_none_or_nothing(__id):
            self.__id = f'handler_{self._handler_id_gen}'
        else:
            self.__id = __id
    
    def get_exec_ranks(self) -> Union[Iterable[int], NoneOrNothing, Pass]:
        return self.__exec_ranks
    
    def set_exec_ranks(self, exec_ranks: Union[Iterable[int], NoneOrNothing, Pass]) -> None:
        self.__exec_ranks = BaseList.create__(exec_ranks)

    def get_wrappers(self) -> Union['CoreHandlerWrapperContainer', NoneOrNothing]:
        return self.__wrappers
    
    def set_wrappers(self, wrappers: Union[Iterable['CoreHandlerWrapper'], NoneOrNothing]) -> None:
        if is_none_or_nothing(wrappers):
            self.__wrappers = NOTHING
        else:
            self.__wrappers = CoreHandlerWrapperContainer(wrappers)
    
    def get_lifecycle(self):
        pass
    
    def set_lifecycle(self):
        pass
    
    def get_display_attr_dict(self) -> dict:
        return {
            'id': self.get_id(),
            'exec_ranks': self.get_exec_ranks(),
            'wrappers': self.get_wrappers(),
            'lifecycle': self.get_lifecycle()
        }


class CoreHandlerContainer(CoreHandler[_CoreContextT, _CoreHandlerT], BiList[_CoreHandlerT]):

    def __init__(
        self,
        handlers: Union[Iterable[_CoreHandlerT], NoneOrNothing] = NOTHING,
        *,
        id: Union[str, NoneOrNothing] = NOTHING,
        exec_ranks: Union[Iterable[int], NoneOrNothing, Pass] = PASS,
        wrappers: Union[Iterable['CoreHandlerWrapper'], NoneOrNothing] = NOTHING,
        lifecycle=NOTHING
    ):
        CoreHandler.__init__(
            self,
            id=id,
            exec_ranks=exec_ranks,
            wrappers=wrappers,
            lifecycle=lifecycle
        )
        # remove ``None`` and ``NOTHING`` in ``handlers``
        handlers = filter(
            lambda item: not is_none_or_nothing(item),
            BaseList(handlers)
        )
        BiList.__init__(
            self,
            handlers
        )
    
    def handle(self, ctx: _CoreContextT) -> None:
        try:
            for handler in self:
                handler(ctx)
        except HandlerContinue:
            # continue in the container
            pass
    
    def __call__(self, ctx: _CoreContextT) -> None:
        try:
            super().__call__(ctx)
        except HandlerBreak:
            # break out of the container
            pass
    
    def composite_iterable__(self) -> Iterable[_CoreHandlerT]: return self


from .wrapper import *
