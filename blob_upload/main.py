from azure.storage.blob.aio import BlobServiceClient
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime
import json
from azure.storage.queue.aio import QueueClient

load_dotenv()

conne_str = os.getenv('BLOB_CONNECT')
container_name = os.getenv('container_name')
queue_name = os.getenv("QUEUE_NAME")


service = BlobServiceClient.from_connection_string(conn_str=conne_str)
container = service.get_container_client(container=container_name)


queue_client = QueueClient.from_connection_string(
    conn_str=conne_str,
    queue_name=queue_name
)
semaphore = asyncio.Semaphore(100)

async def uploadFile(file,filename):
    async with semaphore:
            try:
                blob = container.get_blob_client(filename)
                await blob.upload_blob(file, overwrite=True)
                queueUpload = False
                for _ in range(3):
                    try:
                        await queue_client.send_message(
                            json.dumps({
                        "filename": filename,
                        "container": container_name
                        })
                        )
                        print("Queue update is successful")
                        queueUpload = True
                        break
                    except:
                        print("Retrying...")
                if queueUpload == False:
                        print("Queue Upload Fails.")
                        blob.delete_blob()
                else:
                    print("Everything working")
            except Exception as e:
                raise Exception(f"Upload Failed please reupload the file")
        
        
        
