# Microsoft Entra ID Authentication Setup Guide

This guide explains how to configure and deploy the Video Upload Web App with Microsoft Entra ID (Azure AD) authentication.

## Overview

The application supports **optional authentication** via Microsoft Entra ID using Azure App Service Easy Auth V2. Authentication can be enabled or disabled through deployment parameters.

## Default Deployment (No Authentication)

By default, the application deploys **without authentication** for testing purposes.

```bash
# Deploy without authentication (default)
azd up
```

This is suitable for:
- Development and testing
- Internal demos
- Non-production environments

## Enabling Authentication

To enable Microsoft Entra ID authentication, follow these steps:

### Step 1: Create Azure AD App Registration

1. Navigate to the [Azure Portal](https://portal.azure.com)
2. Go to **Microsoft Entra ID** → **App registrations** → **New registration**
3. Configure the registration:
   - **Name**: `video-upload-web-app` (or your preferred name)
   - **Supported account types**: "Accounts in this organizational directory only"
   - **Redirect URI**: Leave blank (we'll configure this after deployment)
4. Click **Register**
5. Copy the **Application (client) ID** - you'll need this

### Step 2: Create Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Add a description: `video-upload-app-secret`
4. Choose an expiration period (recommend 6-12 months)
5. Click **Add**
6. **IMMEDIATELY COPY THE SECRET VALUE** - it won't be shown again
7. Store it securely (password manager, Azure Key Vault, etc.)

### Step 3: Configure Environment Variables

Set the following environment variables before deployment:

```bash
# Enable authentication
export ENABLE_AUTHENTICATION=true

# Azure AD App Registration details
export AUTH_CLIENT_ID="<your-application-client-id>"
export AUTH_CLIENT_SECRET="<your-client-secret-value>"
```

**Windows PowerShell:**
```powershell
$env:ENABLE_AUTHENTICATION="true"
$env:AUTH_CLIENT_ID="<your-application-client-id>"
$env:AUTH_CLIENT_SECRET="<your-client-secret-value>"
```

### Step 4: Deploy with Authentication

```bash
# Provision and deploy with authentication enabled
azd up
```

Or deploy infrastructure and app separately:

```bash
# Provision infrastructure with authentication
azd provision

# Deploy application code
azd deploy
```

### Step 5: Configure Redirect URI

After deployment completes:

1. Note your application URL: `https://app-<random>.azurewebsites.net`
2. Go back to your Azure AD App Registration
3. Navigate to **Authentication** → **Add a platform** → **Web**
4. Add these redirect URIs:
   - `https://app-<random>.azurewebsites.net/.auth/login/aad/callback`
   - `https://app-<random>.azurewebsites.net/`
5. Under **Implicit grant and hybrid flows**, enable:
   - ✅ ID tokens (used for implicit and hybrid flows)
6. Click **Configure**
7. **Save** the changes

### Step 6: Verify Authentication

1. Navigate to your app URL
2. You should be redirected to Microsoft login page
3. After authentication, you'll be redirected back to the application
4. You should now see the video upload interface

## Authentication Configuration Details

The authentication is configured in `infra/modules/app-service.bicep` with the following settings:

- **Provider**: Microsoft Entra ID (Azure AD)
- **Token Store**: Enabled (stores access tokens for 8 hours)
- **Cookie Expiration**: 8 hours
- **Browser Redirect**: Enabled (`disableWWWAuthenticate: true`)
- **Allowed Audiences**:
  - `api://<app-service-name>`
  - `https://<app-service-name>.azurewebsites.net`
  - Your Azure AD Application Client ID

## Disabling Authentication

To disable authentication after it's been enabled:

```bash
# Unset or set to false
export ENABLE_AUTHENTICATION=false

# Re-provision infrastructure
azd provision
```

Or simply remove the environment variables:

```bash
unset ENABLE_AUTHENTICATION
unset AUTH_CLIENT_ID
unset AUTH_CLIENT_SECRET
```

## Troubleshooting

### Issue: "AADSTS50011: The reply URL specified in the request does not match"

**Solution**: Verify the redirect URI in Azure AD App Registration matches exactly:
- `https://<your-app-name>.azurewebsites.net/.auth/login/aad/callback`

### Issue: Login loop or continuous redirects

**Solution**: 
1. Verify client secret is correct and not expired
2. Check that ID tokens are enabled in Authentication settings
3. Ensure the application URL is in the allowed audiences

### Issue: "401 Unauthorized" after login

**Solution**:
1. Verify the user's account is in the same tenant as the Azure AD app
2. Check that the app registration's "Supported account types" matches your users
3. Review the allowed audiences in the Bicep configuration

### Issue: Client secret expired

**Solution**:
1. Create a new client secret in Azure AD App Registration
2. Update the `AUTH_CLIENT_SECRET` environment variable
3. Redeploy: `azd deploy`

## Security Best Practices

1. **Rotate Secrets Regularly**: Client secrets should be rotated every 6-12 months
2. **Use Key Vault**: For production, store client secrets in Azure Key Vault
3. **Restrict Account Types**: Use "Single tenant" unless multi-tenant is required
4. **Monitor Sign-ins**: Review sign-in logs in Azure AD for suspicious activity
5. **Enable MFA**: Require Multi-Factor Authentication for all users
6. **Use Managed Identity**: The app already uses Managed Identity for Azure Storage access
7. **Automatic Storage Access**: Your deployment account automatically receives Storage Blob Data Contributor role for management access via Storage Explorer

## Architecture

```
User Browser
    ↓
App Service (Easy Auth V2)
    ↓
[Unauthenticated] → Microsoft Entra ID Login → [Authenticated]
    ↓
Flask Application
    ↓
Azure Storage (via Managed Identity)
```

## Parameter Reference

| Parameter | Environment Variable | Required | Default | Description |
|-----------|---------------------|----------|---------|-------------|
| `enableAuthentication` | `ENABLE_AUTHENTICATION` | No | `false` | Enable/disable authentication |
| `authClientId` | `AUTH_CLIENT_ID` | Yes* | - | Azure AD Application (client) ID |
| `authClientSecret` | `AUTH_CLIENT_SECRET` | Yes* | - | Azure AD client secret value |

*Required only when `enableAuthentication=true`

## Additional Resources

- [Azure App Service Authentication](https://learn.microsoft.com/en-us/azure/app-service/overview-authentication-authorization)
- [Microsoft Entra ID Documentation](https://learn.microsoft.com/en-us/entra/identity/)
- [Easy Auth Configuration](https://learn.microsoft.com/en-us/azure/app-service/configure-authentication-provider-aad)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review deployment logs: `azd monitor --logs`
3. Check Azure Portal → App Service → Authentication settings
4. Review Azure AD App Registration configuration
