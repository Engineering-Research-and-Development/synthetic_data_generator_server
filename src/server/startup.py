import threading

from loguru import logger
from sdg_core_lib.browser import browse_algorithms, browse_functions

import server
from server.file_utils import create_server_repo_folder_structure
from server.middleware_handlers.connection import middleware_connect
from server import GENERATOR_ALGORITHM_NAMES, ALGORITHM_LONG_TO_SHORT, ALGORITHM_SHORT_TO_LONG, \
    GENERATOR_FUNCTION_NAMES, StorageType
from server.storage_handlers.garage import check_garage_connection

def try_sync_external():
    if check_garage_connection():
        server.STORAGE_TYPE = StorageType.GARAGE


def server_startup():
    """
    Called at server startup to initialize the server.
    It creates a folder structure for saving models on the server and
    syncs the available algorithms from the middleware to the local server.
    """
    try_sync_external()
    logger.info("Server startup")
    create_server_repo_folder_structure()
    [
        GENERATOR_ALGORITHM_NAMES.append(algorithm["algorithm"]["name"])
        for algorithm in browse_algorithms()
    ]
    for algorithm in GENERATOR_ALGORITHM_NAMES:
        ALGORITHM_LONG_TO_SHORT[algorithm] = algorithm.split(".")[-1]
        ALGORITHM_SHORT_TO_LONG[ALGORITHM_LONG_TO_SHORT[algorithm]] = algorithm

    [
        GENERATOR_FUNCTION_NAMES.append(function["function"]["function_reference"])
        for function in browse_functions()
    ]

    logger.info("Starting connection procedure to middleware")
    reconnection_thread = threading.Thread(target=middleware_connect)
    reconnection_thread.start()
    logger.info("Server startup completed")
