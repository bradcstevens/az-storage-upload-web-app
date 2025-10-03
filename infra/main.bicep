// Azure Video Upload Web Application - Main Infrastructure
// Infrastructure as Code using Azure Bicep
// Configured with private networking and Microsoft Entra ID authentication
targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment (e.g., dev, staging, prod)')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Name of the resource group')
param resourceGroupName string = ''

@description('Id of the user or app to assign application roles (deployment account gets Storage Blob Data Contributor)')
param principalId string = ''

@description('Enable Microsoft Entra ID authentication (default: false for testing)')
param enableAuthentication bool = false

@description('Azure AD client ID for authentication')
param authClientId string = ''

@description('Azure AD client secret for authentication')
@secure()
param authClientSecret string = ''

// Generate unique suffix for resource names
var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = {
  'azd-env-name': environmentName
  'app-name': 'video-upload'
  'managed-by': 'bicep'
  security: 'private-endpoint'
}

// Resource Group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// Network Module - Create VNet first
module network './modules/network.bicep' = {
  name: 'network'
  scope: rg
  params: {
    name: '${abbrs.virtualNetworksVirtualNetworks}${resourceToken}'
    location: location
    tags: tags
  }
}

// Storage Account Module - With private endpoint
module storage './modules/storage.bicep' = {
  name: 'storage'
  scope: rg
  params: {
    name: '${abbrs.storageStorageAccounts}${resourceToken}'
    location: location
    tags: tags
    privateEndpointSubnetId: network.outputs.privateEndpointSubnetId
    vnetId: network.outputs.id
  }
}

// App Service Module - With VNet integration and optional Entra ID auth
module appService './modules/app-service.bicep' = {
  name: 'app-service'
  scope: rg
  params: {
    name: '${abbrs.webSitesAppService}${resourceToken}'
    location: location
    tags: tags
    serviceName: 'web'
    appServicePlanName: '${abbrs.webServerFarms}${resourceToken}'
    storageAccountName: storage.outputs.name
    containerName: 'videos'
    appServiceSubnetId: network.outputs.appServiceSubnetId
    enableAuthentication: enableAuthentication
    authClientId: authClientId
    authClientSecret: authClientSecret
  }
}

// Role Assignment: Grant App Service managed identity Storage Blob Data Contributor
module appServiceStorageRoleAssignment './modules/role-assignment.bicep' = {
  name: 'app-service-storage-role-assignment'
  scope: rg
  params: {
    principalId: appService.outputs.principalId
    storageAccountName: storage.outputs.name
  }
}

// Role Assignment: Grant deployment user Storage Blob Data Contributor (for Storage Explorer access)
module deploymentUserStorageRoleAssignment './modules/role-assignment.bicep' = if (!empty(principalId)) {
  name: 'deployment-user-storage-role-assignment'
  scope: rg
  params: {
    principalId: principalId
    storageAccountName: storage.outputs.name
  }
}

// Outputs
output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP string = rg.name
output AZURE_STORAGE_ACCOUNT_NAME string = storage.outputs.name
output AZURE_CONTAINER_NAME string = 'videos'
output AZURE_APP_SERVICE_NAME string = appService.outputs.name
output AZURE_APP_SERVICE_URL string = appService.outputs.uri
output AZURE_APP_SERVICE_PLAN_NAME string = appService.outputs.appServicePlanName
output AZURE_APP_SERVICE_PRINCIPAL_ID string = appService.outputs.principalId
output AZURE_VNET_NAME string = network.outputs.name
output AZURE_STORAGE_PRIVATE_ENDPOINT_ID string = storage.outputs.privateEndpointId
