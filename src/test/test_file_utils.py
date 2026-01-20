from server.file_utils import (
    create_folder,
    delete_folder,
    check_folder,
    save_model_payload,
    retrieve_model_payload,
    list_trained_models,
    create_server_repo_folder_structure,
    TRAINED_MODELS,
    get_folder_full_path,
    check_latest_version,
)


def test_get_path():
    test_name = "Test"
    full_path = get_folder_full_path(test_name)
    assert full_path == TRAINED_MODELS / test_name


def test_create_server_repo_folder_structure():
    _ = TRAINED_MODELS / "saved_models" / "trained_models"
    create_server_repo_folder_structure()
    assert TRAINED_MODELS.exists() and TRAINED_MODELS.is_dir()


def test_create_folder():
    folder_id = "test_folder"
    folder_path = create_folder(folder_id)
    assert folder_path.exists() and folder_path.is_dir()


def test_check_folder():
    folder_path = TRAINED_MODELS / "test_folder"
    folder_path.mkdir(exist_ok=True)
    assert check_folder(folder_path)
    delete_folder(folder_path)
    assert not check_folder(folder_path)


def test_save_model_payload():
    folder_path = TRAINED_MODELS / "test_folder"
    folder_path.mkdir(exist_ok=True)
    model_payload = '{"key": "value"}'
    save_model_payload(folder_path, model_payload)
    payload_path = folder_path / "model_payload.json"
    assert payload_path.exists()
    with open(payload_path, "r") as f:
        assert f.read() == model_payload


def test_retrieve_model_payload():
    folder_path = TRAINED_MODELS / "test_folder"
    folder_path.mkdir(exist_ok=True)
    payload_path = folder_path / "model_payload.json"
    with open(payload_path, "w") as f:
        f.write('{"key": "value"}')
    retrieved_path = retrieve_model_payload(folder_path)
    assert retrieved_path == payload_path


def test_list_trained_models():
    model_name = "test_folder"
    model_path = TRAINED_MODELS / model_name
    model_path.mkdir(exist_ok=True)
    models = list_trained_models()
    assert model_name in models


def test_delete_folder():
    folder_path = TRAINED_MODELS / "test_folder"
    folder_path.mkdir(exist_ok=True)
    delete_folder(folder_path)
    assert not folder_path.exists()


def test_check_latest_version():
    model_dir = "test_folder"
    versions = [1, 2, 3]
    for version in versions:
        version_path = TRAINED_MODELS / f"{model_dir}-v{version}"
        version_path.mkdir(exist_ok=True)
    latest_version = check_latest_version(model_dir)
    assert latest_version == max(versions)
