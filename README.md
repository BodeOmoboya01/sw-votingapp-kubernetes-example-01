# Voting Application

A modern, microservices-based voting application perfect for Kubernetes tutorials and demonstrations.

## Architecture

```chart
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Voting Application                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌───────────┐      ┌─────────┐      ┌────────┐      ┌──────────────┐     │
│   │           │      │         │      │        │      │              │     │
│   │   Vote    │─────▶│  Redis  │─────▶│ Worker │─────▶│  PostgreSQL │    │
│   │   (Web)   │      │ (Queue) │      │        │      │    (DB)      │     │
│   │           │      │         │      │        │      │              │     │
│   └───────────┘      └─────────┘      └────────┘      └──────────────┘     │
│       :80                                                    │              │
│                                                              │              │
│   ┌───────────┐                                              │              │
│   │           │                                              │              │
│   │  Result   │◀─────────────────────────────────────────────┘              │
│   │   (Web)   │                                                             │
│   │           │                                                             │
│   └───────────┘                                                             │
│       :80                                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Components

| Component | Technology | Description |
|-----------|------------|-------------|
| **Vote** | Python/Flask | Web frontend for casting votes |
| **Result** | Python/Flask | Web frontend showing real-time results |
| **Worker** | Python | Background processor (Redis → PostgreSQL) |
| **Redis** | Redis 7 | In-memory queue for votes |
| **PostgreSQL** | PostgreSQL 15 | Persistent storage for results |

## CI/CD Pipeline

This project uses CircleCI to build and push Docker images to multiple registries.

### Pipeline Overview

```chart
┌─────────────┐     ┌─────────────┐     ┌─────────────────────────────────────┐
│  Validate   │────▶│   Build     │────▶│           Push to Registries        │
│  (on push)  │     │  All Images │     │                                     │
└─────────────┘     └─────────────┘     │  ┌─────────────┐                    │
                                        │  │  DockerHub  │ (public images)    │
                                        │  └─────────────┘                    │
                                        │  ┌─────────────┐  ┌─────────────┐   │
                                        │  │GCP Staging  │─▶│GCP Sandbox  │   │
                                        │  └─────────────┘  └─────────────┘   │
                                        │  ┌─────────────┐  ┌─────────────┐   │
                                        │  │AWS Staging  │─▶│AWS Sandbox  │   │
                                        │  └─────────────┘  └─────────────┘   │
                                        └─────────────────────────────────────┘
```

### Required CircleCI Contexts

Configure the following contexts in CircleCI:

#### `dockerhub` Context
| Variable | Description |
|----------|-------------|
| `DOCKERHUB_USERNAME` | Your DockerHub username |
| `DOCKERHUB_TOKEN` | DockerHub access token (not password) |

#### `gcp-staging` and `gcp-sandbox` Contexts
| Variable | Description |
|----------|-------------|
| `GOOGLE_SERVICE_ACCOUNT_KEY` | Base64-encoded service account JSON key |
| `GOOGLE_PROJECT_ID` | GCP project ID |

#### `aws-staging` and `aws-sandbox` Contexts
| Variable | Description |
|----------|-------------|
| `AWS_ACCESS_KEY_ID` | AWS access key ID |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key |
| `AWS_DEFAULT_REGION` | AWS region (e.g., `us-east-1`) |

### Workflows

1. **validate-branch**: Runs on all branches except `main` - validates project structure
2. **build-and-push-all**: Runs on `main` - builds and pushes to all registries with approvals
3. **quick-push**: Manual trigger to push to all registries without individual approvals

### Image Naming Convention

| Registry | Image Names |
|----------|-------------|
| DockerHub | `{username}/votingapp-vote`, `{username}/votingapp-result`, `{username}/votingapp-worker` |
| GCP | `us-central1-docker.pkg.dev/{project}/votingapp-{env}/vote`, etc. |
| AWS ECR | `{account}.dkr.ecr.{region}.amazonaws.com/votingapp-{env}-vote`, etc. |

### Triggering Builds

Push to `main` branch:
```bash
git add .
git commit -m "Update voting app"
git push origin main
```

Then approve the deployments in CircleCI UI.

---

## Quick Start

### Local Development with Docker Compose

```bash
# Build and start all services
docker compose up --build

# Access the applications
# Vote: http://localhost:5000
# Results: http://localhost:5001

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v
```

### Build and Push to Registry

```bash
# Set your registry (ECR, GCR, or DockerHub)
export REGISTRY=your-registry.com/voting-app

# Build images
docker build -t $REGISTRY/vote:latest ./vote
docker build -t $REGISTRY/result:latest ./result
docker build -t $REGISTRY/worker:latest ./worker

# Push to registry
docker push $REGISTRY/vote:latest
docker push $REGISTRY/result:latest
docker push $REGISTRY/worker:latest
```

### Deploy to Kubernetes

```bash
# Update image references in k8s/voting-app-k8s.yaml first

# Deploy
kubectl apply -f k8s/voting-app-k8s.yaml

# Check status
kubectl get all -n votingapp

# Access (NodePort)
# Vote: http://<node-ip>:30005
# Result: http://<node-ip>:30004

# Delete
kubectl delete -f k8s/voting-app-k8s.yaml
```

## Registry Examples

### Amazon ECR

```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Create repositories
aws ecr create-repository --repository-name voting-app/vote
aws ecr create-repository --repository-name voting-app/result
aws ecr create-repository --repository-name voting-app/worker

# Build and push
export REGISTRY=123456789.dkr.ecr.us-east-1.amazonaws.com/voting-app
docker build -t $REGISTRY/vote:latest ./vote && docker push $REGISTRY/vote:latest
docker build -t $REGISTRY/result:latest ./result && docker push $REGISTRY/result:latest
docker build -t $REGISTRY/worker:latest ./worker && docker push $REGISTRY/worker:latest
```

### Google Container Registry (GCR)

```bash
# Authenticate
gcloud auth configure-docker

# Build and push
export REGISTRY=gcr.io/your-project/voting-app
docker build -t $REGISTRY/vote:latest ./vote && docker push $REGISTRY/vote:latest
docker build -t $REGISTRY/result:latest ./result && docker push $REGISTRY/result:latest
docker build -t $REGISTRY/worker:latest ./worker && docker push $REGISTRY/worker:latest
```

### Docker Hub

```bash
# Login
docker login

# Build and push
export REGISTRY=yourusername/voting-app
docker build -t $REGISTRY-vote:latest ./vote && docker push $REGISTRY-vote:latest
docker build -t $REGISTRY-result:latest ./result && docker push $REGISTRY-result:latest
docker build -t $REGISTRY-worker:latest ./worker && docker push $REGISTRY-worker:latest
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPTION_A` | Cats | First voting option |
| `OPTION_B` | Dogs | Second voting option |
| `REDIS_HOST` | redis | Redis hostname |
| `REDIS_PORT` | 6379 | Redis port |
| `POSTGRES_HOST` | db | PostgreSQL hostname |
| `POSTGRES_PORT` | 5432 | PostgreSQL port |
| `POSTGRES_USER` | postgres | PostgreSQL username |
| `POSTGRES_PASSWORD` | postgres | PostgreSQL password |
| `POSTGRES_DB` | postgres | PostgreSQL database |

### Customizing Vote Options

Change `OPTION_A` and `OPTION_B` in:
- `docker-compose.yml` for local development
- `k8s/voting-app-k8s.yaml` ConfigMap for Kubernetes

## Features

- **Real-time Results**: Server-Sent Events (SSE) for live updates
- **Modern UI**: Dark theme with smooth animations
- **Health Checks**: All components have health endpoints
- **Graceful Shutdown**: Worker handles SIGTERM properly
- **Production Ready**: Uses Gunicorn for Python apps
- **Security**: Non-root containers
- **Kubernetes Ready**: ConfigMaps, Secrets, proper labels
- **Multi-Registry CI/CD**: Automated builds to DockerHub, GCP, and AWS

## Project Structure

```
voting-app/
├── .circleci/
│   └── config.yml          # CircleCI pipeline configuration
├── docker-compose.yml      # Local development setup
├── README.md               # This file
├── vote/                   # Vote frontend
│   ├── app.py              # Flask application
│   ├── Dockerfile          # Container image
│   ├── requirements.txt    # Python dependencies
│   └── templates/
│       └── index.html      # Vote UI
├── result/                 # Result frontend
│   ├── app.py              # Flask application
│   ├── Dockerfile          # Container image
│   ├── requirements.txt    # Python dependencies
│   └── templates/
│       └── index.html      # Results UI
├── worker/                 # Background processor
│   ├── app.py              # Worker application
│   ├── Dockerfile          # Container image
│   └── requirements.txt    # Python dependencies
└── k8s/
    └── voting-app-k8s.yaml # Kubernetes manifests
```

## Kubernetes Tutorial Ideas

1. **Basic Deployment**: Deploy the application and understand Pods, Services, Deployments
2. **Scaling**: Scale the vote and result deployments
3. **ConfigMaps & Secrets**: Modify configuration without rebuilding images
4. **Rolling Updates**: Update the application with zero downtime
5. **Resource Management**: Observe resource requests and limits
6. **Health Checks**: Test liveness and readiness probes
7. **Networking**: Understand ClusterIP vs NodePort vs LoadBalancer
8. **Namespaces**: Deploy to different namespaces
9. **RBAC**: Set up proper access controls
10. **Ingress**: Expose the application with Ingress

## Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n votingapp

# Check logs
kubectl logs <pod-name> -n votingapp
```

### Database connection issues

```bash
# Verify PostgreSQL is running
kubectl exec -it <postgres-pod> -n votingapp -- pg_isready -U postgres

# Check worker logs
kubectl logs -l app.kubernetes.io/name=worker -n votingapp
```

### Redis connection issues

```bash
# Verify Redis is running
kubectl exec -it <redis-pod> -n votingapp -- redis-cli ping
```

### CircleCI Pipeline Issues

```bash
# Validate CircleCI config locally
circleci config validate .circleci/config.yml

# Check context variables are set correctly in CircleCI UI
# Organization Settings > Contexts
```

## License

MIT License - Feel free to use for learning and tutorials!
