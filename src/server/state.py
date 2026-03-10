import threading
from enum import Enum


class StorageType(Enum):
    LOCAL = "Local"
    GARAGE = "GARAGE"


class AppState:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.GENERATOR_ALGORITHM_NAMES = []
        self.ALGORITHM_LONG_NAME_TO_ID = {}
        self.ALGORITHM_LONG_TO_SHORT = {}
        self.ALGORITHM_SHORT_TO_LONG = {}
        self.GENERATOR_FUNCTION_NAMES = []
        self.middleware_on = False
        self.storage_type = StorageType.LOCAL
        self._initialized = True

    def _add_algorithm_short_long_pair(self, long_name: str, short_name: str):
        self.ALGORITHM_LONG_TO_SHORT[long_name] = short_name
        self.ALGORITHM_SHORT_TO_LONG[short_name] = long_name

    def add_algorithm_name(self, algorithm_full_name: str):
        self.GENERATOR_ALGORITHM_NAMES.append(algorithm_full_name)
        short_name = algorithm_full_name.split(".")[-1]
        self._add_algorithm_short_long_pair(algorithm_full_name, short_name)

    def add_algorithm_name_id_mapping(
        self, algorithm_full_name: str, algorithm_id: int
    ):
        self.ALGORITHM_LONG_NAME_TO_ID[algorithm_full_name] = algorithm_id

    def add_function_name(self, function_full_name: str):
        self.GENERATOR_FUNCTION_NAMES.append(function_full_name)

    def toggle_middleware_on(self):
        self.middleware_on = True

    def toggle_middleware_off(self):
        self.middleware_on = False

    def set_storage_type(self, storage_type: StorageType):
        self.storage_type = storage_type

    def reset(self):
        self._initialized = False
        self.__init__()
