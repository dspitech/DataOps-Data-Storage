import os
import json
import sqlite3
from azure.storage.blob import BlobServiceClient

CONTAINER_NAME = "raw"
DATABASE_PATH = "database/dataops.db"


def get_connection_string():
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        raise EnvironmentError(
            "Variable AZURE_STORAGE_CONNECTION_STRING manquante."
        )
    return connection_string


def create_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stg_blob_files (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file  TEXT UNIQUE,
            message      TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Base SQLite prête.")


def load_blobs():
    connection_string = get_connection_string()

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    blobs = container_client.list_blobs()

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    for blob in blobs:
        blob_name = blob.name
        print(f"Lecture blob : {blob_name}")

        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME,
            blob=blob_name
        )

        blob_content = blob_client.download_blob().readall()
        data = json.loads(blob_content)
        message = data.get("message")

        cursor.execute("""
            INSERT OR IGNORE INTO stg_blob_files (source_file, message)
            VALUES (?, ?)
        """, (blob_name, message))

        print(f"Chargé dans SQLite : {blob_name}")

    conn.commit()
    conn.close()
    print("Chargement terminé.")


if __name__ == "__main__":
    create_database()
    load_blobs()
