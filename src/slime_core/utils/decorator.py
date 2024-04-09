import inspect
from functools import wraps
from .exception import APIMisused
from .typing.native import (
    Union,
    Callable,
    TypeVar,
    Type,
    overload,
    overload_dummy,
    List,
    Dict,
    Any,
    cast
)
from .typing.extension import (
    FuncOrMethod,
    MISSING,
    Missing,
    unwrap_method
)

_T = TypeVar("_T")
_FuncOrMethodT = TypeVar("_FuncOrMethodT", bound=FuncOrMethod)


def DecoratorCall(
    *,
    index: Union[int, Missing] = MISSING,
    keyword: Union[str, Missing] = MISSING
) -> Callable[[_T], _T]:
    """
    [func-decorator]
    """
    def decorator(func: _T) -> _T:
        @wraps(func)
        def wrapper(*args, **kwargs):
            arg_match = MISSING

            if keyword is not MISSING:
                arg_match = kwargs.get(str(keyword), MISSING)
            
            if index is not MISSING and arg_match is MISSING:
                arg_match = MISSING if index >= len(args) else args[index]

            _decorator = func(*args, **kwargs)
            return _decorator if arg_match is MISSING else _decorator(arg_match)
        return wrapper
    return decorator


def MethodChaining(func):
    """
    [func, level-1]
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        return self
    return wrapper


def Deprecated():
    """
    [func, level-1]
    """
    # TODO
    pass


def Experimental():
    # TODO
    pass

#
# RemoveOverload.
#

OVERLOAD_FUNC = 'overload_func__'


def OverloadFunc(_func: _FuncOrMethodT) -> _FuncOrMethodT:
    """
    Indicate that a function or method is an overload func, and it could be 
    removed by the ``RemoveOverload`` decorator. It further ensures that the 
    given func is overloaded, in case the ``overload_dummy`` check won't work 
    in certain future versions of Python.
    """
    return FuncSetAttr(_func, attr_dict={OVERLOAD_FUNC: True})


@overload
def RemoveOverload(
    _cls: Missing = MISSING,
    *,
    checklist: Union[Missing, List[str]] = MISSING,
    checklist_strict: bool = True
) -> Callable[[Type[_T]], Type[_T]]: pass
@overload
def RemoveOverload(
    _cls: Type[_T],
    *,
    checklist: Union[Missing, List[str]] = MISSING,
    checklist_strict: bool = True
) -> Type[_T]: pass

@DecoratorCall(index=0, keyword='_cls')
def RemoveOverload(
    _cls=MISSING,
    *,
    checklist: Union[Missing, List[str]] = MISSING,
    checklist_strict: bool = True
):
    """
    Remove a function or method in ``_cls`` if it is an overload func. If ``checklist`` 
    is given, then only functions that are in the ``checklist`` will be checked. If 
    ``checklist_strict`` is True, then all the functions in the ``checklist`` should 
    be an overload func, else an ``APIMisused`` exception will be raised.
    """
    def decorator(cls: Type[_T]) -> Type[_T]:
        _dict = cls.__dict__
        
        def filter_func(key: str) -> bool:
            """
            Check whether the function or method of the given key is to be removed.
            """
            if key not in _dict:
                return False
            static_func = unwrap_method(_dict[key])
            # Check ``OVERLOAD_FUNC`` here for further confirmation.
            if getattr(static_func, OVERLOAD_FUNC, False):
                return True
            # NOTE: The ``overload_dummy`` check may fail in future versions of Python, 
            # so using ``OverloadFunc`` is safer.
            return inspect.unwrap(static_func) is overload_dummy
        
        if checklist is MISSING:
            overloaded = tuple(filter(filter_func, _dict.keys()))
        else:
            overloaded = tuple(filter(filter_func, cast(List[str], checklist)))
            if checklist_strict:
                mismatched_overloaded = set(checklist) - set(overloaded)
                if mismatched_overloaded:
                    raise APIMisused(
                        '``checklist_strict`` is set to True, but not all the functions '
                        'in the ``checklist`` are overload functions. Mismatched functions: '
                        f'{mismatched_overloaded}.'
                    )
        for attr in overloaded:
            try:
                delattr(cls, attr)
            except AttributeError as e:
                from slime_core.logging.logger import core_logger
                core_logger.error(str(e), stack_info=True)
        
        return cls
    return decorator

#
# FuncSetAttr.
#

@overload
def FuncSetAttr(
    _func: Missing = MISSING,
    *,
    attr_dict: Dict[str, Any]
) -> Callable[[_FuncOrMethodT], _FuncOrMethodT]: pass
@overload
def FuncSetAttr(
    _func: _FuncOrMethodT,
    *,
    attr_dict: Dict[str, Any]
) -> _FuncOrMethodT: pass

@DecoratorCall(index=0, keyword='_func')
def FuncSetAttr(_func=MISSING, *, attr_dict: Dict[str, Any]):
    """
    Set attributes to the function in a decorator way.
    """
    def decorator(func: _FuncOrMethodT) -> _FuncOrMethodT:
        for key, value in attr_dict.items():
            try:
                setattr(func, key, value)
            except AttributeError as e:
                from slime_core.logging.logger import core_logger
                core_logger.error(str(e), stack_info=True)
        return func
    return decorator

#
# InitOnce.
#

INIT_ONCE_ATTR_NAME = 'init_once__'


@overload
def InitOnce(
    _func: Missing = MISSING,
    *,
    setattr_func: Union[Callable[[object, str, Any], None], Missing] = MISSING,
    getattr_func: Union[Callable[[object, str, Any], Any], Missing] = MISSING
) -> Callable[[_FuncOrMethodT], _FuncOrMethodT]: pass
@overload
def InitOnce(
    _func: _FuncOrMethodT,
    *,
    setattr_func: Union[Callable[[object, str, Any], None], Missing] = MISSING,
    getattr_func: Union[Callable[[object, str, Any], Any], Missing] = MISSING
) -> _FuncOrMethodT: pass

@DecoratorCall(index=0, keyword='_func')
def InitOnce(
    _func=MISSING,
    *,
    setattr_func: Union[Callable[[object, str, Any], None], Missing] = MISSING,
    getattr_func: Union[Callable[[object, str, Any], Any], Missing] = MISSING
):
    """
    Used for ``__init__`` operations in multiple inheritance scenarios. When ``__init__`` 
    is decorated with ``@InitOnce``, it can be called only once. NOTE that there is an 
    exception that if one ``__init__`` call raises an Exception and it is successfully 
    caught and processed, this ``__init__`` method may be called again by other methods. 
    Because of this, ``InitOnce`` only ensure 'at most one successful call' rather than 
    'one call'.
    
    Example:
    
    ```Python
    class Example:
        @InitOnce
        def __init__(self, arg1, arg2):
            print('Example.__init__', arg1, arg2)
    
    class A(Example):
        def __init__(self):
            Example.__init__(self, arg1=1, arg2=2)
    
    class B(Example):
        def __init__(self):
            Example.__init__(self, arg1=3, arg2=4)
    
    class C(A, B):
        def __init__(self):
            A.__init__(self)
            B.__init__(self)
    
    C()
    
    \"""
    Output:
    Example.__init__ 1 2
    \"""
    ```
    """
    def decorator(func: _FuncOrMethodT) -> _FuncOrMethodT:
        func_id = str(id(func))
        
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> None:
            # NOTE: The default behaviors of ``getattr`` and ``setattr`` are based on ``object``, 
            # because the ``__init__`` method has not been called before ``getattr`` and ``setattr``, 
            # but some custom attr methods may require ``__init__`` to be called.
            # Try to get ``init_once__`` attribute.
            if getattr_func is MISSING:
                try:
                    init_once__: Dict = object.__getattribute__(self, INIT_ONCE_ATTR_NAME)
                except AttributeError:
                    init_once__ = MISSING
            else:
                init_once__: Union[Dict, Missing] = getattr_func(self, INIT_ONCE_ATTR_NAME, MISSING)
            
            if init_once__ is MISSING:
                # Set ``init_once__`` if it does not exists.
                init_once__ = {}
                if setattr_func is MISSING:
                    object.__setattr__(self, INIT_ONCE_ATTR_NAME, init_once__)
                else:
                    setattr_func(self, INIT_ONCE_ATTR_NAME, init_once__)
            
            if not init_once__.get(func_id, False):
                # call the ``__init__`` method.
                func(self, *args, **kwargs)
                # mark this ``__init__`` has been called.
                # Note that it is after ``func`` is called, so ``InitOnce`` only ensure 
                # 'at most one successful call' rather than 'one call'.
                init_once__[func_id] = True

        return wrapper
    return decorator
