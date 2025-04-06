from azure.storage.blob import BlobServiceClient
from sqlmodel import select

from utils.constant import SAS_URL, CONTAINER_NAME
from utils.logger import logger


async def upload_blob(blob_path:str,img_bytes):
    try:
        blob_service_client = BlobServiceClient(account_url=SAS_URL)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_path)
        upload = blob_client.upload_blob(img_bytes,overwrite=True, content_type="image/png")
        if upload:
            blob_url= f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{blob_path}"
            return blob_url
        else:
            raise Exception(f"Blob upload failed for {blob_path}")
    except Exception as e:
        logger.error("Error while uploading blob {}".format(e))
        raise Exception("Error while uploading blob {}".format(e))