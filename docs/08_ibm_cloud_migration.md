# IBM Cloud Migration Runbook

This runbook migrates the project from local execution to an IBM Cloud Code Engine application.

## 1. Prerequisites

- IBM Cloud account access
- IBM Cloud CLI installed
- Container Registry and Code Engine plugins installed:
  - `ibmcloud plugin install container-registry -f`
  - `ibmcloud plugin install code-engine -f`

## 2. API service added in this repo

The repository now includes a production API wrapper in app.py with these endpoints:

- GET /health
- POST /process
- POST /race-context
- GET /audit

## 3. Authenticate IBM Cloud CLI

```bash
ibmcloud login --sso
ibmcloud target -r us-south
```

## 4. Create or target a resource group

```bash
ibmcloud target -g Default
```

## 5. Push the container image to IBM Container Registry

Choose your namespace and image name.

```bash
ibmcloud cr login
ibmcloud cr namespace-add scuderia || true

IMAGE=us.icr.io/scuderia/pit-wall-orchestrator:1.0.0

docker build -t "$IMAGE" .
docker push "$IMAGE"
```

## 6. Create Code Engine project and app

```bash
ibmcloud ce project create --name scuderia-pit-wall || true
ibmcloud ce project select --name scuderia-pit-wall

ibmcloud ce application create \
  --name pit-wall-api \
  --image "$IMAGE" \
  --port 8080 \
  --min-scale 1 \
  --max-scale 3 \
  --cpu 1 \
  --memory 2G
```

## 7. Configure runtime environment variables

Set secrets as environment variables for the app.

```bash
ibmcloud ce application update --name pit-wall-api \
  --env WATSONX_API_KEY=<value> \
  --env WATSONX_URL=https://us-south.ml.cloud.ibm.com \
  --env WATSONX_PROJECT_ID=<value> \
  --env WATSON_STT_API_KEY=<value> \
  --env WATSON_STT_URL=<value> \
  --env WATSON_TTS_API_KEY=<value> \
  --env WATSON_TTS_URL=<value> \
  --env RACE_YEAR=2024 \
  --env RACE_NAME=Bahrain \
  --env RACE_DRIVER=LEC
```

## 8. Validate deployment

```bash
APP_URL=$(ibmcloud ce application get --name pit-wall-api --output url)

echo "$APP_URL"
curl "$APP_URL/health"
```

## 9. Test inference endpoint

```bash
curl -X POST "$APP_URL/process" \
  -H "Content-Type: application/json" \
  -d '{"text_query":"Why did Leclerc lift on the straight?"}'
```

## 10. Optional CI/CD migration step

If you use GitHub Actions, store IBM credentials in repository secrets and automate image build and `ibmcloud ce application update` on merge to main.

See detailed setup:

- `docs/09_code_engine_cicd_and_secrets.md`

## 11. Cost and operations notes

- Keep min scale low outside demo windows.
- Use smaller model calls where possible to reduce token costs.
- Monitor logs and request latency:

```bash
ibmcloud ce application logs --name pit-wall-api --follow
```
