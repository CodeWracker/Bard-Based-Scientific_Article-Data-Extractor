from python:3.9-slim

copy . /app

workdir /app

run pip install -r requirements.txt
