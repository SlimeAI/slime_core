from slime_core.utils.typing import (
    TypeVar,
    Generic,
    Generator
)
from abc import ABC, abstractmethod

_ContextT = TypeVar("_ContextT")


class CoreBuildHook(ABC, Generic[_ContextT]):

    @abstractmethod
    def build_train(self, ctx: _ContextT) -> None: pass
    
    @abstractmethod
    def build_eval(self, ctx: _ContextT) -> None: pass
    
    @abstractmethod
    def build_predict(self, ctx: _ContextT) -> None: pass

    @abstractmethod
    def run_build_train__(self, ctx: _ContextT) -> None: pass
    
    @abstractmethod
    def run_build_eval__(self, ctx: _ContextT) -> None: pass

    @abstractmethod
    def run_build_predict__(self, ctx: _ContextT) -> None: pass


class CoreBuildInterface(ABC, Generic[_ContextT]):
    """
    Interface for building handlers.
    """
    @abstractmethod
    def build_train_yield(self, ctx: _ContextT) -> Generator: pass
    
    @abstractmethod
    def build_eval_yield(self, ctx: _ContextT) -> Generator: pass
    
    @abstractmethod
    def build_predict_yield(self, ctx: _ContextT) -> Generator: pass
