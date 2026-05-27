#!/bin/bash
set -e

while IFS= read -r line || [[ -n "$line" ]]; do
  [[ "$line" =~ ^[[:space:]]*# ]] && continue
  [[ -z "${line// }" ]] && continue
  key="${line%%=*}"
  val="${line#*=}"
  val="${val#"${val%%[![:space:]]*}"}"
  export "$key"="$val"
done < .env

IMAGE="us-central1-docker.pkg.dev/project-d97c2ed2-123c-47df-bc4/pit-wall/pit-wall-orchestrator:latest"

gcloud run deploy pit-wall-orchestrator \
  --image "$IMAGE" \
  --region us-central1 \
  --quiet \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 3 \
  --port 8080 \
  --set-env-vars "WATSONX_API_KEY=$WATSONX_API_KEY,WATSONX_URL=$WATSONX_URL,WATSONX_PROJECT_ID=$WATSONX_PROJECT_ID,WATSON_STT_API_KEY=$WATSON_STT_API_KEY,WATSON_STT_URL=$WATSON_STT_URL,WATSON_TTS_API_KEY=$WATSON_TTS_API_KEY,WATSON_TTS_URL=$WATSON_TTS_URL,RACE_YEAR=2026,RACE_NAME=Miami,RACE_DRIVER=LEC"

echo ""
echo "Service URL: https://pit-wall-orchestrator-l5k23f3kpa-uc.a.run.app"
