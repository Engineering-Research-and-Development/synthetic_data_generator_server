from loguru import logger

from ai_lib.job import job
from server.couch_handlers import add_couch_data
from server.file_utils import (
    check_latest_version,
    create_folder,
    delete_folder,
    save_model_payload,
    check_folder,
)
from server.middleware_handlers.connection import (
    GENERATOR_ALGORITHM_NAMES,
    ALGORITHM_SHORT_TO_LONG,
    ALGORITHM_LONG_NAME_TO_ID,
    middleware,
    MIDDLEWARE_ON,
)
from server.middleware_handlers.models import model_to_middleware
from server.utilities import trim_name
from server.validation_schema import TrainRequest, InferRequest


def execute_train(request: TrainRequest, couch_doc: str):
    request = request.model_dump()
    logger.info("Starting Train Request")
    request["model"]["algorithm_name"] = ALGORITHM_SHORT_TO_LONG[
        request["model"]["algorithm_name"]
    ]
    # Check if the algorithm is implemented by the generator
    if request["model"]["algorithm_name"] not in GENERATOR_ALGORITHM_NAMES:
        logger.error("Error finding algorithm locally")
        add_couch_data(
            couch_doc,
            new_data={"error": "This algorithm does not exist locally"},
        )
        return

    # Here we calculate the unique name of the folder
    model_folder_name = f"{request['model']['model_name']}-{trim_name(request['model']['algorithm_name'])}"
    new_version_name = f"v{check_latest_version(model_folder_name) + 1}"
    folder_id = f"{model_folder_name}-{new_version_name}"

    folder_path = create_folder(folder_id)
    try:
        results, metrics, model, data = job(
            model_info=request["model"],
            dataset=request["dataset"],
            n_rows=request["n_rows"],
            save_filepath=folder_path,
            train=True,
        )
    except (ValueError, TypeError) as e:
        delete_folder(folder_path)
        logger.error(f"Error training model: {e}")
        add_couch_data(couch_doc, new_data={"error": e.args[0]})
        return

    # We invoke the model registry saving the model, if failing delete trained model
    try:
        model_payload = model_to_middleware(
            model,
            data,
            "dataset_name",
            str(folder_path),
            new_version_name,
            middleware=middleware,
            algorithm_long_name_to_id=ALGORITHM_LONG_NAME_TO_ID,
            middleware_on=MIDDLEWARE_ON,
        )
        save_model_payload(folder_path, model_payload)
    except KeyError as e:
        logger.error(f"Error training model: {e}")
        delete_folder(folder_path)
        add_couch_data(couch_doc, new_data={"error": e.args[0]})
        return

    add_couch_data(
        couch_doc,
        new_data={
            "results": results,
            "metrics": metrics,
        },
    )
    logger.info("Training Job completed successfully")


def execute_infer(request: InferRequest, couch_doc: str):
    request = request.model_dump()
    logger.info("Starting Infer Request")
    request["model"]["algorithm_name"] = ALGORITHM_SHORT_TO_LONG[
        request["model"]["algorithm_name"]
    ]
    if not check_folder(request["model"]["image"]):
        logger.error("Error finding trained model model")
        add_couch_data(
            couch_doc,
            new_data={"error": "This model has not been found!"},
        )
        return

    try:
        results, metrics, model, data = job(
            model_info=request["model"],
            dataset=request["dataset"],
            n_rows=request["n_rows"],
            save_filepath="",
            train=False,
        )
    except (ValueError, TypeError) as e:
        logger.error(f"Error while making inference: {e}")
        add_couch_data(couch_doc, new_data={"error": e.args[0]})
        return

    add_couch_data(doc_id=couch_doc, new_data={"results": results, "metrics": metrics})
    logger.info("Infer Job completed successfully")
