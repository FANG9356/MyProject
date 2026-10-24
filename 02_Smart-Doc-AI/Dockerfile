FROM node:20-alpine AS build-stage
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
RUN npm run build
FROM python:3.11-slim
WORKDIR /code
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .
COPY --from=build-stage /frontend/dist ./dist
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 