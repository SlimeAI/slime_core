from .build import CoreBuildInterface
from slime_core.utils.abcs.base import CoreBaseList
from slime_core.utils.typing import (
    TypeVar,
    Generic
)
from abc import ABC

_ContextT = TypeVar("_ContextT")
_PluginHookT = TypeVar("_PluginHookT")


class CorePluginHook(CoreBuildInterface[_ContextT], ABC, Generic[_ContextT]):
    """
    Plugin hook for custom handler build.
    """
    pass


class CorePluginContainer(
    CorePluginHook[_ContextT],
    CoreBaseList[_PluginHookT],
    ABC,
    Generic[_ContextT, _PluginHookT]
):
    """
    Plugin container that calls plugin hooks.
    """
    pass
