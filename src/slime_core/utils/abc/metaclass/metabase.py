from abc import ABC, abstractmethod
from slime_core.utils.typing.native import (
    Tuple,
    Type,
    Union,
    Callable,
    Any,
    Iterable,
    FrozenSet,
)
from slime_core.utils.typing.extension import Missing
from slime_core.utils.decorator import OverloadFunc, RemoveOverload


@RemoveOverload(checklist=["__hash__", "__eq__"])
class CoreClassAttrCompute(ABC):

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of the class attribute to be computed.
        """
        pass

    @abstractmethod
    def get_computed_name(self) -> str:
        """
        Get the computed attribute name.
        """
        pass

    @abstractmethod
    def get_escaped_types(self) -> Tuple[Type, ...]:
        """
        Get escaped types that do not need computation.
        """
        pass

    @abstractmethod
    def get_compute_func(self) -> Callable[[Any, Tuple[Any]], Any]:
        """
        Get the compute func. Return ``default_compute_func`` if the compute func
        is not specified.
        """
        pass

    @OverloadFunc
    def __hash__(self) -> int:
        """
        ``__hash__`` should be implemented by subclasses.
        """
        pass

    @OverloadFunc
    def __eq__(self, __other: Union["CoreClassAttrCompute", Any]) -> bool:
        """
        ``__eq__`` should be implemented by subclasses.
        """
        pass

    @staticmethod
    @abstractmethod
    def default_compute_func(
        attr: Union[Iterable, Missing], computed_base_attrs: Tuple[Iterable]
    ) -> FrozenSet:
        """
        The default compute function used when the compute func is not specified.
        """
        pass
