"""
This module provides version compatibility for the native Python ``typing`` 
module and defines extensions of types, constants, introspection utilities, etc.
"""

# BACKWARD: For backward compatibility, we import native and extension module here. 
# However, import typings directly from ``slime_core.utils.typing`` is no longer 
# encouraged, because the following imports will be removed starting from any 
# future version if there exist naming conflicts between the two modules. Instead, 
# import the corresponding typings from ``slime_core.utils.typing.native`` and 
# ``slime_core.utils.typing.extension``.
from .native import *
from .extension import *
