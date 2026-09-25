from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _workflow_escape(value: object) -> str:
    return str(value).replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def finding_summaries(report: dict[str, Any]) -> list[str]:
    summaries: list[str] = []
    for result in report.get("Results") or []:
        target = result.get("Target", "container")
        for finding in result.get("Vulnerabilities") or []:
            fixed = finding.get("FixedVersion") or "no fix published"
            summaries.append(
                f"{target}: {finding.get('VulnerabilityID', 'unknown')} in "
                f"{finding.get('PkgName', 'unknown')} {finding.get('InstalledVersion', '?')} "
                f"(fixed: {fixed})"
            )
        for finding in result.get("Misconfigurations") or []:
            summaries.append(
                f"{target}: {finding.get('ID', 'unknown')} "
                f"{finding.get('Title', 'container misconfiguration')}"
            )
        for finding in result.get("Secrets") or []:
            summaries.append(f"{target}: {finding.get('RuleID', 'unknown')} secret finding")
    return summaries


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail CI on findings in a Trivy JSON report")
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    findings = finding_summaries(report)
    for finding in findings[:50]:
        print(f"::error title=Trivy container finding::{_workflow_escape(finding)}")
    if findings:
        raise SystemExit(f"Trivy found {len(findings)} high or critical issue(s)")
    print("Trivy container scan: PASS")


if __name__ == "__main__":
    main()
