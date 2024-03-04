from slime_core.utils.typing import (
    Any,
    Dict,
    Union,
    Callable,
    NOTHING,
    NoneOrNothing,
    MISSING,
    TYPE_CHECKING,
    TypeVar,
    Generic
)
from slime_core.utils.common import FuncArgs
import slime_core.logging.logger as logger
if TYPE_CHECKING:
    from . import CoreContext

_CoreContextT = TypeVar("_CoreContextT", bound="CoreContext[CoreCompile]")


class CompileFuncArgs(FuncArgs): pass


class CoreCompile(Generic[_CoreContextT]):
    
    compile_func_suffix__ = '_compile__'
    
    def __init__(
        self,
        ctx: Union[_CoreContextT, NoneOrNothing] = NOTHING
    ) -> None:
        self.ctx = ctx
    
    def __call__(self, **kwargs: Dict[str, Any]) -> None:
        for key, value in kwargs.items():
            # Do nothing.
            if value is MISSING:
                continue
            
            func_name = f'{key}{self.compile_func_suffix__}'
            func: Callable[..., None] = getattr(self, func_name, NOTHING)
            if func is NOTHING:
                logger.core_logger.warning(
                    f'Compile func ``{func_name}`` not found. Compile ``{key}`` attribute failed.',
                    **logger.LoggerKwargs(stacklevel=2)
                )
                continue
            
            if isinstance(value, CompileFuncArgs):
                func(*value.args, **value.kwargs)
            else:
                func(value)
