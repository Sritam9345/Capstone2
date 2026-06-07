import streamlit as st
import requests
import json

st.title("File Upload Example")

API_BASE_URL = "http://agentic-api:8000"

# Upload file
uploaded_file = st.file_uploader(
    "Choose a file",
    type=["pdf", "txt", "csv", "png", "jpg"]
)

# Check if file uploaded
if uploaded_file is not None:
    

    response = requests.post(
        f"{API_BASE_URL}/upload-file",
        files={
    "file": ( 
        uploaded_file.name,
        uploaded_file,
        uploaded_file.type
    )
},
        data={
            'name':uploaded_file.name
        },
        timeout=15,
    )
    
    st.success("File uploaded successfully!")

    # File details
    st.write("Filename:", uploaded_file.name)
    st.write("File type:", uploaded_file.type)
    st.write("File size:", uploaded_file.size, "bytes")
    
    print(uploaded_file.name)

    # Read text files
    if uploaded_file.type == "text/plain":
        content = uploaded_file.read().decode("utf-8")
        st.text(content)

    # Read CSV
    elif uploaded_file.type == "text/csv":
        import pandas as pd

        df = pd.read_csv(uploaded_file)
        st.dataframe(df)

    # Display image
    elif uploaded_file.type.startswith("image"):
        st.image(uploaded_file)