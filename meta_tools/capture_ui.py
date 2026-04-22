import sys
import os
from playwright.sync_api import sync_playwright


def capture_screenshot(url: str, output_path: str = "ui_snapshot.png"):
    print(f"[Antigravity] Launching Playwright to capture: {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="networkidle")
            page.screenshot(path=output_path, full_page=True)
            print(f"[Antigravity] Successfully saved screenshot to {output_path}")
        except Exception as e:
            print(f"[Antigravity] Failed to capture {url}: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5173"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "ui_snapshot.png"

    # Ensure it saves into a predictable spot in the workspace if relative
    if not os.path.isabs(out_file):
        out_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), out_file)

    capture_screenshot(target_url, out_file)
