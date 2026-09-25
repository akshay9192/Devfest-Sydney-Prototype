from __future__ import annotations

import json

from app.services.attestation import ConfidentialSpaceAttestationProvider


def main() -> None:
    evidence = ConfidentialSpaceAttestationProvider().evidence()
    print(json.dumps(evidence.model_dump(mode="json"), indent=2))
    if not evidence.resource_release_allowed:
        raise SystemExit("Attestation/resource-release verification failed")


if __name__ == "__main__":
    main()
