"""
End-to-End tests for Azure Video Upload Web Application.

Tests the complete user flow:
1. Application accessibility
2. Health endpoint verification
3. UI element presence
4. Video upload functionality
5. Success message validation
"""

import os
import pytest
from playwright.sync_api import Page, expect
import time


@pytest.fixture(scope="session")
def app_url():
    """Get the application URL from environment variable."""
    url = os.getenv("APP_URL")
    if not url:
        pytest.fail("APP_URL environment variable is not set")
    return url.rstrip("/")


@pytest.fixture(scope="session")
def test_video_path():
    """Get path to test video file."""
    # Look for video in data folder
    video_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "1416529-uhd_2560_1440_30fps.wmv")
    if not os.path.exists(video_path):
        pytest.fail(f"Test video not found at {video_path}")
    return os.path.abspath(video_path)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_endpoint_responds(self, page: Page, app_url: str):
        """Verify health endpoint returns 200 OK."""
        response = page.goto(f"{app_url}/health")
        assert response.status == 200, f"Health endpoint returned {response.status}"

    def test_health_endpoint_content(self, page: Page, app_url: str):
        """Verify health endpoint returns correct JSON structure."""
        page.goto(f"{app_url}/health")
        content = page.content()
        
        # Verify JSON response contains expected fields
        assert '"status"' in content, "Health response missing 'status' field"
        assert '"azure_storage"' in content, "Health response missing 'azure_storage' field"
        assert '"auth_method"' in content, "Health response missing 'auth_method' field"
        
        # Verify healthy status
        assert '"healthy"' in content or '"connected"' in content, "Health check not reporting healthy"


class TestApplicationUI:
    """Test the main application UI."""

    def test_homepage_loads(self, page: Page, app_url: str):
        """Verify homepage loads successfully."""
        response = page.goto(app_url)
        assert response.status == 200, f"Homepage returned {response.status}"

    def test_page_title(self, page: Page, app_url: str):
        """Verify page has correct title."""
        page.goto(app_url)
        expect(page).to_have_title("Video Upload to Azure Storage")

    def test_header_present(self, page: Page, app_url: str):
        """Verify main header is present."""
        page.goto(app_url)
        header = page.locator("h1")
        expect(header).to_be_visible()
        expect(header).to_contain_text("Video Upload")

    def test_upload_zone_visible(self, page: Page, app_url: str):
        """Verify upload drop zone is visible."""
        page.goto(app_url)
        drop_zone = page.locator("#dropZone")
        expect(drop_zone).to_be_visible()

    def test_upload_button_visible(self, page: Page, app_url: str):
        """Verify upload button is present."""
        page.goto(app_url)
        upload_btn = page.locator("#uploadBtn")
        expect(upload_btn).to_be_visible()

    def test_file_input_present(self, page: Page, app_url: str):
        """Verify file input element exists."""
        page.goto(app_url)
        file_input = page.locator("#fileInput")
        assert file_input.count() > 0, "File input element not found"

    def test_progress_bar_present(self, page: Page, app_url: str):
        """Verify progress bar element exists."""
        page.goto(app_url)
        progress = page.locator("#uploadProgress")
        assert progress.count() > 0, "Progress bar element not found"


class TestVideoUpload:
    """Test video upload functionality."""

    def test_file_selection(self, page: Page, app_url: str, test_video_path: str):
        """Verify file can be selected."""
        page.goto(app_url)
        
        # Set up file chooser listener
        file_input = page.locator("#fileInput")
        file_input.set_input_files(test_video_path)
        
        # Wait a moment for file processing
        page.wait_for_timeout(500)
        
        # Verify selected files display is updated
        selected_files = page.locator("#selectedFiles")
        expect(selected_files).not_to_be_empty()

    def test_upload_button_enabled_with_file(self, page: Page, app_url: str, test_video_path: str):
        """Verify upload button is enabled when file is selected."""
        page.goto(app_url)
        
        # Select file
        file_input = page.locator("#fileInput")
        file_input.set_input_files(test_video_path)
        
        page.wait_for_timeout(500)
        
        # Check if upload button is enabled
        upload_btn = page.locator("#uploadBtn")
        expect(upload_btn).to_be_enabled()

    def test_video_upload_complete_flow(self, page: Page, app_url: str, test_video_path: str):
        """Test complete video upload flow end-to-end."""
        page.goto(app_url)
        
        # Select video file
        file_input = page.locator("#fileInput")
        file_input.set_input_files(test_video_path)
        
        page.wait_for_timeout(500)
        
        # Click upload button
        upload_btn = page.locator("#uploadBtn")
        expect(upload_btn).to_be_enabled()
        upload_btn.click()
        
        # Wait for progress bar to appear
        progress_container = page.locator("#progressContainer")
        expect(progress_container).to_be_visible(timeout=5000)
        
        # Wait for upload to complete (with generous timeout for large file)
        # Look for success message
        success_indicator = page.locator(".alert-success, .success-message, text=success")
        expect(success_indicator).to_be_visible(timeout=60000)  # 60 second timeout
        
        # Verify success message content
        page_content = page.content().lower()
        assert "success" in page_content, "Success message not found after upload"

    def test_upload_shows_progress(self, page: Page, app_url: str, test_video_path: str):
        """Verify progress bar is shown during upload."""
        page.goto(app_url)
        
        # Select and start upload
        file_input = page.locator("#fileInput")
        file_input.set_input_files(test_video_path)
        
        page.wait_for_timeout(500)
        
        upload_btn = page.locator("#uploadBtn")
        upload_btn.click()
        
        # Check progress bar becomes visible
        progress_container = page.locator("#progressContainer")
        expect(progress_container).to_be_visible(timeout=5000)
        
        # Progress bar should have some width
        progress_bar = page.locator("#uploadProgress .progress-bar")
        expect(progress_bar).to_be_visible()


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_invalid_file_type_handling(self, page: Page, app_url: str):
        """Verify appropriate handling of invalid file types."""
        page.goto(app_url)
        
        # Try to upload a text file (invalid)
        # Note: This test assumes client-side validation exists
        # May need to adjust based on actual implementation
        
        # Create a temporary text file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is not a video file")
            temp_file = f.name
        
        try:
            file_input = page.locator("#fileInput")
            file_input.set_input_files(temp_file)
            
            page.wait_for_timeout(500)
            
            # Upload button should either be disabled or show error
            upload_btn = page.locator("#uploadBtn")
            
            # If button is enabled, clicking should show error
            if upload_btn.is_enabled():
                upload_btn.click()
                # Look for error message
                error_indicator = page.locator(".alert-danger, .error-message, text=error")
                expect(error_indicator).to_be_visible(timeout=10000)
        finally:
            # Cleanup temp file
            os.unlink(temp_file)


class TestResponsiveness:
    """Test responsive design."""

    def test_mobile_viewport(self, page: Page, app_url: str):
        """Verify app works on mobile viewport."""
        # Set mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(app_url)
        
        # Main elements should still be visible
        header = page.locator("h1")
        expect(header).to_be_visible()
        
        drop_zone = page.locator("#dropZone")
        expect(drop_zone).to_be_visible()

    def test_tablet_viewport(self, page: Page, app_url: str):
        """Verify app works on tablet viewport."""
        # Set tablet viewport
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto(app_url)
        
        # Main elements should be visible
        header = page.locator("h1")
        expect(header).to_be_visible()
        
        drop_zone = page.locator("#dropZone")
        expect(drop_zone).to_be_visible()
