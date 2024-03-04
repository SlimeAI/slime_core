from functools import wraps
from .typing import (
    Union,
    Callable,
    TypeVar,
    Type,
    overload,
    FuncOrMethod,
    List,
    overload_dummy,
    MISSING,
    Dict,
    Missing,
    unwrap_method,
    Any
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


@overload
def RemoveOverload(_cls: Missing = MISSING, *, checklist: Union[Missing, List[str]] = MISSING) -> Callable[[Type[_T]], Type[_T]]: pass
@overload
def RemoveOverload(_cls: Type[_T], *, checklist: Union[Missing, List[str]] = MISSING) -> Type[_T]: pass

@DecoratorCall(index=0, keyword='_cls')
def RemoveOverload(_cls=MISSING, *, checklist: Union[Missing, List[str]] = MISSING):
    def decorator(cls: Type[_T]) -> Type[_T]:
        nonlocal checklist
        
        _dict = cls.__dict__
        filter_func = lambda key: key in _dict and unwrap_method(_dict[key]) is overload_dummy
        
        if checklist is MISSING:
            checklist = filter(filter_func, _dict.keys())
        else:
            checklist = filter(filter_func, checklist)
        for attr in checklist:
            delattr(cls, attr)
        
        return cls
    return decorator


@overload
def FuncSetAttr(_func: Missing = MISSING, *, attr_dict: Dict[str, Any]) -> Callable[[_T], _T]: pass
@overload
def FuncSetAttr(_func: _T, *, attr_dict: Dict[str, Any]) -> _T: pass

@DecoratorCall(index=0, keyword='_func')
def FuncSetAttr(_func=MISSING, *, attr_dict: Dict[str, Any]):
    """
    Set attributes to the function in a decorator way.
    """
    def decorator(func: _T) -> _T:
        for key, value in attr_dict.items():
            setattr(func, key, value)
        return func
    return decorator


def InitOnce(func: _FuncOrMethodT) -> _FuncOrMethodT:
    """
    Used for ``__init__`` operations in multiple inheritance scenarios.
    Should be used together with ``slime_core.utils.metaclass.InitOnceMetaclass``.
    When ``__init__`` is decorated with ``InitOnce``, it will be called only once during 
    each instance creation. NOTE that there is an exception that if one ``__init__`` call
    raises an Exception and it is successfully caught and processed, this ``__init__`` 
    method may be called again by other methods. Because of this, ``InitOnce`` only ensure 
    'at most one successful call' rather than 'one call'.
    
    Example:
    
    ```Python
    class Example(metaclass=InitOnceMetaclass):
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
    func_id = str(id(func))
    
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Union[_T, None]:
        init_once__: Union[Dict, Missing] = getattr(self, 'init_once__', MISSING)
        # whether the instance is being created.
        instance_creating = init_once__ is not MISSING
        # whether the instance is being created AND this ``__init__`` method has not been called.
        uninitialized = instance_creating and not init_once__.get(func_id, False)
        
        ret = None
        if not instance_creating or uninitialized:
            # call the ``__init__`` method.
            ret = func(self, *args, **kwargs)
        
        if uninitialized:
            """
            mark this ``__init__`` has been called.
            Note that it is after ``func`` is called, so ``InitOnce`` only ensure 
            'at most one successful call' rather than 'one call'.
            """
            init_once__[func_id] = True
        
        return ret

    return wrapper
