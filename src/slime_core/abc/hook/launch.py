"""
Distributed Launch Hook
"""

from abc import ABC, abstractmethod
from slime_core.utils.abc.launch import LaunchUtilABC
from slime_core.utils.typing.native import Generic, TypeVar
from .build import BuildInterfaceABC

_ContextT = TypeVar("_ContextT")


class LaunchHookABC(
    LaunchUtilABC, BuildInterfaceABC[_ContextT], ABC, Generic[_ContextT]
):
    @abstractmethod
    def get_device_info(self, ctx: _ContextT) -> str:
        """
        Get the running device info. In different launch modes, this information may
        differ. For example, in the non-distributed launch mode, it will return the
        concrete devices you use (e.g., cpu, cuda:0, mps, etc.), while in the distributed
        launch mode, it will return information like world_size, current rank, etc.
        """
        pass
