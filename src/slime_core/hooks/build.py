from slime_core.utils.typing import (
    TypeVar,
    Generic,
    Generator
)
from abc import ABC, abstractmethod

_ContextT = TypeVar("_ContextT")


class CoreGeneralBuildHook(ABC, Generic[_ContextT]):
    """
    Build hook for handler building management.
    """

    @abstractmethod
    def build_pipeline(self, ctx: _ContextT) -> None:
        """
        Core build interface to be implemented by subclasses.
        """
        pass

    @abstractmethod
    def run_build_pipeline__(self, ctx: _ContextT) -> None:
        """
        Perform a complete build operation including build-related methods in 
        launch hook, plugin hook, build hook, etc.
        """
        pass


class CoreGeneralBuildInterface(ABC, Generic[_ContextT]):
    """
    Interface for building handlers.
    """
    
    @abstractmethod
    def build_pipeline_yield(self, ctx: _ContextT) -> Generator:
        """
        Perform build-related operations before and after the ``build_pipeline``
        method in ``CoreGeneralBuildHook`` is called.
        """
        pass


class CoreBuildHook(ABC, Generic[_ContextT]):
    
    @abstractmethod
    def build_train(self, ctx: _ContextT) -> None:
        """
        Build the handler structure for training pipelines.
        """
        pass
    
    @abstractmethod
    def build_eval(self, ctx: _ContextT) -> None:
        """
        Build the handler structure for evaluation pipelines.
        """
        pass
    
    @abstractmethod
    def build_predict(self, ctx: _ContextT) -> None:
        """
        Build the handler structure for prediction pipelines.
        """
        pass

    @abstractmethod
    def run_build_train__(self, ctx: _ContextT) -> None:
        """
        Perform a complete build operation for building training pipelines.
        """
        pass
    
    @abstractmethod
    def run_build_eval__(self, ctx: _ContextT) -> None:
        """
        Perform a complete build operation for building evaluation pipelines.
        """
        pass
    
    @abstractmethod
    def run_build_predict__(self, ctx: _ContextT) -> None:
        """
        Perform a complete build operation for building prediction pipelines.
        """
        pass


class CoreBuildInterface(ABC, Generic[_ContextT]):

    @abstractmethod
    def build_train_yield(self, ctx: _ContextT) -> Generator:
        """
        Build operations before and after ``build_train`` is called.
        """
        pass
    
    @abstractmethod
    def build_eval_yield(self, ctx: _ContextT) -> Generator:
        """
        Build operations before and after ``build_eval`` is called.
        """
        pass
    
    @abstractmethod
    def build_predict_yield(self, ctx: _ContextT) -> Generator:
        """
        Build operations before and after ``build_predict`` is called.
        """
        pass
