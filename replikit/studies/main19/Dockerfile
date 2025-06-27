FROM python:3.12.11-slim

WORKDIR /app

COPY ./replicationpackage .
COPY ./requirements.txt .
COPY ./data/*.* .

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python3", "preprocess.py"]
