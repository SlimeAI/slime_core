from slime_core.utils.base import (
    BaseList,
    BaseGenerator,
    BaseGeneratorQueue
)
from slime_core.hooks.build import CoreBuildInterface
from slime_core.utils.typing import (
    Generator,
    TYPE_CHECKING,
    TypeVar
)
if TYPE_CHECKING:
    from slime_core.context.core import CoreContext
    from slime_core.context.compile import CoreCompile

_CoreContextT = TypeVar("_CoreContextT", bound="CoreContext[CoreCompile]")


class CorePluginHook(CoreBuildInterface[_CoreContextT]): pass


_CorePluginHookT = TypeVar("_CorePluginHookT", bound=CorePluginHook["CoreContext"])

class CorePluginContainer(CorePluginHook[_CoreContextT], BaseList[_CorePluginHookT]):
    
    def build_train_yield(self, ctx: _CoreContextT) -> Generator:
        with BaseGeneratorQueue((
            BaseGenerator(plugin.build_train_yield(ctx)) for plugin in self
        )):
            yield
    
    def build_eval_yield(self, ctx: _CoreContextT) -> Generator:
        with BaseGeneratorQueue((
            BaseGenerator(plugin.build_eval_yield(ctx)) for plugin in self
        )):
            yield
    
    def build_predict_yield(self, ctx: _CoreContextT) -> Generator:
        with BaseGeneratorQueue((
            BaseGenerator(plugin.build_predict_yield(ctx)) for plugin in self
        )):
            yield
