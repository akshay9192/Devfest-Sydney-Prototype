from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from app.services.demo_service import DemoService
from app.services.proposer import DeterministicFakeProposer


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    source = Path(__file__).parents[1] / "app" / "config"
    destination = tmp_path / "config"
    shutil.copytree(source, destination)
    return destination


@pytest.fixture
def demo_service(config_dir: Path) -> DemoService:
    return DemoService(
        config_dir=config_dir,
        proposer=DeterministicFakeProposer(),
        offline=True,
    )
