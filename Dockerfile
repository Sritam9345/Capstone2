FROM python:3.13.5-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run data creation before server starts
RUN python dataCreation.py

EXPOSE 8000
EXPOSE 8501

CMD sh -c "uvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run frontend.py --server.address 0.0.0.0 --server.port 8501"