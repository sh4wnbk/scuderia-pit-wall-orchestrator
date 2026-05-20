from __future__ import annotations

import base64
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from main import PitWallOrchestrator


class ProcessRequest(BaseModel):
    text_query: Optional[str] = Field(default=None, description="Fan text question")
    audio_b64: Optional[str] = Field(default=None, description="Base64 encoded wav bytes")
    telemetry_event: Optional[str] = Field(default=None, description="Telemetry event label")
    telemetry_data: Optional[dict] = Field(default=None, description="Telemetry payload")
    language: str = Field(default="en", description="Response language: 'en' or 'it'")


class ProcessResponse(BaseModel):
    output_type: str
    text: str
    traceability_link: Optional[str]
    audit_flag: bool
    timestamp: str
    audio_b64: Optional[str]


class RaceContextRequest(BaseModel):
    year: int
    race: str
    driver: str


app = FastAPI(
    title="Scuderia Pit-Wall Orchestrator API",
    version="1.0.0",
    description="IBM Cloud deployable API wrapper for the Pit-Wall Fan Orchestrator",
)

orchestrator = PitWallOrchestrator()


@app.on_event("startup")
def configure_initial_race_context() -> None:
    year = int(os.getenv("RACE_YEAR", "2026"))
    race = os.getenv("RACE_NAME", "Miami")
    driver = os.getenv("RACE_DRIVER", "LEC")
    orchestrator.set_race_context(year=year, race=race, driver=driver)


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def serve_ui():
    return FileResponse("static/index.html")


@app.get("/service-worker.js", include_in_schema=False)
def serve_sw():
    return FileResponse("static/service-worker.js", media_type="application/javascript")


@app.get("/health")
def healthcheck() -> dict:
    return {
        "status": "ok",
        "service": "pit-wall-orchestrator",
        "time": datetime.utcnow().isoformat(),
    }


@app.post("/race-context")
def set_race_context(payload: RaceContextRequest) -> dict:
    orchestrator.set_race_context(
        year=payload.year,
        race=payload.race,
        driver=payload.driver,
    )
    return {
        "status": "updated",
        "year": payload.year,
        "race": payload.race,
        "driver": payload.driver,
    }


@app.post("/process", response_model=ProcessResponse)
def process(payload: ProcessRequest) -> ProcessResponse:
    provided = [
        payload.text_query is not None,
        payload.audio_b64 is not None,
        payload.telemetry_event is not None,
    ]
    if sum(provided) != 1:
        raise HTTPException(
            status_code=400,
            detail="Provide exactly one input type: text_query, audio_b64, or telemetry_event",
        )

    audio_bytes = None
    if payload.audio_b64 is not None:
        try:
            audio_bytes = base64.b64decode(payload.audio_b64)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid audio_b64 payload: {exc}")

    output = orchestrator.process(
        text_query=payload.text_query,
        audio_bytes=audio_bytes,
        telemetry_event=payload.telemetry_event,
        telemetry_data=payload.telemetry_data,
        language=payload.language,
    )

    output_audio_b64 = (
        base64.b64encode(output.audio_bytes).decode("utf-8")
        if output.audio_bytes
        else None
    )

    return ProcessResponse(
        output_type=output.output_type,
        text=output.text,
        traceability_link=output.traceability_link,
        audit_flag=output.audit_flag,
        timestamp=output.timestamp.isoformat(),
        audio_b64=output_audio_b64,
    )


@app.get("/audit")
def audit_log() -> list[dict]:
    return orchestrator.get_audit_log()
