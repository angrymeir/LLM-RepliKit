FROM python:3.12.11-slim

WORKDIR /app

COPY ./replicationpackage .

RUN pip3 install --no-cache-dir sentence-transformers==2.2.2 \
    huggingface-hub==0.25.2

CMD ["python3", "preprocess.py"]
