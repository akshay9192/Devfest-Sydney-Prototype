from __future__ import annotations

import argparse

from playwright.sync_api import sync_playwright


def main() -> None:
    parser = argparse.ArgumentParser(description="Exercise the demo through a running container")
    parser.add_argument("--base-url", default="http://127.0.0.1:18080")
    args = parser.parse_args()

    console_errors: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.on(
            "console",
            lambda message: (
                console_errors.append(message.text) if message.type == "error" else None
            ),
        )
        page.goto(args.base_url)
        page.wait_for_load_state("networkidle")
        page.locator("#run-safe").click()
        page.get_by_text("ALLOW", exact=True).wait_for()
        page.locator("#poison").click()
        page.get_by_text("Playbook poisoned").wait_for()
        page.locator("#run-again").click()
        page.get_by_text("DENY", exact=True).wait_for()
        execution_result = page.locator("#execution-result").text_content()
        if execution_result != "No executor invoked.":
            raise RuntimeError(f"Denied action reached an executor: {execution_result}")
        page.locator("#reset").click()
        page.get_by_text("Original guidance").wait_for()
        browser.close()

    if console_errors:
        raise SystemExit(f"Unexpected browser console errors: {console_errors}")
    print("Container browser smoke: PASS")


if __name__ == "__main__":
    main()
