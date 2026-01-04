# DockerHub Voting App Deployment

## Build Information

- **Build SHA**: 80da8574c4461a906da5b7af8c2c3530f79189f4
- **Short SHA**: 80da857
- **Build URL**: https://circleci.com/gh/BodeOmoboya01/sw-votingapp-kubernetes-example-01/31
- **Build Time**: 2026-01-04T19:07:39Z

## Docker Images

| Component | Image |
|-----------|-------|
| Vote | `bodeomoboya01/votingapp-vote:80da857` |
| Result | `bodeomoboya01/votingapp-result:80da857` |
| Worker | `bodeomoboya01/votingapp-worker:80da857` |

## Quick Deploy

```bash
# Deploy to any K8s cluster (k3s, minikube, kind, etc.)
kubectl apply -f voting-app-dockerhub.yaml

# Check status
kubectl get all -n votingapp

# Access (NodePort)
# Vote:   http://<node-ip>:30005
# Result: http://<node-ip>:30004
```

## Clean Up

```bash
kubectl delete -f voting-app-dockerhub.yaml
```
