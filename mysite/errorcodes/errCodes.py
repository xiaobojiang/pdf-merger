from enum import Enum, unique


@unique
class errCodes(Enum):
    OK_CODE_BASE = 0    
    ERROR_CODE_BASE = 1000
    ERROR_METHOD_NOT_ALLOWED = (ERROR_CODE_BASE+1)
    ERROR_CONTENT_EMPTY = (ERROR_CODE_BASE+2)
    ERROR_INTERNAL = (ERROR_CODE_BASE+3)
    
    