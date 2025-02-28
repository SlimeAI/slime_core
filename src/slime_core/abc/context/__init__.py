from abc import ABC, abstractmethod
from slime_core.utils.abc.base import BaseABC
from slime_core.utils.abc.base.scoped import ScopedManagerABC
from slime_core.utils.base.execution import ContextGenerator
from slime_core.utils.typing.native import Union, Generic, TypeVar, Any
from slime_core.utils.typing.extension import Nothing
from .scoped import ContextScopedInit

_CompileT = TypeVar("_CompileT")


class TempContextABC(BaseABC[ScopedManagerABC], ABC):
    """
    NOTE: ``Temp`` in the name does NOT mean the context itself is temporal and may
    be destroyed, but means some attributes in the context can be re-initialized by
    calling the ``initialize__`` method.
    """

    def __init__(self) -> None:
        self.initialize__()

    @abstractmethod
    def initialize__(self) -> None:
        """
        Initialization of context object.
        """
        pass

    def scoped_init__(
        self, enter_init: bool = True, exit_init: bool = True
    ) -> ContextGenerator[None, Any, Any]:
        """
        A convenient wrapper for ``ContextScopedInit``.
        """
        return ContextScopedInit(
            enter_init=enter_init, exit_init=exit_init
        ).scoped_ctxgen(self)


class ContextABC(TempContextABC, ABC, Generic[_CompileT]):

    @property
    def compile(self) -> Union[_CompileT, Nothing]:
        """
        We additionally add the mixin property ``compile``, because we want to
        call the compile object like a function. (Specifically, ctx.compile(...)
        is more convenient than ctx.get_compile()(...))
        """
        return self.get_compile()

    @abstractmethod
    def set_compile(self, __compile: _CompileT) -> None:
        """
        Set the compile object to the context.
        """
        pass

    @abstractmethod
    def get_compile(self) -> Union[_CompileT, Nothing]:
        """
        Get the compile object. Return ``NOTHING`` if compile doesn't exit.
        """
        pass

    @abstractmethod
    def del_compile(self) -> None:
        """
        Remove the compile object.
        """
        pass


class HookContextABC(TempContextABC, ABC):

    @abstractmethod
    def initialize__(self) -> None:
        # hooks
        from slime_core.abc.hook.plugin import PluginContainerABC

        self.plugins: PluginContainerABC

        from slime_core.abc.hook.launch import LaunchHookABC

        self.launch: Union[LaunchHookABC, Nothing]

        from slime_core.abc.hook.build import BuildHookABC

        self.build: Union[BuildHookABC, Nothing]
