"""
Global store module that provides global data management.
"""
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
    ``CoreStore`` provides a global singleton helper that manages a set of 
    ``ScopedStore`` instances.
    
    Attribute resolution order: If the attribute name to be accessed is a 
    slime naming, then it will first try to get the attribute from the 
    ``CoreStore``, and if the attribute does not exist, then it will try to 
    get the attribute from the ``ScopedStore`` returned by ``current__`` (
    referred to as 'the current store'). If the attribute name is NOT a 
    slime naming, then directly get it from the current store. Attribute set 
    and del operations on ``CoreStore`` will be directly proxied to the 
    current store, without considering the naming.
    
    NOTE: ``CoreStore`` should be strictly subclassed and create a new 
    ``scoped_store_local__`` attribute in each subclass you create to ensure 
    consistency and namespace independence.
    
    ``scoped_store_local__`` can be set to a ``threading.local`` object to 
    make the store thread-independent, or can be set to a ``StoreLocal`` 
    object (or any other plain object) to be faster under thread-dependent 
    scenarios (where multi-threading is not used or the multiple threads 
    share the same store data).
    """
    scoped_store_local__: Union[StoreLocal, threading.local]

    def current__(self) -> ScopedStore:
        """
        Get the current ``ScopedStore``. The returned store will be different if 
        ``scoped_store_local__`` is set to ``threading.local`` in multi-threading 
        scenarios.
        """
        scoped_store: Union[ScopedStore, Missing] = getattr(
            self.scoped_store_local__, SCOPED_STORE_ATTR_NAME, MISSING
        )
        if scoped_store is MISSING:
            scoped_store = ScopedStore()
            setattr(self.scoped_store_local__, SCOPED_STORE_ATTR_NAME, scoped_store)
        return scoped_store

    def __getattribute__(self, __name: str) -> Any:
        if is_slime_naming(__name):
            # If it is slime naming, then first try to 
            # get the attribute from self.
            try:
                return super().__getattribute__(__name)
            except AttributeError:
                # ``AttributeError`` is ignored, and continue 
                # to get the attribute from the current store.
                pass
        # NOTE: We do not use ``__getattr__`` to process the 
        # above ``AttributeError``, because if the current store 
        # does not have the attribute, the following ``getattr`` 
        # will be called twice (the first time is here, and the 
        # second time is in the ``__getattr__``).
        # Get the attribute from the current store.
        return getattr(self.current__(), __name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        # Directly set the attribute to the current store.
        setattr(self.current__(), __name, __value)
    
    def __delattr__(self, __name: str) -> None:
        # Directly del the attribute from the current store.
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
