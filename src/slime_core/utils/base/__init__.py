"""
slime_core util base classes.
"""
#
# NOTE: ``BaseDict`` should be placed at the beginning of the file in order 
# to avoid circular import error (caused by ``slime_core.logging.logger``).
#
from slime_core.utils.typing.native import (
    TypeVar,
    MutableMapping,
    Generic,
    Union,
    Dict,
    Iterable,
    Tuple,
    overload,
    Iterator,
    cast
)
from slime_core.utils.typing.extension import (
    resolve_instance_classname,
    EmptyFlag,
    is_empty_flag,
    MISSING
)
from slime_core.utils.abc.base import (
    CoreBaseDict
)
from slime_core.utils.decorator import (
    InitOnce
)

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")

#
# Base Dict
#

class BaseDict(CoreBaseDict[_KT, _VT], Generic[_KT, _VT]):
    """
    A dict-like (mutable mapping) object that wraps a real Python ``dict`` (or ``MutableMapping``). 
    Compared to directly inheriting from ``dict``, ``BaseDict`` implements ``set_dict__`` method, 
    which can conveniently change the ``dict`` reference without using ``copy``.
    """

    @InitOnce
    def __init__(
        self,
        __dict_like: Union[MutableMapping[_KT, _VT], Iterable[Tuple[_KT, _VT]], EmptyFlag] = MISSING,
        **kwargs
    ):
        self.__dict: MutableMapping[_KT, _VT] = {}
        if is_empty_flag(__dict_like):
            __dict_like = {}
        # Use ``self.update`` here to make the initialization process controllable. Otherwise, if 
        # ``self.__dict = dict(__dict_like, **kwargs)`` is used here, the initialization process 
        # can't be restricted by the user-defined operations.
        self.update(__dict_like, **kwargs)

    def set_dict__(self, __dict: MutableMapping[_KT, _VT]) -> None:
        self.__dict = __dict

    def get_dict__(self) -> MutableMapping[_KT, _VT]:
        return self.__dict
    
    @overload
    def __getitem__(self, __key: _KT) -> _VT: pass
    @overload
    def __setitem__(self, __key: _KT, __value: _VT) -> None: pass
    @overload
    def __delitem__(self, __key: _KT) -> None: pass
    @overload
    def __iter__(self) -> Iterator[_KT]: pass
    @overload
    def __len__(self) -> int: pass
    
    def __getitem__(self, __key):
        return self.__dict[__key]
    
    def __setitem__(self, __key, __value):
        self.__dict[__key] = __value
    
    def __delitem__(self, __key):
        del self.__dict[__key]
    
    def __iter__(self):
        return iter(self.__dict)
    
    def __len__(self):
        return len(self.__dict)
    
    def __str__(self) -> str:
        classname = resolve_instance_classname(self)
        _id = str(hex(id(self)))
        _dict = str(self.__dict)
        return f'{classname}<{_id}>({_dict})'

#
# NOTE: Other modules should be placed bellow.
#

import re
from collections import deque
from functools import partial
from types import TracebackType
import slime_core.logging.logger as logger
from slime_core.utils.typing.native import (
    Any,
    List,
    Sequence,
    MutableSequence,
    Generic,
    SupportsIndex,
    Type,
    Generator,
    Callable,
    Set,
    Mapping,
    Deque
)
from slime_core.utils.typing.extension import (
    NOTHING,
    Nothing,
    Pass,
    PASS,
    is_none_or_nothing,
    Missing,
    unwrap_method,
    SlimeConstant,
    is_slime_constant,
    resolve_private_attr_name
)
from slime_core.utils.decorator import (
    DecoratorCall,
    FuncSetAttr
)
from slime_core.utils.abc.base import (
    CoreBaseList,
    CoreBiListItem,
    CoreMutableBiListItem,
    CoreBiList,
    CoreCompositeStructure,
    CoreItemAttrSetBinding,
    CoreItemAttrGetBinding,
    CoreItemAttrDelBinding,
    CoreItemAttrBinding,
    CoreBase,
    CoreBaseGenerator,
    CoreAttrObserver,
    CoreAttrObservable
)

_T = TypeVar("_T")
_SlimeConstantT = TypeVar("_SlimeConstantT", bound=SlimeConstant)

#
# Base List
#

class BaseList(CoreBaseList[_T], Generic[_T]):
    """
    A list-like (mutable sequence) object that wraps a real Python ``list`` (or ``MutableSequence``). 
    Compared to directly inheriting from ``list``, ``BaseList`` implements ``set_list__`` method, 
    which can conveniently change the ``list`` reference without using ``copy``.
    """

    @InitOnce
    def __init__(
        self,
        __list_like: Union[Iterable[_T], EmptyFlag] = MISSING
    ):
        self.__list: MutableSequence[_T] = []
        if not is_empty_flag(__list_like):
            # Use ``self.extend`` here to make the initialization process controllable. Otherwise, 
            # if ``self.__list = list(__list_like)`` is used here, the initialization process can't 
            # be restricted by the user-defined operations.
            self.extend(__list_like)

    @classmethod
    def create__(
        cls,
        __list_like: Union[Iterable[_T], _SlimeConstantT, None] = None,
        *,
        return_constant: bool = True
    ) -> Union["BaseList[_T]", _SlimeConstantT]:
        """
        Similar to ``BaseList.__init__``, but can return ``__list_like`` itself if it is a slime 
        constant and ``return_constant`` is ``True``.
        
        NOTE: The following two are equivalent:
        
        ```Python
        # The first.
        foo = BaseList.create__(bar, return_constant=True)
        # The second.
        foo = bar if is_slime_constant(bar) else BaseList(bar)
        ```
        """
        if (
            return_constant and 
            is_slime_constant(__list_like)
        ):
            return __list_like
        return cls(cast(Union[Iterable[_T], None], __list_like))

    def set_list__(self, __list: MutableSequence[_T]) -> None:
        self.__list = __list

    def get_list__(self) -> MutableSequence[_T]:
        return self.__list
    
    def rindex__(
        self,
        __value: _T,
        __start: int = 0,
        __stop: Union[int, Missing] = MISSING
    ) -> int:
        if __start < 0:
            __start = max(len(self) + __start, 0)
        
        if __stop is MISSING:
            __stop = len(self) - 1
        else:
            __stop = cast(int, __stop)
            if __stop < 0:
                __stop += (len(self) - 1)

        i = __stop
        while i >= __start:
            try:
                v = self[i]
            except IndexError:
                break
            if v is __value or v == __value:
                return i
            i -= 1
        raise ValueError
    
    @overload
    def __getitem__(self, __i: SupportsIndex) -> _T: pass
    @overload
    def __getitem__(self, __s: slice) -> MutableSequence[_T]: pass
    @overload
    def __setitem__(self, __key: SupportsIndex, __value: _T) -> None: pass
    @overload
    def __setitem__(self, __key: slice, __value: Iterable[_T]) -> None: pass
    @overload
    def __delitem__(self, __key: Union[SupportsIndex, slice]) -> None: pass
    @overload
    def insert(self, __index: SupportsIndex, __object: _T) -> None: pass
    
    def __getitem__(self, __key):
        return self.__list[__key]
    
    def __setitem__(self, __key, __value):
        self.__list[__key] = __value
    
    def __delitem__(self, __key):
        del self.__list[__key]
    
    def __len__(self) -> int:
        return len(self.__list)
    
    def insert(self, __index, __object):
        return self.__list.insert(__index, __object)
    
    def __str__(self) -> str:
        classname = resolve_instance_classname(self)
        _id = str(hex(id(self)))
        _list = str(self.__list)
        return f'{classname}<{_id}>({_list})'

#
# Bidirectional List.
#

_BiListT = TypeVar("_BiListT", bound=CoreBiList)
_BiListItemT = TypeVar("_BiListItemT", bound=CoreBiListItem)
_MutableBiListItemT = TypeVar("_MutableBiListItemT", bound=CoreMutableBiListItem)


class BiListItem(CoreBiListItem[_BiListT], Generic[_BiListT]):
    """
    Bidirectional list item, which keeps the reference of its parent.
    
    NOTE: The item can only have at most one parent at a time, and inserting or assigning 
    an item that already has a parent to another ``BiList`` will trigger warning.
    """
    
    @InitOnce
    def __init__(self) -> None:
        self.__parent: Union[_BiListT, Nothing] = NOTHING
        # Cache the name of the private attribute ``__parent``.
        self.__parent_attr_name: str = resolve_private_attr_name(BiListItem, '__parent')
    
    def set_parent__(self, parent: _BiListT) -> None:
        prev_parent = self.get_parent__()
        if not is_empty_flag(prev_parent) and parent is not prev_parent:
            # duplicate parent
            logger.core_logger.warning(
                f'BiListItem ``{str(self)}`` has already had a parent, but another parent is set. '
                'This may be because you add a single BiListItem object to multiple BiLists '
                'and may cause some inconsistent problems.'
            )
        self.__parent = parent
    
    def get_parent__(self) -> Union[_BiListT, Nothing]:
        return getattr(self, self.__parent_attr_name, NOTHING)
    
    def get_verified_parent__(self, contain_check: bool = True) -> Union[_BiListT, Nothing]:
        parent = self.get_parent__()
        if is_empty_flag(parent):
            # root node
            logger.core_logger.warning(
                f'BiListItem ``{str(self)}`` does not have a parent.'
            )
            return NOTHING
        if contain_check and self not in parent:
            self.process_unmatched_parent__()
            return NOTHING
        return parent
    
    def process_unmatched_parent__(self) -> None:
        """
        Output warnings and delete the ``__parent`` reference if the parent is unmatched. 
        NOTE: This method does not perform any actual checking, and it should not be called 
        externally in most cases, otherwise inconsistency may occur.
        """
        logger.core_logger.warning(
            f'BiListItem ``{str(self)}`` is not contained in its specified parent.'
        )
        self.del_parent__()
    
    def del_parent__(self):
        self.__parent = NOTHING


class MutableBiListItem(
    BiListItem[_BiListT],
    CoreMutableBiListItem[_MutableBiListItemT, _BiListT],
    Generic[_MutableBiListItemT, _BiListT]
):
    """
    Similar to ``BiListItem``, but defines more modification operations.
    """
    def replace_self__(self, __item: _MutableBiListItemT) -> None:
        parent = self.get_verified_parent__(contain_check=False)
        try:
            index = parent.index(self)
        except ValueError:
            self.process_unmatched_parent__()
        else:
            parent[index] = __item
    
    def insert_before_self__(self, __item: _MutableBiListItemT) -> None:
        parent = self.get_verified_parent__(contain_check=False)
        try:
            index = parent.index(self)
        except ValueError:
            self.process_unmatched_parent__()
        else:
            parent.insert(index, __item)
    
    def insert_after_self__(self, __item: _MutableBiListItemT) -> None:
        parent = self.get_verified_parent__(contain_check=False)
        try:
            index = parent.index(self)
        except ValueError:
            self.process_unmatched_parent__()
        else:
            parent.insert(index + 1, __item)
    
    def remove_self__(self) -> None:
        parent = self.get_verified_parent__(contain_check=False)
        try:
            parent.remove(self)
        except ValueError:
            self.process_unmatched_parent__()


class BiList(BaseList[_BiListItemT], CoreBiList[_BiListItemT], Generic[_BiListItemT]):
    """
    The ``BiList`` container that contains ``BiListItem``.
    """
    
    def set_list__(self, __list: List[_BiListItemT]) -> None:
        prev_list = self.get_list__()
        
        for prev_item in prev_list:
            prev_item.del_parent__()
        
        for item in __list:
            item.set_parent__(self)
        
        return super().set_list__(__list)

    @overload
    def __setitem__(self, __key: SupportsIndex, __value: _BiListItemT) -> None: pass
    @overload
    def __setitem__(self, __key: slice, __value: Iterable[_BiListItemT]) -> None: pass
    
    def __setitem__(
        self,
        __key: Union[SupportsIndex, slice],
        __value: Union[_BiListItemT, Iterable[_BiListItemT]]
    ) -> None:
        # delete parents of the replaced items and set parents to the replacing items
        if isinstance(__key, slice):
            for replaced_item in self[__key]:
                replaced_item.del_parent__()
            
            for item in __value:
                item: _BiListItemT
                item.set_parent__(self)
        else:
            self[__key].del_parent__()
            __value: _BiListItemT
            __value.set_parent__(self)
        return super().__setitem__(__key, __value)
    
    @overload
    def __delitem__(self, __key: SupportsIndex) -> None: pass
    @overload
    def __delitem__(self, __key: slice) -> None: pass
    
    def __delitem__(self, __key: Union[SupportsIndex, slice]) -> None:
        if isinstance(__key, slice):
            for item in self[__key]:
                item.del_parent__()
        else:
            self[__key].del_parent__()
        return super().__delitem__(__key)
    
    def insert(self, __index: SupportsIndex, __item: _BiListItemT) -> None:
        __item.set_parent__(self)
        return super().insert(__index, __item)

#
# BaseGenerator.
#

_YieldT_co = TypeVar("_YieldT_co", covariant=True)
_SendT_contra = TypeVar("_SendT_contra", contravariant=True)
_ReturnT_co = TypeVar("_ReturnT_co", covariant=True)


class BaseGenerator(
    CoreBaseGenerator[_YieldT_co, _SendT_contra, _ReturnT_co],
    Generic[_YieldT_co, _SendT_contra, _ReturnT_co]
):
    """
    Call a generator more safely without rasing ``StopIteration``. When the 
    generator ends, the ``stop`` attribute is set to ``True``.
    """

    @InitOnce
    def __init__(
        self,
        __gen: Generator[_YieldT_co, _SendT_contra, _ReturnT_co],
        *,
        stop_allowed: bool = True
    ) -> None:
        if not isinstance(__gen, Generator):
            raise TypeError(f'Argument ``__gen`` should be a generator.')
        self.gen = __gen
        self.stop_allowed = stop_allowed
        self.stop = False

    def __call__(self) -> _YieldT_co:
        return next(self)

    def send(self, __value: _SendT_contra) -> _YieldT_co:
        return self.call__(partial(self.gen.send, __value))

    @overload
    def throw(
        self,
        __exc_type: Type[BaseException],
        __exc_value: Union[BaseException, object] = None,
        __traceback: Union[TracebackType, None] = None
    ) -> _YieldT_co: pass
    @overload
    def throw(
        self,
        __exc_type: BaseException,
        __exc_value: None = None,
        __traceback: Union[TracebackType, None] = None
    ) -> _YieldT_co: pass

    def throw(self, __exc_type, __exc_value=None, __traceback=None) -> _YieldT_co:
        return self.call__(partial(self.gen.throw, __exc_type, __exc_value, __traceback))

    def call__(self, __caller: Callable[[], _T]) -> Union[_T, Pass]:
        if self.stop and not self.stop_allowed:
            from slime_core.utils.exception import APIMisused
            raise APIMisused(
                '``stop_allowed`` is set to False, and the generator already '
                'stopped but you still try to call ``next``.'
            )
        elif self.stop:
            return PASS

        try:
            return __caller()
        except StopIteration:
            self.stop = True


from .execution import *

#
# ItemAttrBinding
#

class ItemAttrSetBinding(CoreItemAttrSetBinding):
    """
    Bind ``__setitem__`` to ``__setattr__``.
    """
    
    def __setitem__(self, __name: str, __value: Any) -> None:
        return setattr(self, __name, __value)


class ItemAttrGetBinding(CoreItemAttrGetBinding):
    """
    Bind ``__getitem__`` to ``getattr``.
    """
    
    def __getitem__(self, __name: str) -> Any:
        return getattr(self, __name)


class ItemAttrDelBinding(CoreItemAttrDelBinding):
    """
    Bind ``__delitem__`` to ``delattr``.
    """
    
    def __delitem__(self, __name: str) -> None:
        return delattr(self, __name)


class ItemAttrBinding(
    ItemAttrSetBinding,
    ItemAttrGetBinding,
    ItemAttrDelBinding,
    CoreItemAttrBinding
):
    """
    Bind item operations to attribute operations.
    """
    pass


from .scoped import *

#
# Base
#

class Base(Scoped, ScopedAttr, ItemAttrBinding, CoreBase[CoreScopedManager]):
    """
    ``Base`` class provides abundant object services:
    
    - ``Scoped``: Provides scoped lifecycle management.
    - ``ScopedAttr``: Provides a simple interface for scoped attribute management. It is actually 
    a convenient wrapper for ``ScopedAttrAssign`` and ``ScopedAttrRestore``.
    - ``ItemAttrBinding``: Binds item operations to attribute operations.
    - Other extended APIs (such as ``from_kwargs__``, ``from__dict__``, ``pop__``, etc.).
    """

    @InitOnce
    def __init__(self) -> None:
        Scoped.__init__(self)
        ScopedAttr.__init__(self)
        ItemAttrBinding.__init__(self)

    def from_kwargs__(self, **kwargs) -> None:
        self.from_dict__(kwargs)

    def from_dict__(self, __dict: Mapping[str, Any]) -> None:
        self.__dict__.update(__dict)
    
    def hasattr__(self, __name: str) -> bool:
        return hasattr(self, __name)

    def pop__(self, __name: str, __default: Any = MISSING) -> Any:
        if self.hasattr__(__name):
            value = getattr(self, __name)
            delattr(self, __name)
        else:
            value = __default
        return value
    
    def __str__(self) -> str:
        from slime_core.utils.common import dict_to_key_value_str
        classname = resolve_instance_classname(self)
        _id = str(hex(id(self)))
        _dict = dict_to_key_value_str(self.__dict__)
        return f'{classname}<{_id}>({_dict})'

#
# Composite Structure
#

_CompositeStructureT = TypeVar("_CompositeStructureT", bound="CompositeStructure")


class CompositeStructure(
    CoreCompositeStructure[_CompositeStructureT],
    Generic[_CompositeStructureT]
):
    pass


def CompositeDFT(
    __item: _CompositeStructureT,
    __func: Callable[[_CompositeStructureT], None]
) -> None:
    stack: Deque[Union[Iterator[_CompositeStructureT], Nothing]] = deque([iter([__item])])
    
    while len(stack) > 0:
        node_iter = stack[-1]
        
        try:
            node = next(node_iter)
        except StopIteration:
            stack.pop()
            continue
        
        __func(node)
        stack.append(iter(node.composite_iterable__()))


def CompositeDFS(
    __item: _CompositeStructureT,
    __func: Callable[[_CompositeStructureT], bool]
) -> List[_CompositeStructureT]:
    results = []
    
    def _search(item):
        if __func(item):
            results.append(item)
    
    CompositeDFT(__item, _search)
    return results


def CompositeBFT(
    __item: _CompositeStructureT,
    __func: Callable[[_CompositeStructureT], None]
) -> None:
    queue: Deque[Union[Iterator[_CompositeStructureT], Nothing]] = deque([iter([__item])])
    
    while len(queue) > 0:
        node_iter = queue[0]
        
        try:
            node = next(node_iter)
        except StopIteration:
            queue.popleft()
            continue
        
        __func(node)
        queue.append(iter(node.composite_iterable__()))


def CompositeBFS(
    __item: _CompositeStructureT,
    __func: Callable[[_CompositeStructureT], bool]
) -> List[_CompositeStructureT]:
    results = []
    
    def _search(item):
        if __func(item):
            results.append(item)
    
    CompositeBFT(__item, _search)
    return results

#
# Attr Observer
#

OBSERVE_FUNC_SUFFIX = '_observe__'
OBSERVE_FUNC_SUFFIX_PATTERN = re.compile(f'{OBSERVE_FUNC_SUFFIX}$')
OBSERVE_INIT = 'observe_init__'
OBSERVE_NAMESPACE = 'observe_namespace__'
ObserveFuncType = Callable[[Any, Any, "AttrObservable"], None]


class _AttrObservableInfo:
    
    def __init__(
        self,
        observable: "AttrObservable",
        attr_set: Union[Set[str], Missing] = MISSING
    ) -> None:
        self.observable = observable
        self.attr_set: Set[str] = set() if attr_set is MISSING else attr_set
    
    def add_attr__(self, __name: str) -> None:
        return self.attr_set.add(__name)
    
    def remove_attr__(self, __name: str) -> None:
        if __name in self.attr_set:
            self.attr_set.remove(__name)
    
    def is_empty__(self) -> bool:
        return len(self.attr_set) < 1


class _AttrObservableDict(BaseDict[str, _AttrObservableInfo]):
    
    @staticmethod
    def get_observable_id__(__observable: "AttrObservable") -> str:
        # this behavior may change through different ``slime_core`` versions
        return str(id(__observable))
    
    def add__(self, __observable: "AttrObservable", __name: str) -> None:
        observable_id = self.get_observable_id__(__observable)
        
        if observable_id not in self:
            self[observable_id] = _AttrObservableInfo(__observable)
        self[observable_id].add_attr__(__name)
    
    def remove__(self, __observable: "AttrObservable", __name: str) -> None:
        observable_id = self.get_observable_id__(__observable)
        
        if observable_id in self:
            observable_info = self[observable_id]
            observable_info.remove_attr__(__name)
            if observable_info.is_empty__():
                del self[observable_id]
    
    def get__(self, __observable: "AttrObservable") -> Set[str]:
        observable_id = self.get_observable_id__(__observable)
        
        if observable_id in self:
            return self[observable_id].attr_set
        else:
            return set()
    
    def contains__(self, __observable: "AttrObservable") -> bool:
        return self.get_observable_id__(__observable) in self


class AttrObserver(CoreAttrObserver):
    
    @InitOnce
    def __init__(self) -> None:
        self.__observable_dict = _AttrObservableDict()
    
    @staticmethod
    def check_namespace__(
        func: ObserveFuncType,
        namespaces: Union[Sequence[str], EmptyFlag]
    ) -> bool:
        return (
            # ``None`` or ``NOTHING`` namespace won't match any function.
            not is_none_or_nothing(namespaces) and 
            (
                # ``MISSING`` namespace will match all the functions.
                namespaces is MISSING or 
                # Otherwise check if the function's namespace exists in ``namespaces``.
                getattr(unwrap_method(func), OBSERVE_NAMESPACE, MISSING) in namespaces
            )
        )
    
    def detach_inspect__(
        self,
        namespaces: Union[Sequence[str], EmptyFlag] = MISSING
    ) -> Dict[str, ObserveFuncType]:
        return self.observe_inspect__(
            # Check namespace.
            lambda func: self.check_namespace__(func, namespaces)
        )
    
    def attach_inspect__(
        self,
        namespaces: Union[Sequence[str], EmptyFlag] = MISSING
    ) -> Dict[str, ObserveFuncType]:
        return self.observe_inspect__(
            # Check namespace.
            lambda func: self.check_namespace__(func, namespaces)
        )
    
    def observe_inspect__(
        self,
        __func: Callable[[ObserveFuncType], bool]
    ) -> Dict[str, ObserveFuncType]:
        observe_dict: Dict[str, ObserveFuncType] = {}
        """
        NOTE: ``func_name`` here is actually the attribute name in the object, rather than the 
        real function name.
        
        Example:
            ```Python
            class A: pass
            
            def b(): pass
            
            a = A()
            a.c = b  # The ``func_name`` is ``c`` rather than ``b``
            ```
        """
        for func_name in filter(
            lambda func_name: OBSERVE_FUNC_SUFFIX_PATTERN.search(func_name) is not None,
            dir(self)
        ):
            func: ObserveFuncType = getattr(self, func_name)
            # inspect checking
            if __func(func):
                observe_attr_name = OBSERVE_FUNC_SUFFIX_PATTERN.sub('', func_name)
                observe_dict[observe_attr_name] = func
        return observe_dict
    
    def detach_all__(self) -> None:
        # NOTE: create a new list of ``__observable_dict.values()`` to 
        # avoid value change during iteration.
        for observable_info in list(self.__observable_dict.values()):
            observable_info.observable.detach__(self)
    
    def __del__(self) -> None:
        self.detach_all__()
    
    def get_observable_dict__(self) -> _AttrObservableDict:
        return self.__observable_dict


def get_observe_func_name(name: str) -> str:
    return f'{name}{OBSERVE_FUNC_SUFFIX}'


class _AttrObserverDict(BaseDict[str, List[AttrObserver]]):
    
    def add__(self, __name: str, __observer: AttrObserver) -> None:
        if __name not in self:
            self[__name] = []
        
        observers = self[__name]
        if __observer not in observers:
            observers.append(__observer)
    
    def remove__(self, __name: str, __observer: AttrObserver) -> None:
        if __name in self:
            observers = self[__name]
            if __observer in observers:
                observers.remove(__observer)
            if len(observers) < 1:
                del self[__name]


class AttrObservable(CoreAttrObservable[AttrObserver]):
    """
    NOTE: The ``__init__`` method of ``AttrObservable`` should always be called 
    first before other attributes can be set.
    """

    @InitOnce
    def __init__(self) -> None:
        # attr name to observers
        self.__attr_observer_dict: _AttrObserverDict
        # Use ``object.__setattr__`` to escape from any custom attribute operations.
        object.__setattr__(
            self,
            resolve_private_attr_name(AttrObservable, '__attr_observer_dict'),
            _AttrObserverDict()
        )
    
    def attach__(
        self,
        __observer: AttrObserver,
        *,
        init: Union[bool, Missing] = MISSING,
        namespaces: Union[Sequence[str], EmptyFlag] = MISSING
    ) -> None:
        observe_dict = __observer.attach_inspect__(namespaces)
        
        names = set(observe_dict.keys())
        # inspect new observe attrs
        names = names - __observer.get_observable_dict__().get__(self)
        
        for name in names:
            attr_init = getattr(
                unwrap_method(observe_dict[name]),
                OBSERVE_INIT,
                True
            ) if init is MISSING else init
            self.attach_attr__(__observer, name, init=bool(attr_init))
    
    def attach_attr__(self, __observer: AttrObserver, __name: str, *, init: bool = True) -> None:
        self.__attr_observer_dict.add__(__name, __observer)
        __observer.get_observable_dict__().add__(self, __name)
        
        if init:
            value = getattr(self, __name, MISSING)
            self.notify__(__observer, __name, value, MISSING)
    
    def detach__(
        self,
        __observer: AttrObserver,
        *,
        namespaces: Union[Sequence[str], EmptyFlag] = MISSING
    ) -> None:
        observable_dict = __observer.get_observable_dict__()
        if not observable_dict.contains__(self):
            return
        # Check names to detach.
        detach_names = observable_dict.get__(self)
        detach_names = set(__observer.detach_inspect__(namespaces).keys()) & detach_names
        
        # NOTE: use a copy of ``detach_names`` to avoid value change during iteration
        for name in list(detach_names):
            self.detach_attr__(__observer, name)
    
    def detach_attr__(self, __observer: AttrObserver, __name: str) -> None:
        self.__attr_observer_dict.remove__(__name, __observer)
        __observer.get_observable_dict__().remove__(self, __name)
    
    def notify__(self, __observer: AttrObserver, __name: str, __new_value: Any, __old_value: Any) -> None:
        """
        Notify one observer with new value, old value and observable object.
        """
        func: ObserveFuncType = getattr(__observer, get_observe_func_name(__name))
        return func(__new_value, __old_value, self)
    
    def __setattr__(self, __name: str, __value: Any) -> None:
        if (
            __name in _ATTR_OBSERVABLE_ESCAPED_SETATTRS or 
            __name not in self.__attr_observer_dict
        ):
            return super().__setattr__(__name, __value)
        else:
            old_value = getattr(self, __name, MISSING)
            super().__setattr__(__name, __value)
            # observer is called only when the new value is different from the old value
            if __value is not old_value:
                for observer in self.__attr_observer_dict[__name]:
                    self.notify__(observer, __name, __value, old_value)
    
    def get_attr_observer_dict__(self) -> _AttrObserverDict:
        return self.__attr_observer_dict


# These attributes are escaped from ``__setattr__`` to avoid circular or infinite 
# recursion problems.
_ATTR_OBSERVABLE_ESCAPED_SETATTRS = frozenset([
    resolve_private_attr_name(AttrObservable, '__attr_observer_dict')
])


@overload
def AttrObserve(
    _func: Missing = MISSING,
    *,
    init: bool = True,
    namespace: Union[str, Missing] = MISSING
) -> Callable[[ObserveFuncType], ObserveFuncType]: pass
@overload
def AttrObserve(
    _func: ObserveFuncType,
    *,
    init: bool = True,
    namespace: Union[str, Missing] = MISSING
) -> ObserveFuncType: pass

@DecoratorCall(index=0, keyword='_func')
def AttrObserve(
    _func=MISSING,
    *,
    init: bool = True,
    namespace: Union[str, Missing] = MISSING
):
    """
    Set observe settings to the observe func.
    """
    def decorator(func: ObserveFuncType) -> ObserveFuncType:
        return FuncSetAttr(
            func,
            attr_dict={
                OBSERVE_INIT: init,
                OBSERVE_NAMESPACE: namespace
            }
        )
    return decorator
