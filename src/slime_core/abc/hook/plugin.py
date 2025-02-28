from abc import ABC
from slime_core.utils.abc.base import BaseListABC
from slime_core.utils.typing.native import TypeVar, Generic
from .build import BuildInterfaceABC

_ContextT = TypeVar("_ContextT")
_PluginHookT = TypeVar("_PluginHookT")


class PluginHookABC(BuildInterfaceABC[_ContextT], ABC, Generic[_ContextT]):
    """
    Plugin hook for custom handler build.
    """

    pass


class PluginContainerABC(
    PluginHookABC[_ContextT],
    BaseListABC[_PluginHookT],
    ABC,
    Generic[_ContextT, _PluginHookT],
):
    """
    Plugin container that calls plugin hooks.
    """

    pass
