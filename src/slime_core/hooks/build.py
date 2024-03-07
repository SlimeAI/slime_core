from slime_core.utils.typing import (
    TypeVar,
    Generic,
    Generator
)
from slime_core.utils.exception import APIMisused
from abc import ABC, abstractmethod

_ContextT = TypeVar("_ContextT")


class CoreGeneralBuildHook(ABC, Generic[_ContextT]):
    """
    Build hook for handler building management.
    """

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


class CoreGeneralBuildInterface(ABC, Generic[_ContextT]):
    """
    Interface for building handlers.
    """
    
    @abstractmethod
    def build_xxx_yield(self, ctx: _ContextT) -> Generator:
        """
        Perform build-related operations before and after the ``build_xxx`` method 
        in ``CoreGeneralBuildHook`` is called.
        
        NOTE: This abstract method only serves as a template for method naming 
        and framework design. Subclasses should deprecate this method and 
        extend to other build interfaces such as ``build_yield``, 
        ``build_train_yield``, ``build_eval_yield``, etc.
        """
        raise APIMisused(
            'The method ``build_xxx_yield`` only serves as a template for method '
            'naming and framework design, and it should never be called at runtime.'
        )


class CoreBuildHook(CoreGeneralBuildHook[_ContextT], ABC, Generic[_ContextT]):
    
    def build_xxx(self, ctx: _ContextT) -> None:
        # Do Nothing here.
        return super().build_xxx(ctx)
    
    def run_build_xxx__(self, ctx: _ContextT) -> None:
        # Do Nothing here.
        return super().run_build_xxx__(ctx)
    
    #
    # Other extended interfaces following the framework design.
    #
    
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


class CoreBuildInterface(CoreGeneralBuildInterface[_ContextT], ABC, Generic[_ContextT]):
    
    def build_xxx_yield(self, ctx: _ContextT) -> Generator:
        # Do nothing here.
        return super().build_xxx_yield(ctx)

    #
    # Other extended interfaces following the framework design.
    #

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
