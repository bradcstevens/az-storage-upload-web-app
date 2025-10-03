# Infrastructure as Code - Azure Bicep

This directory contains the Azure infrastructure definitions using **Bicep** (Infrastructure as Code) and deployment automation via **Azure Developer CLI (azd)**.

## 📁 Structure

```
infra/
├── main.bicep                 # Main infrastructure orchestration
├── main.parameters.json       # Parameter values (environment-specific)
├── abbreviations.json         # Resource naming abbreviations
├── modules/
│   ├── storage.bicep         # Storage Account module
│   └── app-service.bicep     # App Service module
└── README.md                  # This file
```

## 🏗️ Infrastructure Components

### Storage Account Module (`storage.bicep`)
- **Purpose**: Azure Blob Storage for video uploads
- **Features**:
  - Standard LRS redundancy (configurable)
  - Hot access tier for frequent access
  - **Private networking** with VNet integration
  - **Private endpoint** for secure access
  - Public blob access disabled
  - Automatic blob container creation (`videos`)
  - TLS 1.2 minimum, HTTPS-only

### Network Module (`network.bicep`)
- **Purpose**: Virtual network infrastructure for private networking
- **Features**:
  - VNet with configurable CIDR (default: 10.0.0.0/16)
  - App Service subnet for VNet integration
  - Private endpoint subnet for storage access
  - Network security configuration

### App Service Module (`app-service.bicep`)
- **Purpose**: Host Flask Python web application
- **Features**:
  - Linux-based App Service Plan (B1 Basic tier default)
  - Python 3.11 runtime (configurable: 3.9-3.12)
  - Gunicorn WSGI server with 4 workers
  - HTTPS-only enforced
  - TLS 1.2 minimum
  - Always On enabled (except F1 tier)
  - **System-assigned Managed Identity** for passwordless auth
  - **VNet integration** for private networking
  - **Optional Microsoft Entra ID authentication**
  - Environment variables pre-configured
  - 600-second timeout for large uploads

### Main Orchestration (`main.bicep`)
- Subscription-level deployment
- Resource group creation with tags
- Module composition (network + storage + app service + role assignments)
- Unique resource naming with hash suffix
- Optional authentication configuration
- Comprehensive outputs for CI/CD integration

### Role Assignment Module (`role-assignment.bicep`)
- **Purpose**: Grant storage access to App Service and deployment user
- **Features**:
  - **Storage Blob Data Contributor** role assignment
  - Automatically grants access to:
    - App Service managed identity (for application access)
    - Deployment user account (for Storage Explorer/management)
  - Passwordless authentication to Azure Storage
  - Principle of least privilege

## 🚀 Deployment Methods

### Method 1: Azure Developer CLI (Recommended)

**Prerequisites**:
- Azure Developer CLI installed (`azd version 1.19.0+`)
- Azure CLI logged in (`az login`)

**Commands**:
```bash
# Initialize environment (first time only)
azd init

# Provision infrastructure + deploy application
azd up

# Or step-by-step:
azd provision  # Create infrastructure only
azd deploy     # Deploy application only

# View deployment outputs
azd env get-values

# View logs
azd monitor --logs

# Clean up all resources
azd down
```

### Method 2: Azure CLI with Bicep

**Direct deployment**:
```bash
# Set variables
ENVIRONMENT_NAME="dev"
LOCATION="eastus"

# Deploy infrastructure
az deployment sub create \
  --name video-upload-deployment \
  --location $LOCATION \
  --template-file infra/main.bicep \
  --parameters environmentName=$ENVIRONMENT_NAME location=$LOCATION

# Get outputs
az deployment sub show \
  --name video-upload-deployment \
  --query properties.outputs
```

### Method 3: CI/CD Pipeline

**GitHub Actions / Azure DevOps**:
```yaml
# Example workflow step
- name: Deploy Infrastructure
  run: |
    az deployment sub create \
      --name ${{ github.run_id }} \
      --location eastus \
      --template-file infra/main.bicep \
      --parameters infra/main.parameters.json
```

## 🔧 Configuration

### Environment Variables

The infrastructure automatically configures these application settings:

| Setting | Description | Default Value |
|---------|-------------|---------------|
| `AZURE_STORAGE_ACCOUNT_NAME` | Storage account name | Auto-generated |
| `CONTAINER_NAME` | Blob container name | `videos` |
| `FLASK_ENV` | Flask environment | `production` |
| `PORT` | Application port | `8000` |
| `MAX_FILE_SIZE` | Maximum upload size (bytes) | `104857600` (100MB) |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | Enable build during deployment | `true` |
| `WEBSITES_PORT` | App Service port | `8000` |
| `MICROSOFT_PROVIDER_AUTHENTICATION_SECRET` | Azure AD client secret | Set when auth enabled |

**Note**: The application uses **Managed Identity** for storage access (no connection strings needed).

### Automatic Permissions

During deployment, the infrastructure automatically grants:
- **App Service Managed Identity**: Storage Blob Data Contributor role
- **Deployment User Account**: Storage Blob Data Contributor role (enables Storage Explorer access)

This allows you to manage blobs using Azure Storage Explorer, Azure Portal, or Azure CLI immediately after deployment.

### Customization

**Change location**:
```bicep
param location string = 'westus2'  // or any Azure region
```

**Change App Service tier**:
```bicep
param sku string = 'S1'  // Standard tier
```

**Change Python version**:
```bicep
param pythonVersion string = '3.12'
```

**Change storage redundancy**:
```bicep
param sku string = 'Standard_GRS'  // Geo-redundant
```

**Enable authentication**:
```bash
export ENABLE_AUTHENTICATION=true
export AUTH_CLIENT_ID="<your-azure-ad-app-client-id>"
export AUTH_CLIENT_SECRET="<your-client-secret>"
```

See [Authentication Guide](../docs/AUTHENTICATION-GUIDE.md) for complete setup instructions.

## 📊 Resource Naming Convention

Resources are named using Azure recommended abbreviations:

| Resource Type | Prefix | Example |
|---------------|--------|---------|
| Resource Group | `rg-` | `rg-dev` |
| Storage Account | `st` | `stxa7k2jq3d5e` |
| App Service | `app-` | `app-xa7k2jq3d5e` |
| App Service Plan | `plan-` | `plan-xa7k2jq3d5e` |

The suffix is a unique hash generated from: subscription ID + environment name + location

## 🔍 Validation

**Validate Bicep syntax**:
```bash
az bicep build --file infra/main.bicep
```

**What-if analysis** (preview changes):
```bash
az deployment sub what-if \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters environmentName=dev location=eastus
```

**Linting**:
```bash
az bicep lint --file infra/main.bicep
```

## 📤 Outputs

After deployment, these outputs are available:

| Output | Description | Example |
|--------|-------------|---------|
| `AZURE_LOCATION` | Deployment region | `eastus` |
| `AZURE_RESOURCE_GROUP` | Resource group name | `rg-dev` |
| `AZURE_STORAGE_ACCOUNT_NAME` | Storage account name | `stxa7k2jq3d5e` |
| `AZURE_STORAGE_CONNECTION_STRING` | Connection string | `DefaultEndpoints...` |
| `AZURE_CONTAINER_NAME` | Blob container | `videos` |
| `AZURE_APP_SERVICE_NAME` | App Service name | `app-xa7k2jq3d5e` |
| `AZURE_APP_SERVICE_URL` | Application URL | `https://app-xa7k2jq3d5e.azurewebsites.net` |
| `AZURE_APP_SERVICE_PLAN_NAME` | App Service Plan | `plan-xa7k2jq3d5e` |

**Access outputs**:
```bash
# Via azd
azd env get-values

# Via Azure CLI
az deployment sub show \
  --name video-upload-deployment \
  --query properties.outputs.AZURE_APP_SERVICE_URL.value -o tsv
```

## 🔐 Security Features

- ✅ **Managed Identity** for passwordless authentication
- ✅ **Private networking** with VNet integration
- ✅ **Private endpoints** for storage (no public access)
- ✅ **Optional Microsoft Entra ID authentication** (Easy Auth V2)
- ✅ HTTPS-only enforced on all services
- ✅ TLS 1.2 minimum version
- ✅ Secrets marked as @secure in Bicep
- ✅ FTPS disabled on App Service
- ✅ Always on enabled for better availability
- ✅ Role-based access control (RBAC) for storage

See [Authentication Guide](../docs/AUTHENTICATION-GUIDE.md) for authentication setup.

## 💰 Cost Estimation

**Default configuration (B1 tier with private networking)**:
- App Service B1 Basic: ~$13/month
- Storage Account (LRS, Hot): ~$0.02/GB/month + transactions
- Virtual Network: No charge
- Private Endpoints: ~$7.30/month per endpoint (~$1 for storage)
- Bandwidth: First 5GB free, then ~$0.087/GB

**Total**: ~$20-25/month for typical usage

**Cost optimization**:
- Development: Use F1 (Free) tier for App Service (note: VNet integration not available)
- Production: Use B1 or higher with reserved instances
- Remove private endpoints for development (use public access with network ACLs)

## 🧪 Testing

**Local testing** (before deployment):
```bash
# Validate Bicep files
az bicep build --file infra/main.bicep

# Preview deployment
az deployment sub what-if \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters environmentName=test location=eastus
```

## 🗑️ Cleanup

**Delete all resources**:
```bash
# Via azd (recommended)
azd down --purge

# Via Azure CLI
az group delete --name rg-dev --yes --no-wait
```

## 📚 Resources

- [Azure Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [Azure Developer CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [Bicep Best Practices](https://learn.microsoft.com/azure/azure-resource-manager/bicep/best-practices)
- [Resource Naming Conventions](https://learn.microsoft.com/azure/cloud-adoption-framework/ready/azure-best-practices/resource-naming)

## 🤝 Contributing

When modifying infrastructure:

1. Update Bicep files with clear comments
2. Test with `az bicep build` and `what-if`
3. Update this README with any new parameters or outputs
4. Document breaking changes
5. Update version in `azure.yaml`

---

**Last Updated**: October 2, 2025  
**Bicep Version**: Latest  
**Azure Developer CLI**: v1.19.0+
