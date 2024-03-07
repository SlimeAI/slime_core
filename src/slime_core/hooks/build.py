from slime_core.utils.typing import (
    TypeVar,
    Generic,
    Generator
)
from slime_core.utils.exception import APIMisused
from abc import ABC, abstractmethod

_ContextT = TypeVar("_ContextT")


class CoreBuildHook(ABC, Generic[_ContextT]):

    @abstractmethod
    def build_xxx(self, ctx: _ContextT) -> None:
        """
        Core build interface to be implemented by subclasses.
        
        NOTE: This abstract method only serves as a template for method naming 
        and framework design. Subclasses should deprecate this method and 
        extend to other build interfaces such as ``build``, ``build_train``, 
        ``build_eval``, etc.
        """
        raise APIMisused(
            'The method ``build_xxx`` only serves as a template for method naming '
            'and framework design, and it should never be called at runtime.'
        )

    @abstractmethod
    def run_build_xxx__(self, ctx: _ContextT) -> None:
        """
        Perform a complete build operation including build-related methods in 
        launch hook, plugin hook, build hook, etc.
        
        NOTE: This abstract method only serves as a template for method naming 
        and framework design. Subclasses should deprecate this method and 
        extend to other build interfaces such as ``run_build__``, 
        ``run_build_train__``, ``run_build_eval__``, etc.
        """
        raise APIMisused(
            'The method ``run_build_xxx__`` only serves as a template for method '
            'naming and framework design, and it should never be called at runtime.'
        )


class CoreBuildInterface(ABC, Generic[_ContextT]):
    """
    Interface for building handlers.
    """
    
    @abstractmethod
    def build_xxx_yield(self, ctx: _ContextT) -> Generator:
        """
        Perform build-related operations before and after the ``build`` method 
        in ``CoreBuildHook`` is called.
        
        NOTE: This abstract method only serves as a template for method naming 
        and framework design. Subclasses should deprecate this method and 
        extend to other build interfaces such as ``build_yield``, 
        ``build_train_yield``, ``build_eval_yield``, etc.
        """
        raise APIMisused(
            'The method ``build_xxx_yield`` only serves as a template for method '
            'naming and framework design, and it should never be called at runtime.'
        )
