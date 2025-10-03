# CI/CD Pipeline Setup Guide

This guide explains how to set up the GitHub Actions CI/CD pipeline for automated deployment, testing, and cleanup.

## Overview

The CI/CD pipeline automatically:
1. ✅ **Deploys** infrastructure and application to Azure
2. ✅ **Tests** the deployment with Playwright E2E tests
3. ✅ **Cleans up** all Azure resources (guaranteed, even on failure)

**Trigger**: Pushes to `main` branch (excluding documentation changes)

## 🔐 Required GitHub Secrets

You need to create an Azure Service Principal and configure GitHub secrets.

### Step 1: Create Azure Service Principal

Run these commands in Azure CLI:

```bash
# Set variables
SUBSCRIPTION_ID="<your-subscription-id>"
APP_NAME="github-actions-video-upload"

# Create service principal with Contributor role
az ad sp create-for-rbac \
  --name "$APP_NAME" \
  --role Contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID \
  --sdk-auth

# This will output JSON - save this entire output
```

The output will look like:
```json
{
  "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  ...
}
```

### Step 2: Configure GitHub Secrets

Go to your GitHub repository: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Create these secrets:

| Secret Name | Value | Example |
|-------------|-------|---------|
| `AZURE_CLIENT_ID` | `clientId` from service principal output | `12345678-1234-1234-1234-123456789abc` |
| `AZURE_CLIENT_SECRET` | `clientSecret` from service principal output | `abc123def456...` |
| `AZURE_TENANT_ID` | `tenantId` from service principal output | `87654321-4321-4321-4321-210987654321` |
| `AZURE_SUBSCRIPTION_ID` | `subscriptionId` from service principal output | `11111111-2222-3333-4444-555555555555` |

### Step 3: Enable GitHub OIDC (Recommended)

For enhanced security, configure OIDC (OpenID Connect) authentication:

```bash
# Get your GitHub repository details
GITHUB_ORG="bradcstevens"
GITHUB_REPO="az-storage-upload-web-app"

# Create OIDC federated credential
az ad app federated-credential create \
  --id <APP_ID> \
  --parameters '{
    "name": "github-actions-oidc",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'"$GITHUB_ORG/$GITHUB_REPO"':ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

## 🚀 Pipeline Workflow

### Workflow File Location
`.github/workflows/ci-cd.yml`

### Pipeline Stages

#### 1️⃣ Setup
- Checkout code
- Install Python 3.11
- Install Azure Developer CLI
- Install Playwright and dependencies
- Authenticate with Azure (OIDC)

#### 2️⃣ Deployment
- Initialize azd environment with unique name: `ci-test-{run_number}`
- Provision infrastructure (Bicep)
- Deploy application code
- Wait for App Service to be ready (health check polling)
- **Outputs**: App URL, Storage Account, Resource Group

#### 3️⃣ Testing
- Run Playwright E2E tests:
  - Health endpoint verification
  - UI element presence checks
  - Video upload functionality
  - Success message validation
- Verify uploaded blobs in Azure Storage
- Upload test artifacts (videos, screenshots) on failure

#### 4️⃣ Cleanup (Always Runs)
- Delete Azure Resource Group (async)
- Purge azd environment
- Verify no resources remain
- **Guaranteed**: Runs even if deployment or tests fail

#### 5️⃣ Summary
- Generate pipeline summary with results
- Report deployment status, test results, cleanup confirmation

## 📊 Monitoring Pipeline

### View Pipeline Runs
1. Go to GitHub repository
2. Click **Actions** tab
3. Click on a workflow run to see details

### Pipeline Summary
Each run generates a summary showing:
- ✅/❌ Deployment status
- ✅/❌ Test results  
- ✅ Cleanup confirmation
- Application URL
- Storage account name
- Resource group name

### Artifacts
Failed test runs automatically upload:
- 📹 Video recordings
- 📸 Screenshots
- 📄 Test reports

Located in: **Actions** → Workflow run → **Artifacts** section

## 🧪 Running Tests Locally

### Prerequisites
```bash
# Install test dependencies
pip install playwright pytest-playwright
playwright install chromium
```

### Set Environment Variable
```bash
export APP_URL="https://your-app-name.azurewebsites.net"
```

### Run Tests
```bash
# All tests (headless)
pytest tests/e2e/ -v

# With visible browser
pytest tests/e2e/ -v --headed

# Specific test
pytest tests/e2e/test_video_upload.py::TestVideoUpload::test_video_upload_complete_flow -v

# With video recording
pytest tests/e2e/ -v --video=on

# Debug mode (slow motion)
pytest tests/e2e/ -v --headed --slowmo=1000
```

## 🔧 Customizing the Pipeline

### Change Azure Location
Edit `.github/workflows/ci-cd.yml`:
```yaml
env:
  AZURE_LOCATION: westus3  # Change to your preferred region
```

### Adjust Test Timeout
Edit `pytest.ini`:
```ini
timeout = 300  # Seconds (default: 5 minutes)
```

### Skip Documentation Changes
Pipeline automatically ignores changes to:
- `**.md` files
- `docs/**` directory
- `memory-bank/**` directory
- `.github/instructions/**` directory
- `.github/chatmodes/**` directory

### Manual Trigger
You can manually trigger the pipeline:
1. Go to **Actions** tab
2. Select **CI/CD - Deploy, Test, and Cleanup**
3. Click **Run workflow**
4. Select branch and click **Run workflow**

## 🛡️ Security Best Practices

### Service Principal Permissions
- ✅ Use **Contributor** role (required for resource creation/deletion)
- ✅ Scope to specific subscription
- ✅ Rotate client secret regularly (every 6-12 months)
- ✅ Use descriptive name: `github-actions-video-upload`

### GitHub Secrets
- ✅ Use repository secrets (not environment secrets for this use case)
- ✅ Never log secret values
- ✅ Rotate secrets when team members leave
- ✅ Use OIDC instead of long-lived secrets (recommended)

### Resource Cleanup
- ✅ Unique environment names prevent conflicts: `ci-test-{run_number}`
- ✅ Async deletion to avoid blocking pipeline
- ✅ Verification step confirms cleanup
- ✅ Always runs (even on failure) via `if: always()`

## 🐛 Troubleshooting

### Issue: "Unable to resolve action azure/login@v2"

**Cause**: Action version doesn't exist or network issue.

**Solution**: Use `azure/login@v1` instead:
```yaml
uses: azure/login@v1
```

### Issue: Authentication fails

**Solutions**:
1. Verify all 4 GitHub secrets are configured correctly
2. Ensure service principal has Contributor role
3. Check subscription ID is correct
4. Verify service principal hasn't expired

```bash
# Test service principal
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID
```

### Issue: Tests fail but app works manually

**Solutions**:
1. Check APP_URL environment variable is set correctly
2. Verify test video file exists in `data/` folder
3. Increase timeout in tests (large video file)
4. Check Playwright browser compatibility

### Issue: Resources not cleaned up

**Solutions**:
1. Check Azure Portal for resource groups with prefix `rg-ci-test-`
2. Manually delete: `az group delete --name rg-ci-test-XXX --yes`
3. Check service principal has delete permissions
4. Review cleanup step logs in GitHub Actions

### Issue: Playwright tests timeout

**Solutions**:
1. Increase timeout in test: `expect(...).to_be_visible(timeout=60000)`
2. Check App Service is fully started (health check)
3. Verify network connectivity
4. Check App Service logs for errors

## 📈 Performance Tips

### Reduce Pipeline Runtime
1. Use smaller test video file (current: ~10MB WMV)
2. Run tests in parallel (if multiple test files)
3. Use faster Azure region (closer to GitHub runners)
4. Cache Python dependencies (already configured)

### Optimize Costs
- Pipeline creates temporary resources (~20 minutes max)
- Estimated cost per run: $0.01-0.05 USD
- Resources always cleaned up (no ongoing costs)
- Use fewer test runs by combining related changes

## 📚 Test Coverage

The E2E test suite covers:

### Health Checks
- ✅ Health endpoint responds (200 OK)
- ✅ JSON structure validation
- ✅ Storage connectivity verification

### UI Elements
- ✅ Homepage loads successfully
- ✅ Page title correct
- ✅ Header and main elements visible
- ✅ Upload zone present
- ✅ File input and buttons functional

### Upload Functionality
- ✅ File selection works
- ✅ Upload button enables with file
- ✅ Complete upload flow (select → upload → success)
- ✅ Progress bar displays
- ✅ Success message appears

### Error Handling
- ✅ Invalid file type handling
- ✅ Error messages display appropriately

### Responsive Design
- ✅ Mobile viewport (375x667)
- ✅ Tablet viewport (768x1024)
- ✅ Desktop viewport (1280x720)

## 🎯 Success Criteria

Pipeline is considered successful when:
- ✅ Infrastructure provisions without errors
- ✅ Application deploys successfully
- ✅ Health endpoint returns 200 OK
- ✅ All Playwright tests pass
- ✅ Video uploads to storage
- ✅ All resources are deleted

## 📞 Support

**Issues with pipeline**:
- Check [GitHub Actions logs](../../actions)
- Review [troubleshooting section](#-troubleshooting)
- Create issue in repository

**Azure authentication issues**:
- Verify service principal: `az ad sp list --display-name github-actions-video-upload`
- Check role assignments: `az role assignment list --assignee <CLIENT_ID>`

**Test failures**:
- Download test artifacts from workflow run
- Review screenshots and videos
- Run tests locally for debugging

---

**Related Documentation**:
- [Deployment Checklist](./DEPLOYMENT-CHECKLIST.md)
- [Main README](../README.md)
- [Infrastructure README](../infra/README.md)
