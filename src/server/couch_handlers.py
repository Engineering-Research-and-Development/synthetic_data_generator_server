import os
from loguru import logger
import requests

COUCHDB_USER = os.environ.get("COUCHDB_USER", "admin")
COUCHDB_PASSWORD = os.environ.get("COUCHDB_PASSWORD", "password")
COUCHDB_HOST = os.environ.get("COUCHDB_HOST", "127.0.0.1")
DATABASE_NAME = os.environ.get("COUCHDB_DB", "model_results")
COUCHDB_URL = f"http://{COUCHDB_USER}:{COUCHDB_PASSWORD}@{COUCHDB_HOST}:5984"


def init_db():
    try:
        url = f"{COUCHDB_URL}/{DATABASE_NAME}/"
        response = requests.get(url)
        if response.status_code != 200:
            requests.put(url)
    except (ConnectionError, ConnectionRefusedError):
        logger.error("Cannot reach CouchDB, running in isolated environment")
        pass


def create_couch_entry() -> str | None:
    """Creates a new document in CouchDB and returns its _id."""
    url = f"{COUCHDB_URL}/{DATABASE_NAME}/"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json={})
    if response.status_code == 201:
        return response.json().get("id")
    else:
        logger.error(f"Error creating document: {response.text}")


def add_couch_data(doc_id: str, new_data: dict) -> None:
    """Adds a new dictionary to the existing document in CouchDB."""
    url = f"{COUCHDB_URL}/{DATABASE_NAME}/{doc_id}"

    # Fetch the existing document to get the _rev
    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"Error fetching document: {response.text}")

    doc = response.json()
    doc.update(new_data)
    response = requests.put(url, json=doc)
    if response.status_code not in [200, 201]:
        logger.error(f"Error updating document: {response.text}")
