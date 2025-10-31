# Deployment Guide for XAU-API

This guide provides detailed instructions for deploying XAU-API in containerized environments including Docker, Docker Compose, and Kubernetes.

## Prerequisites

- Docker 20.10+ or Docker Engine with BuildKit support
- Docker Compose 2.0+ (for local testing)
- Kubernetes cluster (for K8s deployment)
- `.env` file with your `API_KEY` configured

## Quick Start with Docker Compose

The easiest way to run the application locally:

```bash
# 1. Clone the repository
git clone <repository-url>
cd XAU-API

# 2. Create .env file
cp .env.example .env
# Edit .env and set your API_KEY

# 3. Build and run with docker-compose
docker-compose up -d

# 4. Check logs
docker-compose logs -f

# 5. Test the endpoints
curl http://localhost:8085/health
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8085/price
```

## Standard Docker Deployment

### Build the Image

```bash
# Build with default tag
docker build -t xau-api:latest .

# Build with specific tag
docker build -t xau-api:v1.0.0 .

# Build with BuildKit (recommended for better caching)
DOCKER_BUILDKIT=1 docker build -t xau-api:latest .
```

### Run the Container

```bash
# Basic run
docker run -d \
  --name xau-api \
  --restart always \
  -p 8085:8000 \
  -e API_KEY="your-api-key-here" \
  xau-api:latest

# Run with all recommended options
docker run -d \
  --name xau-api \
  --restart always \
  -p 8085:8000 \
  --shm-size=2gb \
  --memory=2g \
  --cpus=2 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  xau-api:latest

# View logs
docker logs -f xau-api

# Stop container
docker stop xau-api

# Remove container
docker rm xau-api
```

## Kubernetes Deployment

### 1. Create Namespace (Optional)

```bash
kubectl create namespace xau-api
```

### 2. Create Secret for API Key

```bash
kubectl create secret generic xau-api-secret \
  --from-literal=api-key=YOUR_API_KEY_HERE \
  -n xau-api
```

### 3. Apply Deployment

Create `k8s-deployment.yaml`:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: xau-api-service
  namespace: xau-api
spec:
  selector:
    app: xau-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: xau-api
  namespace: xau-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: xau-api
  template:
    metadata:
      labels:
        app: xau-api
    spec:
      containers:
      - name: xau-api
        image: exrienz/xau-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: xau-api-secret
              key: api-key
        - name: TZ
          value: "Asia/Kuala_Lumpur"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2"
        # Increase shared memory for Chromium
        volumeMounts:
        - name: dshm
          mountPath: /dev/shm
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 40
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 20
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
      volumes:
      - name: dshm
        emptyDir:
          medium: Memory
          sizeLimit: 2Gi
```

Apply the deployment:

```bash
kubectl apply -f k8s-deployment.yaml

# Check status
kubectl get pods -n xau-api
kubectl get svc -n xau-api

# View logs
kubectl logs -f deployment/xau-api -n xau-api

# Get service URL
kubectl get svc xau-api-service -n xau-api
```

## Troubleshooting

### Issue: Playwright browser not found

**Symptoms:**
```
BrowserType.launch: Executable doesn't exist at /ms-playwright/chromium_headless_shell-1187/chrome-linux/headless_shell
```

**Solution:**
The Dockerfile has been updated to properly install browsers. Rebuild the image:
```bash
docker build --no-cache -t xau-api:latest .
```

### Issue: Browser crashes in container

**Symptoms:**
```
❌ Failed to fetch prices: Browser closed unexpectedly
```

**Solutions:**

1. **Increase shared memory:**
```bash
docker run -d --shm-size=2gb xau-api:latest
```

2. **For Kubernetes, ensure dshm volume is mounted** (see k8s-deployment.yaml above)

3. **Check resource limits:**
```bash
docker run -d --memory=2g --cpus=2 xau-api:latest
```

### Issue: Permission denied errors

**Solution:**
The container runs as root by default. If you uncommented the non-root user section in the Dockerfile, ensure permissions are correct:

```dockerfile
# In Dockerfile
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app /ms-playwright
USER appuser
```

### Issue: API returns 404 for prices

**Symptoms:**
```
INFO: 10.42.0.1:51342 - "GET /price HTTP/1.1" 404 Not Found
```

**Solution:**
The scraper hasn't fetched prices yet or failed to scrape. Check logs:
```bash
docker logs xau-api | grep "Failed to fetch"
```

Wait 10-20 seconds for the first scrape cycle to complete.

### Issue: High memory usage

**Solution:**
Chromium can use significant memory. Recommended container limits:
- Minimum: 1GB RAM, 0.5 CPU
- Recommended: 2GB RAM, 1-2 CPU

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `API_KEY` | Authentication key for API endpoints | - | Yes |
| `TZ` | Timezone for timestamps | `Asia/Kuala_Lumpur` | No |
| `PLAYWRIGHT_BROWSERS_PATH` | Browser installation path | `/ms-playwright` | No |
| `NODE_OPTIONS` | Node.js memory settings | `--max-old-space-size=2048` | No |

## Performance Optimization

### 1. Use BuildKit for faster builds
```bash
export DOCKER_BUILDKIT=1
docker build -t xau-api:latest .
```

### 2. Multi-stage builds (future enhancement)
Consider implementing multi-stage builds to reduce final image size.

### 3. Resource allocation
For production, allocate:
- 2GB RAM minimum
- 2 CPU cores recommended
- 2GB shared memory (`/dev/shm`)

### 4. Persistent storage (optional)
Mount a volume for price data persistence:
```bash
docker run -d -v ./data:/app/data xau-api:latest
```

Note: You'll need to update the code to use `/app/data/price.json` instead of `/app/price.json`.

## Monitoring

### Health Check Endpoint
```bash
curl http://localhost:8085/health
```

Expected response:
```json
{"status": "healthy"}
```

### Container Health Status
```bash
# Docker
docker ps --filter name=xau-api

# Kubernetes
kubectl get pods -n xau-api
```

### Log Monitoring
```bash
# Docker
docker logs -f xau-api

# Docker Compose
docker-compose logs -f

# Kubernetes
kubectl logs -f deployment/xau-api -n xau-api
```

## CI/CD Integration

The project includes GitHub Actions for automated Docker builds:
- Builds on push to `main` or `develop` branches
- Tags images with `:latest` and `:<git-sha>`
- Pushes to DockerHub: `exrienz/xau-api`

## Security Considerations

1. **Never commit `.env` file** - Use secrets management
2. **API Key rotation** - Regularly rotate your API_KEY
3. **Run as non-root** - Uncomment the non-root user section in Dockerfile
4. **Network policies** - Use Kubernetes NetworkPolicies to restrict traffic
5. **Resource limits** - Always set memory/CPU limits in production

## Support

For issues or questions:
- Check logs first: `docker logs xau-api`
- Review this troubleshooting guide
- Check GitHub issues
- Verify all system dependencies are installed correctly
