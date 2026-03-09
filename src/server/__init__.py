from typing import Literal
from enum import Enum

class StorageType(Enum):
    LOCAL = "Local"
    GARAGE = "GARAGE"

GENERATOR_ALGORITHM_NAMES = []
ALGORITHM_LONG_NAME_TO_ID = {}
ALGORITHM_LONG_TO_SHORT = {}
ALGORITHM_SHORT_TO_LONG = {}
GENERATOR_FUNCTION_NAMES = []
MIDDLEWARE_ON = False
STORAGE_TYPE = StorageType.LOCAL
