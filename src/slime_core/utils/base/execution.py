"""
Execution control.
"""
from types import TracebackType
from contextlib import contextmanager, ExitStack
from slime_core.utils.abc.base.execution import (
    CoreContextGenerator,
    CoreBaseGeneratorQueue,
    CoreContextManagerStack
)
from slime_core.utils.typing.native import (
    TypeVar,
    Union,
    Generator,
    Tuple,
    Any,
    ContextManager,
    Generic,
    Type,
    List
)
from slime_core.utils.typing.extension import (
    MISSING,
    Stop,
    STOP,
    NOTHING,
    Missing,
    is_none_or_nothing
)
from slime_core.utils.decorator import (
    InitOnce
)
from . import (
    BaseGenerator,
    BaseList
)

_BaseGeneratorT = TypeVar("_BaseGeneratorT", bound=BaseGenerator)


class BaseGeneratorQueue(
    BaseList[_BaseGeneratorT],
    CoreBaseGeneratorQueue[_BaseGeneratorT],
    Generic[_BaseGeneratorT]
):
    """
    Queue execution of base generators before and after ``yield``.
    """
    
    @contextmanager
    def queue(self) -> Generator[Tuple, Any, Any]:
        """
        Sequentially call the generators on ``__enter__`` and ``__exit__``. Tuple of 
        yielded values from the generators will be yielded.
        
        NOTE: ``BaseGeneratorQueue`` simply calls ``next`` and no ``send`` values can be 
        specified.
        
        NOTE: Exceptions will NOT be processed in ``BaseGeneratorQueue``.
        
        NOTE: Queue modifications only take effect for subsequent ``queue`` method calls.
        """
        # Copy ``self`` for consistency.
        gen_queue = BaseList(self)
        # Call next and yield a tuple of yielded values.
        vals = tuple(gen() for gen in gen_queue)
        yield vals
        # Call next.
        for gen in gen_queue:
            gen()

#
# ContextGenerator.
#

_YieldT_co = TypeVar("_YieldT_co", covariant=True)
_SendT_contra = TypeVar("_SendT_contra", contravariant=True)
_ReturnT_co = TypeVar("_ReturnT_co", covariant=True)


class ContextGenerator(
    BaseGenerator[_YieldT_co, _SendT_contra, _ReturnT_co],
    CoreContextGenerator[_YieldT_co, _SendT_contra, _ReturnT_co, _YieldT_co],
    Generic[_YieldT_co, _SendT_contra, _ReturnT_co]
):
    """
    Make the generator a context manager. ``__enter__`` will call ``next`` 
    to the generator and return the yielded value, while ``__exit__`` will 
    call ``next``, send ``exit_send_value`` or process exceptions (call 
    ``throw``) according to different situations: if no exception is raised 
    and ``exit_send_value`` is ``MISSING``, then ``next`` is called, or if 
    ``exit_send_value`` is NOT ``MISSING``, then ``send`` is called, or 
    if the exception is NOT None, then ``throw`` is called.
    """
    
    @InitOnce
    def __init__(
        self,
        __gen: Generator[_YieldT_co, _SendT_contra, _ReturnT_co],
        *,
        stop_allowed: bool = True,
        exit_send_value: Union[Any, Missing] = MISSING
    ) -> None:
        super().__init__(__gen, stop_allowed=stop_allowed)
        self.exit_send_value = exit_send_value
    
    def __enter__(self) -> _YieldT_co:
        """
        Call ``next`` and return the yield value from the generator.
        """
        return self()
    
    def __exit__(
        self,
        __exc_type: Union[Type[BaseException], None],
        __exc_value: Union[BaseException, None],
        __traceback: Union[TracebackType, None]
    ) -> Union[bool, None]:
        if (
            __exc_type is None and 
            __exc_value is None and 
            __traceback is None
        ):
            if self.exit_send_value is MISSING:
                # Directly call ``next`` and return.
                self()
            else:
                # Send ``exit_send_value``.
                self.send(self.exit_send_value)
            return False
        
        # Throw the exception to the generator.
        exception = (__exc_type, __exc_value, __traceback)
        try:
            self.gen.throw(*exception)
        except Exception as e:
            exception = (
                type(e),
                e,
                e.__traceback__
            )
        else:
            exception = NOTHING
        # Suppress or re-raise the exception.
        if is_none_or_nothing(exception):
            return True
        elif exception[1] is __exc_value:
            return False
        else:
            raise exception[1]


def _empty_yield(yield_value: Any = NOTHING) -> Generator[Any, Any, None]:
    """
    An empty generator function used to create empty context generators.
    """
    yield yield_value


def EmptyContextGenerator(yield_value: Any = NOTHING) -> ContextGenerator[Any, Any, None]:
    """
    Create an empty context generator that does nothing.
    """
    return ContextGenerator(_empty_yield(yield_value=yield_value), stop_allowed=True)

#
# Context Manager Stack
#

_EnterT_co = TypeVar("_EnterT_co", covariant=True)


class ContextManagerStack(
    BaseList[ContextManager[_EnterT_co]],
    CoreContextManagerStack[ContextManager[_EnterT_co]],
    Generic[_EnterT_co]
):
    """
    Stack execution of context managers before and after ``yield``.
    """
    
    @contextmanager
    def stack(self) -> Union[Generator[Tuple, Any, Any]]:
        """
        Call context managers in FILO order. Exceptions will be passed through each 
        context manager until they are processed. Compared to the standard ``with`` 
        statement, it can handle context managers of indefinite quantity. The below 
        two examples are totally equivalent:
            ```Python
            # Example 1
            with A(), B(), C():
                ...
            
            # Example 2
            cm_list = [A(), B(), C()]
            with ContextManagerStack(cm_list).stack():
                ...
            ```
        """
        cm_list = BaseList(self)
        # Use ``ExitStack`` to correctly process exceptions.
        with ExitStack() as stack:
            # Returned values.
            vals: List[_EnterT_co] = []
            for cm in cm_list:
                val = stack.enter_context(cm)
                vals.append(val)
                # If the context manager returns ``STOP``, then directly break.
                if val is STOP:
                    break
            yield tuple(vals)

    @staticmethod
    def check_stop(values: Tuple[Union[Stop, Any], ...]) -> bool:
        # Only check whether the last value is ``STOP`` if the tuple is not empty.
        return (
            values[-1] is STOP if len(values) > 0 else False
        )
