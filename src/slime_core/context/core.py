from slime_core.utils.base import Base
from slime_core.utils.typing import (
    Union,
    Sequence,
    Nothing,
    Generic,
    TYPE_CHECKING,
    TypeVar,
    is_none_or_nothing,
    NOTHING
)
from slime_core.utils.exception import APIMisused
import slime_core.logging.logger as logger
from abc import ABC, abstractmethod
if TYPE_CHECKING:
    from .compile import CoreCompile

_CoreCompileT = TypeVar("_CoreCompileT", bound="CoreCompile[CoreContext]")


class CoreContext(Base, Generic[_CoreCompileT]):
    
    def __init__(self) -> None:
        Base.__init__(self)
        self.hook_ctx: CoreHookContext

    #
    # Context check.
    #

    def ctx_check(self, items: Union[str, Sequence[str]], silent: bool = True):
        # check single item
        def _check(_item):
            _result = self.check__(_item)
            if _result is False:
                msg = 'Context check failed: got NOTHING with key \'%s\'.' % _item
                if silent is True:
                    logger.core_logger.debug(msg, logger.LoggerKwargs(stacklevel=3))
                else:
                    logger.core_logger.warning(msg, logger.LoggerKwargs(stacklevel=3))
            return _result

        if isinstance(items, (list, tuple)):
            # sequence value
            for item in items:
                if _check(str(item)) is False:
                    return False
            return True
        else:
            # single value
            return _check(str(items))
    
    #
    # ``compile`` property
    #

    @property
    def compile(self) -> _CoreCompileT:
        from .compile import CoreCompile
        
        if not self.hasattr__('_BaseContext__compile'):
            logger.warning(
                'Property ``compile`` has not been bound to an object yet.'
            )
        compile = self.__compile
        if not isinstance(compile, CoreCompile):
            logger.warning(
                f'Property ``compile`` is not set to a ``CoreCompile`` instance, but {compile}. This may '
                'cause some unknown problems.'
            )
        elif compile.ctx is not self:
            raise APIMisused(
                f'Bindings between ``compile`` and ``CoreContext`` mismatch. ``compile`` is bound to {compile.ctx}, '
                f'while ``CoreContext`` is {self}.'
            )
        return compile

    @compile.setter
    def compile(self, value: _CoreCompileT) -> None:
        if (
            not is_none_or_nothing(value.ctx) and 
            value.ctx is not self
        ):
            raise APIMisused(
                f'The property ``compile`` ({value}) being set has already been bound to another ``CoreContext`` object ({value.ctx}). '
                f'You should unbind it from the other ``CoreContext`` ({value.ctx}) using ``del`` first.'
            )
        value.ctx = self
        self.__compile = value

    @compile.deleter
    def compile(self) -> None:
        self.compile.ctx = NOTHING
        del self.__compile


class CoreTempContext(Base, ABC):
    
    def __init__(self):
        Base.__init__(self)
        ABC.__init__(self)
        
        # initialize
        self.initialize()
    
    @abstractmethod
    def initialize(self): pass


class CoreHookContext(CoreTempContext):

    def initialize(self):
        # hooks
        from slime_core.hooks.plugin import CorePluginContainer
        self.plugins: CorePluginContainer
        
        from slime_core.hooks.launch import CoreLaunchHook
        self.launch: Union[CoreLaunchHook, Nothing]
        
        from slime_core.hooks.build import CoreBuildHook
        self.build: Union[CoreBuildHook, Nothing]
