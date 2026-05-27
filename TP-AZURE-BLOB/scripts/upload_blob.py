import os
from pathlib import Path
from azure.storage.blob import BlobServiceClient

CONTAINER_NAME = "raw"
LOCAL_FILE_PATH = Path("data/test.json")
BLOB_NAME = "bitcoin/year=2026/month=05/day=10/test_3.json"


def get_connection_string():
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise EnvironmentError(
            "Variable AZURE_STORAGE_CONNECTION_STRING manquante."
        )
    return connection_string


def upload_file():
    connection_string = get_connection_string()

    if not LOCAL_FILE_PATH.exists():
        raise FileNotFoundError(f"Fichier introuvable : {LOCAL_FILE_PATH}")

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    try:
        container_client.create_container()
        print(f"Container créé : {CONTAINER_NAME}")
    except Exception:
        print(f"Container déjà existant : {CONTAINER_NAME}")

    blob_client = blob_service_client.get_blob_client(
        container=CONTAINER_NAME,
        blob=BLOB_NAME
    )

    with open(LOCAL_FILE_PATH, "rb") as file:
        blob_client.upload_blob(file, overwrite=True)

    print(f"Upload réussi : {BLOB_NAME}")


if __name__ == "__main__":
    upload_file()
