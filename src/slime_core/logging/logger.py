"""
Core logger module.
"""
import logging
from slime_core.utils.base import BaseDict
from slime_core.utils.typing import (
    Any,
    NOTHING
)
import sys


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

class set_core_logger:
    
    def __init__(self) -> None:
        pass

#
# Logger Func Arg Adapter
#

class LoggerKwargs(BaseDict[str, Any]):
    
    def __init__(self, **kwargs):
        # ``stacklevel`` argument was added after py3.8
        if sys.version_info < (3, 8):
            kwargs.pop('stacklevel', NOTHING)
        super().__init__(**kwargs)
