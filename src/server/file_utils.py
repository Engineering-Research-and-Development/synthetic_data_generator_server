import os
import shutil
from pathlib import Path

APP_FOLDER = os.path.dirname(os.path.abspath(__file__))
TRAINED_MODELS = Path(APP_FOLDER) / "saved_models" / "trained_models"
MODEL_PAYLOAD_NAME = "model_payload.json"


def create_server_repo_folder_structure() -> None:
    """
    Creates a folder structure for saving models on the server.

    The structure includes:
    - saved_models/
      - trained_models/
    """
    TRAINED_MODELS.mkdir(parents=True, exist_ok=True)


def get_folder_full_path(folder_name: str):
    return TRAINED_MODELS / folder_name


def create_folder(folder_id: str):
    folder_path = get_folder_full_path(folder_id)
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path


def delete_folder(folder_path: Path | str):
    if type(folder_path) is str:
        folder_path = Path(folder_path)
    shutil.rmtree(folder_path)


def check_folder(folder_path: Path | str):
    if type(folder_path) is str:
        folder_path = Path(folder_path)
    return folder_path.exists()


def check_latest_version(model_dir: Path | str):
    version = 0
    try:
        versions = [
            int(path.split("-")[-1].split("v")[-1])
            for path in os.listdir(TRAINED_MODELS)
            if model_dir in path
        ]
        version = max(versions)
    except ValueError:
        pass
    return version


def list_trained_models():
    return os.listdir(TRAINED_MODELS)


def save_model_payload(folder_path: Path, model_payload: str):
    with open(folder_path / MODEL_PAYLOAD_NAME, "w") as f:
        f.write(model_payload)


def retrieve_model_payload(base_path: Path | str) -> Path:
    if type(base_path) is str:
        base_path = Path(base_path)
    return TRAINED_MODELS / base_path / MODEL_PAYLOAD_NAME
