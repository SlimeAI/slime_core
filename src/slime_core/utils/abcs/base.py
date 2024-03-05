"""
ABCs for ``slime_core.utils.base``.
"""
from abc import ABC, abstractmethod
from slime_core.utils.typing import (
    Generic,
    TypeVar,
    Nothing,
    List,
    Union,
    SupportsIndex,
    Iterable,
    MutableSequence,
    MutableMapping,
    Dict
)

_T = TypeVar("_T")
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")

#
# BaseDict ABC
#

class CoreBaseDict(MutableMapping[_KT, _VT], ABC):

    @abstractmethod
    def set_dict__(self, __dict: Dict[_KT, _VT]) -> None:
        """
        Change the dict reference.
        """
        pass

    @abstractmethod
    def get_dict__(self) -> Dict[_KT, _VT]:
        """
        Get the dict reference.
        """
        pass

#
# BaseList ABC
#

class CoreBaseList(MutableSequence[_T], ABC):

    @abstractmethod
    def set_list__(self, __list: List[_T]) -> None:
        """
        Change the list reference.
        """
        pass

    @abstractmethod
    def get_list__(self) -> List[_T]:
        """
        Get the list reference.
        """
        pass

#
# ABCs for BiList.
#

_BiListT = TypeVar("_BiListT")
_BiListItemT = TypeVar("_BiListItemT")
_MutableBiListItemT = TypeVar("_MutableBiListItemT")


class CoreBiListItem(ABC, Generic[_BiListT]):
    
    @abstractmethod
    def set_parent__(self, parent: _BiListT) -> None:
        """
        Set parent of the BiListItem.
        """
        pass
    
    @abstractmethod
    def get_parent__(self) -> Union[_BiListT, Nothing]:
        """
        Get the parent. If no parent is specified, return ``NOTHING``.
        """
        pass
    
    @abstractmethod
    def get_verified_parent__(self) -> Union[_BiListT, Nothing]:
        """
        Check parent validity and return the parent. If any inconsistencies occur, 
        try to fix them and return ``NOTHING``.
        """
        pass
    
    @abstractmethod
    def del_parent__(self):
        """
        Remove the parent.
        """
        pass


class CoreMutableBiListItem(CoreBiListItem[_BiListT], ABC, Generic[_MutableBiListItemT, _BiListT]):
    
    @abstractmethod
    def replace_self__(self, __item: _MutableBiListItemT) -> None:
        """
        Replace self with ``__item`` in the parent.
        """
        pass
    
    @abstractmethod
    def insert_before_self__(self, __item: _MutableBiListItemT) -> None:
        """
        Insert ``__item`` before self in the parent.
        """
        pass
    
    @abstractmethod
    def insert_after_self__(self, __item: _MutableBiListItemT) -> None:
        """
        Insert ``__item`` after self in the parent.
        """
        pass
    
    @abstractmethod
    def remove_self__(self) -> None:
        """
        Remove self from the parent.
        """
        pass


class CoreBiList(CoreBaseList[_BiListItemT], ABC, Generic[_BiListItemT]):
    
    # NOTE: Some abstract methods have already been defined in super classes,
    # but we still re-define them here to denote that these method should be 
    # overridden.
    
    @abstractmethod
    def set_list__(self, __list: List[_BiListItemT]) -> None:
        """
        Change the list reference of self.
        """
        pass
    
    @abstractmethod
    def __setitem__(
        self,
        __key: Union[SupportsIndex, slice],
        __value: Union[_BiListItemT, Iterable[_BiListItemT]]
    ) -> None:
        """
        BiList set item.
        """
        pass
    
    @abstractmethod
    def __delitem__(self, __key: Union[SupportsIndex, slice]) -> None:
        """
        BiList delete item.
        """
        pass
    
    @abstractmethod
    def insert(self, __index: SupportsIndex, __item: _BiListItemT) -> None:
        """
        BiList insert.
        """
        pass

#
# CompositeStructure ABC.
#

_CompositeStructureT = TypeVar("_CompositeStructureT")


class CoreCompositeStructure(ABC, Generic[_CompositeStructureT]):
    
    @abstractmethod
    def composite_iterable__(self) -> Union[Iterable[_CompositeStructureT], Nothing]:
        """
        Return the composite components.
        """
        pass
