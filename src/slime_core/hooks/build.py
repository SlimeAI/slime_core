from slime_core.utils.typing import (
    Generator,
    TYPE_CHECKING,
    TypeVar,
    Generic
)
from slime_core.utils.base import (
    BaseGenerator,
    BaseGeneratorQueue
)
from abc import ABC, abstractmethod
if TYPE_CHECKING:
    from slime_core.context.core import CoreContext
    from slime_core.context.compile import CoreCompile

_CoreContextT = TypeVar("_CoreContextT", bound="CoreContext[CoreCompile]")


class CoreBuildHook(ABC, Generic[_CoreContextT]):

    @abstractmethod
    def build_train(self, ctx: _CoreContextT) -> None: pass
    
    @abstractmethod
    def build_eval(self, ctx: _CoreContextT) -> None: pass
    
    @abstractmethod
    def build_predict(self, ctx: _CoreContextT) -> None: pass

    def _build_train(self, ctx: _CoreContextT):
        """
        Build order:
        Launch -> Plugin -> Build -> Launch -> Plugin
        """
        h = ctx.hook_ctx
        
        with BaseGeneratorQueue((
            BaseGenerator(h.launch.build_train_yield(ctx)),
            BaseGenerator(h.plugins.build_train_yield(ctx))
        )):
            h.build.build_train(ctx)
    
    def _build_eval(self, ctx: _CoreContextT):
        """
        Build order:
        Launch -> Plugin -> Build -> Launch -> Plugin
        """
        h = ctx.hook_ctx
        
        with BaseGeneratorQueue((
            BaseGenerator(h.launch.build_eval_yield(ctx)),
            BaseGenerator(h.plugins.build_eval_yield(ctx))
        )):
            h.build.build_eval(ctx)

    def _build_predict(self, ctx: _CoreContextT):
        """
        Build order:
        Launch -> Plugin -> Build -> Launch -> Plugin
        """
        h = ctx.hook_ctx

        with BaseGeneratorQueue((
            BaseGenerator(h.launch.build_predict_yield(ctx)),
            BaseGenerator(h.plugins.build_predict_yield(ctx))
        )):
            h.build.build_predict(ctx)


class CoreBuildInterface(Generic[_CoreContextT]):
    """
    Interface for building handlers.
    """
    def build_train_yield(self, ctx: _CoreContextT) -> Generator: yield
    def build_eval_yield(self, ctx: _CoreContextT) -> Generator: yield
    def build_predict_yield(self, ctx: _CoreContextT) -> Generator: yield
