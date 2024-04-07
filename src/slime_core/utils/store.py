import os
import threading
from abc import ABCMeta
from .metaclass import (
    SingletonMetaclass,
    Metaclasses
)
from .metaclass.metabase import Singleton
from .typing.native import (
    Any,
    MutableMapping,
    overload,
    Union,
    TYPE_CHECKING,
    Sequence
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

@RemoveOverload(checklist=[
    'attach__',
    'attach_attr__',
    'detach__',
    'detach_attr__',
    'assign__',
    'restore__'
])
class CoreStore(
    ItemAttrBinding,
    Singleton,
    metaclass=Metaclasses(ABCMeta, SingletonMetaclass)
):
    """
    NOTE: ``CoreStore`` should be strictly subclassed and create a new 
    ``scoped_store_dict__`` attribute in each subclass you create to 
    ensure the consistency and namespace independence.
    """
    scoped_store_dict__: MutableMapping[str, ScopedStore]
    
    def scope__(self, __key: str) -> ScopedStore:
        if __key not in self.scoped_store_dict__:
            self.scoped_store_dict__[__key] = ScopedStore()
        
        return self.scoped_store_dict__[__key]

    def current__(self) -> ScopedStore:
        return self.scope__(self.get_current_key__())

    def destroy__(self, __key: Union[str, Missing] = MISSING):
        if __key is MISSING:
            __key = self.get_current_key__()
        
        if __key in self.scoped_store_dict__:
            del self.scoped_store_dict__[__key]

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
    
    @staticmethod
    def get_current_key__() -> str:
        pid = os.getpid()
        tid = threading.get_ident()
        return f'p{pid}-t{tid}'
    
    #
    # Overload functions for type hints.
    #
    
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
    @OverloadFunc
    @overload
    def assign__(self, **kwargs) -> "ScopedAttrAssign[ScopedStore]": pass
    @OverloadFunc
    @overload
    def restore__(self, *attrs: str) -> "ScopedAttrRestore[ScopedStore]": pass
