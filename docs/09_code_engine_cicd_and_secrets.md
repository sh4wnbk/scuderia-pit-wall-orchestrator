# Code Engine CI/CD and Secrets Integration

This document completes two migration tasks:

1. GitHub Actions based deployment to IBM Code Engine
2. Secret-safe runtime configuration using mounted secret files

## 1. GitHub Actions deployment

Workflow file:

- .github/workflows/deploy-code-engine.yml

Required GitHub repository secrets:

- IBM_CLOUD_API_KEY
- IBM_REGION (example: us)
- IBM_RESOURCE_GROUP
- ICR_NAMESPACE
- CE_PROJECT
- CE_APP_NAME

Behavior:

- Builds and pushes an image to IBM Container Registry
- Creates/selects the Code Engine project
- Creates or updates the Code Engine application with the new image

## 2. Secret-safe runtime configuration

The application now supports both direct env values and file-based secrets:

- WATSONX_API_KEY or WATSONX_API_KEY_FILE
- WATSONX_PROJECT_ID or WATSONX_PROJECT_ID_FILE
- WATSON_STT_API_KEY or WATSON_STT_API_KEY_FILE
- WATSON_TTS_API_KEY or WATSON_TTS_API_KEY_FILE

File-based secrets are preferred for IBM Cloud deployments.

## 3. Integrate IBM Secrets Manager with Code Engine (recommended flow)

1. Store your credentials in IBM Secrets Manager.
2. In Code Engine UI, open your application.
3. Open Variables and secrets.
4. Add secret references and mount them as files in the container.
5. Set the corresponding *_FILE environment variables to those mount paths.

Example mounted paths:

- /var/secrets/watsonx_api_key
- /var/secrets/watsonx_project_id
- /var/secrets/watson_stt_api_key
- /var/secrets/watson_tts_api_key

Then set:

- WATSONX_API_KEY_FILE=/var/secrets/watsonx_api_key
- WATSONX_PROJECT_ID_FILE=/var/secrets/watsonx_project_id
- WATSON_STT_API_KEY_FILE=/var/secrets/watson_stt_api_key
- WATSON_TTS_API_KEY_FILE=/var/secrets/watson_tts_api_key

## 4. Validation

After deployment:

```bash
APP_URL=$(ibmcloud ce application get --name <app-name> --output url)
curl "$APP_URL/health"
```

Inference test:

```bash
curl -X POST "$APP_URL/process" \
  -H "Content-Type: application/json" \
  -d '{"text_query":"Why did Leclerc lift on the straight?"}'
```
