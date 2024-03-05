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

_T = TypeVar("_T")


class Registry(BaseDict[str, _T], Generic[_T]):

    def __init__(
        self,
        namespace: str,
        *,
        strict: bool = True
    ):
        super().__init__({})
        self.__namespace = namespace
        self.strict = strict
    
    @overload
    def __call__(
        self,
        _cls: Missing = MISSING,
        *,
        name: Union[str, Missing] = MISSING,
        strict: Union[bool, Missing] = MISSING
    ) -> Callable[[_T], _T]: pass
    @overload
    def __call__(
        self,
        _cls: _T,
        *,
        name: Union[str, Missing] = MISSING,
        strict: Union[bool, Missing] = MISSING
    ) -> _T: pass
    
    @DecoratorCall(index=1, keyword='_cls')
    def __call__(
        self,
        _cls: Union[_T, Missing] = MISSING,
        *,
        name: Union[str, Missing] = MISSING,
        strict: Union[bool, Missing] = MISSING
    ) -> _T:
        strict = self._get_strict(strict)

        def decorator(cls: _T) -> _T:
            nonlocal name
            if name is MISSING:
                name = getattr(cls, '__name__', 'UNKNOWN NAME')
            if name in self and strict:
                namespace = self.get_namespace()
                raise ValueError(f'Name "{name}" already in registry "{namespace}".')
            self[name] = cls
            return cls
        
        return decorator

    @overload
    def register_multi(
        self,
        names: Sequence[str],
        *,
        _cls: Missing = MISSING,
        strict: Union[bool, Missing] = MISSING
    ) -> Callable[[_T], _T]: pass
    @overload
    def register_multi(
        self,
        names: Sequence[str],
        *,
        _cls: _T,
        strict: Union[bool, Missing] = MISSING
    ) -> _T: pass

    @DecoratorCall(keyword='_cls')
    def register_multi(
        self,
        names: Sequence[str],
        *,
        _cls: Union[_T, Missing] = MISSING,
        strict: Union[bool, Missing] = MISSING
    ) -> _T:
        strict = self._get_strict(strict)

        def decorator(cls: _T) -> _T:
            for name in names:
                self(_cls=cls, name=name, strict=strict)
            return cls
        
        return decorator

    def get_namespace(self) -> str:
        return self.__namespace

    def _get_strict(self, strict: Union[bool, Missing] = MISSING):
        return strict if strict is not MISSING else self.strict
