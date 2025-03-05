from abc import ABC
from slime_core.utils.abc.base import BaseListABC
from slime_core.utils.typing.native import TypeVar, Generic
from . import BuilderWrapperABC

_ContextT = TypeVar("_ContextT")
_BuilderPluginT = TypeVar("_BuilderPluginT")


class BuilderPluginABC(BuilderWrapperABC[_ContextT], ABC, Generic[_ContextT]):
    """
    Plugin for custom handler build.
    """

    pass


class BuilderPluginContainerABC(
    BuilderPluginABC[_ContextT],
    BaseListABC[_BuilderPluginT],
    ABC,
    Generic[_ContextT, _BuilderPluginT],
):
    """
    Plugin container that calls plugins.
    """

    pass
