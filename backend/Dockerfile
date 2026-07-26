FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY attest ./attest

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Shell form so an injected $PORT (OpenShip / Railway / Render / Fly) is honored,
# defaulting to 8000 for local `docker run`.
CMD ["sh", "-c", "uvicorn attest.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
