from abc import ABC, abstractmethod
from slime_core.utils.abc.base import BaseListABC
from slime_core.utils.typing.native import TypeVar, Generic, Generator

_ContextT = TypeVar("_ContextT")
_BuilderPluginT = TypeVar("_BuilderPluginT")


class BuilderExtensionABC(ABC, Generic[_ContextT]):
    """
    Extension for custom handler build.
    """

    @abstractmethod
    def build_yield(self, ctx: _ContextT) -> Generator:
        """
        Build operations before and after ``build`` is called.
        """
        pass


class BuilderExtensionContainerABC(
    BuilderExtensionABC[_ContextT],
    BaseListABC[_BuilderPluginT],
    ABC,
    Generic[_ContextT, _BuilderPluginT],
):
    """
    Extension container that calls extensions.
    """

    pass
