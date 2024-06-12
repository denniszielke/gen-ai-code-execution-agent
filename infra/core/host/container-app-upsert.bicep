param name string
param location string = resourceGroup().location
param tags object = {}

param containerAppsEnvironmentName string
param containerName string = 'main'
param imageName string
param containerRegistryName string
param secrets array = []
param env array = []
param external bool = true
param targetPort int = 8000
param exists bool
param openaiName string
@description('User assigned identity name')
param identityName string = ''
param dynamcSessionsName string

@description('CPU cores allocated to a single container instance, e.g. 0.5')
param containerCpuCoreCount string = '0.5'

@description('Memory allocated to a single container instance, e.g. 1Gi')
param containerMemory string = '1.0Gi'

resource existingApp 'Microsoft.App/containerApps@2022-03-01' existing = if (exists) {
  name: name
}

module app 'container-app.bicep' = {
  name: '${deployment().name}-update'
  params: {
    name: name
    location: location
    tags: tags
    identityName: identityName
    containerName: containerName
    containerAppsEnvironmentName: containerAppsEnvironmentName
    containerRegistryName: containerRegistryName
    containerCpuCoreCount: containerCpuCoreCount
    containerMemory: containerMemory
    secrets: secrets
    external: external
    env: env
    imageName: imageName
    targetPort: targetPort
    openaiName: openaiName
    dynamcSessionsName: dynamcSessionsName
  }
}

output defaultDomain string = app.outputs.defaultDomain
output imageName string = app.outputs.imageName
output name string = app.outputs.name
output uri string = app.outputs.uri
