from slime_core.utils.typing import (
    Dict,
    Any,
    TypeVar,
    Generic,
    Union,
    EmptyFlag,
    Nothing
)
from slime_core.utils.common import FuncArgs
from abc import ABC, abstractmethod

_ContextT = TypeVar("_ContextT")


class CompileFuncArgs(FuncArgs):
    """
    Pack multiple func arguments in a single ``CompileFuncArgs`` object. 
    Used as an indicator that the compile function accepts multiple args and 
    the ``CompileFuncArgs`` object should be unpacked to call the compile 
    function.
    """
    pass


class CoreCompile(ABC, Generic[_ContextT]):
    
    @property
    @abstractmethod
    def ctx(self) -> Union[_ContextT, Nothing]:
        """
        We additionally set the abstract property ``ctx`` for more convenient 
        access of the attribute.
        """
        pass
    
    @abstractmethod
    def set_ctx(self, ctx: Union[_ContextT, EmptyFlag]) -> None:
        """
        Bind context to the Compile object.
        """
        pass
    
    @abstractmethod
    def get_ctx(self) -> Union[_ContextT, Nothing]:
        """
        Get the bound context of the Compile object. If no context is bound, 
        return ``NOTHING``.
        """
        pass
    
    @abstractmethod
    def del_ctx(self) -> None:
        """
        Remove the bound context of the Compile object.
        """
        pass
    
    @abstractmethod
    def __call__(self, **kwargs: Dict[str, Any]) -> None:
        """
        Compile attributes using given ``kwargs``.
        """
        pass
