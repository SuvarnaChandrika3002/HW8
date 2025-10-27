import pytest
import threading
import time
import requests
import uvicorn
from playwright.sync_api import sync_playwright

# Import your FastAPI app directly
from main import app


@pytest.fixture(scope="session")
def fastapi_server():
    """
    Starts the FastAPI app in a background thread using uvicorn.
    This avoids subprocess timing issues on Windows.
    """
    server_url = "http://127.0.0.1:8000"

    # Start FastAPI in a background thread
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait until the server is ready
    timeout = 30
    start_time = time.time()
    while True:
        try:
            res = requests.get(server_url)
            if res.status_code == 200:
                print("✅ FastAPI server is running at", server_url)
                break
        except requests.exceptions.ConnectionError:
            if time.time() - start_time > timeout:
                raise RuntimeError("❌ FastAPI server failed to start in time.")
            time.sleep(1)

    yield server_url  # provide base URL to tests if needed

    # No explicit shutdown — daemon thread ends with pytest session
    print("🛑 FastAPI server thread stopped.")


@pytest.fixture(scope="session")
def playwright_instance_fixture():
    """
    Initialize Playwright once per session.
    """
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance_fixture):
    """
    Launch a headless Chromium browser once per session.
    """
    browser = playwright_instance_fixture.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def page(browser):
    """
    Creates a new browser page for each test function.
    """
    page = browser.new_page()
    yield page
    page.close()
