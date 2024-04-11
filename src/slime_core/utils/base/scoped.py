"""
Scoped lifecycle management.
"""
import slime_core.logging.logger as logger
from slime_core.utils.abc.base.scoped import (
    CoreScopedManager,
    CoreScoped,
    CoreScopedAttr
)
from slime_core.utils.typing.native import (
    Generator,
    Generic,
    Any,
    Union,
    Iterable,
    Tuple,
    Dict,
    ContextManager,
    TypeVar,
    cast,
    Mapping
)
from slime_core.utils.typing.extension import (
    EmptyFlag,
    MISSING,
    NOTHING,
    resolve_instance_classname,
    is_empty_flag
)
from . import ContextManagerStack, ContextGenerator, BaseGenerator

_EnterT_co = TypeVar("_EnterT_co", covariant=True)
_ScopedT = TypeVar("_ScopedT")

#
# Scoped base class.
#

class ScopedManager(CoreScopedManager[_ScopedT, _EnterT_co], Generic[_ScopedT, _EnterT_co]):
    """
    ``ScopedManager`` defines a generator method API used for scoped 
    lifecycle management.
    """
    
    def scoped_ctxgen(self, scoped: _ScopedT) -> ContextGenerator[_EnterT_co, Any, Any]:
        return ContextGenerator(self.scoped_yield(scoped))


_ScopedManagerT = TypeVar("_ScopedManagerT", bound=ScopedManager)


class Scoped(CoreScoped[_ScopedManagerT], Generic[_ScopedManagerT]):
    
    def scoped__(
        self,
        __scoped_managers: Union[Iterable[_ScopedManagerT], EmptyFlag] = MISSING
    ) -> ContextManager[Tuple]:
        if is_empty_flag(__scoped_managers):
            return ContextManagerStack(__scoped_managers)
        else:
            return ContextManagerStack(map(
                lambda manager: manager.scoped_ctxgen(self),
                cast(Iterable[_ScopedManagerT], __scoped_managers)
            ))

#
# Scoped Attribute.
#

class ScopedAttrRestore(ScopedManager[_ScopedT, Any], Generic[_ScopedT]):

    def __init__(self, attrs: Iterable[str]) -> None:
        self.attrs = list(attrs)
        self.prev_value_dict: Dict[str, Any] = {}

    def scoped_yield(self, scoped: _ScopedT) -> Generator["ScopedAttrRestore[_ScopedT]", Any, Any]:
        for attr in self.attrs:
            # Only cache existing attributes of ``obj``.
            if hasattr(scoped, attr):
                self.prev_value_dict[attr] = getattr(scoped, attr, NOTHING)
        try:
            yield self
        finally:
            for attr in self.attrs:
                # Restore the attributes.
                try:
                    if attr in self.prev_value_dict:
                        # Restore previously existing attributes before the scope.
                        setattr(scoped, attr, self.prev_value_dict[attr])
                    elif hasattr(scoped, attr):
                        # Remove previously non-existing attributes before the scope.
                        delattr(scoped, attr)
                except Exception as e:
                    logger.core_logger.error(
                        f'Restoring scoped attribute failed. Object: {str(scoped)}, '
                        f'attribute: {attr}. {resolve_instance_classname(e)}: {str(e)}'
                    )
            # NOTE: Should clear the ``prev_value_dict`` for reuse.
            self.prev_value_dict.clear()


class ScopedAttrAssign(ScopedAttrRestore[_ScopedT], Generic[_ScopedT]):

    def __init__(self, attr_assign: Mapping[str, Any]) -> None:
        super().__init__(attr_assign.keys())
        self.attr_assign = attr_assign

    def scoped_yield(self, scoped: _ScopedT) -> Generator["ScopedAttrAssign[_ScopedT]", Any, Any]:
        super_gen = BaseGenerator(super().scoped_yield(scoped))
        super_gen()
        for attr, value in self.attr_assign.items():
            try:
                setattr(scoped, attr, value)
            except Exception as e:
                logger.core_logger.error(
                    f'Assigning scoped attribute failed. Object: {str(scoped)}, '
                    f'attribute: {attr}. {resolve_instance_classname(e)}: {str(e)}'
                )
        try:
            yield self
        finally:
            super_gen()


class ScopedAttr(CoreScopedAttr):
    """
    Helper class that implements ``ScopedAttrAssign`` and ``ScopedAttrRestore`` 
    through methods.
    """
    
    def __init__(self) -> None: pass
    
    def assign__(self, attr_assign: Mapping[str, Any]) -> ContextGenerator[ScopedAttrAssign, Any, Any]:
        return ScopedAttrAssign(attr_assign).scoped_ctxgen(self)
    
    def restore__(self, attrs: Iterable[str]) -> ContextGenerator[ScopedAttrRestore, Any, Any]:
        return ScopedAttrRestore(attrs).scoped_ctxgen(self)
