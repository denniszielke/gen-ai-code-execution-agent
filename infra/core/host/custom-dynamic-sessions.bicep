param name string
param imageName string
param location string = resourceGroup().location
param tags object = {}
param environmentName string
param containerRegistryName string
param identityName string

resource userIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: identityName
}

resource dynamicSessions 'Microsoft.App/sessionPools@2024-08-02-preview' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userIdentity.id}': {}
    }
  }
  properties: {
    environmentId: containerAppsEnvironment.id
    poolManagementType: 'Dynamic'
      containerType: 'CustomContainer'
      scaleConfiguration: {
          maxConcurrentSessions: 10
          readySessionInstances: 1
      }
      dynamicPoolConfiguration: {
        executionType: 'Timed'
        cooldownPeriodInSeconds: 300
      }
      sessionNetworkConfiguration: {
        status: 'EgressEnabled'
      }
      customContainerTemplate: {
        registryCredentials: {
          server: '${containerRegistryName}.azurecr.io'
          identity: userIdentity.id
        }
        containers: [
          {
            name: 'custom-container'
            image: imageName
            resources: {
              cpu: 1
              memory: '2Gi'
            }
            command: [
              '/bin/sh'
            ]
            args: [
              '-c'
              'while true; do echo hello world; sleep 1000; done'
            ]
            env: [
              {
                name: 'EXAMPLE_ENV_VAR'
                value: 'example-value'
              }
            ]
          }
        ]
        ingress: {
          targetPort: 8000
        }
      }
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2022-03-01' existing = {
  name: environmentName
}

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2022-02-01-preview' existing = {
  name: containerRegistryName
}

output poolManagementEndpoint string = dynamicSessions.properties.poolManagementEndpoint
output name string = dynamicSessions.name
