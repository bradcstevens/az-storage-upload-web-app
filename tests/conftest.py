"""Pytest configuration for E2E tests."""

import pytest
from playwright.sync_api import Browser, BrowserContext, Page


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context with custom settings."""
    return {
        **browser_context_args,
        "viewport": {
            "width": 1280,
            "height": 720,
        },
        "locale": "en-US",
        "timezone_id": "America/Los_Angeles",
        "permissions": [],
        "color_scheme": "light",
    }


@pytest.fixture(scope="function")
def context(browser: Browser, browser_context_args):
    """Create a new browser context for each test."""
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext):
    """Create a new page for each test."""
    page = context.new_page()
    yield page
    page.close()
