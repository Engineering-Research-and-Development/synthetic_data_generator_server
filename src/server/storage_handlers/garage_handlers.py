import shutil
from pathlib import Path
import minio
from loguru import logger
from minio.error import MinioException

from server.storage_handlers import GARAGE_HOST, GARAGE_USERNAME, GARAGE_PASSWORD, GARAGE_MODEL_BUCKET


def get_client():
    return minio.Minio(
        endpoint=GARAGE_HOST,
        access_key=GARAGE_USERNAME,
        secret_key=GARAGE_PASSWORD,
        region="garage"
    )


def get_model_if_exists(path: Path):
    client = get_client()
    prefix = str(path).rstrip("/") + "/"

    found = client.bucket_exists(bucket_name=GARAGE_MODEL_BUCKET)
    if not found:
        logger.error(f"Model Bucket: {GARAGE_MODEL_BUCKET} not found. Models cannot be downloaded")
        return

    objects = list(client.list_objects(GARAGE_MODEL_BUCKET, prefix=prefix, recursive=True))
    if not objects:
        raise ValueError(
            f"No objects found in bucket '{GARAGE_MODEL_BUCKET}' under prefix '{prefix}'"
        )

    written: list[str] = []
    for obj in objects:
        # Strip the prefix to get a relative path, then join with dest_root
        relative_path = obj.object_name[len(prefix):]
        local_path = path / relative_path

        # Create parent directories as needed
        local_path.parent.mkdir(parents=True, exist_ok=True)

        try :
            client.fget_object(GARAGE_MODEL_BUCKET, obj.object_name, str(local_path))
        except MinioException:
            logger.error(f"An error occurred while downloading the model in: {path}, rollback")
            shutil.rmtree(path)

        written.append(str(local_path))
        print(f"Downloaded: {obj.object_name}  →  {local_path}")

    logger.info(f"\n✓ {len(written)} file(s) copied to '{path}'")



def copy_folder_to_minio(path: Path):

    if not path.exists():
        raise ValueError(f"Local path '{path}' does not exist.")
    if not path.is_dir():
        raise ValueError(f"'{path}' is not a directory.")

    client = get_client()
    prefix = str(path).rstrip("/") + "/"

    # Ensure the bucket exists
    if not client.bucket_exists(GARAGE_MODEL_BUCKET):
        client.make_bucket(GARAGE_MODEL_BUCKET)
        logger.info(f"Created bucket '{GARAGE_MODEL_BUCKET}'")

    uploaded: list[str] = []

    for local_path in sorted(path.rglob("*")):
        if not local_path.is_file():
            continue

        relative_path = local_path.relative_to(path)
        object_name = prefix + relative_path.as_posix()  # MinIO uses forward slashes

        client.fput_object(GARAGE_MODEL_BUCKET, object_name, str(local_path))
        uploaded.append(object_name)
        logger.info(f"Model Uploaded to MinIO: {local_path}  →  {object_name}")

    print(f"\n✓ {len(uploaded)} file(s) uploaded to '{GARAGE_MODEL_BUCKET}/{prefix}'")
    return uploaded