import subprocess
import time
import pytest
from playwright.sync_api import sync_playwright
import requests


@pytest.fixture(scope='session')
def fastapi_server():
    """
    Fixture to start the FastAPI server before E2E tests and stop it after tests complete.
    """
    # Start FastAPI app
    fastapi_process = subprocess.Popen(['python', 'main.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    server_url = 'http://127.0.0.1:8000/'
    timeout = 40  # give a bit more time for Windows startup
    start_time = time.time()
    server_up = False

    print("Starting FastAPI server...")

    # Poll until the server is responding
    while time.time() - start_time < timeout:
        try:
            response = requests.get(server_url)
            if response.status_code in (200, 404):
                # Treat 200 or 404 as success (server is alive)
                server_up = True
                print("✅ FastAPI server is up and running.")
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
