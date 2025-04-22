from azure.storage.blob import BlobServiceClient

import pandas as pd
import os
import io

from typing import Optional

class AzureBlobStorageGetter() :
    def __init__(self):
        pass

    def get_storage_content(self) -> Optional[pd.DataFrame]:
        
        account_url = os.getenv("ACCOUNT_URL")
        container_name = os.getenv("CONTAINER_NAME")
        blob_name = os.getenv("BLOB_NAME")
       
        # URL du fichier ciblé : https://allocinestorage.blob.core.windows.net/scraping-container/allocine.csv
        blob_url = f"{account_url}{container_name}/{blob_name}"
   
        # trouvable dans azure :  dans allocinestorage => securite + reseau => cle d'acces
        account_key = os.getenv("ACCOUNT_KEY1")

        blob_service_client = BlobServiceClient(account_url=account_url, credential=account_key)

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_downloader = blob_client.download_blob()
        downloaded_blob = blob_downloader.readall()

        dataframe = None

        try :
            dataframe = pd.read_csv(io.BytesIO(downloaded_blob))
        except Exception as ex :
            print( ex.__doc__ )

        return dataframe