from slime_core.utils.typing.native import (
    Tuple,
    Dict,
    Any
)


class InstanceCreationHookMetaclass(type):
    """
    NOTE: Deprecated. This metaclass was created to insert a hook after 
    ``__new__`` and before ``__init__``. However, it is impossible to do so 
    using ``super().__call__``, and we can only manually simulate the ``__call__``
    process, which may cause unforeseen problems. Therefore, we use ``metaclass`` + 
    ``metabase`` as a substitute. In the ``__new__`` method of ``metabase``, 
    we can define some operations before ``__init__``, while in the ``__call__`` 
    method of ``metaclass``, we can define some other operations after ``__init__``. 
    Although this design is not uniform (``__new__`` in ``metabase`` and 
    ``__call__`` in ``metaclass``), it is safer.
    
    ---
    
    This metaclass breaks the inheritance chain of ``__call__`` method, so 
    it should better be the highest possible level base class.
    """
    
    def __call__(cls, *args, **kwargs):
        instance = cls.new_hook_metaclass__(*args, **kwargs)
        if isinstance(instance, cls):
            cls.init_hook_metaclass__(instance, args=args, kwargs=kwargs)
        return instance
    
    def new_hook_metaclass__(cls, *args, **kwargs):
        return cls.__new__(cls, *args, **kwargs)
    
    def init_hook_metaclass__(cls, instance, args: Tuple, kwargs: Dict[str, Any]) -> None:
        # init
        cls.__init__(instance, *args, **kwargs)
