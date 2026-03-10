import shutil

from loguru import logger
from minio.error import MinioException

from sdg_core_lib.job import Job

import server
from server.storage_handlers.couch import add_couch_data
from server.file_utils import (
    check_latest_version,
    create_folder,
    delete_folder,
    save_model_payload,
    check_folder,
)
from server.middleware_handlers.connection import (
    is_middleware_on,
)
from server import (
    GENERATOR_ALGORITHM_NAMES,
    ALGORITHM_LONG_NAME_TO_ID,
    ALGORITHM_SHORT_TO_LONG,
    StorageType,
)
from server.middleware_handlers.models import model_to_middleware
from server.storage_handlers.garage import (
    copy_model_to_garage,
    get_model_from_garage_if_exists,
)
from server.utilities import trim_name
from server.validation_schema import TrainRequest, InferRequest, GenerationRequest


def save_external_storage(model_path: str):
    if server.STORAGE_TYPE == StorageType.GARAGE:
        copy_model_to_garage(model_path)


def load_from_external_storage(model_path: str):
    if server.STORAGE_TYPE == StorageType.GARAGE:
        get_model_from_garage_if_exists(model_path)


# TODO: Implement this in middleware and delete from here
def _detect_dataset_type(dataset: list[dict], model: dict) -> str:
    if len(dataset) == 0:
        dataset = model.get("training_data_info")
    col_types = [col["column_type"] for col in dataset]
    if "group_index" in col_types:
        return "time_series"
    return "table"


# TODO: Implement this in middleware and delete from here
def get_full_dataset(dataset: list[dict], model: dict) -> dict:
    return {"data": dataset, "dataset_type": _detect_dataset_type(dataset, model)}


def execute_train(request: TrainRequest, couch_doc: str):
    request = request.model_dump()
    logger.info("Starting Train Request")
    logger.info(request)
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
        results, metrics, model, data = Job(
            model_info=request["model"],
            dataset=get_full_dataset(request["dataset"], request["model"]),
            n_rows=request["n_rows"],
            save_filepath=folder_path,
        ).train()
    except (ValueError, TypeError, AttributeError, KeyError) as e:
        delete_folder(folder_path)
        logger.error(f"Error training model: {e}")
        add_couch_data(couch_doc, new_data={"error": e.args[0]})
        return

    # We invoke the model registry saving the model, if failing delete trained model
    try:
        if is_middleware_on():
            model_payload = model_to_middleware(
                model,
                data,
                "dataset_name",
                str(folder_path),
                new_version_name,
                algorithm_long_name_to_id=ALGORITHM_LONG_NAME_TO_ID,
            )
            save_model_payload(folder_path, model_payload)
            save_external_storage(folder_path)
        else:
            error_message = "Middleware connection failed while saving trained model"
            logger.error(error_message)
            delete_folder(folder_path)
            add_couch_data(couch_doc, new_data={"error": error_message})
            return
    except (MinioException, ValueError, KeyError) as e:
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
    logger.info(request)
    request["model"]["algorithm_name"] = ALGORITHM_SHORT_TO_LONG[
        request["model"]["algorithm_name"]
    ]
    model_path = request["model"]["image"]
    load_from_external_storage(model_path)
    if not check_folder(model_path):
        logger.error("Error finding trained model model")
        add_couch_data(
            couch_doc,
            new_data={"error": "This model has not been found!"},
        )
        return

    try:
        results, metrics = Job(
            model_info=request["model"],
            dataset=get_full_dataset(request["dataset"], request["model"]),
            n_rows=request["n_rows"],
            save_filepath=model_path,
        ).infer()
    except (ValueError, TypeError, AttributeError, KeyError) as e:
        logger.error(f"Error while making inference: {e}")
        add_couch_data(couch_doc, new_data={"error": e.args[0]})
        return

    if server.STORAGE_TYPE != StorageType.LOCAL:
        shutil.rmtree(model_path)
    add_couch_data(doc_id=couch_doc, new_data={"results": results, "metrics": metrics})
    logger.info("Infer Job completed successfully")


def execute_scratch_generation(request: GenerationRequest, couch_doc: str):
    request = request.model_dump()
    logger.info("Starting Generation from Scratch")
    logger.info(request)

    try:
        results = Job(
            functions=request["functions"],
            n_rows=request["n_rows"],
        ).generate_from_functions()
    except (ValueError, TypeError, AttributeError, KeyError) as e:
        logger.error(f"Error while making generation from scratch: {e}")
        add_couch_data(couch_doc, new_data={"error": e.args[0]})
        return

    add_couch_data(
        doc_id=couch_doc, new_data={"results": results, "metrics": {"Not Available"}}
    )
    logger.info("Generation Job completed successfully")
