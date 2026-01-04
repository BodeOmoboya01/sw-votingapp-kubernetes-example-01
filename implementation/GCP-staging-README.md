# GCP staging Voting App Deployment

## Build Information

- **Build SHA**: 80da8574c4461a906da5b7af8c2c3530f79189f4
- **Short SHA**: 80da857
- **Build URL**: https://circleci.com/gh/BodeOmoboya01/sw-votingapp-kubernetes-example-01/23
- **Build Time**: 2026-01-04T19:07:52Z
- **GCP Project**: wideazimuth
- **Registry**: us-central1-docker.pkg.dev/wideazimuth/votingapp-staging

## Docker Images

| Component | Image |
|-----------|-------|
| Vote | `us-central1-docker.pkg.dev/wideazimuth/votingapp-staging/vote:80da857` |
| Result | `us-central1-docker.pkg.dev/wideazimuth/votingapp-staging/result:80da857` |
| Worker | `us-central1-docker.pkg.dev/wideazimuth/votingapp-staging/worker:80da857` |

## Quick Deploy to GKE

```bash
# Authenticate with GKE cluster
gcloud container clusters get-credentials <cluster-name> --zone <zone> --project wideazimuth

# Deploy
kubectl apply -f voting-app-gcp-staging.yaml

# Check status
kubectl get all -n votingapp

# Access (NodePort)
# Vote:   http://<node-ip>:30005
# Result: http://<node-ip>:30004
```

## Clean Up

```bash
kubectl delete -f voting-app-gcp-staging.yaml
```
