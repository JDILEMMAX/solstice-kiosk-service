import pytest
import subprocess
import time
import os
import sys
from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from data.seed import seed_db

@pytest.fixture(scope="module")
def setup_environment():
    seed_db()
    
    project_root = os.path.dirname(os.path.dirname(__file__))

    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=project_root
    )
    
    time.sleep(3)
    
    yield
    
    process.terminate()
    process.wait()

def test_kiosk_e2e(setup_environment):
    frontend_path = f"file:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html'))}".replace("\\", "/")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(frontend_path)
        
        page.fill("#qr-input", "QR-ALICE-101")
        page.click("#scan-btn")
        
        page.wait_for_selector(".card.pending", timeout=5000)
        assert "Printing Badge..." in page.inner_text("#result-title")
        assert "Alice Smith" in page.inner_text("#attendee-details")
        
        page.wait_for_selector(".card.success", timeout=10000)
        assert "Checked In / Badge Printed" in page.inner_text("#result-title")
        
        page.fill("#qr-input", "QR-BOB-202")
        page.click("#scan-btn")
        
        page.wait_for_selector(".card.error", timeout=5000)
        error_msg = page.inner_text("#result-title")
        assert "Duplicate Scan" in error_msg
        
        page.wait_for_selector("#directory-table")
        rows = page.query_selector_all("#directory-table tbody tr")
        found_alice = False
        for row in rows:
            text = row.inner_text()
            if "QR-ALICE-101" in text:
                assert "CHECKED_IN" in text
                found_alice = True
        assert found_alice
        
        browser.close()
