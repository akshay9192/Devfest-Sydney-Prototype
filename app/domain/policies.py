from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StrictStr


class SystemPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: StrictInt
    allowed_actions: frozenset[StrictStr]
    external_destination_allowlist: frozenset[StrictStr]
    confidential_external_requires_confirmation: StrictBool
    maximum_request_characters: StrictInt = Field(gt=0, le=100_000)


class ValidatedUserPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: StrictInt
    deny_all_external: StrictBool
