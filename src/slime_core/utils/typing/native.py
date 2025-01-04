"""
This module provides version compatibility for the native Python ``typing`` module.

NOTE: This module may not provide a complete ``typing`` version compatibility. It may only 
process typings that may be used by ``slime_core``.
"""

import sys
from typing import *

if sys.version_info < (3, 8):
    try:
        from typing_extensions import (
            SupportsIndex,
            TypedDict,
            Literal,
            Protocol,
            runtime_checkable,
        )
    except Exception:
        print(
            "Loading ``typing_extensions`` module failed. "
            "Please make sure you have installed it correctly."
        )
        raise

if sys.version_info < (3, 9):
    # FIX: ``from typing import *`` does not include the following modules in Python 3.9
    # and earlier versions.
    from typing import BinaryIO, IO, Match, Pattern, TextIO

if sys.version_info >= (3, 9):
    from builtins import (
        dict as Dict,
        list as List,
        set as Set,
        frozenset as FrozenSet,
        tuple as Tuple,
        type as Type,
        # for compatibility for Python 2.x
        str as Text,
    )

    from collections import (
        defaultdict as DefaultDict,
        OrderedDict as OrderedDict,
        ChainMap as ChainMap,
        Counter as Counter,
        deque as Deque,
    )

    from re import Pattern as Pattern, Match as Match

    from collections.abc import (
        Set as AbstractSet,
        Collection as Collection,
        Container as Container,
        ItemsView as ItemsView,
        KeysView as KeysView,
        Mapping as Mapping,
        MappingView as MappingView,
        MutableMapping as MutableMapping,
        MutableSequence as MutableSequence,
        MutableSet as MutableSet,
        Sequence as Sequence,
        ValuesView as ValuesView,
        Coroutine as Coroutine,
        AsyncGenerator as AsyncGenerator,
        AsyncIterable as AsyncIterable,
        AsyncIterator as AsyncIterator,
        Awaitable as Awaitable,
        Iterable as Iterable,
        Iterator as Iterator,
        Callable as Callable,
        Generator as Generator,
        Hashable as Hashable,
        Reversible as Reversible,
        Sized as Sized,
    )

    # deprecated type: ByteString
    try:
        from typing_extensions import Buffer as ByteString
    except Exception:
        ByteString = Union[bytes, bytearray, memoryview]

    from contextlib import (
        AbstractContextManager as ContextManager,
        AbstractAsyncContextManager as AsyncContextManager,
    )

try:
    from typing import _overload_dummy as overload_dummy
except Exception:

    @overload
    def overload_dummy():
        pass
