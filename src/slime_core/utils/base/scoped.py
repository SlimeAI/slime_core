"""
Scoped lifecycle management.
"""
from abc import ABCMeta
import slime_core.logging.logger as logger
from slime_core.utils.exception import APIMisused
from slime_core.utils.abc.base.scoped import (
    CoreScopedManager,
    CoreScopedManagerContainer,
    CoreScoped,
    CoreScopedAttr,
    CoreScopedGuard,
    CoreScopedGuardContainer
)
from slime_core.utils.typing.native import (
    Callable,
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
    Stop,
    resolve_instance_classname,
    is_empty_flag
)
from slime_core.utils.metaclass import Metaclasses, ComputedClassAttrMetaclass
from slime_core.utils.metaclass.metabase import ComputedClassAttr, ClassAttrCompute
from slime_core.utils.decorator import InitOnce
from . import BaseList
from .execution import (
    ContextManagerStack,
    ContextGenerator,
    BaseGenerator,
    EmptyContextGenerator
)

_EnterT_co = TypeVar("_EnterT_co", covariant=True)
# NOTE: The ``ScopedManager`` may accept plain objects that are not 
# instances of ``CoreScoped``.
_GeneralScopedT = TypeVar("_GeneralScopedT", bound=Union[CoreScoped, Any])
# NOTE: The ``ScopedGuard`` can only accept ``CoreScoped`` objects.
_ScopedT = TypeVar("_ScopedT", bound=CoreScoped)

#
# Scoped base class.
#

class ScopedManager(CoreScopedManager[_GeneralScopedT, _EnterT_co], Generic[_GeneralScopedT, _EnterT_co]):
    """
    ``ScopedManager`` defines a generator method API used for scoped 
    lifecycle management.
    """
    
    def scoped_ctxgen(self, scoped: _GeneralScopedT) -> ContextGenerator[_EnterT_co, Any, Any]:
        manager_container: Union[
            CoreScopedManagerContainer[CoreScopedManager[CoreScoped, Any], CoreScoped], EmptyFlag
        ] = (
            getattr(scoped, 'scoped_managers__', MISSING)
        )
        ctxgen = ContextGenerator(self.scoped_yield(scoped))
        if is_empty_flag(manager_container):
            # Disable traceback.
            return ctxgen
        else:
            manager_container = cast(
                CoreScopedManagerContainer[CoreScopedManager[CoreScoped, Any], CoreScoped],
                manager_container
            )
            
            def wrapper():
                """
                Wrapper generator function that sets traceback of ``ScopedManager``.
                """
                manager_container.append(self)
                try:
                    with ctxgen as value:
                        yield value
                finally:
                    try:
                        # Use ``rindex__`` is faster, because it is stack-like.
                        del manager_container[manager_container.rindex__(self)]
                    except ValueError:
                        logger.core_logger.warning(
                            f'ScopedManager ``{str(self)}`` is not found in ``{str(scoped)}``. '
                            'Maybe external modifications have been made to the traceback container.'
                        )
            
            return ContextGenerator(wrapper())


class ScopedManagerContainer(
    BaseList[CoreScopedManager[CoreScoped, Any]],
    CoreScopedManagerContainer[CoreScopedManager[CoreScoped, Any], CoreScoped]
):
    """
    A container that contains entered scoped managers.
    """
    pass


class ScopedGuard(
    ScopedManager[_ScopedT, _EnterT_co],
    CoreScopedGuard[_ScopedT, _EnterT_co],
    Generic[_ScopedT, _EnterT_co]
):
    """
    NOTE: We strongly recommend to explicitly raise an Exception rather than 
    yield ``STOP`` to intercept the guarded operations, because there is no 
    way to really know whether the operations have succeeded through the 
    returned value of the methods like ``__setattr__`` (which always returns 
    ``None``).
    """
    def setattr_guard_yield(
        self,
        __scoped: _ScopedT,
        __name: str,
        __value: Any
    ) -> Generator[Union[Stop, None], Any, Any]:
        # Do nothing here, and subclasses can optionally implement it.
        yield

    def getattr_guard_yield(
        self,
        __scoped: _ScopedT,
        __name: str
    ) -> Generator[Union[Stop, None], Any, Any]:
        # Do nothing here, and subclasses can optionally implement it.
        yield
    
    def delattr_guard_yield(
        self,
        __scoped: _ScopedT,
        __name: str
    ) -> Generator[Union[Stop, None], Any, Any]:
        # Do nothing here, and subclasses can optionally implement it.
        yield
    
    def scoped_ctxgen(self, scoped: _ScopedT) -> ContextGenerator[_EnterT_co, Any, Any]:
        if not isinstance(scoped, CoreScoped):
            raise APIMisused(
                '``ScopedGuard`` can only be applied to instances of ``Scoped`` or '
                '``CoreScoped``.'
            )
        
        guard_enabled = scoped.is_scoped_guard_enabled__()
        if not guard_enabled:
            # Do nothing here.
            return EmptyContextGenerator()
        
        def wrapper():
            """
            Wrapper generator function that manages guard container.
            """
            guard_container = scoped.scoped_guards__
            guard_container.append(self)
            try:
                with ContextGenerator(self.scoped_yield(scoped)) as value:
                    yield value
            finally:
                try:
                    # NOTE: Get the container again, in case the reference 
                    # has changed.
                    guard_container = scoped.scoped_guards__
                    # Use ``rindex__`` is faster, because it is stack-like.
                    del guard_container[guard_container.rindex__(self)]
                except ValueError:
                    logger.core_logger.warning(
                        f'ScopedGuard ``{str(self)}`` is not found in ``{str(scoped)}``. '
                        'Maybe external modifications have been made to the guard container.'
                    )
        
        return ContextGenerator(wrapper())


class ScopedGuardContainer(
    BaseList[CoreScopedGuard[CoreScoped, Any]],
    CoreScopedGuardContainer[CoreScopedGuard[CoreScoped, Any], CoreScoped]
):
    """
    A container that contains entered scoped guards.
    """
    def setattr_guard(
        self,
        __scoped: CoreScoped,
        __setattr_func: Callable[[str, Any], None],
        __name: str,
        __value: Any
    ) -> None:
        with ContextManagerStack((
            guard.setattr_guard_yield(__scoped, __name, __value)
            for guard in self
        )).stack() as vals:
            if ContextManagerStack.check_stop(vals):
                return
            return __setattr_func(__name, __value)
    
    def getattr_guard(
        self,
        __scoped: CoreScoped,
        __getattr_func: Callable[[str], Any],
        __name: str
    ) -> Any:
        with ContextManagerStack((
            guard.getattr_guard_yield(__scoped, __name)
            for guard in self
        )).stack() as vals:
            if ContextManagerStack.check_stop(vals):
                # Return ``MISSING`` to denote that ``getattr`` is intercepted.
                return MISSING
            return __getattr_func(__name)
    
    def delattr_guard(
        self,
        __scoped: CoreScoped,
        __delattr_func: Callable[[str], None],
        __name: str
    ) -> None:
        with ContextManagerStack((
            guard.delattr_guard_yield(__scoped, __name)
            for guard in self
        )).stack() as vals:
            if ContextManagerStack.check_stop(vals):
                return
            return __delattr_func(__name)


class Scoped(
    ComputedClassAttr,
    CoreScoped[CoreScopedManager],
    metaclass=Metaclasses(ComputedClassAttrMetaclass, ABCMeta)
):
    class_attr_compute__ = (ClassAttrCompute('escaped_scoped_attrs__', 'escaped_scoped_attrs_computed__'),)
    
    @InitOnce
    def __init__(self) -> None:
        # Use ``object.__setattr__`` to escape from any custom attribute operations.
        object.__setattr__(self, 'scoped_managers__', ScopedManagerContainer())
        object.__setattr__(self, 'scoped_guards__', ScopedGuardContainer())
    
    def scoped__(
        self,
        __scoped_managers: Union[Iterable[CoreScopedManager], EmptyFlag] = MISSING
    ) -> ContextManager[Tuple]:
        if is_empty_flag(__scoped_managers):
            return ContextManagerStack(__scoped_managers).stack()
        else:
            return ContextManagerStack((
                manager.scoped_ctxgen(self)
                for manager in cast(Iterable[CoreScopedManager], __scoped_managers)
            )).stack()
    
    def is_scoped_guard_enabled__(self) -> bool:
        """
        Scoped guard is enabled by default.
        """
        return True
    
    def __setattr__(self, __name: str, __value: Any) -> None:
        if (
            not self.is_scoped_guard_enabled__() or 
            __name in self.escaped_scoped_attrs_computed__ or 
            len(self.scoped_guards__) == 0
        ):
            return super().__setattr__(__name, __value)
        # Pass the attribute to the guard container.
        return self.scoped_guards__.setattr_guard(
            self, super().__setattr__, __name, __value
        )
    
    def __getattribute__(self, __name: str) -> Any:
        if __name in _ATTR_OBSERVABLE_ESCAPED_SETATTRS:
            return super().__getattribute__(__name)
        if (
            not self.is_scoped_guard_enabled__() or 
            __name in self.escaped_scoped_attrs_computed__ or 
            len(self.scoped_guards__) == 0
        ):
            return super().__getattribute__(__name)
        # Pass the attribute to the guard container.
        return self.scoped_guards__.getattr_guard(
            self, super().__getattribute__, __name
        )
    
    def __delattr__(self, __name: str) -> None:
        if (
            not self.is_scoped_guard_enabled__() or 
            __name in self.escaped_scoped_attrs_computed__ or 
            len(self.scoped_guards__) == 0
        ):
            return super().__delattr__(__name)
        # Pass the attribute to the guard container.
        return self.scoped_guards__.delattr_guard(
            self, super().__delattr__, __name
        )


# These attributes are escaped from ``__getattribute__`` to avoid circular 
# or infinite recursion problems.
_ATTR_OBSERVABLE_ESCAPED_SETATTRS = frozenset([
    'is_scoped_guard_enabled__',
    'escaped_scoped_attrs_computed__',
    'scoped_guards__'
])

#
# Scoped Attribute.
#

class ScopedAttrRestore(ScopedManager[_GeneralScopedT, Any], Generic[_GeneralScopedT]):

    @InitOnce
    def __init__(self, attrs: Iterable[str]) -> None:
        self.attrs = list(attrs)
        self.prev_value_dict: Dict[str, Any] = {}

    def scoped_yield(self, scoped: _GeneralScopedT) -> Generator["ScopedAttrRestore[_GeneralScopedT]", Any, Any]:
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


class ScopedAttrAssign(ScopedAttrRestore[_GeneralScopedT], Generic[_GeneralScopedT]):

    @InitOnce
    def __init__(self, attr_assign: Mapping[str, Any]) -> None:
        super().__init__(attr_assign.keys())
        self.attr_assign = attr_assign

    def scoped_yield(self, scoped: _GeneralScopedT) -> Generator["ScopedAttrAssign[_GeneralScopedT]", Any, Any]:
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
    
    @InitOnce
    def __init__(self) -> None: pass
    
    def assign__(self, attr_assign: Mapping[str, Any]) -> ContextGenerator[ScopedAttrAssign, Any, Any]:
        return ScopedAttrAssign(attr_assign).scoped_ctxgen(self)
    
    def restore__(self, attrs: Iterable[str]) -> ContextGenerator[ScopedAttrRestore, Any, Any]:
        return ScopedAttrRestore(attrs).scoped_ctxgen(self)
