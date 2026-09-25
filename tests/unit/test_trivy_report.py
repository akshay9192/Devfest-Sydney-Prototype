from scripts.check_trivy_report import finding_summaries


def test_trivy_summary_reports_identity_without_secret_content() -> None:
    report = {
        "Results": [
            {
                "Target": "python-packages",
                "Vulnerabilities": [
                    {
                        "VulnerabilityID": "CVE-2099-0001",
                        "PkgName": "example",
                        "InstalledVersion": "1.0",
                        "FixedVersion": "1.1",
                    }
                ],
                "Secrets": [
                    {
                        "RuleID": "demo-token",
                        "Match": "DO_NOT_RENDER_THIS_VALUE",
                    }
                ],
            }
        ]
    }

    summaries = finding_summaries(report)

    assert summaries == [
        "python-packages: CVE-2099-0001 in example 1.0 (fixed: 1.1)",
        "python-packages: demo-token secret finding",
    ]
    assert "DO_NOT_RENDER_THIS_VALUE" not in " ".join(summaries)
