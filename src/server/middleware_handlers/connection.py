from loguru import logger
import time
from requests.exceptions import ConnectionError
from server.middleware_handlers.algorithms import sync_available_algorithms
from server.middleware_handlers.functions import sync_available_functions
from server.middleware_handlers.models import sync_trained_models
from server.middleware_handlers import middleware

MIDDLEWARE_ON = False
MAX_RETRIES = 10
GENERATOR_ALGORITHM_NAMES = []
ALGORITHM_LONG_NAME_TO_ID = {}
ALGORITHM_LONG_TO_SHORT = {}
ALGORITHM_SHORT_TO_LONG = {}
GENERATOR_FUNCTION_NAMES = []


def middleware_connect(tries: int = 1) -> None:
    if tries >= MAX_RETRIES:
        logger.error(
            f"{tries} connection attempts failed, restart to try new connections"
        )
        return None
    if not middleware:
        logger.error("Middleware not available, running in isolated environment")
        return None
    try:
        logger.info(f"Connection attempt n.{tries}")
        sync_available_algorithms(
            algorithm_short_to_long=ALGORITHM_SHORT_TO_LONG,
            algorithm_long_to_short=ALGORITHM_LONG_TO_SHORT,
            algorithm_long_name_to_id=ALGORITHM_LONG_NAME_TO_ID,
        )
        sync_trained_models(
            algorithm_long_name_to_id=ALGORITHM_LONG_NAME_TO_ID,
        )
        sync_available_functions(
            list_function_names=GENERATOR_FUNCTION_NAMES,
        )
    except ConnectionError:
        time.sleep(2**tries)
        return middleware_connect(tries + 1)
    global MIDDLEWARE_ON
    MIDDLEWARE_ON = True
    logger.info("Middleware connection successful")
    return None


def is_middleware_on():
    return MIDDLEWARE_ON
