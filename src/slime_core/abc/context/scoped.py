from slime_core.utils.base.scoped import (
    ScopedManager
)
from slime_core.utils.typing.native import (
    TYPE_CHECKING,
    Any,
    Generator,
    TypeVar
)
if TYPE_CHECKING:
    from . import CoreTempContext

_ScopedT = TypeVar("_ScopedT", bound="CoreTempContext")


class CoreContextScopedManager(ScopedManager[_ScopedT, None]):
    pass


class ContextScopedInit(CoreContextScopedManager["CoreTempContext"]):
    """
    Try to call ``initialize__`` when entering or exiting the context.
    
    ``enter_init`` / ``exit_init``: Whether to call ``initialize__`` 
    when entering / exiting the context.
    """
    def __init__(self, enter_init: bool = True, exit_init: bool = True) -> None:
        super().__init__()
        self.enter_init = enter_init
        self.exit_init = exit_init
    
    def scoped_yield(self, scoped: "CoreTempContext") -> Generator[None, Any, Any]:
        if self.enter_init:
            # Init at entering.
            scoped.initialize__()
        try:
            yield
        finally:
            if self.exit_init:
                # Init at exiting.
                scoped.initialize__()
