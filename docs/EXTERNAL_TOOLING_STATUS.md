# External tooling status

Checked on 2026-09-25 on the local Windows host.

| Tool | Status | Version / resolution |
|---|---|---|
| Python | installed | 3.12.6 |
| Git | installed | 2.47.0.windows.2 |
| GitHub CLI | installed; authentication invalid | 2.97.0; `gh auth status` reports an invalid stored token. Git transport is independently authenticated. Interactive `gh auth login` is required to repair it. |
| Docker | missing locally | Container build, run, browser smoke, and Trivy scan are delegated to GitHub Actions. This is not reported as a local Docker pass. |
| Google Cloud CLI | missing | Cloud resource creation is blocked until the official CLI or Cloud Shell and an intended billed project are available. |
| Trivy | missing locally | CI uses the official Trivy action pinned to the immutable `v0.36.0` commit. |
| gitleaks | missing locally | CI runs the official `v8.30.1` container; the repository's independent scanner also runs locally and in CI. |
| GNU Make | missing locally | Commands are run directly with `.venv\\Scripts\\python.exe`; CI executes the same underlying commands. |
| Bash | missing locally | The deployment script must run from Cloud Shell or another reviewed Bash environment. |

No host security setting was weakened and no untrusted binary was installed.
