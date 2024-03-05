from .build import CoreBuildInterface
from slime_core.utils.abcs.base import CoreBaseList
from slime_core.utils.typing import (
    TypeVar,
    Generator,
    Generic
)
from abc import ABC, abstractmethod

_ContextT = TypeVar("_ContextT")
_PluginHookT = TypeVar("_PluginHookT")


class CorePluginHook(CoreBuildInterface[_ContextT], ABC):
    """
    Plugin hook for custom handler build.
    """
    pass


class PluginContainer(
    CorePluginHook[_ContextT],
    CoreBaseList[_PluginHookT],
    ABC,
    Generic[_ContextT, _PluginHookT]
):
    @abstractmethod
    def build_train_yield(self, ctx: _ContextT) -> Generator:
        """
        NOTE: This method should be overridden.
        """
        pass
    
    @abstractmethod
    def build_eval_yield(self, ctx: _ContextT) -> Generator:
        """
        NOTE: This method should be overridden.
        """
        pass
    
    @abstractmethod
    def build_predict_yield(self, ctx: _ContextT) -> Generator:
        """
        NOTE: This method should be overridden.
        """
        pass
