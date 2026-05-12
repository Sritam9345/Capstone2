from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv('mongo_url')

client = MongoClient(url)

db = client.RAGcumChat

collection_user = db["user"]
collection_chat = db["chat"]
