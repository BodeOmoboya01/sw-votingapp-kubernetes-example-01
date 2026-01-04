# AWS staging Voting App Deployment

## Build Information

- **Build SHA**: 80da8574c4461a906da5b7af8c2c3530f79189f4
- **Short SHA**: 80da857
- **Build URL**: https://circleci.com/gh/BodeOmoboya01/sw-votingapp-kubernetes-example-01/27
- **Build Time**: 2026-01-04T19:07:40Z
- **AWS Account**: 719026782228
- **AWS Region**: us-east-1
- **ECR Registry**: 719026782228.dkr.ecr.us-east-1.amazonaws.com

## Docker Images

| Component | Image |
|-----------|-------|
| Vote | `719026782228.dkr.ecr.us-east-1.amazonaws.com/votingapp-staging-vote:80da857` |
| Result | `719026782228.dkr.ecr.us-east-1.amazonaws.com/votingapp-staging-result:80da857` |
| Worker | `719026782228.dkr.ecr.us-east-1.amazonaws.com/votingapp-staging-worker:80da857` |

## Quick Deploy to EKS

```bash
# Authenticate with EKS cluster
aws eks update-kubeconfig --name <cluster-name> --region us-east-1

# Deploy
kubectl apply -f voting-app-aws-staging.yaml

# Check status
kubectl get all -n votingapp

# Access (NodePort)
# Vote:   http://<node-ip>:30005
# Result: http://<node-ip>:30004
```

## Clean Up

```bash
kubectl delete -f voting-app-aws-staging.yaml
```
