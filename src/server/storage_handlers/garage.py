import time
from pathlib import Path
import minio
from loguru import logger
from minio.error import MinioException
from urllib3.exceptions import NewConnectionError

from server.file_utils import (
    TRAINED_MODELS,
    MODEL_PAYLOAD_NAME,
    delete_local_folder,
    list_trained_models,
)
from server.storage_handlers import (
    GARAGE_URL,
    GARAGE_USERNAME,
    GARAGE_PASSWORD,
    GARAGE_MODEL_BUCKET,
)

MAX_REMOVE_TRIES = 3
client = minio.Minio(
    endpoint=GARAGE_URL,
    access_key=GARAGE_USERNAME,
    secret_key=GARAGE_PASSWORD,
    region="garage",
)


def remote_storage_connect_and_sync() -> bool:
    if GARAGE_URL is None:
        return False

    if bucket_exists():
        try:
            get_available_models()
            return True
        except MinioException as e:
            logger.info(f"Cannot connect to Garage Instance: {e}")
            for local_residue in list_trained_models():
                delete_local_folder(TRAINED_MODELS / local_residue)
            return False
    return False


def bucket_exists() -> bool:
    try:
        found = client.bucket_exists(bucket_name=GARAGE_MODEL_BUCKET)
        if not found:
            logger.error(
                f"Model Bucket: {GARAGE_MODEL_BUCKET} not found, cannot perform read/write operation on Garage"
            )
            return False
        return True
    except NewConnectionError as e:
        logger.error(f"Cannot connect to Garage Instance: {e}")
        return False


def get_available_models():
    local_root = TRAINED_MODELS

    logger.info("Garage instance found, Syncing models")
    objects = list(client.list_objects(GARAGE_MODEL_BUCKET, recursive=True))
    if not objects:
        logger.info("No models found on remote server")
        return

    written: list[str] = []
    for obj in objects:
        if MODEL_PAYLOAD_NAME not in obj.object_name:
            continue

        model_name = obj.object_name.lstrip("/")
        local_path = local_root / model_name
        local_path.parent.mkdir(parents=True, exist_ok=True)
        client.fget_object(GARAGE_MODEL_BUCKET, obj.object_name, str(local_path))
        written.append(str(local_path))
        logger.info(f"Downloaded: {obj.object_name}  →  {local_path}")

    logger.info(f"✓ {len(written)} model(s) found'")


def get_model_from_remote(model_full_path: str):
    model_full_path = Path(model_full_path)
    prefix = str(model_full_path).rstrip("/").split("/")[-1] + "/"
    local_root = TRAINED_MODELS

    objects = list(
        client.list_objects(GARAGE_MODEL_BUCKET, prefix=prefix, recursive=True)
    )
    if not objects:
        raise ValueError(
            f"No objects found in bucket '{GARAGE_MODEL_BUCKET}' under prefix '{prefix}'"
        )

    written: list[str] = []
    for obj in objects:
        relative_path = obj.object_name[len(prefix) :]
        local_path = local_root / prefix / relative_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        client.fget_object(GARAGE_MODEL_BUCKET, obj.object_name, str(local_path))
        written.append(str(local_path))

    logger.info(f"\n✓ {len(written)} file(s) downloaded to '{model_full_path}'")


def copy_model_to_remote(model_full_path: str):
    model_full_path = Path(model_full_path)
    if not model_full_path.exists():
        raise ValueError(f"Local path '{model_full_path}' does not exist.")
    if not model_full_path.is_dir():
        raise ValueError(f"'{model_full_path}' is not a directory.")

    prefix = str(model_full_path).rstrip("/").split("/")[-1] + "/"
    uploaded: list[str] = []

    for local_path in sorted(model_full_path.rglob("*")):
        if not local_path.is_file():
            continue

        relative_path = local_path.relative_to(model_full_path)
        object_name = prefix + relative_path.as_posix()  # MinIO uses forward slashes
        client.fput_object(GARAGE_MODEL_BUCKET, object_name, str(local_path))
        uploaded.append(object_name)

    logger.info(
        f"{len(uploaded)} file(s) uploaded to MinIO: {model_full_path}  →  {GARAGE_MODEL_BUCKET}/{prefix}"
    )
    return


def remove_remote_model(model_full_path: str, max_tries=MAX_REMOVE_TRIES):
    model_full_path = Path(model_full_path)
    prefix = str(model_full_path).rstrip("/").split("/")[-1] + "/"
    if max_tries == 0:
        raise MinioException(
            f"After {MAX_REMOVE_TRIES} times the remote model under {prefix} was not removed"
        )

    objects = list(
        client.list_objects(GARAGE_MODEL_BUCKET, prefix=prefix, recursive=True)
    )
    if not objects:
        logger.info(f"No objects found under {prefix}")
        return

    deleted: list[str] = []
    for obj in objects:
        try:
            client.remove_object(GARAGE_MODEL_BUCKET, obj.object_name)
        except MinioException:
            logger.error(
                f"An error occurred while downloading the model in: {model_full_path}, retrying"
            )
            time.sleep(3)
            remove_remote_model(str(model_full_path), max_tries - 1)
        deleted.append(obj.object_name)
    logger.info(f"All objects in {prefix} are successfully removed")
    return
