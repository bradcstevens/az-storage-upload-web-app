# Analysis: CI/CD Pipeline Health Check Failure

**Document Type**: Bug Analysis  
**Created**: 2025-10-03  
**Status**: Analysis Complete  

---

## Executive Summary

The GitHub Actions CI/CD pipeline successfully deploys Azure resources but fails during the health check phase, waiting 5 minutes (30 attempts × 10 seconds) before timing out. The deployment completes successfully, App Service starts, but the application never responds to health checks.

---

## Problem Statement

**Symptom**: Pipeline health check fails after 30 attempts  
**Impact**: Pipeline marked as failed despite successful deployment  
**Frequency**: 100% of pipeline runs  
**Environment**: GitHub Actions + Azure App Service (West US 3)

### Error Message
```
❌ App failed to become ready after 30 attempts
Attempt 1-30: curl -sf https://app-w62zdl4j6beoy.azurewebsites.net/health fails
```

---

## Root Cause Analysis

### 🔴 Critical Issue #1: Health Endpoint Path Mismatch

**Location**: `.github/workflows/ci-cd.yml` line 111

**Current Code**:
```yaml
if curl -sf "$APP_URL/health" > /dev/null 2>&1; then
```

**Actual Endpoint**: `/api/health` (defined in `app.py` line 83)

**Impact**: Health check hits wrong endpoint (404 Not Found), causing infinite retry loop until timeout.

---

### 🟡 Issue #2: Port Configuration Inconsistency

**Locations**: 
- `app.py` line 241: `port = int(os.getenv('PORT', 5000))`
- `infra/modules/app-service.bicep` line 119: `value: '8000'`
- `infra/modules/app-service.bicep` line 128: `value: '8000'`
- `startup.txt`: `gunicorn --bind=0.0.0.0 --timeout 600 --workers 4 app:app`

**Analysis**:
- Gunicorn binds to 0.0.0.0 (all interfaces) - ✅ Correct
- App Service expects port 8000 via `WEBSITES_PORT` - ✅ Correct
- Flask app defaults to port 5000 but reads from `PORT` env var - ✅ Works in Azure
- Gunicorn command doesn't specify `--bind :8000` explicitly

**Status**: ⚠️ Works but fragile. Gunicorn reads PORT env var by default.

---

### 🟢 Issue #3: VNet Integration Impact (Potential)

**Configuration**: 
- App Service has VNet integration enabled
- Private endpoint configured for storage
- `vnetRouteAllEnabled: true` routes all outbound traffic through VNet

**Analysis**: 
- VNet integration affects **outbound** traffic from App Service to other Azure resources
- **Inbound** traffic to App Service still works via public endpoint
- Health checks from GitHub Actions runners (external) should work

**Status**: ✅ Not the root cause, but good to verify.

---

### 🔵 Issue #4: App Service Startup Time

**Observations from logs**:
```
19:06:30 - 19:12:16: "Deploying service web (Running build process)" - 5m 46s
19:10:55 - 19:12:16: "Starting runtime process" - 1m 21s
19:12:16: azd reports deployment complete
19:12:17 - 19:17:25: Health check attempts fail for 5m 08s
```

**Analysis**:
- Build process takes ~6 minutes (normal for Python with dependencies)
- Runtime starts at 19:10:55 but azd completes at 19:12:16
- Health checks start immediately after azd completes
- App may still be initializing when health checks begin

**Status**: ⚠️ Timing issue but not root cause. Wrong endpoint path is the blocker.

---

## Evidence

### Deployment Logs (Successful)
```
2025-10-03T19:12:16.7210692Z   (✓) Done: Deploying service web
2025-10-03T19:12:16.7211370Z   - Endpoint: https://app-w62zdl4j6beoy.azurewebsites.net/
2025-10-03T19:12:16.7212192Z SUCCESS: Your up workflow to provision and deploy to Azure completed in 12 minutes 22 seconds.
```

### Health Check Attempts (All Failed)
```
2025-10-03T19:12:17.3994092Z Attempt 1/30 - waiting 10 seconds...
2025-10-03T19:12:27.9870679Z Attempt 2/30 - waiting 10 seconds...
...
2025-10-03T19:17:15.7680005Z Attempt 30/30 - waiting 10 seconds...
2025-10-03T19:17:25.7696876Z ❌ App failed to become ready after 30 attempts
```

### Application Code
```python
# app.py line 83-93
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    azure_configured = blob_service_client is not None
    auth_method = 'managed-identity' if AZURE_STORAGE_ACCOUNT_NAME else 'not-configured'
    return jsonify({
        'status': 'healthy',
        'azure_storage': 'connected' if azure_configured else 'not_configured',
        'auth_method': auth_method,
        'timestamp': datetime.utcnow().isoformat()
    })
```

---

## Affected Components

| Component | Status | Issue |
|-----------|--------|-------|
| Azure App Service | ✅ Deployed | Running successfully |
| Flask Application | ✅ Running | Listening on correct port |
| Health Endpoint | ⚠️ Available | At `/api/health` not `/health` |
| GitHub Actions Workflow | ❌ Failing | Checks wrong path |
| Resource Cleanup | ✅ Working | Executes regardless of health check |

---

## Impact Assessment

### Current State
- ✅ Deployments complete successfully
- ✅ Infrastructure provisioned correctly
- ✅ App Service starts and runs
- ❌ Health checks fail (wrong endpoint)
- ❌ Playwright tests never run (skipped due to health check failure)
- ✅ Cleanup executes (guaranteed by `if: always()`)
- ❌ Pipeline marked as failed

### Business Impact
- **Severity**: Medium
- **Workaround**: Manual verification that app is running
- **Risk**: False negative - app works but pipeline reports failure
- **Blocker**: E2E tests never execute, limiting validation

---

## Recommended Solutions

### ✅ Solution 1: Fix Health Check Endpoint (RECOMMENDED)

**Change**: Update workflow to use correct path

**File**: `.github/workflows/ci-cd.yml`

**Line 111**: Change from:
```yaml
if curl -sf "$APP_URL/health" > /dev/null 2>&1; then
```

To:
```yaml
if curl -sf "$APP_URL/api/health" > /dev/null 2>&1; then
```

**Benefits**:
- ✅ Minimal change
- ✅ Matches actual endpoint
- ✅ No code changes required
- ✅ Preserves RESTful API convention

**Risks**: None

---

### ⚠️ Solution 2: Add Root Health Endpoint (ALTERNATIVE)

**Change**: Add `/health` endpoint to Flask app

**File**: `app.py`

**After line 93**: Add:
```python
@app.route('/health', methods=['GET'])
def health_check_root():
    """Root health check endpoint (alias)"""
    return health_check()
```

**Benefits**:
- ✅ Backwards compatible
- ✅ Provides both `/health` and `/api/health`
- ✅ Common pattern for container health checks

**Risks**:
- ⚠️ Duplicates endpoint logic
- ⚠️ Requires code deployment
- ⚠️ Adds maintenance burden

---

### 🔧 Solution 3: Improve Health Check Robustness

**Additional improvements** (apply with Solution 1):

1. **Add startup delay** (30 seconds before first check):
```yaml
- name: Wait for App Service to be ready
  run: |
    echo "⏳ Waiting 30 seconds for app startup..."
    sleep 30
    
    APP_URL="${{ steps.deploy.outputs.app_url }}"
    echo "Waiting for app to be responsive at $APP_URL..."
```

2. **Add diagnostic output on failure**:
```yaml
if [ $attempt -eq $max_attempts ]; then
  echo "❌ App failed to become ready after $max_attempts attempts"
  echo "Checking if app is running..."
  curl -v "$APP_URL/api/health" || true
  exit 1
fi
```

3. **Verify Azure App Service status**:
```yaml
# Before health checks
az webapp show --name "$APP_NAME" --resource-group "$RG_NAME" \
  --query "{state: state, hostNames: hostNames}" -o table
```

---

## Testing Strategy

### Verification Steps

1. **Test health endpoint locally**:
```bash
# Start app locally
python app.py

# Test endpoints
curl http://localhost:5000/api/health
curl http://localhost:5000/health  # Should 404
```

2. **Test against deployed app** (manual):
```bash
APP_URL="https://app-w62zdl4j6beoy.azurewebsites.net"
curl -v $APP_URL/api/health  # Should return 200 OK
curl -v $APP_URL/health       # Should return 404 Not Found
```

3. **Run updated pipeline**:
- Commit workflow changes
- Push to main branch
- Monitor pipeline execution
- Verify health check passes
- Verify tests execute

---

## Prevention Measures

### Code Review Checklist
- [ ] Health check endpoint paths match between app and deployment
- [ ] Port configurations consistent across app, startup, and Bicep
- [ ] Environment variables documented in deployment guides
- [ ] Health check timeouts appropriate for app startup time

### Documentation Updates
- [ ] Document health check endpoint in README
- [ ] Add API documentation for `/api/health`
- [ ] Update deployment docs with health check expectations
- [ ] Add troubleshooting guide for health check failures

### Monitoring
- [ ] Add Application Insights health check monitoring
- [ ] Set up availability tests in Azure Monitor
- [ ] Alert on health check failures in production
- [ ] Dashboard for CI/CD pipeline health

---

## Next Steps

1. **Immediate** (Today):
   - ✅ Complete this analysis
   - ⏳ Present findings to user
   - ⏳ Get approval for Solution 1
   - ⏳ Implement fix
   - ⏳ Test pipeline

2. **Short-term** (This Week):
   - Update documentation
   - Add diagnostic improvements
   - Verify tests execute successfully

3. **Long-term** (Next Sprint):
   - Add Application Insights monitoring
   - Create health check dashboard
   - Document lessons learned

---

## Related Documents

- `.github/workflows/ci-cd.yml` - Pipeline configuration
- `app.py` - Flask application with health endpoint
- `docs/CI-CD-SETUP.md` - CI/CD documentation
- `logs/failed-job-01.txt` - Failure logs

---

## Lessons Learned

1. **Endpoint consistency**: Always verify health check paths match between deployment scripts and application code
2. **Early testing**: Test health endpoints during local development
3. **Diagnostic logging**: Add verbose output to deployment scripts for faster debugging
4. **Separation of concerns**: Health checks shouldn't block resource cleanup (already handled correctly)
5. **Documentation**: Keep deployment docs synchronized with actual endpoint paths

---

## Conclusion

**Root Cause**: Health check endpoint path mismatch (`/health` vs `/api/health`)

**Recommended Fix**: Update workflow to use `/api/health` endpoint (Solution 1)

**Estimated Impact**: 
- Fix time: 5 minutes
- Test time: 15 minutes (1 pipeline run)
- Total downtime: 0 (deployment works, only health check affected)

**Confidence Level**: 🟢 High - Clear evidence, simple fix, low risk
