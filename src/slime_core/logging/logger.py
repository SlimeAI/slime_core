"""
Core logger module.
"""
import sys
import logging
from contextlib import ContextDecorator
from slime_core.utils.typing import (
    Any,
    NOTHING
)


def _create_core_logger() -> logging.Logger:
    """
    Create default core logger and return.
    """
    logger = logging.getLogger('core_logger__')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        '[slime_core {levelname}] - {asctime} - "{filename}:{lineno}" - {message}',
        datefmt='%Y/%m/%d %H:%M:%S',
        style='{'
    ))
    logger.addHandler(handler)
    return logger


_default_core_logger = _create_core_logger()
core_logger = _default_core_logger

#
# Other logger utils
#

class set_core_logger(ContextDecorator):
    """
    Change the core logger. Can be used as a context manager or a 
    function decorator, with the previous value restored when exit 
    or the function ends.
    """
    
    def __init__(self, logger: logging.Logger) -> None:
        global core_logger
        self.prev = core_logger
        core_logger = logger
        # Cache ``logger`` for ``_recreate_cm``.
        self.logger = logger
    
    def __enter__(self) -> None: pass
    
    def __exit__(self, *args, **kwargs) -> None:
        global core_logger
        core_logger = self.prev
    
    def _recreate_cm(self):
        return self.__class__(self.logger)

#
# Logger Func Arg Adapter
# NOTE: Should be put at the end of the file to avoid circular import.
#

from slime_core.utils.base import BaseDict


class LoggerKwargs(BaseDict[str, Any]):
    """
    A logger kwargs adapter that removes unsupported params according to 
    different Python versions.
    """
    
    def __init__(self, **kwargs):
        # ``stacklevel`` argument was added after py3.8
        if sys.version_info < (3, 8):
            kwargs.pop('stacklevel', NOTHING)
        super().__init__(**kwargs)
