"""
Archived APIs and features.
These APIs and features will no longer be maintained and will be removed in any 
version without notice. They are temporarily kept in this package because they 
may show some design concepts or code insights, which may be used for reference 
in future development.
"""
from slime_core.logging.logger import core_logger

core_logger.warning(
    'The APIs and features in ``slime_core._archived`` have been deprecated, '
    'which means you may never access this package. Check your code and remove '
    'the corresponding parts.'
)
