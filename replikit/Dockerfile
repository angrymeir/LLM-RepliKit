FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN pip install uv
RUN uv sync

COPY . .

ENTRYPOINT ["uv", "run"]
CMD ["main.py", "--study", "002", "--test", "3"]
