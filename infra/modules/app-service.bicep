// App Service Module
// Creates Azure App Service with Python runtime for Flask application

@description('App Service name')
param name string

@description('Location for the App Service')
param location string = resourceGroup().location

@description('Tags for the App Service')
param tags object = {}

@description('App Service Plan name')
param appServicePlanName string

@description('App Service Plan SKU')
@allowed([
  'F1'
  'B1'
  'B2'
  'B3'
  'S1'
  'S2'
  'S3'
  'P1v2'
  'P2v2'
  'P3v2'
])
param sku string = 'B1'

@description('Python version')
@allowed([
  '3.9'
  '3.10'
  '3.11'
  '3.12'
])
param pythonVersion string = '3.11'

@description('Blob container name')
param containerName string = 'videos'

@description('Maximum file upload size in bytes')
param maxFileSize int = 104857600

@description('Storage Account name for managed identity access')
param storageAccountName string

@description('App Service subnet ID for VNet integration')
param appServiceSubnetId string

@description('Microsoft Entra ID tenant ID')
param tenantId string = tenant().tenantId

@description('Service name tag for azd deployment')
param serviceName string = ''

@description('Enable Microsoft Entra ID authentication')
param enableAuthentication bool = false

@description('Azure AD client ID for authentication (required if enableAuthentication is true)')
param authClientId string = ''

@description('Azure AD client secret for authentication (required if enableAuthentication is true)')
@secure()
param authClientSecret string = ''

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: appServicePlanName
  location: location
  tags: tags
  sku: {
    name: sku
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// App Service
resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: name
  location: location
  tags: !empty(serviceName) ? union(tags, {'azd-service-name': serviceName}) : tags
  kind: 'app,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    virtualNetworkSubnetId: appServiceSubnetId
    vnetRouteAllEnabled: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|${pythonVersion}'
      alwaysOn: sku != 'F1'
      ftpsState: 'Disabled'
      minTlsVersion: '1.2'
      appCommandLine: 'gunicorn --bind=0.0.0.0 --timeout 600 --workers 4 app:app'
      appSettings: [
        {
          name: 'AZURE_STORAGE_ACCOUNT_NAME'
          value: storageAccountName
        }
        {
          name: 'CONTAINER_NAME'
          value: containerName
        }
        {
          name: 'FLASK_ENV'
          value: 'production'
        }
        {
          name: 'PORT'
          value: '8000'
        }
        {
          name: 'MAX_FILE_SIZE'
          value: string(maxFileSize)
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'WEBSITES_PORT'
          value: '8000'
        }
        {
          name: 'MICROSOFT_PROVIDER_AUTHENTICATION_SECRET'
          value: enableAuthentication ? authClientSecret : ''
        }
      ]
    }
  }
}

// Configure Microsoft Entra ID Authentication (Easy Auth)
// Enabled based on enableAuthentication parameter
resource authSettings 'Microsoft.Web/sites/config@2023-01-01' = if (enableAuthentication) {
  parent: appService
  name: 'authsettingsV2'
  properties: {
    platform: {
      enabled: true
      runtimeVersion: '~1'
    }
    globalValidation: {
      requireAuthentication: true
      unauthenticatedClientAction: 'RedirectToLoginPage'
      redirectToProvider: 'azureActiveDirectory'
    }
    identityProviders: {
      azureActiveDirectory: {
        enabled: true
        login: {
          disableWWWAuthenticate: true
        }
        registration: {
          clientId: authClientId
          clientSecretSettingName: 'MICROSOFT_PROVIDER_AUTHENTICATION_SECRET'
          openIdIssuer: 'https://sts.windows.net/${tenantId}/v2.0'
        }
        validation: {
          allowedAudiences: [
            'api://${appService.name}'
            'https://${appService.properties.defaultHostName}'
            authClientId
          ]
        }
      }
    }
    login: {
      tokenStore: {
        enabled: true
      }
      preserveUrlFragmentsForLogins: false
      cookieExpiration: {
        convention: 'FixedTime'
        timeToExpiration: '08:00:00'
      }
    }
  }
}

// Outputs
output id string = appService.id
output name string = appService.name
output uri string = 'https://${appService.properties.defaultHostName}'
output appServicePlanId string = appServicePlan.id
output appServicePlanName string = appServicePlan.name
output principalId string = appService.identity.principalId
