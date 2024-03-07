"""
A convenient module register util that helps you dynamically build modules.
"""
from .base import BaseDict
from .decorator import DecoratorCall
from .typing import (
    Union,
    Sequence,
    TypeVar,
    overload,
    Callable,
    Missing,
    MISSING,
    Generic
)

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class GeneralRegistry(BaseDict[_KT, _VT], Generic[_KT, _VT]):
    """
    A general registry whose type of keys can be any specified value. 
    
    We name the parameter in the methods ``cls`` (or ``_cls``) because at 
    first the registry is designed for classes, and for compatibility we 
    have not renamed the parameter.
    """
    
    def __init__(
        self,
        namespace: str,
        *,
        strict: bool = True
    ):
        super().__init__({})
        self.__namespace = namespace
        self.strict = strict
    
    def get_namespace(self) -> str:
        """
        Get the namespace of the registry.
        """
        return self.__namespace

    def parse_strict__(self, strict: Union[bool, Missing] = MISSING):
        """
        Parse the given ``strict`` value. If ``strict`` is ``MISSING``, then 
        return ``self.strict`` (i.e., the config of the registry), else 
        directly return ``strict`` (which will override the registry config 
        when registering a specific item).
        """
        return (
            strict if strict is not MISSING else self.strict
        )
    
    #
    # Register a single item using ``__call__``.
    #
    
    @overload
    def __call__(
        self,
        _cls: Missing = MISSING,
        *,
        key: Union[_KT, Missing] = MISSING,
        strict: Union[bool, Missing] = MISSING
    ) -> Callable[[_VT], _VT]: pass
    @overload
    def __call__(
        self,
        _cls: _VT,
        *,
        key: Union[_KT, Missing] = MISSING,
        strict: Union[bool, Missing] = MISSING
    ) -> _VT: pass
    
    @DecoratorCall(index=1, keyword='_cls')
    def __call__(
        self,
        _cls: Union[_VT, Missing] = MISSING,
        *,
        key: Union[_KT, Missing] = MISSING,
        strict: Union[bool, Missing] = MISSING
    ) -> _VT:
        """
        Register an item. Can be used as a decorator or a normal method.
        """
        def decorator(cls: _VT) -> _VT:
            # Call the core register method.
            self.register__(cls, key, strict)
            return cls
        
        return decorator

    #
    # Register a single item with multiple keys.
    #

    @overload
    def register_multi(
        self,
        keys: Sequence[_KT],
        *,
        _cls: Missing = MISSING,
        strict: Union[bool, Missing] = MISSING
    ) -> Callable[[_VT], _VT]: pass
    @overload
    def register_multi(
        self,
        keys: Sequence[_KT],
        *,
        _cls: _VT,
        strict: Union[bool, Missing] = MISSING
    ) -> _VT: pass

    @DecoratorCall(keyword='_cls')
    def register_multi(
        self,
        keys: Sequence[_KT],
        *,
        _cls: Union[_VT, Missing] = MISSING,
        strict: Union[bool, Missing] = MISSING
    ) -> _VT:
        strict = self.parse_strict__(strict)

        def decorator(cls: _VT) -> _VT:
            for key in keys:
                # Respectively register the item with different keys.
                self(_cls=cls, key=key, strict=strict)
            return cls
        
        return decorator

    #
    # The core register method.
    #

    def register__(
        self,
        cls: _VT,
        key: Union[_KT, Missing],
        strict: Union[bool, Missing]
    ) -> None:
        """
        Core register method. Can be overridden by subclasses for extended features.
        """
        strict = self.parse_strict__(strict)
        if key is MISSING:
            # The key should be explicitly specified or be properly handled by subclasses, 
            # so it should never be ``MISSING`` here.
            from .exception import APIMisused
            namespace = self.get_namespace()
            raise APIMisused(
                f'Error when registering ``{repr(cls)}`` in registry ``{namespace}``. '
                f'Key cannot be ``MISSING``. Check the key setting.'
            )
        if key in self and strict:
            namespace = self.get_namespace()
            raise ValueError(
                f'Key ``{key}`` already exists in registry ``{namespace}``.'
            )
        # Register ``cls`` with ``key``.
        self[key] = cls


class Registry(GeneralRegistry[str, _VT], Generic[_VT]):
    """
    A more commonly used registry with key type set to str.
    """

    def register__(
        self,
        cls: _VT,
        key: Union[str, Missing],
        strict: Union[bool, Missing]
    ) -> None:
        """
        Core register method. If ``key`` is not specified, get the ``__name__`` of 
        ``cls`` as ``key``.
        """
        if key is MISSING:
            # Try to get the ``__name__`` of ``cls`` if ``key`` is not specified.
            key = getattr(cls, '__name__', MISSING)
        if key is MISSING:
            from .exception import APIMisused
            namespace = self.get_namespace()
            raise APIMisused(
                f'Registry cannot correctly infer the ``key`` when registering '
                f'``{repr(cls)}`` in registry {namespace}. Neither is the ``key`` '
                f'param specified, nor does the attribute ``__name__`` exist in '
                f'``{repr(cls)}``.'
            )
        return super().register__(cls, key, strict)
