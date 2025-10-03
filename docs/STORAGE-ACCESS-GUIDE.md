# Storage Access Guide

This guide explains how to access and manage the Azure Blob Storage used by the Video Upload Web App.

## Automatic Permission Grant

When you deploy the application using `azd up` or `azd provision`, the infrastructure **automatically grants your account** the **Storage Blob Data Contributor** role. This means you can:

- ✅ View all blobs in the storage account
- ✅ Upload files directly to containers
- ✅ Download blobs
- ✅ Delete blobs
- ✅ Manage blob metadata and properties
- ✅ Use Azure Storage Explorer, Portal, or CLI

## Access Methods

### Method 1: Azure Portal

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Go to **Resource Groups** → Your resource group (e.g., `rg-video-upload-demo`)
3. Click on the **Storage Account** (e.g., `styxiwyogm4dh3g`)
4. In the left menu, click **Storage Browser** → **Blob containers**
5. Click on the **videos** container
6. You can now:
   - View uploaded videos
   - Upload new files (click **Upload**)
   - Download files (select file → **Download**)
   - Delete files (select file → **Delete**)

### Method 2: Azure Storage Explorer (Recommended)

**Download**: [Azure Storage Explorer](https://azure.microsoft.com/features/storage-explorer/)

1. Install and open Azure Storage Explorer
2. Sign in with your Azure account (same account used for deployment)
3. Expand **Storage Accounts**
4. Find your storage account (check deployment outputs for the name)
5. Expand **Blob Containers** → **videos**
6. You can now:
   - Drag-and-drop files to upload
   - Right-click files for operations (download, delete, copy URL, etc.)
   - View blob properties and metadata
   - Generate SAS tokens

### Method 3: Azure CLI

**List blobs:**
```bash
# Get storage account name from deployment
STORAGE_ACCOUNT=$(azd env get-values | grep AZURE_STORAGE_ACCOUNT_NAME | cut -d'=' -f2 | tr -d '"')

# List all blobs in the videos container
az storage blob list \
  --account-name $STORAGE_ACCOUNT \
  --container-name videos \
  --auth-mode login \
  --output table
```

**Upload a file:**
```bash
az storage blob upload \
  --account-name $STORAGE_ACCOUNT \
  --container-name videos \
  --name myvideo.mp4 \
  --file ./path/to/myvideo.mp4 \
  --auth-mode login
```

**Download a file:**
```bash
az storage blob download \
  --account-name $STORAGE_ACCOUNT \
  --container-name videos \
  --name myvideo.mp4 \
  --file ./downloaded-video.mp4 \
  --auth-mode login
```

**Delete a file:**
```bash
az storage blob delete \
  --account-name $STORAGE_ACCOUNT \
  --container-name videos \
  --name myvideo.mp4 \
  --auth-mode login
```

### Method 4: Python SDK

```python
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# Use your Azure credentials
credential = DefaultAzureCredential()
storage_account_name = "your-storage-account-name"

# Create blob service client
blob_service_client = BlobServiceClient(
    account_url=f"https://{storage_account_name}.blob.core.windows.net",
    credential=credential
)

# List blobs
container_client = blob_service_client.get_container_client("videos")
for blob in container_client.list_blobs():
    print(f"Blob: {blob.name}, Size: {blob.size} bytes")

# Upload a blob
with open("local-video.mp4", "rb") as data:
    blob_client = container_client.get_blob_client("uploaded-video.mp4")
    blob_client.upload_blob(data, overwrite=True)

# Download a blob
blob_client = container_client.get_blob_client("uploaded-video.mp4")
with open("downloaded-video.mp4", "wb") as download_file:
    download_file.write(blob_client.download_blob().readall())
```

## Understanding the Permissions

### Your Account Permissions

**Role**: Storage Blob Data Contributor  
**Granted During**: Initial deployment (`azd up` or `azd provision`)  
**Scope**: The storage account created for this application  

**What you can do**:
- Read blob data and metadata
- Write blob data and metadata
- Delete blobs and containers
- List containers and blobs

**What you cannot do**:
- Manage storage account configuration (keys, networking rules, etc.) - requires Contributor role
- Assign roles to other users - requires Owner role
- Access storage account keys directly - use RBAC instead

### App Service Permissions

**Role**: Storage Blob Data Contributor  
**Identity**: System-assigned Managed Identity  
**Purpose**: Allow the Flask application to upload videos

The App Service has the same Storage Blob Data Contributor role but uses its Managed Identity (passwordless authentication) instead of your user credentials.

## Private Networking Considerations

The storage account is configured with:
- ✅ **Public network access disabled**
- ✅ **Private endpoint** for secure access
- ✅ **VNet integration** for App Service

### Accessing from Your Computer

When accessing storage from your computer (via Portal, Storage Explorer, or CLI), traffic goes through:
1. Your computer → Azure backbone network
2. Azure Private Link (if available in your region)
3. Storage account private endpoint

**Note**: You can access the storage account from anywhere because your user account has proper RBAC permissions. The private endpoint is primarily for App Service → Storage communication.

## Troubleshooting

### Issue: "Authorization permission mismatch" in Storage Explorer

**Cause**: Your account doesn't have the Storage Blob Data Contributor role yet.

**Solution**:
```bash
# Re-provision infrastructure to grant permissions
azd provision
```

Or manually grant via Azure CLI:
```bash
STORAGE_ACCOUNT=$(azd env get-values | grep AZURE_STORAGE_ACCOUNT_NAME | cut -d'=' -f2 | tr -d '"')
RESOURCE_GROUP=$(azd env get-values | grep AZURE_RESOURCE_GROUP | cut -d'=' -f2 | tr -d '"')
MY_USER_ID=$(az ad signed-in-user show --query id -o tsv)

az role assignment create \
  --role "Storage Blob Data Contributor" \
  --assignee $MY_USER_ID \
  --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT"
```

### Issue: Cannot see storage account in Storage Explorer

**Solution**:
1. Ensure you're signed in with the correct Azure account
2. Refresh the Storage Explorer
3. Check that the subscription is visible (Account Management → Subscriptions)

### Issue: "Public access is not permitted" error

**Solution**: This is expected. Use one of these authentication methods:
- Azure AD authentication (`--auth-mode login` in CLI)
- Storage Explorer with Azure AD sign-in
- Azure Portal (authenticates automatically)

**Do NOT use**:
- Storage account keys (not needed with RBAC)
- Connection strings (not needed with RBAC)
- Anonymous access (disabled for security)

### Issue: Access denied from App Service

**Solution**: Verify the Managed Identity has proper role assignment:
```bash
APP_NAME=$(azd env get-values | grep AZURE_APP_SERVICE_NAME | cut -d'=' -f2 | tr -d '"')
PRINCIPAL_ID=$(az webapp identity show --name $APP_NAME --resource-group $RESOURCE_GROUP --query principalId -o tsv)

# Verify role assignment exists
az role assignment list \
  --assignee $PRINCIPAL_ID \
  --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT" \
  --query "[?roleDefinitionName=='Storage Blob Data Contributor']" \
  --output table
```

## Granting Access to Other Users

To grant another user Storage Blob Data Contributor access:

```bash
# Get their user principal ID
OTHER_USER_ID=$(az ad user show --id "user@domain.com" --query id -o tsv)

# Grant role
az role assignment create \
  --role "Storage Blob Data Contributor" \
  --assignee $OTHER_USER_ID \
  --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Storage/storageAccounts/$STORAGE_ACCOUNT"
```

Or via Azure Portal:
1. Navigate to Storage Account → **Access Control (IAM)**
2. Click **Add** → **Add role assignment**
3. Select **Storage Blob Data Contributor**
4. Click **Next**
5. Click **Select members** → Search for user
6. Click **Review + assign**

## Best Practices

1. **Use RBAC over Storage Keys**: Always use Azure AD authentication instead of storage account keys
2. **Least Privilege**: Only grant Storage Blob Data Contributor, not Contributor or Owner
3. **Audit Access**: Regularly review role assignments in Access Control (IAM)
4. **Use Storage Explorer**: Best tool for managing blobs with a GUI
5. **Monitor Activity**: Check storage logs for unusual access patterns

## Quick Reference Commands

```bash
# Get storage account name
azd env get-values | grep AZURE_STORAGE_ACCOUNT_NAME

# List all videos
az storage blob list \
  --account-name <storage-name> \
  --container-name videos \
  --auth-mode login \
  --output table

# Get blob URL
az storage blob url \
  --account-name <storage-name> \
  --container-name videos \
  --name <filename> \
  --auth-mode login

# Check your role assignments
az role assignment list \
  --assignee $(az ad signed-in-user show --query id -o tsv) \
  --all \
  --query "[?contains(roleDefinitionName, 'Storage')]" \
  --output table
```

---

**Related Documentation**:
- [Deployment Checklist](./DEPLOYMENT-CHECKLIST.md)
- [Infrastructure README](../infra/README.md)
- [Authentication Guide](./AUTHENTICATION-GUIDE.md)
