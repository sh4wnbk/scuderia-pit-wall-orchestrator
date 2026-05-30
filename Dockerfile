FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.runtime.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.runtime.txt

COPY . .

# Pre-warm FastF1 session cache so Cloud Run serves telemetry on cold start.
# messages=True ensures race_control_messages are cached for event-driven prompts.
RUN python -c "import fastf1; fastf1.Cache.enable_cache('./fastf1_cache'); fastf1.get_session(2026,'Miami','R').load(telemetry=False,weather=False,messages=True); print('[Build] Miami 2026')" && \
    python -c "import fastf1; fastf1.Cache.enable_cache('./fastf1_cache'); fastf1.get_session(2026,'Canadian','R').load(telemetry=False,weather=False,messages=True); print('[Build] Canada 2026')" && \
    python -c "import fastf1; fastf1.Cache.enable_cache('./fastf1_cache'); fastf1.get_session(2024,'Azerbaijan','R').load(telemetry=False,weather=False,messages=True); print('[Build] Azerbaijan 2024')" && \
    python -c "import fastf1; fastf1.Cache.enable_cache('./fastf1_cache'); fastf1.get_session(2024,'Italian','R').load(telemetry=False,weather=False,messages=True); print('[Build] Monza 2024')"

ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
