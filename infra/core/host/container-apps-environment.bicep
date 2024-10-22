param name string
param location string = resourceGroup().location
param tags object = {}

param logAnalyticsWorkspaceName string
param applicationInsightsName string

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2024-02-02-preview' = {
  name: name
  location: location
  tags: tags
  properties: {
    appInsightsConfiguration: {
      connectionString: applicationInsights.properties.ConnectionString
    }
    openTelemetryConfiguration: {
      tracesConfiguration:{
        destinations: ['appInsights']
      }
      logsConfiguration: {
        destinations: ['appInsights']
      }
    }
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
    workloadProfiles: [
      {
        name: 'consumption'
        workloadProfileType: 'Consumption'
      }
      {
        name: 'd4-compute'
        workloadProfileType: 'D4'
        minimumCount: 1
        maximumCount: 3
      }
    ]
  }
}

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' existing = {
  name: logAnalyticsWorkspaceName
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02'  existing = {
  name: applicationInsightsName
}

output defaultDomain string = containerAppsEnvironment.properties.defaultDomain
output name string = containerAppsEnvironment.name
