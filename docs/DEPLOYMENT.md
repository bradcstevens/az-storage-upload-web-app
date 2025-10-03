# 🚀 Modern Deployment Guide - Azure Developer CLI + Bicep

This guide uses **modern Azure deployment tools** for Infrastructure as Code:
- **Azure Developer CLI (azd)** - Unified deployment experience
- **Azure Bicep** - Infrastructure as Code (declarative)
- **Azure CLI** - Supporting commands

---

## ✅ Prerequisites

### 1. Install Azure Developer CLI

**macOS**:
```bash
brew tap azure/azd && brew install azd
```

**Windows**:
```powershell
winget install microsoft.azd
```

**Linux**:
```bash
curl -fsSL https://aka.ms/install-azd.sh | bash
```

### 2. Verify Installation

```bash
azd version  # Should be 1.19.0+
az --version # Should be 2.77.0+
```

### 3. Login to Azure

```bash
az login
azd auth login
```

---

## 🎯 Quick Start (3 Commands)

### Option 1: One-Command Deployment ⚡

```bash
# Initialize + Provision + Deploy (all-in-one)
azd up
```

That's it! The command will:
1. ✅ Create all Azure resources (Storage, App Service)
2. ✅ Configure environment variables
3. ✅ Deploy the application
4. ✅ Display the application URL

**Time**: 5-8 minutes

---

### Option 2: Step-by-Step Deployment 📋

```bash
# Step 1: Initialize environment (first time only)
azd init

# Enter environment name when prompted (e.g., "dev", "prod")
# Example: dev

# Step 2: Provision infrastructure only
azd provision

# Step 3: Deploy application only
azd deploy

# Step 4: View your application
azd env get-values | grep AZURE_APP_SERVICE_URL
```

**Time**: 8-10 minutes

---

## 🔍 What Gets Created?

### Azure Resources

| Resource | Name Pattern | Purpose |
|----------|--------------|---------|
| Resource Group | `rg-{env}` | Container for all resources |
| Storage Account | `st{hash}` | Video blob storage |
| Blob Container | `videos` | Stores uploaded videos |
| App Service Plan | `plan-{hash}` | Hosting plan (B1 Basic) |
| App Service | `app-{hash}` | Flask application host |

**Example**:
- Resource Group: `rg-dev`
- Storage Account: `stxa7k2jq3d5e`
- App Service: `app-xa7k2jq3d5e`
- App URL: `https://app-xa7k2jq3d5e.azurewebsites.net`

### Infrastructure Configuration

All infrastructure is defined in Bicep files (`infra/` directory):

```
infra/
├── main.bicep              # Main infrastructure
├── modules/
│   ├── storage.bicep       # Storage Account
│   └── app-service.bicep   # App Service
└── main.parameters.json    # Parameters
```

---

## 📊 Post-Deployment

### View Deployment Information

```bash
# View all environment variables
azd env get-values

# Get application URL
azd env get-value AZURE_APP_SERVICE_URL

# Get storage account name
azd env get-value AZURE_STORAGE_ACCOUNT_NAME
```

### Test Your Application

```bash
# Get the URL
APP_URL=$(azd env get-value AZURE_APP_SERVICE_URL)

# Test health endpoint
curl "$APP_URL/api/health" | python3 -m json.tool

# Expected output:
# {
#   "status": "healthy",
#   "azure_storage": "connected",
#   "timestamp": "2025-10-02T..."
# }
```

### Open in Browser

```bash
# Get URL and open automatically
open $(azd env get-value AZURE_APP_SERVICE_URL)

# Or manually visit: https://app-\{hash\}.azurewebsites.net
```

---

## 🔄 Common Operations

### Update Application Code

```bash
# After making code changes
azd deploy
```

### Update Infrastructure

```bash
# Edit infra/main.bicep or modules/*.bicep
# Then re-provision
azd provision
```

### View Logs

```bash
# Real-time logs
azd monitor --logs

# Or via Azure CLI
az webapp log tail \
  --name $(azd env get-value AZURE_APP_SERVICE_NAME) \
  --resource-group $(azd env get-value AZURE_RESOURCE_GROUP)
```

### Check Deployment Status

```bash
# View environment info
azd env list

# Show current environment
azd env get-values
```

---

## 🌍 Multi-Environment Deployment

Deploy to multiple environments (dev, staging, prod):

```bash
# Create dev environment
azd env new dev
azd up

# Create production environment
azd env new prod
azd env set AZURE_LOCATION eastus2  # Different region
azd up

# Switch between environments
azd env select dev
azd env select prod
```

---

## 🔧 Configuration

### Change Location

```bash
# Before first deployment
azd env set AZURE_LOCATION westus2
azd up
```

Available regions: `eastus`, `westus2`, `centralus`, `northeurope`, `westeurope`, etc.

### Customize App Service Tier

Edit `infra/modules/app-service.bicep`:

```bicep
param sku string = 'S1'  // Change from B1 to S1 (Standard)
```

### Change Python Version

Edit `infra/modules/app-service.bicep`:

```bicep
param pythonVersion string = '3.12'  // Change from 3.11 to 3.12
```

---

## 🗑️ Cleanup

### Delete All Resources

```bash
# Delete infrastructure but keep environment configuration
azd down

# Delete everything including environment
azd down --purge

# Force delete without prompts
azd down --force --purge
```

**Cost Savings**: Removes all billable resources (~$15-20/month)

---

## 🐛 Troubleshooting

### Issue: Deployment Fails

**Check logs**:
```bash
# View deployment logs
azd monitor --logs

# Or
az webapp log tail \
  --name $(azd env get-value AZURE_APP_SERVICE_NAME) \
  --resource-group $(azd env get-value AZURE_RESOURCE_GROUP)
```

### Issue: Resource Name Conflicts

Azure generates unique names automatically. If you see conflicts:

```bash
# Delete environment and start fresh
azd env delete {env-name}
azd init
azd up
```

### Issue: Application Not Starting

**Check app settings**:
```bash
az webapp config appsettings list \
  --name $(azd env get-value AZURE_APP_SERVICE_NAME) \
  --resource-group $(azd env get-value AZURE_RESOURCE_GROUP)
```

**Restart app**:
```bash
az webapp restart \
  --name $(azd env get-value AZURE_APP_SERVICE_NAME) \
  --resource-group $(azd env get-value AZURE_RESOURCE_GROUP)
```

### Issue: Storage Connection Failed

**Verify connection string**:
```bash
azd env get-value AZURE_STORAGE_CONNECTION_STRING
```

**Test storage account**:
```bash
az storage container list \
  --connection-string "$(azd env get-value AZURE_STORAGE_CONNECTION_STRING)"
```

---

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Azure CLI installed and logged in (`az login`)
- [ ] Azure Developer CLI installed (`azd version`)
- [ ] Code tested locally (see QA-TEST-REPORT.md)

### Deployment
- [ ] Run `azd up` or `azd provision` + `azd deploy`
- [ ] Note the application URL
- [ ] Verify no errors in output

### Post-Deployment
- [ ] Open application URL in browser
- [ ] Test health endpoint (`/api/health`)
- [ ] Upload a test video file
- [ ] Verify video appears in list
- [ ] Check Azure Portal → Storage → Containers → videos
- [ ] Test from mobile device

---

## 📚 Additional Resources

### Documentation
- **Infrastructure Details**: See `infra/README.md`
- **QA Report**: See `memory-bank/QA-TEST-REPORT.md`
- **API Documentation**: See `README.md`

### Azure Resources
- [Azure Developer CLI Docs](https://learn.microsoft.com/azure/developer/azure-developer-cli/)
- [Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [App Service on Linux](https://learn.microsoft.com/azure/app-service/overview)
- [Blob Storage](https://learn.microsoft.com/azure/storage/blobs/)

---

## 🎯 Quick Reference

### Most Common Commands

```bash
# Deploy everything
azd up

# Deploy code only (after changes)
azd deploy

# View application URL
azd env get-value AZURE_APP_SERVICE_URL

# View logs
azd monitor --logs

# Clean up
azd down
```

### Validate Infrastructure Before Deployment

```bash
# Validate Bicep syntax
az bicep build --file infra/main.bicep

# Preview changes (what-if)
az deployment sub what-if \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters environmentName=dev location=eastus
```

---

## ✅ Success Criteria

Your deployment is successful when:

- ✅ `azd up` completes without errors
- ✅ Health endpoint returns `"azure_storage": "connected"`
- ✅ Application URL loads in browser with correct styling
- ✅ Video upload works end-to-end
- ✅ Uploaded videos visible in Azure Storage container

---

## 💡 Pro Tips

1. **Use environments** for dev/staging/prod separation
2. **Version control** your infra changes (Bicep files in Git)
3. **Use `azd down`** when not testing to save costs
4. **Check logs** with `azd monitor --logs` for debugging
5. **Use `what-if`** before infrastructure changes

---

**Ready to deploy?** Run:

```bash
azd up
```

**Estimated time**: 5-8 minutes  
**Cost**: ~$15-20/month  
**Application Quality**: Grade A (93/100)
