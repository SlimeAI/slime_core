from .typing import (
    Union,
    Callable,
    TypeVar,
    Sequence,
    NoneOrNothing,
    Pass,
    PASS,
    Any
)
from abc import ABC, abstractmethod

_T = TypeVar("_T")


class CoreLaunchUtil(ABC):
    """
    Launch util that defines different behaviors in different launch modes such as 
    non-distributed (vanilla) launch, distributed launch, etc.
    """
    
    def __init__(self) -> None:
        # Just for type hint here. Concrete attribute assignment should be completed 
        # in the subclasses.
        self.dist_comm: Union[CoreDistComm, NoneOrNothing]

    @abstractmethod
    def call(
        self,
        __caller: Callable[[], _T],
        *,
        exec_ranks: Union[Sequence[int], NoneOrNothing, Pass] = PASS
    ) -> Union[_T, None]:
        """
        Controller that decides whether to call the ``__caller`` according to the 
        ``exec_ranks`` parameter. The behaviors may differ based on different subclass 
        implementations. For example, in the distributed launch mode, the ``__caller`` 
        will be called if and only if the current distributed rank is matched in the 
        ``exec_ranks``, while in the non-distributed (vanilla) mode, the ``__caller`` 
        is always called no matter what the ``exec_ranks`` value is.
        """
        pass
    
    @abstractmethod
    def is_exec(self, exec_ranks: Union[Sequence[int], NoneOrNothing, Pass] = PASS) -> bool:
        """
        Determine whether the current rank is matched in the ``exec_ranks``.
        """
        pass
    
    @abstractmethod
    def is_distributed(self) -> bool:
        """
        An indicator attribute that indicates whether the launch util is for distributed 
        mode.
        """
        pass
    
    @abstractmethod
    def is_distributed_ready(self) -> bool:
        """
        An indicator attribute that indicates whether the current env is ready for 
        distributed running.
        """
        pass
    
    @abstractmethod
    def get_rank(self, *args, **kwargs) -> Union[int, NoneOrNothing]:
        """
        Get the current distributed rank. If not in distributed mode, return ``NOTHING``.
        """
    
    @abstractmethod
    def get_world_size(self, *args, **kwargs) -> Union[int, NoneOrNothing]:
        """
        Get the total distributed ranks. If not in distributed mode, return ``NOTHING``.
        """
        pass


class CoreDistComm(ABC):
    """
    Distributed communication APIs including gather, all_gather, broadcast, 
    scatter, etc.
    
    NOTE: The difference between the names ``xxx`` and ``xxx_object`` (e.g., 
    ``gather`` and ``gather_object``) is that ``xxx`` may be used for optimized 
    object transmission (e.g., ``torch.Tensor`` in PyTorch), while ``xxx_object`` 
    is used for more general usage (e.g., plain Python object transmission). If 
    there doesn't exist special optimization for some specific objects, you can 
    simply call ``xxx_object`` and return the result of it in the ``xxx`` method.
    """

    @abstractmethod
    def gather(self, *args, **kwargs) -> Any: pass
    
    @abstractmethod
    def gather_object(self, *args, **kwargs) -> Any: pass
    
    @abstractmethod
    def all_gather(self, *args, **kwargs) -> Any: pass
    
    @abstractmethod
    def all_gather_object(self, *args, **kwargs) -> Any: pass
    
    @abstractmethod
    def broadcast(self, *args, **kwargs) -> Any: pass
    
    @abstractmethod
    def broadcast_object(self, *args, **kwargs) -> Any: pass

    @abstractmethod
    def scatter(self, *args, **kwargs) -> Any: pass
    
    @abstractmethod
    def scatter_object(self, *args, **kwargs) -> Any: pass
