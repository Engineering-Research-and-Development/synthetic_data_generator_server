from pathlib import Path
import minio
from loguru import logger
from minio.error import MinioException

from server.file_utils import TRAINED_MODELS, MODEL_PAYLOAD_NAME, delete_local_folder
from server.storage_handlers import (
    GARAGE_URL,
    GARAGE_USERNAME,
    GARAGE_PASSWORD,
    GARAGE_MODEL_BUCKET,
)


def get_client():
    return minio.Minio(
        endpoint=GARAGE_URL,
        access_key=GARAGE_USERNAME,
        secret_key=GARAGE_PASSWORD,
        region="garage",
    )


def check_garage_connection() -> bool:
    client = get_client()
    try:
        found = client.bucket_exists(bucket_name=GARAGE_MODEL_BUCKET)
        if not found:
            logger.info(
                f"Connection established but bucket not found. Trying creation of a new bucket: {GARAGE_MODEL_BUCKET}"
            )
            client.make_bucket(GARAGE_MODEL_BUCKET, location="garage")
        logger.info("Garage instance found, Syncing models")
        sync_available_models()
        return True
    except Exception as e:
        logger.info(f"Cannot connect to Garage Instance: {e}")
        return False


def sync_available_models():
    client = get_client()
    local_root = TRAINED_MODELS

    found = client.bucket_exists(bucket_name=GARAGE_MODEL_BUCKET)
    if not found:
        logger.error(
            f"Model Bucket: {GARAGE_MODEL_BUCKET} not found. Model info cannot be downloaded"
        )
        return
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

        try:
            client.fget_object(GARAGE_MODEL_BUCKET, obj.object_name, str(local_path))
        except MinioException:
            logger.error(
                f"An error occurred while downloading the model payload of: {model_name}, rollback"
            )
            delete_local_folder(local_path)

        written.append(str(local_path))
        logger.info(f"Downloaded: {obj.object_name}  →  {local_path}")

    logger.info(f"✓ {len(written)} model(s) found'")


def get_model_from_garage_if_exists(model_full_path: str):
    model_full_path = Path(model_full_path)
    client = get_client()
    prefix = str(model_full_path).rstrip("/").split("/")[-1] + "/"
    local_root = TRAINED_MODELS

    found = client.bucket_exists(bucket_name=GARAGE_MODEL_BUCKET)
    if not found:
        logger.error(
            f"Model Bucket: {GARAGE_MODEL_BUCKET} not found. Models cannot be downloaded"
        )
        return

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
        try:
            client.fget_object(GARAGE_MODEL_BUCKET, obj.object_name, str(local_path))
        except MinioException:
            logger.error(
                f"An error occurred while downloading the model in: {model_full_path}, rollback"
            )
            delete_local_folder(model_full_path)
        written.append(str(local_path))

    logger.info(f"\n✓ {len(written)} file(s) downloaded to '{model_full_path}'")


def copy_model_to_garage(model_full_path: str, remove_after_upload=True):
    model_full_path = Path(model_full_path)
    if not model_full_path.exists():
        raise ValueError(f"Local path '{model_full_path}' does not exist.")
    if not model_full_path.is_dir():
        raise ValueError(f"'{model_full_path}' is not a directory.")

    client = get_client()
    prefix = str(model_full_path).rstrip("/").split("/")[-1] + "/"

    # Ensure the bucket exists
    if not client.bucket_exists(GARAGE_MODEL_BUCKET):
        client.make_bucket(GARAGE_MODEL_BUCKET)
        logger.info(f"Created bucket '{GARAGE_MODEL_BUCKET}'")

    uploaded: list[str] = []

    for local_path in sorted(model_full_path.rglob("*")):
        if not local_path.is_file():
            continue

        relative_path = local_path.relative_to(model_full_path)
        object_name = prefix + relative_path.as_posix()  # MinIO uses forward slashes

        try:
            client.fput_object(GARAGE_MODEL_BUCKET, object_name, str(local_path))
        except MinioException:
            logger.error(f"An error Occurred while uploading {prefix} model. Rollback")
            delete_local_folder(model_full_path)
            return
        uploaded.append(object_name)

    logger.info(
        f"{len(uploaded)} file(s) uploaded to MinIO: {model_full_path}  →  {GARAGE_MODEL_BUCKET}/{prefix}"
    )
    if remove_after_upload:
        delete_local_folder(model_full_path)
    return
