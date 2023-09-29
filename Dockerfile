# app/Dockerfile

FROM python:3.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

RUN mkdir data

HEALTHCHECK CMD curl --fail http://localhost:8501/health

ENTRYPOINT ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8501"]
