from vectorDB.main import client
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import numpy as np
import os
import uuid
import chromadb
import numpy as np

from pypdf import PdfReader
from vectorDB.main import client

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document




pdf_path = "data/data.pdf"

reader = PdfReader(pdf_path)

full_text = ""

for page in reader.pages:
    text = page.extract_text()

    if text:
        full_text += text + "\n"


documents = [
    Document(
        page_content=full_text,
        metadata={"source": pdf_path}
    )
]




splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

chunks = splitter.split_documents(documents)

print(f"Total Chunks: {len(chunks)}")




embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)




collection = client.get_or_create_collection(
    name="pdf_collection"
)




texts = [chunk.page_content for chunk in chunks]

embeddings = embedding_model.embed_documents(texts)





ids = [str(uuid.uuid4()) for _ in range(len(chunks))]

metadatas = [chunk.metadata for chunk in chunks]

collection.add(
    ids=ids,
    documents=texts,
    embeddings=embeddings,
    metadatas=metadatas
)

print("Data successfully stored in vector DB!")





