import threading

from loguru import logger
from sdg_core_lib.browser import browse_algorithms, browse_functions

from server.file_utils import create_server_repo_folder_structure
from server.middleware_handlers.connection import middleware_connect
from server.state import AppState, StorageType
from server.storage_handlers.garage import check_garage_connection

appstate = AppState()

def server_startup():
    """
    Called at server startup to initialize the server.
    It creates a folder structure for saving models on the server and
    syncs the available algorithms from the middleware to the local server.
    """
    if check_garage_connection():
        appstate.set_storage_type(StorageType.GARAGE)

    logger.info("Server startup")
    create_server_repo_folder_structure()
    [
        appstate.add_algorithm_name(algorithm["algorithm"]["name"])
        for algorithm in browse_algorithms()
    ]

    [
        appstate.add_function_name(function["function"]["function_reference"])
        for function in browse_functions()
    ]

    logger.info("Starting connection procedure to middleware")
    reconnection_thread = threading.Thread(target=middleware_connect)
    reconnection_thread.start()
    logger.info("Server startup completed")
