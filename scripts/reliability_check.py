from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import time
from pathlib import Path

from app.services.demo_service import DemoService
from app.services.proposer import DeterministicFakeProposer


def main() -> None:
    parser = argparse.ArgumentParser(description="Repeat the complete offline demo flow")
    parser.add_argument("--cycles", type=int, default=10)
    args = parser.parse_args()
    if not 1 <= args.cycles <= 100:
        raise SystemExit("--cycles must be between 1 and 100")

    records: list[dict[str, object]] = []
    durations_ms: list[float] = []
    with tempfile.TemporaryDirectory(prefix="devfest-reliability-") as temporary:
        config = Path(temporary) / "config"
        shutil.copytree(Path("app/config"), config)
        service = DemoService(
            config_dir=config,
            proposer=DeterministicFakeProposer(),
            offline=True,
        )
        for cycle in range(1, args.cycles + 1):
            started = time.perf_counter()
            service.reset()
            safe = service.run(
                request_id=f"safe_{cycle:03}_a",
                explicit_user_confirmation=False,
            )
            service.reset()
            service.poison()
            poisoned = service.run(
                request_id=f"poison_{cycle:03}",
                explicit_user_confirmation=False,
            )
            denied_count = service.executor_call_count
            service.reset()
            final_safe = service.run(
                request_id=f"safe_{cycle:03}_b",
                explicit_user_confirmation=False,
            )
            passed = (
                safe.decision == "ALLOW"
                and poisoned.decision == "DENY"
                and denied_count == 0
                and final_safe.decision == "ALLOW"
                and service.executor_call_count == 1
            )
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            durations_ms.append(duration_ms)
            records.append(
                {
                    "cycle": cycle,
                    "passed": passed,
                    "duration_ms": duration_ms,
                    "safe": safe.decision,
                    "poisoned": poisoned.decision,
                    "final_safe": final_safe.decision,
                }
            )

    output = Path("artifacts/local_reliability.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    passed_cycles = sum(record["passed"] is True for record in records)
    slowest = max(durations_ms)
    print(
        f"Offline reliability: {passed_cycles}/{args.cycles} cycles passed; "
        f"slowest {slowest:.2f} ms"
    )
    if passed_cycles != args.cycles:
        raise SystemExit("Offline reliability invariant failed")


if __name__ == "__main__":
    main()
