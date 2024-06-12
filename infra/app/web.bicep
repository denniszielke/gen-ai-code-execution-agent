param name string
param location string = resourceGroup().location
param tags object = {}

@minLength(1)
@description('Openai API resource name for the API to use.')
param openaiName string

@minLength(1)
@description('Openai API Endpoint for the API to use.')
param openaiEndpoint string

@minLength(1)
@description('Name of the OpenAI Completion model deployment name.')
param completionDeploymentName string

param exists bool
param identityName string
param applicationInsightsName string
param containerAppsEnvironmentName string
param containerRegistryName string
param serviceName string = 'web'
param imageName string
param openaiApiVersion string
param dynamcSessionsName string
param poolManagementEndpoint string

resource apiIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

module web '../core/host/container-app-upsert.bicep' = {
  name: '${serviceName}-container-app'
  params: {
    name: name
    location: location
    imageName: imageName
    tags: union(tags, { 'azd-service-name': serviceName })
    identityName: identityName
    exists: exists
    openaiName: openaiName
    containerAppsEnvironmentName: containerAppsEnvironmentName
    containerRegistryName: containerRegistryName
    dynamcSessionsName: dynamcSessionsName
    env: [
      {
        name: 'AZURE_CLIENT_ID'
        value: apiIdentity.properties.clientId
      }
      {
        name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
        value: applicationInsights.properties.ConnectionString
      }
      {
        name: 'POOL_MANAGEMENT_ENDPOINT'
        value: poolManagementEndpoint}
      {
        name: 'AZURE_OPENAI_ENDPOINT'
        value: openaiEndpoint
      }
      {
        name: 'AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME'
        value: completionDeploymentName
      }
      {
        name: 'AZURE_OPENAI_VERSION'
        value: openaiApiVersion
      }
      {
        name: 'OPENAI_API_TYPE'
        value: 'azure'
      }
      {
        name: 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME'
        value: 'text-embedding-ada-002'
      }
      {
        name: 'AZURE_OPENAI_EMBEDDING_MODEL'
        value: 'text-embedding-ada-002'
      }
    ]
    targetPort: 8000
  }
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: applicationInsightsName
}

output SERVICE_API_IDENTITY_PRINCIPAL_ID string = apiIdentity.properties.principalId
output SERVICE_API_NAME string = web.outputs.name
output SERVICE_API_URI string = web.outputs.uri
output SERVICE_API_IMAGE_NAME string = web.outputs.imageName
