# AWS sandbox Voting App Deployment

## Build Information

- **Build SHA**: 80da8574c4461a906da5b7af8c2c3530f79189f4
- **Short SHA**: 80da857
- **Build URL**: https://circleci.com/gh/BodeOmoboya01/sw-votingapp-kubernetes-example-01/29
- **Build Time**: 2026-01-04T19:08:35Z
- **AWS Account**: 716982328683
- **AWS Region**: us-east-1
- **ECR Registry**: 716982328683.dkr.ecr.us-east-1.amazonaws.com

## Docker Images

| Component | Image |
|-----------|-------|
| Vote | `716982328683.dkr.ecr.us-east-1.amazonaws.com/votingapp-sandbox-vote:80da857` |
| Result | `716982328683.dkr.ecr.us-east-1.amazonaws.com/votingapp-sandbox-result:80da857` |
| Worker | `716982328683.dkr.ecr.us-east-1.amazonaws.com/votingapp-sandbox-worker:80da857` |

## Quick Deploy to EKS

```bash
# Authenticate with EKS cluster
aws eks update-kubeconfig --name <cluster-name> --region us-east-1

# Deploy
kubectl apply -f voting-app-aws-sandbox.yaml

# Check status
kubectl get all -n votingapp

# Access (NodePort)
# Vote:   http://<node-ip>:30005
# Result: http://<node-ip>:30004
```

## Clean Up

```bash
kubectl delete -f voting-app-aws-sandbox.yaml
```
