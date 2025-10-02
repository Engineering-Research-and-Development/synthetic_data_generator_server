import requests
from loguru import logger

from ai_lib.browser import browse_algorithms


def sync_available_algorithms(
    middleware: str,
    algorithm_short_to_long: dict,
    algorithm_long_to_short: dict,
    algorithm_long_name_to_id: dict,
):
    """
    Syncs the available algorithms from the middleware to the local server.
    """
    response = requests.get(f"{middleware}algorithms/")

    for remote_algo in response.json().get("algorithms", []):
        if remote_algo.get("name") not in algorithm_short_to_long.keys():
            requests.delete(url=f"{middleware}algorithms/{remote_algo.get('id')}")

    for algorithm in browse_algorithms():
        long_name = algorithm["algorithm"]["name"]
        algorithm["algorithm"]["name"] = algorithm_long_to_short[long_name]
        response = requests.post(url=f"{middleware}algorithms/", json=algorithm)

        if not response.status_code == 201:
            logger.error(f"Error syncing algorithm: {response.text}")
        else:
            algo_id = response.json().get("id")
            algorithm_long_name_to_id[long_name] = algo_id

    logger.info("Algorithm sync completed")
