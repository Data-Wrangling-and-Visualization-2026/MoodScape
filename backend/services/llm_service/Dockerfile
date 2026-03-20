# services/llm_service/Dockerfile
FROM python:latest

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
    -i https://pypi.org/simple \
    -r requirements.txt

COPY . .

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--reload"]