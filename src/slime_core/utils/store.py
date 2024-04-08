import threading
from abc import ABCMeta
from .metaclass import (
    SingletonMetaclass,
    Metaclasses
)
from .metaclass.metabase import Singleton
from .typing.native import (
    Any,
    overload,
    Union,
    TYPE_CHECKING,
    Sequence,
    Mapping
)
from .typing.extension import (
    is_slime_naming,
    Missing,
    MISSING,
    NoneOrNothing
)
from .base import (
    Base,
    AttrObservable,
    ItemAttrBinding
)
from .decorator import RemoveOverload, OverloadFunc
# type hint only
if TYPE_CHECKING:
    from .base import (
        AttrObserver,
        ScopedAttrAssign,
        ScopedAttrRestore
    )

#
# Scoped Store
#

class ScopedStore(Base, AttrObservable):
    """
    A global scoped store that contains data.
    """
    
    def __init__(self) -> None:
        Base.__init__(self)
        AttrObservable.__init__(self)
    
    def init__(self, __name: str, __value: Any):
        """
        Init attribute only when it is not set or is ``MISSING``
        """
        if (
            not self.hasattr__(__name) or 
            getattr(self, __name, MISSING) is MISSING
        ):
            setattr(self, __name, __value)

#
# Store
#

# Attribute name used when assigning the ``ScopedStore`` to ``threading.local``.
SCOPED_STORE_ATTR_NAME = 'scoped_store__'


class StoreLocal:
    """
    Plain local object that does not support thread-independent store. Can be faster 
    than ``threading.local``, but you should make sure that the store won't be used 
    in thread-independent scenarios.
    """
    __slots__ = (SCOPED_STORE_ATTR_NAME,)


@RemoveOverload(checklist=[
    'attach__',
    'attach_attr__',
    'detach__',
    'detach_attr__',
    'assign__',
    'restore__',
    'from_kwargs__',
    'from_dict__',
    'hasattr__',
    'pop__'
])
class CoreStore(
    ItemAttrBinding,
    Singleton,
    metaclass=Metaclasses(ABCMeta, SingletonMetaclass)
):
    """
    NOTE: ``CoreStore`` should be strictly subclassed and create a new 
    ``scoped_store_local__`` attribute in each subclass you create to 
    ensure consistency and namespace independence.
    
    ``scoped_store_local__`` can be set to a ``threading.local`` object 
    to make the store thread-independent, or can be set to a ``StoreLocal`` 
    object (or any other plain object) to be faster under thread-dependent 
    scenarios (where multi-threading is not used or the multiple threads 
    share the same store data).
    """
    scoped_store_local__: Union[StoreLocal, threading.local]

    def current__(self) -> ScopedStore:
        scoped_store: Union[ScopedStore, Missing] = getattr(
            self.scoped_store_local__, SCOPED_STORE_ATTR_NAME, MISSING
        )
        if scoped_store is MISSING:
            scoped_store = ScopedStore()
            setattr(self.scoped_store_local__, SCOPED_STORE_ATTR_NAME, scoped_store)
        return scoped_store

    def __getattr__(self, __name: str) -> Any:
        return getattr(self.current__(), __name)

    def __getattribute__(self, __name: str) -> Any:
        # slime naming
        if is_slime_naming(__name) is True:
            return super().__getattribute__(__name)
        # else get from ScopedStore object
        return getattr(self.current__(), __name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        setattr(self.current__(), __name, __value)
    
    def __delattr__(self, __name: str) -> None:
        delattr(self.current__(), __name)
    
    #
    # Overload functions for type hints.
    #
    
    # Observable APIs.
    @OverloadFunc
    @overload
    def attach__(
        self,
        __observer: "AttrObserver",
        *,
        init: Union[bool, Missing] = MISSING,
        namespaces: Union[Sequence[str], Missing, NoneOrNothing] = MISSING
    ) -> None:
        pass
    @OverloadFunc
    @overload
    def attach_attr__(self, __observer: "AttrObserver", __name: str, *, init: bool = True) -> None: pass
    @OverloadFunc
    @overload
    def detach__(
        __observer: "AttrObserver",
        *,
        namespaces: Union[Sequence[str], Missing, NoneOrNothing] = MISSING
    ) -> None:
        pass
    @OverloadFunc
    @overload
    def detach_attr__(self, __observer: "AttrObserver", __name: str) -> None: pass
    
    # ScopedAttr APIs.
    @OverloadFunc
    @overload
    def assign__(self, **kwargs) -> "ScopedAttrAssign[ScopedStore]": pass
    @OverloadFunc
    @overload
    def restore__(self, *attrs: str) -> "ScopedAttrRestore[ScopedStore]": pass
    
    # Base APIs.
    @OverloadFunc
    @overload
    def from_kwargs__(self, **kwargs) -> None: pass
    @OverloadFunc
    @overload
    def from_dict__(self, __dict: Mapping[str, Any]) -> None: pass
    @OverloadFunc
    @overload
    def hasattr__(self, __name: str) -> bool: pass
    @OverloadFunc
    @overload
    def pop__(self, __name: str, __default: Any = MISSING) -> Any: pass
