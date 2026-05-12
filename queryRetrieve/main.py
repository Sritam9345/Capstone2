import os
import uuid
import chromadb
import numpy as np

from pypdf import PdfReader
from vectorDB.main import client

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from model.main import embedding_model


def context_retrieval(userInput: str):
    
    query_embedding = embedding_model.embed_query(userInput)
    
    collection = client.get_or_create_collection(
    name="pdf_collection"
    )
    
    results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
        )
    
    
    retrieved_ids = results["ids"][0]
    retrieved_docs = results["documents"][0]
    
    print(type(retrieved_ids[0]))
    
    return {
        'id':retrieved_ids,
        'doc':retrieved_docs
    }
    
context_retrieval('what is this about')