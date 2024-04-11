"""
ABCs for ``slime_core.utils.base``.
"""
from abc import ABC, abstractmethod
from slime_core.utils.typing.native import (
    Generic,
    TypeVar,
    List,
    Union,
    SupportsIndex,
    Iterable,
    MutableSequence,
    MutableMapping,
    Any,
    Mapping,
    Generator,
    Callable,
    ContextManager,
    Dict,
    Sequence
)
from slime_core.utils.typing.extension import (
    Nothing,
    MISSING,
    Pass,
    EmptyFlag,
    Missing
)

_T = TypeVar("_T")
_KT = TypeVar("_KT")
_VT = TypeVar("_VT")

#
# BaseDict ABC
#

class CoreBaseDict(MutableMapping[_KT, _VT], ABC, Generic[_KT, _VT]):
    """
    ABC of ``BaseDict``.
    """

    @abstractmethod
    def set_dict__(self, __dict: MutableMapping[_KT, _VT]) -> None:
        """
        Change the dict reference.
        """
        pass

    @abstractmethod
    def get_dict__(self) -> MutableMapping[_KT, _VT]:
        """
        Get the dict reference.
        """
        pass

#
# BaseList ABC
#

class CoreBaseList(MutableSequence[_T], ABC, Generic[_T]):
    """
    ABC of ``BaseList``.
    """

    @abstractmethod
    def set_list__(self, __list: MutableSequence[_T]) -> None:
        """
        Change the list reference.
        """
        pass

    @abstractmethod
    def get_list__(self) -> MutableSequence[_T]:
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
    """
    ABC of ``BiListItem``.
    """
    
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
    """
    ABC of ``MutableBiListItem``.
    """
    
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
    """
    ABC of ``BiList``.
    """
    
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
# Generator ABCs.
#

_YieldT_co = TypeVar("_YieldT_co", covariant=True)
_SendT_contra = TypeVar("_SendT_contra", contravariant=True)
_ReturnT_co = TypeVar("_ReturnT_co", covariant=True)


class CoreBaseGenerator(
    Generator[_YieldT_co, _SendT_contra, _ReturnT_co],
    ABC,
    Generic[_YieldT_co, _SendT_contra, _ReturnT_co]
):
    """
    ABC of ``BaseGenerator``.
    """
    
    @abstractmethod
    def __call__(self) -> _YieldT_co:
        """
        Call ``next`` and return the yielded value.
        """
        pass
    
    @abstractmethod
    def call__(self, __caller: Callable[[], _T]) -> Union[_T, Pass]:
        """
        A unified controller that controls over the method calls (e.g., 
        ``send``, ``throw``, etc.) of the generator.
        """
        pass


_EnterT_co = TypeVar("_EnterT_co", covariant=True)


class CoreContextGenerator(
    CoreBaseGenerator[_YieldT_co, _SendT_contra, _ReturnT_co],
    ContextManager[_EnterT_co],
    Generic[_YieldT_co, _SendT_contra, _ReturnT_co, _EnterT_co]
):
    """
    ABC of ``ContextGenerator``.
    """
    pass


class CoreGeneralYieldContext(ABC, Generic[_EnterT_co]):
    """
    Provide a method template for yield context.
    """
    
    @abstractmethod
    def gen_yield(self, *args, **kwargs) -> Generator[_EnterT_co, Any, Any]:
        """
        A generator method used to build a context manager.
        """
        pass
    
    @abstractmethod
    def gen_ctxgen(self, *args, **kwargs) -> CoreContextGenerator[_EnterT_co, Any, Any, _EnterT_co]:
        """
        A mixin method that wraps the generator returned by ``gen_yield`` into 
        a ``ContextGenerator``.
        """
        pass

#
# ItemAttrBinding
#

class CoreItemAttrSetBinding(ABC):
    
    @abstractmethod
    def __setitem__(self, __name: str, __value: Any) -> None:
        """
        Bind ``__setitem__`` to ``__setattr__``.
        """
        pass


class CoreItemAttrGetBinding(ABC):
    
    @abstractmethod
    def __getitem__(self, __name: str) -> Any:
        """
        Bind ``__getitem__`` to ``getattr``.
        """
        pass


class CoreItemAttrDelBinding(ABC):
    
    @abstractmethod
    def __delitem__(self, __name: str) -> None:
        """
        Bind ``__delitem__`` to ``delattr``.
        """
        pass


class CoreItemAttrBinding(
    CoreItemAttrSetBinding,
    CoreItemAttrGetBinding,
    CoreItemAttrDelBinding,
    ABC
):
    """
    Bind item operations to attribute operations.
    """
    pass


from .scoped import *

#
# Base ABC.
#

_ScopedManagerT = TypeVar("_ScopedManagerT")


class CoreBase(
    CoreScoped[_ScopedManagerT],
    CoreScopedAttr,
    CoreItemAttrBinding,
    ABC,
    Generic[_ScopedManagerT]
):
    """
    ABC of ``Base``.
    """
    
    @abstractmethod
    def from_kwargs__(self, **kwargs) -> None:
        """
        Update ``Base`` attributes using kwargs.
        """
        pass
    
    @abstractmethod
    def from_dict__(self, __dict: Mapping[str, Any]) -> None:
        """
        Update ``Base`` attributes using a dict (or a mapping object).
        """
        pass
    
    @abstractmethod
    def hasattr__(self, __name: str) -> bool:
        """
        Check whether ``Base`` has the given attribute.
        """
        pass
    
    @abstractmethod
    def pop__(self, __name: str, __default: Any = MISSING) -> Any:
        """
        Pop the given attribute. Similar to ``dict.pop``. If the attribute 
        does not exist, return ``__default``.
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

#
# AttrObserver ABCs.
#

class CoreAttrObserver(ABC):
    """
    ABC of ``AttrObserver``.
    """
    
    @abstractmethod
    def detach_inspect__(
        self,
        namespaces: Union[Sequence[str], EmptyFlag] = MISSING
    ) -> Dict[str, Callable]:
        """
        Inspect detach items of the observer.
        """
        pass
    
    @abstractmethod
    def attach_inspect__(
        self,
        namespaces: Union[Sequence[str], EmptyFlag] = MISSING
    ) -> Dict[str, Callable]:
        """
        Inspect attach items of the observer.
        """
        pass
    
    @abstractmethod
    def detach_all__(self) -> None:
        """
        Detach self from all the observers it has attached to.
        """
        pass


_AttrObserverT = TypeVar("_AttrObserverT")


class CoreAttrObservable(ABC, Generic[_AttrObserverT]):
    """
    ABC of ``AttrObservable``.
    """
    
    @abstractmethod
    def attach__(
        self,
        __observer: _AttrObserverT,
        *,
        init: Union[bool, Missing] = MISSING,
        namespaces: Union[Sequence[str], EmptyFlag] = MISSING
    ) -> None:
        """
        Attach the observer functions to self.
        """
        pass
    
    @abstractmethod
    def attach_attr__(self, __observer: _AttrObserverT, __name: str, *, init: bool = True) -> None:
        """
        Attach a single observer function to self.
        """
        pass
    
    @abstractmethod
    def detach__(
        self,
        __observer: _AttrObserverT,
        *,
        namespaces: Union[Sequence[str], EmptyFlag] = MISSING
    ) -> None:
        """
        Detach the observer functions from self.
        """
        pass
    
    @abstractmethod
    def detach_attr__(self, __observer: _AttrObserverT, __name: str) -> None:
        """
        Detach a single observer function from self.
        """
        pass
    
    @abstractmethod
    def notify__(
        self,
        __observer: _AttrObserverT,
        __name: str,
        __new_value: Any,
        __old_value: Any
    ) -> None:
        """
        Notify the attached observers that the corresponding attribute has changed. 
        """
        pass
    
    @abstractmethod
    def __setattr__(self, __name: str, __value: Any) -> None:
        """
        Set attribute and notify changes.
        """
        # NOTE: Pass ``__setattr__`` along the mro.
        super().__setattr__(__name, __value)
