from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
from collections.abc import Iterator
from pathlib import Path

import httpx
import pytest
from playwright.sync_api import Page, sync_playwright

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def live_server(tmp_path_factory: pytest.TempPathFactory) -> Iterator[tuple[str, Path]]:
    temp = tmp_path_factory.mktemp("e2e")
    config = temp / "config"
    shutil.copytree(Path("app/config"), config)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = os.environ.copy()
    env.update({"APP_MODE": "offline_demo", "APP_CONFIG_DIR": str(config)})
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--no-access-log",
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    base_url = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            if httpx.get(f"{base_url}/healthz", timeout=0.2).status_code == 200:
                break
        except httpx.HTTPError:
            time.sleep(0.05)
    else:
        output = process.stdout.read() if process.stdout else ""
        process.terminate()
        raise RuntimeError(f"Demo server failed to start: {output}")
    yield base_url, config
    process.terminate()
    process.wait(timeout=10)


@pytest.fixture(scope="module")
def browser_page(live_server: tuple[str, Path]) -> Iterator[tuple[Page, list[str]]]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        console_errors: list[str] = []
        page.on(
            "console",
            lambda message: (
                console_errors.append(message.text) if message.type == "error" else None
            ),
        )
        page.goto(live_server[0])
        page.wait_for_load_state("networkidle")
        yield page, console_errors
        browser.close()


def test_rendered_safe_poison_reset_flow(
    browser_page: tuple[Page, list[str]],
    live_server: tuple[str, Path],
) -> None:
    page, console_errors = browser_page
    page.get_by_role("button", name="Run scenario").click()
    page.get_by_text("ALLOW", exact=True).wait_for()
    assert page.locator("#proposal-action").text_content() == "SUMMARIZE_LOCALLY"

    page.get_by_role("button", name="Poison playbook").click()
    page.get_by_text("Playbook changed — authority unchanged").wait_for()
    page.get_by_role("button", name="Run again").click()
    page.get_by_text("DENY", exact=True).wait_for()
    assert page.locator("#proposal-action").text_content() == "UPLOAD_EXTERNAL"
    assert page.locator("#execution-result").text_content() == "No executor invoked."
    assert "CACHED ATTESTATION EXAMPLE" in (
        page.locator("#attestation-status").text_content() or ""
    )

    screenshot = Path("artifacts/e2e/demo-poisoned.png")
    screenshot.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(screenshot), full_page=True)

    page.get_by_role("button", name="Reset").click()
    page.get_by_text("Original guidance").wait_for()
    assert console_errors == []


def test_keyboard_controls_and_xss_render_as_text(
    browser_page: tuple[Page, list[str]],
    live_server: tuple[str, Path],
) -> None:
    page, _ = browser_page
    _, config = live_server
    payload = '<img src=x onerror="document.body.dataset.pwned=1">'
    playbook = config / "PLAYBOOK.md"
    playbook.write_text(payload, encoding="utf-8")
    page.reload()
    page.wait_for_load_state("networkidle")
    assert page.locator("#playbook-text").text_content() == payload
    assert page.locator("img").count() == 0
    assert page.locator("body").get_attribute("data-pwned") is None

    page.get_by_role("button", name="Run scenario").focus()
    page.keyboard.press("Enter")
    page.get_by_text("ALLOW", exact=True).wait_for()
    assert page.locator("#receipt").text_content() not in (None, "No decision yet.")
