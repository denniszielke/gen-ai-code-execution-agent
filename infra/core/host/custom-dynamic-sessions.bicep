param name string
param imageName string
param location string = resourceGroup().location
param tags object = {}

resource dynamicSessions 'Microsoft.App/sessionPools@2024-02-02-preview' = {
  name: name
  location: location
  tags: tags
  properties: {
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

output poolManagementEndpoint string = dynamicSessions.properties.poolManagementEndpoint
output name string = dynamicSessions.name
