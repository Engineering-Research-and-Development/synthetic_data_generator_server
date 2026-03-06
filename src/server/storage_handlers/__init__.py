import os

COUCHDB_USER = os.environ.get("COUCHDB_USER", "admin")
COUCHDB_PASSWORD = os.environ.get("COUCHDB_PASSWORD", "password")
COUCHDB_HOST = os.environ.get("COUCHDB_HOST", "127.0.0.1")
DATABASE_NAME = os.environ.get("COUCHDB_DB", "model_results")
COUCHDB_URL = f"http://{COUCHDB_USER}:{COUCHDB_PASSWORD}@{COUCHDB_HOST}:5984"

GARAGE_HOST = os.environ.get("GARAGE_HOST", "127.0.0.1")
GARAGE_USERNAME = os.environ.get("GARAGE_USERNAME", "admin")
GARAGE_PASSWORD = os.environ.get("GARAGE_PASSWORD", "password")
GARAGE_MODEL_BUCKET = os.environ.get("GARAGE_MODEL_BUCKET", "trained_models")