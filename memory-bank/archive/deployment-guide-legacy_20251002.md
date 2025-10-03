# Azure Deployment Guide - Video Upload Web Application

**Date**: October 2, 2025  
**Status**: 🚀 READY FOR DEPLOYMENT  
**Application Score**: 93/100 (Grade A)  
**Tests Passed**: 60/60 (100% pass rate)

---

## Prerequisites

Before deploying, ensure you have:

- ✅ Azure Subscription (active)
- ✅ Azure CLI installed and configured (`az --version`)
- ✅ Git installed (for deployment)
- ✅ Application tested locally (Phase 4 complete)

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AZURE CLOUD                               │
│                                                              │
│  ┌──────────────────────┐      ┌────────────────────────┐  │
│  │  Azure App Service   │      │  Azure Storage Account │  │
│  │  (Linux, Python 3.11)│─────▶│  (Blob Storage)        │  │
│  │                      │      │                        │  │
│  │  - Flask App         │      │  Container: "videos"   │  │
│  │  - Gunicorn Server   │      │  - mp4, mov, avi, etc. │  │
│  │  - 4 Workers         │      │  - Public read access  │  │
│  └──────────────────────┘      └────────────────────────┘  │
│           ▲                              ▲                   │
│           │                              │                   │
└───────────┼──────────────────────────────┼───────────────────┘
            │                              │
            │ HTTPS                        │ Backend Upload
            │                              │
    ┌───────┴────────┐            ┌────────┴─────────┐
    │   Web Browser   │            │   Flask API      │
    │                 │            │   (Backend Proxy)│
    └─────────────────┘            └──────────────────┘
```

---

## Step 1: Create Azure Storage Account

### Option A: Azure Portal (GUI)

1. **Navigate to Azure Portal**: https://portal.azure.com
2. **Create Storage Account**:
   - Click "Create a resource" → "Storage" → "Storage account"
   - **Subscription**: Select your subscription
   - **Resource Group**: Create new or select existing (e.g., `rg-video-upload-app`)
   - **Storage account name**: Choose unique name (e.g., `stvideouploadXXXX`)
   - **Region**: Select closest region (e.g., `East US`)
   - **Performance**: Standard
   - **Redundancy**: LRS (Locally-redundant storage) for MVP
   - Click "Review + Create" → "Create"

3. **Create Blob Container**:
   - Navigate to your storage account
   - Click "Containers" under "Data storage"
   - Click "+ Container"
   - **Name**: `videos`
   - **Public access level**: Blob (anonymous read access for blobs)
   - Click "Create"

4. **Configure CORS** (Important!):
   - In storage account, navigate to "Resource sharing (CORS)" under "Settings"
   - Add CORS rule for Blob service:
     - **Allowed origins**: `*` (or your App Service URL for production)
     - **Allowed methods**: GET, POST, PUT, OPTIONS
     - **Allowed headers**: `*`
     - **Exposed headers**: `*`
     - **Max age**: 3600
   - Click "Save"

5. **Get Connection String**:
   - Navigate to "Access keys" under "Security + networking"
   - Click "Show keys"
   - Copy **Connection string** from key1 or key2
   - **IMPORTANT**: Keep this secure, never commit to Git

### Option B: Azure CLI (Command Line)

```bash
# Set variables
RESOURCE_GROUP="rg-video-upload-app"
LOCATION="eastus"
STORAGE_ACCOUNT="stvideouploadXXXX"  # Replace XXXX with unique numbers
CONTAINER_NAME="videos"

# Login to Azure
az login

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create storage account
az storage account create \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --sku Standard_LRS \
  --kind StorageV2

# Get connection string
CONNECTION_STRING=$(az storage account show-connection-string \
  --name $STORAGE_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --output tsv)

echo "Connection String: $CONNECTION_STRING"

# Create blob container
az storage container create \
  --name $CONTAINER_NAME \
  --connection-string "$CONNECTION_STRING" \
  --public-access blob

# Configure CORS
az storage cors add \
  --services b \
  --methods GET POST PUT OPTIONS \
  --origins "*" \
  --allowed-headers "*" \
  --exposed-headers "*" \
  --max-age 3600 \
  --connection-string "$CONNECTION_STRING"

echo "✅ Azure Storage Account configured successfully!"
```

---

## Step 2: Test Local Configuration

Before deploying to Azure, test with real Azure Storage:

```bash
# Navigate to project directory
cd /Users/bradcstevens/code/github/bradcstevens/az-storage-upload-web-app

# Activate virtual environment
source venv/bin/activate

# Create .env file with your connection string
cat > .env << 'ENVEOF'
AZURE_STORAGE_CONNECTION_STRING=your_actual_connection_string_here
CONTAINER_NAME=videos
FLASK_ENV=development
PORT=5000
MAX_FILE_SIZE=104857600
ENVEOF

# IMPORTANT: Edit .env and replace with your actual connection string
nano .env  # or use: code .env

# Run Flask application
python3 -m flask --app app run --port 5000

# Test in browser: http://localhost:5000
# Try uploading a video file
# Verify it appears in Azure Portal → Storage Account → Containers → videos
```

---

## Step 3: Create Azure App Service

### Option A: Azure Portal (GUI)

1. **Create App Service**:
   - Click "Create a resource" → "Web" → "Web App"
   - **Subscription**: Select your subscription
   - **Resource Group**: Use same as storage (e.g., `rg-video-upload-app`)
   - **Name**: Choose unique name (e.g., `app-video-upload-XXXX`)
   - **Publish**: Code
   - **Runtime stack**: Python 3.11
   - **Operating System**: Linux
   - **Region**: Same as storage account
   - **Pricing plan**: B1 Basic (recommended for MVP)
   - Click "Review + Create" → "Create"

2. **Configure Application Settings**:
   - Navigate to your App Service
   - Click "Configuration" under "Settings"
   - Click "New application setting" for each:
     - **Name**: `AZURE_STORAGE_CONNECTION_STRING`
     - **Value**: Your connection string from Step 1
     - Click "OK"
     
     - **Name**: `CONTAINER_NAME`
     - **Value**: `videos`
     - Click "OK"
     
     - **Name**: `FLASK_ENV`
     - **Value**: `production`
     - Click "OK"
     
     - **Name**: `PORT`
     - **Value**: `8000`
     - Click "OK"
     
     - **Name**: `MAX_FILE_SIZE`
     - **Value**: `104857600`
     - Click "OK"
   
   - Click "Save" → "Continue"

3. **Configure Startup Command**:
   - In "Configuration", click "General settings" tab
   - **Startup Command**: `gunicorn --bind=0.0.0.0 --timeout 600 --workers 4 app:app`
   - Click "Save"

### Option B: Azure CLI (Command Line)

```bash
# Set variables
RESOURCE_GROUP="rg-video-upload-app"
LOCATION="eastus"
APP_SERVICE_PLAN="asp-video-upload"
APP_SERVICE_NAME="app-video-upload-XXXX"  # Replace XXXX with unique numbers
CONNECTION_STRING="your_connection_string_here"  # From Step 1

# Create App Service Plan
az appservice plan create \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --is-linux \
  --sku B1

# Create App Service
az webapp create \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan $APP_SERVICE_PLAN \
  --runtime "PYTHON:3.11"

# Configure application settings
az webapp config appsettings set \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
    AZURE_STORAGE_CONNECTION_STRING="$CONNECTION_STRING" \
    CONTAINER_NAME="videos" \
    FLASK_ENV="production" \
    PORT="8000" \
    MAX_FILE_SIZE="104857600"

# Set startup command
az webapp config set \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 --workers 4 app:app"

echo "✅ Azure App Service configured successfully!"
echo "App URL: https://${APP_SERVICE_NAME}.azurewebsites.net"
```

---

## Step 4: Deploy Application

### Option A: Git Deployment (Recommended)

```bash
# Navigate to project directory
cd /Users/bradcstevens/code/github/bradcstevens/az-storage-upload-web-app

# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial commit - Video upload web app"

# Configure Azure deployment
az webapp deployment source config-local-git \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP

# Get deployment credentials
DEPLOY_URL=$(az webapp deployment source config-local-git \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --query url \
  --output tsv)

echo "Deployment URL: $DEPLOY_URL"

# Add Azure as git remote
git remote add azure $DEPLOY_URL

# Deploy to Azure
git push azure main  # or master, depending on your branch name

# Monitor deployment
az webapp log tail --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP
```

### Option B: ZIP Deployment

```bash
# Navigate to project directory
cd /Users/bradcstevens/code/github/bradcstevens/az-storage-upload-web-app

# Create ZIP file (exclude venv, .env, etc.)
zip -r app.zip . -x "venv/*" ".env" ".git/*" "*.pyc" "__pycache__/*"

# Deploy ZIP to Azure
az webapp deployment source config-zip \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --src app.zip

echo "✅ Application deployed successfully!"
```

### Option C: VS Code Azure Extension

1. Install "Azure App Service" extension in VS Code
2. Click Azure icon in sidebar
3. Sign in to Azure account
4. Right-click on App Service → "Deploy to Web App"
5. Select your App Service
6. Confirm deployment

---

## Step 5: Post-Deployment Validation

### 5.1. Check Application Logs

```bash
# View real-time logs
az webapp log tail --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP

# Or via Portal:
# Navigate to App Service → Monitoring → Log stream
```

### 5.2. Test Deployed Application

```bash
# Get application URL
APP_URL="https://${APP_SERVICE_NAME}.azurewebsites.net"
echo "Application URL: $APP_URL"

# Test health endpoint
curl -s "$APP_URL/api/health" | python3 -m json.tool

# Expected output:
# {
#   "status": "healthy",
#   "azure_storage": "connected",
#   "timestamp": "2025-10-02T..."
# }
```

### 5.3. Browser Testing Checklist

Open `https://<your-app-name>.azurewebsites.net` in browser and test:

- [ ] Page loads successfully
- [ ] Bootstrap CSS applied correctly
- [ ] JavaScript loaded without errors (check browser console)
- [ ] Health check indicator shows "connected" or "healthy"
- [ ] Upload zone visible and styled correctly
- [ ] Click "Browse Files" button opens file dialog
- [ ] Select video file (mp4, mov, avi, mkv, or webm)
- [ ] Upload progress bar appears and updates
- [ ] Success notification appears after upload
- [ ] Video appears in "Uploaded Videos" list
- [ ] Video thumbnail/icon displays correctly
- [ ] "View" button opens blob URL in new tab
- [ ] Video plays in browser
- [ ] Drag-and-drop functionality works
- [ ] Multiple file uploads work
- [ ] Error handling works (try invalid file type)
- [ ] Responsive design works on mobile (use browser dev tools)

### 5.4. Verify Azure Storage

1. Navigate to Azure Portal → Storage Account → Containers → videos
2. Verify uploaded videos appear in container
3. Click on a blob to view properties
4. Copy blob URL and test in browser (should play video)

---

## Step 6: Monitoring and Troubleshooting

### Application Insights (Optional but Recommended)

```bash
# Create Application Insights
az monitor app-insights component create \
  --app ai-video-upload \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --application-type web

# Link to App Service
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app ai-video-upload \
  --resource-group $RESOURCE_GROUP \
  --query instrumentationKey \
  --output tsv)

az webapp config appsettings set \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY="$INSTRUMENTATION_KEY"
```

### Common Issues and Solutions

#### Issue 1: Application Won't Start
**Symptoms**: App Service shows "Service Unavailable" or 502 error

**Solutions**:
1. Check logs: `az webapp log tail --name $APP_SERVICE_NAME --resource-group $RESOURCE_GROUP`
2. Verify startup command is correct in Configuration → General settings
3. Ensure requirements.txt includes all dependencies
4. Check Python version matches runtime (Python 3.11)

#### Issue 2: Azure Storage Connection Failed
**Symptoms**: Health check shows "not_configured" or uploads fail

**Solutions**:
1. Verify connection string in Application Settings
2. Ensure connection string format is correct (starts with `DefaultEndpointsProtocol=https`)
3. Check storage account access keys are valid
4. Verify container "videos" exists

#### Issue 3: File Upload Fails
**Symptoms**: Upload returns 500 error or fails silently

**Solutions**:
1. Check CORS configuration on storage account
2. Verify container public access level is "Blob"
3. Check file size limits (100MB max)
4. Review application logs for error details
5. Test with smaller file first

#### Issue 4: Static Files Not Loading
**Symptoms**: Page loads but no CSS/JavaScript

**Solutions**:
1. Verify static files are in correct directory structure
2. Check Flask static folder configuration
3. Clear browser cache
4. Check browser console for 404 errors

#### Issue 5: Slow Upload Performance
**Symptoms**: Large files take too long or timeout

**Solutions**:
1. Increase timeout in startup command: `--timeout 900`
2. Consider implementing chunked uploads (future enhancement)
3. Adjust worker count based on App Service tier
4. Monitor App Service metrics (CPU, Memory)

---

## Step 7: Production Optimization (Optional)

### Enable HTTPS Redirect

```bash
az webapp update \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --https-only true
```

### Configure Custom Domain (Optional)

```bash
# Add custom domain
az webapp config hostname add \
  --webapp-name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --hostname yourdomain.com

# Enable managed SSL certificate
az webapp config ssl bind \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --certificate-thumbprint auto \
  --ssl-type SNI
```

### Scale App Service (If Needed)

```bash
# Scale up (more resources per instance)
az appservice plan update \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --sku S1  # Standard tier

# Scale out (more instances)
az appservice plan update \
  --name $APP_SERVICE_PLAN \
  --resource-group $RESOURCE_GROUP \
  --number-of-workers 2
```

### Enable Storage Analytics (Monitor Costs)

```bash
# Enable logging
az storage logging update \
  --services b \
  --log rwd \
  --retention 7 \
  --connection-string "$CONNECTION_STRING"

# Enable metrics
az storage metrics update \
  --services b \
  --hour true \
  --minute false \
  --retention 7 \
  --connection-string "$CONNECTION_STRING"
```

---

## Cost Estimation (Monthly)

**MVP Configuration**:
- **App Service B1 Basic**: ~$13.14/month
- **Storage Account (LRS, Standard)**: 
  - Storage: $0.0184/GB (~$1.84 for 100GB)
  - Transactions: $0.004/10,000 (~$0.40 for 100,000 uploads)
- **Bandwidth**: First 5GB free, then $0.087/GB

**Total Estimated Cost**: ~$15-20/month for MVP usage

**Cost Optimization Tips**:
- Use B1 Basic tier for development/MVP
- Implement blob lifecycle policies to archive old videos
- Monitor usage with Azure Cost Management
- Consider reserved instances for production (up to 72% savings)

---

## Security Checklist

Before going to production:

- [ ] Connection string stored in App Settings (not in code)
- [ ] `.env` file in `.gitignore` (never committed)
- [ ] HTTPS enforced on App Service
- [ ] CORS configured properly (restrict origins in production)
- [ ] File validation enabled (type and size)
- [ ] Rate limiting implemented (future enhancement)
- [ ] IP restrictions configured (optional)
- [ ] Storage account access keys rotated regularly
- [ ] Consider SAS tokens instead of connection string (Phase 2)
- [ ] Application Insights enabled for monitoring
- [ ] Backup strategy in place

---

## Rollback Procedure

If deployment fails or issues arise:

### Rollback via Azure Portal
1. Navigate to App Service → Deployment Center
2. Click "Logs" tab
3. Find previous successful deployment
4. Click "Redeploy"

### Rollback via Git
```bash
# Revert to previous commit
git log --oneline  # Find previous commit hash
git revert <commit-hash>
git push azure main
```

### Quick Fix via ZIP
```bash
# Deploy previous working version
az webapp deployment source config-zip \
  --name $APP_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --src app-backup.zip
```

---

## Next Steps After Deployment

1. **Monitor Application**:
   - Set up Application Insights alerts
   - Monitor storage costs
   - Track upload success rates

2. **Phase 2 Enhancements** (Future):
   - User authentication (Azure AD)
   - SAS tokens for direct uploads
   - Video thumbnail generation
   - Video transcoding
   - Delete functionality
   - Search and filtering
   - Video sharing links

3. **Documentation**:
   - Update README.md with production URL
   - Document API endpoints
   - Create user guide
   - Add troubleshooting section

---

## Support and Resources

- **Azure Documentation**: https://docs.microsoft.com/azure
- **Flask Documentation**: https://flask.palletsprojects.com
- **Azure Storage SDK**: https://learn.microsoft.com/python/api/overview/azure/storage
- **Application Logs**: Azure Portal → App Service → Monitoring → Log stream
- **Azure Support**: https://azure.microsoft.com/support

---

## Deployment Checklist

Copy this checklist and check off as you complete each step:

### Pre-Deployment
- [ ] Application tested locally (Phase 4 complete)
- [ ] Azure subscription active
- [ ] Azure CLI installed and logged in
- [ ] `.env` file in `.gitignore`
- [ ] All sensitive data removed from code

### Azure Resources
- [ ] Storage Account created
- [ ] Blob container "videos" created
- [ ] CORS configured on storage account
- [ ] Connection string obtained and secured
- [ ] App Service created
- [ ] App Service Plan configured (B1 Basic)
- [ ] Application Settings configured
- [ ] Startup command set

### Deployment
- [ ] Application deployed via Git/ZIP
- [ ] Deployment logs checked for errors
- [ ] Application URL accessible
- [ ] Health check endpoint returns "connected"
- [ ] Static files loading correctly

### Testing
- [ ] Upload single video file
- [ ] Upload multiple video files
- [ ] Drag-and-drop functionality works
- [ ] Progress tracking works
- [ ] Notifications display correctly
- [ ] Video list updates after upload
- [ ] Videos accessible via blob URL
- [ ] Error handling works (invalid file type)
- [ ] Responsive design tested
- [ ] Browser console shows no errors

### Post-Deployment
- [ ] Application Insights configured (optional)
- [ ] Monitoring alerts set up
- [ ] Documentation updated
- [ ] README.md includes production URL
- [ ] Team notified of deployment
- [ ] Backup strategy documented

---

**Deployment Status**: ⏳ READY TO START  
**Next Action**: Execute Step 1 (Create Azure Storage Account)  
**Estimated Time**: 30-60 minutes for full deployment

