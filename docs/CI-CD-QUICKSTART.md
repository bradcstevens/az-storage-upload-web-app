# Quick Setup: CI/CD Pipeline

This is a quick reference for setting up the CI/CD pipeline. See [CI-CD-SETUP.md](./CI-CD-SETUP.md) for detailed instructions.

## ⚡ Quick Steps

### 1. Create Service Principal

```bash
# Replace with your subscription ID
SUBSCRIPTION_ID="<your-subscription-id>"

# Create service principal
az ad sp create-for-rbac \
  --name "github-actions-video-upload" \
  --role Contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID \
  --sdk-auth
```

**Save the entire JSON output!**

### 2. Add GitHub Secrets

Go to: **GitHub Repository** → **Settings** → **Secrets and variables** → **Actions**

Add these 4 secrets:

| Secret Name | Get Value From |
|-------------|----------------|
| `AZURE_CLIENT_ID` | `clientId` from JSON output |
| `AZURE_CLIENT_SECRET` | `clientSecret` from JSON output |
| `AZURE_TENANT_ID` | `tenantId` from JSON output |
| `AZURE_SUBSCRIPTION_ID` | `subscriptionId` from JSON output |

### 3. Push to Main Branch

```bash
git push origin main
```

The pipeline will automatically run!

### 4. Monitor Pipeline

Go to: **GitHub Repository** → **Actions** tab

You'll see the pipeline:
1. ⚙️ Deploy infrastructure
2. 🧪 Run Playwright tests  
3. 🧹 Clean up resources

## 📊 What the Pipeline Does

```
┌─────────────────────────────────────────────────────────┐
│  Push to main branch                                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  DEPLOY                                                 │
│  • Create unique environment (ci-test-{run_number})     │
│  • Provision Azure infrastructure                       │
│  • Deploy Flask application                             │
│  • Wait for app to be ready                             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  TEST                                                   │
│  • Health endpoint check                                │
│  • UI element validation                                │
│  • Video upload test                                    │
│  • Storage verification                                 │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  CLEANUP (ALWAYS RUNS)                                  │
│  • Delete resource group                                │
│  • Purge azd environment                                │
│  • Verify no resources remain                           │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│  SUMMARY                                                │
│  • Deployment status                                    │
│  • Test results                                         │
│  • Cleanup confirmation                                 │
└─────────────────────────────────────────────────────────┘
```

## 🔐 Service Principal Details

**What it does**:
- Creates Azure resources (App Service, Storage, VNet)
- Deletes resource groups
- Runs Azure CLI commands

**Permissions needed**:
- Role: **Contributor** (on subscription)
- Can create/delete resources
- Cannot assign roles to other principals

**Security**:
- Scoped to specific subscription only
- Stored as GitHub encrypted secrets
- Only accessible by GitHub Actions
- Rotate secret every 6-12 months

## ✅ Verification Checklist

After setup, verify:

- [ ] All 4 GitHub secrets are configured
- [ ] Service principal can authenticate: `az login --service-principal ...`
- [ ] Pipeline appears in Actions tab
- [ ] First push to main triggers pipeline
- [ ] Pipeline deploys successfully
- [ ] Tests run and pass
- [ ] Resources are cleaned up (check Azure Portal)

## 🐛 Common Issues

### "Authentication failed"
→ Double-check all 4 secrets are correct (copy/paste from JSON output)

### "Unable to resolve action azure/login@v2"  
→ Change to `azure/login@v1` in `.github/workflows/ci-cd.yml`

### "Insufficient permissions"
→ Ensure service principal has **Contributor** role on subscription

### Tests timeout
→ Tests need ~60 seconds for large video upload (this is normal)

### Resources not deleted
→ Check Azure Portal for `rg-ci-test-*` resource groups and delete manually

## 📚 Full Documentation

- **[Complete Setup Guide](./CI-CD-SETUP.md)** - Detailed instructions and troubleshooting
- **[Pipeline Workflow](./.github/workflows/ci-cd.yml)** - Full workflow YAML
- **[Test Suite](../tests/e2e/)** - Playwright test code

## 💡 Tips

**Manual trigger**: Actions → Select workflow → "Run workflow"

**Test locally**:
```bash
pip install -r requirements-test.txt
playwright install chromium
export APP_URL="https://your-app.azurewebsites.net"
pytest tests/e2e/ -v
```

**View test artifacts**: Actions → Workflow run → Artifacts (on failure)

**Cost**: ~$0.01-0.05 per pipeline run (resources deleted after 20 minutes)

---

**Need help?** See [CI-CD-SETUP.md](./CI-CD-SETUP.md) for detailed troubleshooting.
