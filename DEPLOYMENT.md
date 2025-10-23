# Klypa Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- At least 8GB RAM
- GPU support (optional, for faster processing)

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/Sourcesiri-Kamelot/klypa.git
cd klypa
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

4. Access the application at http://localhost:8501

### Azure Deployment

#### Using Azure Container Instances (ACI)

1. Login to Azure:
```bash
az login
az acr login --name <your-registry>
```

2. Build and push Docker image:
```bash
docker build -t <your-registry>.azurecr.io/klypa:latest .
docker push <your-registry>.azurecr.io/klypa:latest
```

3. Deploy to ACI:
```bash
az container create \
  --resource-group klypa-rg \
  --name klypa-app \
  --image <your-registry>.azurecr.io/klypa:latest \
  --cpu 4 \
  --memory 8 \
  --ports 8501 \
  --environment-variables \
    OLLAMA_HOST=http://ollama:11434 \
    OLLAMA_MODEL=llama2 \
  --registry-login-server <your-registry>.azurecr.io \
  --registry-username <username> \
  --registry-password <password>
```

#### Using Azure App Service

1. Create App Service plan:
```bash
az appservice plan create \
  --name klypa-plan \
  --resource-group klypa-rg \
  --is-linux \
  --sku P1V2
```

2. Create web app:
```bash
az webapp create \
  --name klypa-app \
  --resource-group klypa-rg \
  --plan klypa-plan \
  --deployment-container-image-name <your-registry>.azurecr.io/klypa:latest
```

3. Configure environment variables:
```bash
az webapp config appsettings set \
  --name klypa-app \
  --resource-group klypa-rg \
  --settings \
    OLLAMA_HOST=http://ollama:11434 \
    OLLAMA_MODEL=llama2
```

#### Using Azure Kubernetes Service (AKS)

1. Create AKS cluster:
```bash
az aks create \
  --resource-group klypa-rg \
  --name klypa-cluster \
  --node-count 2 \
  --node-vm-size Standard_D4s_v3 \
  --enable-managed-identity
```

2. Get credentials:
```bash
az aks get-credentials \
  --resource-group klypa-rg \
  --name klypa-cluster
```

3. Apply Kubernetes manifests:
```bash
kubectl apply -f k8s/
```

### Environment Variables

Required environment variables:

- `AZURE_STORAGE_CONNECTION_STRING`: Azure Storage connection string
- `AZURE_STORAGE_CONTAINER_NAME`: Container name for video storage
- `OLLAMA_HOST`: Ollama API host URL
- `OLLAMA_MODEL`: Ollama model to use (e.g., llama2)
- `TTS_ENGINE`: TTS engine (coqui or bark)

Optional variables:

- `MAX_VIDEO_DURATION`: Maximum video duration in seconds (default: 3600)
- `MIN_SCENE_DURATION`: Minimum scene duration in seconds (default: 3)
- `MAX_SCENE_DURATION`: Maximum scene duration in seconds (default: 60)
- `OUTPUT_RESOLUTION`: Output resolution (default: 1080x1920)
- `OUTPUT_FPS`: Output FPS (default: 30)
- `ENABLE_ANALYTICS`: Enable analytics tracking (default: true)

## Scaling

### Horizontal Scaling

For processing multiple videos simultaneously, increase the number of replicas:

```bash
docker-compose up --scale klypa=3
```

### Vertical Scaling

Adjust resource limits in docker-compose.yml:

```yaml
services:
  klypa:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
```

## Monitoring

### Health Checks

The application includes health checks at:
- HTTP endpoint: http://localhost:8501/_stcore/health

### Logs

View application logs:
```bash
docker-compose logs -f klypa
```

### Azure Monitor

Configure Azure Application Insights for production monitoring:

```python
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    connection_string="<your-connection-string>"
)
```

## Backup and Recovery

### Data Persistence

Important data directories to backup:
- `/app/uploads` - Uploaded videos
- `/app/output` - Generated shorts
- `/app/analytics.json` - Analytics data

### Azure Storage Backup

Enable Azure Storage backup for persistent data:

```bash
az backup enable \
  --resource-group klypa-rg \
  --vault-name klypa-vault \
  --storage-account <storage-account> \
  --container-name klypa-videos
```

## Security

### SSL/TLS

Configure SSL certificate:

```bash
az webapp config ssl bind \
  --name klypa-app \
  --resource-group klypa-rg \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI
```

### Network Security

Configure network security groups:

```bash
az network nsg rule create \
  --resource-group klypa-rg \
  --nsg-name klypa-nsg \
  --name allow-https \
  --priority 100 \
  --destination-port-ranges 443
```

## Troubleshooting

### Common Issues

1. **FFmpeg not found**: Ensure FFmpeg is installed in the Docker container
2. **Out of memory**: Increase memory allocation in Docker settings
3. **Ollama connection failed**: Verify Ollama service is running
4. **Azure connection issues**: Check connection string and permissions

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
streamlit run src/app.py
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/Sourcesiri-Kamelot/klypa/issues
- Documentation: https://github.com/Sourcesiri-Kamelot/klypa/wiki
