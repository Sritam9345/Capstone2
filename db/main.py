from pymongo import AsyncMongoClient
from dotenv import load_dotenv
import os
import redis.asyncio as redis

load_dotenv()

url = os.getenv('mongo_url')

client = AsyncMongoClient(url)

db = client.RAGcumChat

collection_chat = db["chat"]

redis = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)