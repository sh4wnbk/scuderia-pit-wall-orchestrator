FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.runtime.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.runtime.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "python scripts/download_assets.py && uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
