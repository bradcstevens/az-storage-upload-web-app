// Network Module
// Creates Azure Virtual Network with subnets for App Service integration and Private Endpoints

@description('Virtual Network name')
param name string

@description('Location for the virtual network')
param location string = resourceGroup().location

@description('Tags for the virtual network')
param tags object = {}

@description('Virtual Network address prefix')
param addressPrefix string = '10.0.0.0/16'

@description('App Service subnet address prefix')
param appServiceSubnetPrefix string = '10.0.1.0/24'

@description('Private Endpoint subnet address prefix')
param privateEndpointSubnetPrefix string = '10.0.2.0/24'

// Virtual Network
resource vnet 'Microsoft.Network/virtualNetworks@2023-05-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    addressSpace: {
      addressPrefixes: [
        addressPrefix
      ]
    }
    subnets: [
      {
        name: 'appServiceSubnet'
        properties: {
          addressPrefix: appServiceSubnetPrefix
          delegations: [
            {
              name: 'appServiceDelegation'
              properties: {
                serviceName: 'Microsoft.Web/serverFarms'
              }
            }
          ]
          privateEndpointNetworkPolicies: 'Enabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
      {
        name: 'privateEndpointSubnet'
        properties: {
          addressPrefix: privateEndpointSubnetPrefix
          privateEndpointNetworkPolicies: 'Disabled'
          privateLinkServiceNetworkPolicies: 'Enabled'
        }
      }
    ]
  }
}

// App Service Subnet Reference
resource appServiceSubnet 'Microsoft.Network/virtualNetworks/subnets@2023-05-01' existing = {
  parent: vnet
  name: 'appServiceSubnet'
}

// Private Endpoint Subnet Reference
resource privateEndpointSubnet 'Microsoft.Network/virtualNetworks/subnets@2023-05-01' existing = {
  parent: vnet
  name: 'privateEndpointSubnet'
}

// Outputs
output id string = vnet.id
output name string = vnet.name
output appServiceSubnetId string = appServiceSubnet.id
output privateEndpointSubnetId string = privateEndpointSubnet.id
