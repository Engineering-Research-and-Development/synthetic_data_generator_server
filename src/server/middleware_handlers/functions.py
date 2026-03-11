import requests
from loguru import logger

from sdg_core_lib.browser import browse_functions
from server.middleware_handlers import middleware
from server.state import AppState


def sync_available_functions(appstate: AppState):
    """
    Syncs the available functions from the middleware to the local server.
    """
    response = requests.get(f"{middleware}functions/")

    for remote_function in response.json():
        if (
            remote_function.get("function").get("function_reference")
            not in appstate.GENERATOR_FUNCTION_NAMES
        ):
            requests.delete(url=f"{middleware}functions/{remote_function.get('id')}")

    for function in browse_functions():
        response = requests.post(url=f"{middleware}functions/", json=function)

        if not response.status_code == 201:
            logger.error(f"Error syncing functions: {response.text}")

    logger.info("Function sync completed")
