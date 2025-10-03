# Playwright Python Configuration

# This file serves as documentation for Playwright settings.
# Actual configuration is done via pytest.ini and command-line options.

## Browser Configuration
# Browser: Chromium (headless in CI, headed for local debugging)
# Viewport: 1280x720 default
# Device emulation: Configurable per test

## Test Configuration
# Base URL: Set via APP_URL environment variable
# Timeout: 30 seconds default for assertions
# Navigation timeout: 60 seconds for page loads
# Video: Retained only on failure
# Screenshots: Captured only on failure
# Trace: Not enabled by default (can enable for debugging)

## Running Tests

### CI/CD (GitHub Actions)
# pytest tests/e2e/ -v --headed=false --video=retain-on-failure --screenshot=only-on-failure

### Local Development
# With headed browser:
# pytest tests/e2e/ -v --headed

### Specific test:
# pytest tests/e2e/test_video_upload.py::TestVideoUpload::test_video_upload_complete_flow -v

### With video recording:
# pytest tests/e2e/ -v --video=on

### With screenshots:
# pytest tests/e2e/ -v --screenshot=on

### Debug mode (slow motion):
# pytest tests/e2e/ -v --headed --slowmo=1000

## Environment Variables Required
# APP_URL: Application URL to test against
# STORAGE_ACCOUNT: (Optional) For additional storage verification
# RESOURCE_GROUP: (Optional) For Azure resource verification
