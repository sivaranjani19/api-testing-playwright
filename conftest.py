import os
import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Playwright, APIRequestContext

BASE_URL = "https://gorest.co.in/public/v2/"

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as playwright:
        yield playwright
@pytest.fixture(scope="session")
def api_request_context(playwright_instance):
    load_dotenv()
    token = os.getenv("GOREST_TOKEN")
    if not token:
        pytest.exit("CRITICAL: GOREST_TOKEN is missing or empty in .env file. Aborting test run.")
    request_context = playwright_instance.request.new_context(
        base_url=BASE_URL,
        extra_http_headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
    )
    yield request_context
    request_context.dispose()

@pytest.fixture(scope="session")
def unauthenticated_request_context(playwright_instance):
    request_context = playwright_instance.request.new_context(
        base_url=BASE_URL,
        extra_http_headers={
            "Content-Type": "application/json"
        },
    )
    yield request_context
    request_context.dispose()



