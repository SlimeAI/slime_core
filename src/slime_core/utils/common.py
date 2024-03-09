"""
Common utils in slime_core.
"""
import threading
import multiprocessing
from textwrap import indent
from .typing import (
    Mapping,
    Sequence,
    Generic,
    TypeVar,
    Hashable,
    Set,
    Type,
    Union
)
from .base import (
    ReadonlyAttr
)

_ArgsT = TypeVar('_ArgsT')
_KwdsT = TypeVar('_KwdsT')


class Count:
    """
    Count times of variable-get. It can be used to generate unique ids 
    of objects (e.g., handler ids can be automatically generated if 
    they are not specified by the users). The class uses a thread lock 
    and a process lock to make the generated value globally unique.
    """
    def __init__(self):
        super().__init__()
        self.value = 0
        self.__t_lock = threading.Lock()
        self.__p_lock = multiprocessing.Lock()

    def __set__(self, *_):
        pass

    def __get__(self, *_):
        with self.__t_lock, self.__p_lock:
            value = self.value
            self.value += 1
        return value


class FuncParams(Generic[_ArgsT, _KwdsT]):
    """
    Pack multiple function params in a single object.
    """
    def __init__(self, *args: _ArgsT, **kwargs: _KwdsT) -> None:
        self.args = args
        self.kwargs = kwargs


class HashCache(ReadonlyAttr):
    """
    Cache the hash value of the given hashable item in order to improve 
    efficiency. NOTE: ``hashable`` and ``hash_value`` are set as readonly 
    attributes to maintain the consistency.
    """
    __slots__ = ('hashable', 'hash_value')
    readonly_attr__ = ('hashable', 'hash_value')
    
    def __init__(self, hashable: Hashable) -> None:
        self.hashable = hashable
        self.hash_value = hash(hashable)
    
    def __hash__(self) -> int:
        return self.hash_value


def make_params_hashable(
    func_params: FuncParams[Hashable, Hashable],
    typed: bool = False,
    kwd_mark: Hashable = object(),
    type_mark: Hashable = object(),
    fast_types: Set[Type] = {int, str}
) -> Union[Hashable, HashCache]:
    """
    Make the function params a hashable item and return. If there is 
    only a single argument and its type is in ``fast_types``, directly 
    return it as the hashable item. If ``typed`` is True, then the type 
    of each param value is added in the hashable item and same values 
    with different types will be treated as different (e.g., 1 and 1.0). 
    
    NOTE: ``kwd_mark`` and ``type_mark`` are two newly created object so 
    that they are distinguishable from any given func params.
    """
    args = func_params.args
    kwargs = func_params.kwargs
    # Make ``hashable`` a list here, because list modification is faster 
    # than tuple.
    hashable = list(args)
    if kwargs:
        hashable.append(kwd_mark)
        hashable.extend(kwargs.items())
    if typed:
        # Distinguish between different param types.
        hashable.append(type_mark)
        hashable.extend((type(v) for v in args))
        if kwargs:
            hashable.extend((type(v) for v in kwargs.values()))
    elif len(hashable) == 1 and type(hashable[0]) in fast_types:
        # If fast type, return the value itself.
        return hashable[0]
    # Return ``HashCache`` to improve efficiency.
    return HashCache(tuple(hashable))

#
# dict and list formatter
#

def dict_to_key_value_str_list(
    __dict: Mapping,
    key_value_sep: str = '='
) -> list:
    return [f'{key}{key_value_sep}{value}' for key, value in __dict.items()]


def dict_to_key_value_str(
    __dict: Mapping,
    key_value_sep: str = '=',
    str_sep: str = ', '
) -> str:
    return str_sep.join(dict_to_key_value_str_list(__dict, key_value_sep=key_value_sep))


def _concat_format(
    __left: str,
    __content: Sequence[str],
    __right: str,
    *,
    item_sep: str = ',',
    indent_prefix: str = ' ' * 4,
    break_line: bool = True
) -> str:
    """
    A format function version that doesn't rely on the ``builtin_store`` config. In slime 
    implementations, the ``concat_format`` function relies on the ``builtin_store`` config 
    value (e.g., ``concat_format`` in ``torchslime.utils.common``).
    """
    if len(__content) < 1:
        # empty content: simply concat ``__left`` and ``__right``
        return __left + __right

    break_line_sep = '\n'
    if not break_line:
        indent_prefix = ''
    # format content
    content_sep = item_sep + (break_line_sep if break_line else '')
    __content = indent(content_sep.join(__content), prefix=indent_prefix)
    # format concat
    concat_sep = break_line_sep if break_line else ''
    return concat_sep.join([__left, __content, __right])
