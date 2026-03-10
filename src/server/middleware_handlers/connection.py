from loguru import logger
import time
from requests.exceptions import ConnectionError
from server.middleware_handlers.algorithms import sync_available_algorithms
from server.middleware_handlers.functions import sync_available_functions
from server.middleware_handlers.models import sync_trained_models
from server.middleware_handlers import middleware
from server.state import AppState

MAX_RETRIES = 10
appstate = AppState()


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
        sync_available_algorithms(appstate)
        sync_trained_models(appstate)
        sync_available_functions(appstate)
    except ConnectionError:
        time.sleep(2**tries)
        return middleware_connect(tries + 1)
    appstate.toggle_middleware_on()
    logger.info("Middleware connection successful")
    return None
