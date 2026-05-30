FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.runtime.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.runtime.txt

COPY . .

# Pre-warm FastF1 session cache so Cloud Run serves telemetry on cold start
RUN python -c "\
import fastf1; \
fastf1.Cache.enable_cache('./fastf1_cache'); \
s = fastf1.get_session(2026, 'Miami', 'R'); \
s.load(telemetry=False, weather=False, messages=False); \
print('[Build] FastF1 Miami 2026 Race session cached')"

ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
