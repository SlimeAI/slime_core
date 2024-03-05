from abc import ABC, abstractmethod
from slime_core.utils.typing import (
    Union,
    Nothing,
    Generic,
    TypeVar
)

_CompileT = TypeVar("_CompileT")


class CoreTempContext(ABC):
    """
    NOTE: ``Temp`` in the name does NOT mean the context itself is temporal and may 
    be destroyed, but means some attributes in the context can be re-initialized by 
    calling the ``initialize`` method.
    """
    
    def __init__(self) -> None:
        self.initialize()
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialization of context object.
        """
        pass


class CoreContext(CoreTempContext, ABC, Generic[_CompileT]):
    
    @property
    @abstractmethod
    def compile(self) -> Union[_CompileT, Nothing]:
        """
        We additionally set the abstract property ``compile``, because we 
        want to call the compile object like a function. (Specifically, 
        ctx.compile(...) is more convenient than ctx.get_compile()(...))
        """
        pass
    
    @abstractmethod
    def set_compile(self, __compile: _CompileT) -> None:
        """
        Set the compile object to the context.
        """
        pass
    
    @abstractmethod
    def get_compile(self) -> Union[_CompileT, Nothing]:
        """
        Get the compile object. Return ``NOTHING`` if compile doesn't exit.
        """
        pass
    
    @abstractmethod
    def del_compile(self) -> None:
        """
        Remove the compile object.
        """
        pass


class CoreHookContext(CoreTempContext, ABC):

    @abstractmethod
    def initialize(self) -> None:
        # hooks
        from slime_core.hooks.plugin import CorePluginContainer
        self.plugins: CorePluginContainer
        
        from slime_core.hooks.launch import CoreLaunchHook
        self.launch: Union[CoreLaunchHook, Nothing]
        
        from slime_core.hooks.build import CoreBuildHook
        self.build: Union[CoreBuildHook, Nothing]
