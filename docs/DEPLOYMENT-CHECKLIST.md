# Deployment Checklist

Use this checklist to ensure a successful deployment of the Video Upload Web App.

## Prerequisites

- [ ] Azure CLI installed (`az --version` shows 2.77.0+)
- [ ] Azure Developer CLI installed (`azd version` shows 1.19.0+)
- [ ] Logged into Azure (`az login` and `azd auth login`)
- [ ] Active Azure subscription with appropriate permissions

> **💡 Automatic Permission Grant**: The deployment automatically grants your account **Storage Blob Data Contributor** role, allowing you to manage blobs using Azure Storage Explorer, Portal, or CLI immediately after deployment.

## Deployment Options

### Option A: Deploy WITHOUT Authentication (Default - Recommended for Testing)

This is the default configuration and requires no additional setup.

**Steps:**

1. [ ] Clone or navigate to the project directory
2. [ ] Run deployment:
   ```bash
   azd up
   ```
3. [ ] Wait for completion (~5-8 minutes)
4. [ ] Copy the application URL from outputs
5. [ ] Test the application in a browser
6. [ ] Verify video upload functionality

**Expected Outputs:**
```
AZURE_APP_SERVICE_URL: https://app-<random>.azurewebsites.net
AZURE_STORAGE_ACCOUNT_NAME: st<random>
AZURE_RESOURCE_GROUP: rg-<environment>-<location>
```

---

### Option B: Deploy WITH Microsoft Entra ID Authentication

Follow these steps to deploy with authentication enabled.

#### Step 1: Create Azure AD App Registration

- [ ] Go to Azure Portal → Microsoft Entra ID → App registrations
- [ ] Click "New registration"
- [ ] Name: `video-upload-web-app` (or your preference)
- [ ] Account types: "Accounts in this organizational directory only"
- [ ] Leave Redirect URI blank (configure after deployment)
- [ ] Click "Register"
- [ ] **Copy the Application (client) ID** - save it securely

#### Step 2: Create Client Secret

- [ ] In your app registration, go to "Certificates & secrets"
- [ ] Click "New client secret"
- [ ] Description: `video-upload-app-secret`
- [ ] Expiration: 6-12 months recommended
- [ ] Click "Add"
- [ ] **IMMEDIATELY COPY THE SECRET VALUE** (won't be shown again)
- [ ] Store it securely (password manager or Key Vault)

#### Step 3: Set Environment Variables

**macOS/Linux:**
```bash
export ENABLE_AUTHENTICATION=true
export AUTH_CLIENT_ID="<your-client-id-from-step-1>"
export AUTH_CLIENT_SECRET="<your-secret-value-from-step-2>"
```

**Windows PowerShell:**
```powershell
$env:ENABLE_AUTHENTICATION="true"
$env:AUTH_CLIENT_ID="<your-client-id-from-step-1>"
$env:AUTH_CLIENT_SECRET="<your-secret-value-from-step-2>"
```

- [ ] Environment variables set correctly

#### Step 4: Deploy Application

- [ ] Run deployment:
   ```bash
   azd up
   ```
- [ ] Wait for completion (~5-8 minutes)
- [ ] **Copy the application URL** from outputs

#### Step 5: Configure Redirect URI

- [ ] Go back to Azure Portal → App registrations → Your app
- [ ] Click "Authentication" → "Add a platform" → "Web"
- [ ] Add redirect URI: `https://app-<random>.azurewebsites.net/.auth/login/aad/callback`
- [ ] Also add: `https://app-<random>.azurewebsites.net/`
- [ ] Enable "ID tokens (used for implicit and hybrid flows)"
- [ ] Click "Configure"
- [ ] Click "Save"

#### Step 6: Test Authentication

- [ ] Navigate to your app URL
- [ ] You should be redirected to Microsoft login
- [ ] Sign in with your organizational account
- [ ] You should be redirected back to the app
- [ ] Verify video upload functionality works

---

## Post-Deployment Verification

### Health Check

- [ ] Navigate to: `https://<your-app-url>/health`
- [ ] Verify response shows:
  ```json
  {
    "status": "healthy",
    "azure_storage": "connected",
    "auth_method": "managed-identity"
  }
  ```

### Upload Test

- [ ] Click "Choose Files" or drag-and-drop a video
- [ ] Select a video file (MP4, AVI, MOV, or WMV)
- [ ] Click "Upload"
- [ ] Verify successful upload message
- [ ] Check Azure Storage in portal:
  - Storage Account → Containers → videos
  - Verify your uploaded file appears

### Storage Access Verification

Your deployment account automatically has Storage Blob Data Contributor access:

- [ ] Open Azure Storage Explorer or Azure Portal
- [ ] Navigate to the storage account (name shown in deployment outputs)
- [ ] Access the `videos` container
- [ ] Verify you can view, download, and manage blobs
- [ ] Try uploading a file directly via Storage Explorer (should work)

### Network Verification (Advanced)

- [ ] Azure Portal → Resource Group → App Service
- [ ] Check "Networking" → "VNet integration" is Active
- [ ] Check "Identity" → System assigned is On
- [ ] Azure Portal → Storage Account
- [ ] Check "Networking" → "Private endpoint connections" shows Approved
- [ ] Check "Access Control (IAM)" → App Service has "Storage Blob Data Contributor"

---

## Troubleshooting

### Issue: `azd up` fails with authentication error

**Solution:**
- Run `azd auth login` and `az login` again
- Verify you have appropriate permissions in the subscription

### Issue: App shows "Application Error" or 500

**Solution:**
- Check App Service logs: `azd monitor --logs`
- Verify environment variables are set correctly
- Check that Managed Identity has Storage Blob Data Contributor role

### Issue: Authentication redirect loop

**Solution:**
- Verify redirect URI is configured correctly in Azure AD
- Ensure ID tokens are enabled in Authentication settings
- Check client secret hasn't expired

### Issue: Upload fails with "Network error"

**Solution:**
- Verify VNet integration is active
- Check private endpoint connection is approved
- Verify Managed Identity has proper role assignment

---

## Cleanup

To delete all resources:

```bash
azd down --purge
```

This will:
- Delete the resource group and all resources
- Remove local environment configuration
- **Warning**: This is permanent and cannot be undone

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `azd up` | Provision + deploy in one command |
| `azd provision` | Create infrastructure only |
| `azd deploy` | Deploy application code only |
| `azd env get-values` | Show environment variables |
| `azd monitor --logs` | View application logs |
| `azd down` | Delete all resources |

---

## Documentation

- [Storage Access Guide](./STORAGE-ACCESS-GUIDE.md) - How to access and manage blob storage
- [Authentication Setup Guide](../AUTHENTICATION-GUIDE.md) - Detailed authentication configuration
- [Infrastructure README](../infra/README.md) - Bicep modules and customization
- [Main README](../README.md) - Project overview and local development

---

**Last Updated**: December 2024  
**Version**: 1.0.0
