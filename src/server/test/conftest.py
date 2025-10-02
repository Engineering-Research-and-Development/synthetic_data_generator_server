import os
from pathlib import Path
from shutil import rmtree

test_folder = os.path.dirname(os.path.abspath(__file__))
trained_models_folder = os.path.join(test_folder, Path("saved_models/trained_models"))
algorithms_folder = os.path.join(test_folder, Path("saved_models/algorithms"))
# Creating test folder structure for the tests
if not os.path.isdir(os.path.join(test_folder, Path("saved_models"))):
    os.makedirs(os.path.join(test_folder, Path("saved_models")))
if not os.path.isdir(trained_models_folder):
    os.makedirs(trained_models_folder)
if not os.path.isdir(algorithms_folder):
    os.makedirs(algorithms_folder)


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    # We make some dirs that emulate some trained models in the system
    for i in range(1, 6):
        mock_tr = os.path.join(
            Path(test_folder), Path(f"saved_models/trained_models/{i}")
        )
        os.makedirs(mock_tr)


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    # Deleting temp files for server sync
    # Files cleanup
    rmtree(os.path.join(test_folder, Path("saved_models")))
    assert not os.path.isdir(os.path.join(test_folder, Path("/saved_models")))
