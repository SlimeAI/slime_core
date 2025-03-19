from abc import ABC, abstractmethod
from slime_core.utils.typing.native import TypeVar, Generic

_ContextT = TypeVar("_ContextT")


class BuilderABC(ABC, Generic[_ContextT]):

    @abstractmethod
    def build(self, ctx: _ContextT) -> None:
        """
        Build the handler structure for pipelines.
        """
        pass

    @abstractmethod
    def run_build__(self, ctx: _ContextT) -> None:
        """
        Perform a complete build operation for building pipelines.
        """
        pass
