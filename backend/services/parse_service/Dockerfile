FROM python:3.12.3

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/services/parse_service/requirementsparse.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend /app/backend
COPY storage /app/storage

ENV PYTHONPATH=/app
ENV LOCAL_AUDIO_STORAGE_PATH=/app/storage

EXPOSE 8001

CMD ["uvicorn", "backend.services.parse_service.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
