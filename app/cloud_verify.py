from __future__ import annotations

import json

from app.services.attestation import ConfidentialSpaceAttestationProvider


def main() -> None:
    """Emit only safe release evidence and fail when live release is unavailable."""
    evidence = ConfidentialSpaceAttestationProvider().evidence()
    print(json.dumps(evidence.model_dump(mode="json"), sort_keys=True))
    if not evidence.resource_release_allowed:
        raise SystemExit("Attestation-gated protected resource release failed")


if __name__ == "__main__":
    main()
