#!/bin/bash
# Build and push all voting app images to a registry
# Usage: ./build-push.sh <registry>
# Example: ./build-push.sh 123456789.dkr.ecr.us-east-1.amazonaws.com/voting-app
# Example: ./build-push.sh gcr.io/my-project/voting-app
# Example: ./build-push.sh myusername

set -e

REGISTRY=${1:-"voting-app"}
TAG=${2:-"latest"}

echo "============================================"
echo "Building Voting Application Images"
echo "Registry: $REGISTRY"
echo "Tag: $TAG"
echo "============================================"

# Vote App
echo ""
echo "Building vote app..."
docker build -t "$REGISTRY/vote:$TAG" ./vote
echo "✓ Vote app built successfully"

# Result App
echo ""
echo "Building result app..."
docker build -t "$REGISTRY/result:$TAG" ./result
echo "✓ Result app built successfully"

# Worker App
echo ""
echo "Building worker app..."
docker build -t "$REGISTRY/worker:$TAG" ./worker
echo "✓ Worker app built successfully"

echo ""
echo "============================================"
echo "All images built successfully!"
echo "============================================"
echo ""
echo "Images:"
echo "  - $REGISTRY/vote:$TAG"
echo "  - $REGISTRY/result:$TAG"
echo "  - $REGISTRY/worker:$TAG"
echo ""

# Ask to push
read -p "Push images to registry? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Pushing images..."
    
    docker push "$REGISTRY/vote:$TAG"
    echo "✓ Vote app pushed"
    
    docker push "$REGISTRY/result:$TAG"
    echo "✓ Result app pushed"
    
    docker push "$REGISTRY/worker:$TAG"
    echo "✓ Worker app pushed"
    
    echo ""
    echo "============================================"
    echo "All images pushed successfully!"
    echo "============================================"
fi
