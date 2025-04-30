import os
import sys
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv(dotenv_path='.env')

# Fichier à uploader passé en argument
if len(sys.argv) < 2:
    raise ValueError("❌ Le nom du fichier CSV à uploader doit être fourni.")
local_file_name = sys.argv[1]

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
container_name = os.getenv('AZURE_BLOB_CONTAINER_NAME', 'scraping-container')

def upload_to_blob():
    if not connect_str:
        raise ValueError("❌ La variable AZURE_STORAGE_CONNECTION_STRING est manquante.")

    if not os.path.exists(local_file_name):
        raise FileNotFoundError(f"❌ Le fichier {local_file_name} n'existe pas.")

    try:
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_client = blob_service_client.get_container_client(container_name)

        try:
            container_client.get_container_properties()
        except ResourceNotFoundError:
            container_client.create_container()

        blob_client = container_client.get_blob_client(local_file_name)

        with open(local_file_name, 'rb') as data:
            blob_client.upload_blob(data, overwrite=True)

        print(f"✅ Fichier '{local_file_name}' envoyé dans le conteneur '{container_name}'.")

    except Exception as e:
        print("❌ Erreur lors de l'envoi vers Azure Blob :", e)

if __name__ == "__main__":
    upload_to_blob()
