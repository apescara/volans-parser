# volans-parser
Normalizacion de datos y subida a la nube

## Deploy

### Infra 

``` sh
cd infra
terraform plan
terraform apply
```

### Cloud Function

gcloud functions deploy volans-data \
    --gen2 \
    --runtime=python310 \
    --timeout 60s \
    --project clinica-volans \
    --region us-east1 \
    --service-account sa-clinica-volans@clinica-volans.iam.gserviceaccount.com \
    --source=function/. \
    --entry-point=main \
    --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
    --trigger-event-filters="bucket=archivos-base" \
    --memory=512MB