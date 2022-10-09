FROM python:3.10-slim

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY ./requirements.txt .

RUN python -m pip install -r requirements.txt

RUN apt update && apt install nano -y

