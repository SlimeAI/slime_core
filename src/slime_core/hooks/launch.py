"""
Distributed Launch Hook
"""
from slime_core.utils.launch import CoreLaunchUtil
from slime_core.utils.typing import (
    TYPE_CHECKING,
    TypeVar,
    Generic
)
from .build import CoreBuildInterface
if TYPE_CHECKING:
    from slime_core.context.core import CoreContext
    from slime_core.context.compile import CoreCompile

_CoreContextT = TypeVar("_CoreContextT", bound="CoreContext[CoreCompile]")


class CoreLaunchHook(CoreLaunchUtil, CoreBuildInterface[_CoreContextT], Generic[_CoreContextT]):

    def get_device_info(self, ctx: _CoreContextT): pass
