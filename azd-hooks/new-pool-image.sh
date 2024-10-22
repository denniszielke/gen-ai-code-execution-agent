#!/bin/bash

set -e

IMAGE_NAME="$1"

if [ "$IMAGE_NAME" == "" ]; then
echo "No phase name provided - aborting"
exit 0;
fi

AZURE_ENV_NAME="$2"

LOCATION="$3"

if [ "$AZURE_ENV_NAME" == "" ]; then
echo "No environment name provided - aborting"
exit 0;
fi

if [[ $IMAGE_NAME =~ ^[a-z0-9-]{3,12}$ ]]; then
    echo "image name $IMAGE_NAME is valid"
else
    echo "image name $IMAGE_NAME is invalid - only numbers and lower case min 5 and max 12 characters allowed - aborting"
    exit 0;
fi

RESOURCE_GROUP="rg-$AZURE_ENV_NAME"

AZURE_CONTAINER_REGISTRY_NAME=$(az resource list -g $RESOURCE_GROUP --resource-type "Microsoft.ContainerRegistry/registries" --query "[0].name" -o tsv)
ENVIRONMENT_NAME=$(az resource list -g $RESOURCE_GROUP --resource-type "Microsoft.App/managedEnvironments" --query "[0].name" -o tsv)
AZURE_SUBSCRIPTION_ID=$(az account show --query id -o tsv)
IDENTITY_NAME=$(az resource list -g $RESOURCE_GROUP --resource-type "Microsoft.ManagedIdentity/userAssignedIdentities" --query "[0].name" -o tsv)

echo "identity name: $IDENTITY_NAME"
echo "container registry name: $AZURE_CONTAINER_REGISTRY_NAME"
echo "environment name: $ENVIRONMENT_NAME"
echo "service name: $IMAGE_NAME"
echo "location: $LOCATION"

sleep 4

IMAGE_TAG=$(date '+%m%d%H%M%S')

#az acr build --subscription ${AZURE_SUBSCRIPTION_ID} --registry ${AZURE_CONTAINER_REGISTRY_NAME} --image $IMAGE_NAME:$IMAGE_TAG ./src/$IMAGE_NAME
FULL_IMAGE_NAME="${AZURE_CONTAINER_REGISTRY_NAME}.azurecr.io/$SERVICE_NAME:$IMAGE_TAG"

echo "deploying image: $FULL_IMAGE_NAME"

URI=$(az deployment group create -g $RESOURCE_GROUP -f ./infra/core/host/custom-dynamic-sessions.bicep \
          -p name=$IMAGE_NAME -p containerRegistryName=$AZURE_CONTAINER_REGISTRY_NAME -p location=$LOCATION -p identityName=$IDENTITY_NAME -p environmentName=$ENVIRONMENT_NAME \
          -p imageName=$FULL_IMAGE_NAME --query properties.outputs.uri.value)

echo "deployment uri: $URI"