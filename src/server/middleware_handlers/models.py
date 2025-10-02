import json

import requests
from loguru import logger

from ai_lib.NumericDataset import NumericDataset
from ai_lib.data_generator.models.UnspecializedModel import UnspecializedModel
from server.file_utils import (
    list_trained_models,
    retrieve_model_payload,
    save_model_payload,
    get_folder_full_path,
    delete_folder,
)


def model_to_middleware(
    model: UnspecializedModel,
    data: NumericDataset,
    dataset_name: str,
    save_path: str,
    version_name: str,
    middleware: str,
    middleware_on: bool,
    algorithm_long_name_to_id: dict,
) -> str:
    """
    Pushes a trained model to the middleware.

    This function logs the process of pushing a trained model to the middleware.
    It gathers necessary information from the model and dataset, such as feature list
    and training information, and constructs a payload to send to the middleware.
    The payload includes model metadata, version information, and datatype details.
    The function ultimately posts the model to the middleware for storage and returns
    the response body of the POST request.

    :param middleware:
    :param middleware_on:
    :param algorithm_long_name_to_id:
    :param model: The trained model to be pushed
    :param data: The dataset used for training the model
    :param dataset_name: The name of the dataset
    :param save_path: The path where the model is saved
    :param version_name: The version name of the model
    :return: The response body of the POST request
    """

    feature_list = data.parse_data_to_registry()
    training_info = model.training_info.to_dict()
    version_info = {
        "version_name": version_name,
        "image_path": save_path,
    }
    # Getting the algorithm id
    algorithm_id = algorithm_long_name_to_id.get(
        model.self_describe().get("algorithm").get("name")
    )
    trained_model_misc = {
        "name": model.model_name,
        "dataset_name": dataset_name,
        "size": model.self_describe().get("size", "Not Available"),
        "input_shape": str(model.input_shape).replace(" ", ""),
        "algorithm": algorithm_id,
        "algorithm_long_name": model.self_describe().get("algorithm").get("name"),
    }
    version_info.update(training_info)
    model_to_save = {
        "model": trained_model_misc,
        "version": version_info,
        "datatypes": feature_list,
    }
    return post_model_to_middleware(
        model_to_save, middleware=middleware, middleware_on=middleware_on
    )


def post_model_to_middleware(model_to_save: dict, middleware: str, middleware_on: bool):
    """
    Posts a trained model to the middleware

    :param middleware:
    :param middleware_on:
    :param model_to_save: The model to be saved
    :return: The body of the POST request
    """

    headers = {"Content-Type": "application/json"}
    body = json.dumps(model_to_save)
    if middleware_on:
        logger.info(f"Pushing {model_to_save.get('model').get('name')} middleware")
        response = requests.post(
            f"{middleware}trained_models/", headers=headers, data=body
        )
        if response.status_code != 201:
            logger.error(
                f"Something went wrong in saving the model, rollback to latest version\n {response.content}"
            )
        else:
            logger.info("Model pushed successfully")

    return body


def sync_trained_models(
    middleware: str, algorithm_long_name_to_id: dict, middleware_on: bool
):
    """
    Syncs the trained models from the middleware to the local server.
    First check remote trained model with their versions. If models and versions are not available,
    delete locally
    Then check for local models. If a local payload is stored, post to middleware.
    Moreover, double checks for algorithm id. If not found, updates with current algorithm id in middleware
    Finally, if a local payload is not found, delete the folder
    """
    logger.info("Syncing trained models")
    remote_trained_models = requests.get(f"{middleware}trained_models/").json()[
        "models"
    ]
    local_trained_models = list_trained_models()  # Image Paths

    for remote_trained_model in remote_trained_models:
        model_id = remote_trained_model["model"]["id"]
        model_payload = requests.get(f"{middleware}trained_models/{model_id}").json()
        for version in model_payload["versions"]:
            version_trimmed_name = version["image_path"].split("/")[-1]
            if version_trimmed_name not in local_trained_models:
                requests.delete(
                    f"{middleware}trained_models/{model_id}/?version_id={version['id']}"
                )
                logger.info(f"Deleted {model_id} from remote server")
            else:
                local_trained_models.remove(version_trimmed_name)

    for local_trained_model in local_trained_models:
        try:
            local_payload_filepath = retrieve_model_payload(local_trained_model)
            with open(local_payload_filepath, "r") as f:
                model_payload = json.load(f)
                if not model_payload.get("model").get("algorithm"):
                    algo_long_name = model_payload.get("model").get(
                        "algorithm_long_name"
                    )
                    model_payload["model"]["algorithm"] = algorithm_long_name_to_id.get(
                        algo_long_name
                    )
                    save_model_payload(
                        get_folder_full_path(local_trained_model), model_payload
                    )
                post_model_to_middleware(
                    model_payload, middleware=middleware, middleware_on=middleware_on
                )
        except FileNotFoundError:
            logger.error("Local Payload not found, deleting folder")
            delete_folder(get_folder_full_path(local_trained_model))

    logger.info("Sync completed")
